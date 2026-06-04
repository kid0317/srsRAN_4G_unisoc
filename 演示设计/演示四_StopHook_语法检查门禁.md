# 演示四：Stop Hook —— C 代码语法检查门禁

**对应正文**：第二课 §6.5（实战演示：Stop Hook——C 代码语法检查门禁）
**预计时长**：5–7 分钟
**所在模块**：第五小节「Hooks——安装好的被动技能」
**前置依赖**：已讲完 §6.1–§6.4（Hook 的三大阵营 + 三个核心 Hook）

---

## 一、演示目标

配置一个 Stop Hook，让 Claude Code 在"任务完成"时自动检查本次修改的 C/C++ 文件语法，不通过则自动修复。

**核心教学点**：
1. Hook 是**被动技能**——装好就永远触发，100% 确定性
2. Stop Hook 独有 `continue:true` 能力——可以强制 Claude 继续修复
3. 调试信息走 stderr，JSON 结果走 stdout——最常见的坑

---

## 二、前置准备

### 2.1 环境要求

| 项目 | 要求 |
|------|------|
| 代码库 | `/root/course/code/ziguangzhanrui_2/srsRAN_4G` |
| 编译器 | `gcc` 和 `g++`（用于 `fsyntax-only` 检查） |
| Python | Python 3.x（Hook 脚本用 Python 编写） |

确认编译器可用：
```bash
gcc --version && g++ --version
```

### 2.2 创建 Hook 脚本

在 srsRAN_4G 项目下创建 `hooks/stop_check_syntax.py`：

```python
#!/usr/bin/env python3
"""Stop Hook: 检查本次修改的 C/C++ 文件语法。

返回值约定：
  exit 0  = 通过，Claude 正常结束
  exit 2  = 有意阻止，Claude 读取 stdout JSON 并自动修复
  其他非零 = 脚本自身出错，不阻止

注意：调试信息走 stderr，stdout 专供 Claude 读 JSON。
"""

import subprocess
import sys
import json
import os

def get_modified_files():
    """获取本次 git diff 中修改的 C/C++ 文件"""
    try:
        result = subprocess.run(
            ['git', 'diff', '--name-only', 'HEAD'],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0:
            result = subprocess.run(
                ['git', 'diff', '--name-only'],
                capture_output=True, text=True, timeout=10
            )
        files = result.stdout.strip().split('\n')
        c_extensions = ('.c', '.cc', '.cpp', '.h', '.hpp')
        return [f for f in files if f and any(f.endswith(ext) for ext in c_extensions)]
    except Exception as e:
        print(f"Warning: git diff failed: {e}", file=sys.stderr)
        return []

def get_include_paths():
    """从 compile_commands.json 或默认路径获取 include 路径"""
    compile_db = 'build/compile_commands.json'
    if os.path.exists(compile_db):
        return []  # compile_commands.json 存在时由编译器自行处理
    # 默认 include 路径（srsRAN_4G 项目）
    return ['-I', 'lib/include', '-I', 'srsue/hdr', '-I', 'srsenb/hdr', '-I', 'build']

def check_syntax(filepath):
    """对单个文件做语法检查"""
    if filepath.endswith('.c'):
        compiler = 'gcc'
        std_flag = '-std=c11'
    else:
        compiler = 'g++'
        std_flag = '-std=c++14'

    cmd = [compiler, '-fsyntax-only', std_flag] + get_include_paths() + [filepath]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True, text=True, timeout=30
        )
        return result.returncode == 0, result.stderr.strip()
    except Exception as e:
        print(f"Warning: syntax check failed for {filepath}: {e}", file=sys.stderr)
        return True, ""  # 检查失败不阻止

def main():
    # 读取 stdin 获取 Hook 上下文
    try:
        hook_input = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, EOFError):
        hook_input = {}

    # 防死循环：如果已经是 Stop Hook 触发的重试，直接放行
    stop_hook_active = hook_input.get('stop_hook_active', False)
    if stop_hook_active:
        print(json.dumps({"decision": "allow"}))
        sys.exit(0)

    # 获取修改的 C/C++ 文件
    files = get_modified_files()
    if not files:
        print("No C/C++ files modified, skipping syntax check.", file=sys.stderr)
        print(json.dumps({"decision": "allow"}))
        sys.exit(0)

    # 逐个检查语法
    errors = []
    for f in files:
        if not os.path.exists(f):
            continue
        ok, err_msg = check_syntax(f)
        if not ok:
            errors.append({"file": f, "error": err_msg})

    if errors:
        # 有语法错误 → exit 2 阻止，并通过 stdout 告诉 Claude 去修
        error_detail = "\n".join(
            f"  {e['file']}: {e['error']}" for e in errors
        )
        print(f"Syntax check found {len(errors)} error(s):", file=sys.stderr)
        print(error_detail, file=sys.stderr)

        # stdout: Claude 读这个 JSON
        print(json.dumps({
            "decision": "block",
            "reason": f"Syntax errors in {len(errors)} file(s). Please fix them.",
            "continue": True,
            "errors": errors
        }))
        sys.exit(2)
    else:
        print(f"Syntax check passed for {len(files)} file(s).", file=sys.stderr)
        print(json.dumps({"decision": "allow"}))
        sys.exit(0)

if __name__ == '__main__':
    main()
```

### 2.3 配置 settings.json

在项目的 `.claude/settings.local.json` 中添加 Hook 配置：

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "python3 hooks/stop_check_syntax.py"
          }
        ]
      }
    ]
  }
}
```

### 2.4 测试 Hook 脚本

```bash
cd /root/course/code/ziguangzhanrui_2/srsRAN_4G
echo '{}' | python3 hooks/stop_check_syntax.py
# 预期：stdout 输出 {"decision": "allow"}，stderr 输出 "No C/C++ files modified"
```

---

## 三、演示流程

### Step 1：展示 Hook 配置（1min）

**讲述**：
> "我现在给 srsRAN_4G 配置一个 Stop Hook。逻辑很简单——如果这次会话修改了 C/C++ 文件，结束前自动跑一次语法检查。不通过的话，Claude 自己去修。这个脚本用 Python 写只是因为方便演示，你们完全可以用 C、Shell 或任何语言写——核心是 exit code 约定和 stdout JSON 格式。"

展示 settings.local.json 中的 Hook 配置 + 脚本核心逻辑：
```python
# 1. git diff --name-only 找到本次修改的文件
# 2. 过滤出 .c / .cc / .cpp / .h 文件
# 3. .c 用 gcc -fsyntax-only -std=c11，C++ 用 g++ -fsyntax-only -std=c++14
# 4. 有错误 → exit(2) + stdout 输出 JSON（Claude 读这个）+ stderr 输出人类可读详情
# 5. 全部通过 → exit(0)
```

> ⚠️ **讲师注意**：正文 §6.5 伪代码中写的是"stderr 输出错误详情"，但实际上 Claude 读的是 **stdout JSON**。讲课时请按 §6.4 的返回值约定讲——"调试信息走 stderr，JSON 结果走 stdout"。

### Step 2：触发演示（3–4min）

给 Claude Code 一条会引入语法问题的指令（或让它做一次修改）：

**方案 A（推荐）**：复用演示一的指令
```
srsRAN_4G 的 sync::radio_recv_fnc 在射频接收失败时返回通用的 SRSRAN_ERROR，请新增一个专用错误码 SRSRAN_ERROR_RADIO_RECV_FAIL 并让相关调用点正确处理它。
```

Claude 完成修改后说"任务完成"→ Stop Hook 触发。

**方案 B（可控性更高）**：手动引入语法错误
```bash
# 提前在 sync.cc 引入一个语法错误
sed -i 's/return SRSRAN_ERROR;/return SRSRAN_ERROR/' srsue/src/phy/sync.cc
```
然后让 Claude 做一个简单任务，任务完成时 Stop Hook 检测到语法错误。

### Step 3：观察自动修复（1–2min）

**预期效果**：
1. Claude 说"任务完成"
2. Stop Hook 触发 → `gcc -fsyntax-only` 检查
3. 发现错误 → exit 2 + JSON 反馈
4. Claude 读到错误信息 → 自动修复
5. 再次尝试 Stop → 检查通过 → 正常结束

**讲解**：
> "整个过程**完全自动**——你不需要手动告诉 Claude 去检查。Hook 是被动技能，装好就永远生效。"

### Step 4：强调防死循环 + 工程进阶方案（1min）

> "Stop Hook 要注意**防死循环**：脚本里检查了 `stop_hook_active` 字段，如果已经重试过一次就放行。不然 Claude 修不好的话会无限循环。"

> "补充一个工程进阶方向：今天的演示用的是 `gcc -fsyntax-only`，只能检查自有头文件闭合的简单文件。你们实际项目依赖大量外部库头文件，裸 fsyntax-only 会误报。**更工业级的做法**是用 CMake 生成的 `compile_commands.json` 配合 `clang-tidy`——自动获取正确的 include path、宏定义和编译选项。我们课上的 cmake 参数已经包含了 `-DCMAKE_EXPORT_COMPILE_COMMANDS=ON`，生成好了 `compile_commands.json`。改造 Hook 脚本很简单——把 `gcc -fsyntax-only` 换成 `clang-tidy --quiet -p build/`。"

---

## 四、关键讲解点

### 4.1 Hook vs Rules 的本质区别

> "用正则表达式匹配语法错误——命中即阻止。没有'可能''大概'的中间地带。**Hook 是法律，Rules 是建议。**"

**课程原则映射**：§6.4 "Hook = 确定性执行"

### 4.2 stderr vs stdout 的分工

> "调试信息**必须走 stderr**，stdout 专供 Claude 读 JSON。混淆 stdout/stderr 是 Hook 开发最常见的坑。如果调试日志跑进了 stdout，Claude 会把你的调试信息当成指令去执行。"

**课程原则映射**：§6.4 返回值约定

### 4.3 Stop Hook 的独有能力

> "`continue:true` 是 Stop Hook 独有的——PreToolUse 和 PostToolUse 没有这个能力。它让 Claude 在被拦截后**自动继续修复**，而不是直接退出。"

**课程原则映射**：§6.4 Stop Hook 核心能力

### 4.4 与米哈游案例的关联

> "还记得刚才讲的米哈游 200 万一晚吗？如果他们有成本管控的 Hook——比如 Token 超过阈值就 exit 2 终止——就不会出那种事。Hook 不靠模型自觉，用代码做护栏。"

**课程原则映射**：§6.2 米哈游案例

---

## 五、脚本文件位置

```
/root/course/code/ziguangzhanrui_2/srsRAN_4G/
├── .claude/
│   ├── hooks/
│   │   └── stop_check_syntax.py     ← Hook 脚本
│   └── settings.local.json           ← Hook 配置
```

---

## 六、失败预案

| 风险 | 概率 | 应对 |
|------|------|------|
| gcc 不可用 | 低 | `apt install gcc g++` 或用 PPT 讲解 |
| Hook 不触发 | 中 | 检查 settings.json 路径是否正确、脚本是否有执行权限 |
| Claude 修不好 | 低 | 防死循环机制保证最多重试一次后放行 |
| 语法检查误报 | 低 | 确保 C 文件用 `-std=c11`，C++ 文件用 `-std=c++14` |
| fsyntax-only 因缺少 include path 全部报错 | 高 | 方案一：只检查 .h 头文件（宏定义不需要 include path）；方案二：切 PPT 讲解 |
| Claude 修不好后放行 | 中 | 话术："这就是防死循环的保底——修不好先放行。实际工程中可把未修复错误输出到日志" |

---

## 七、演示后恢复

```bash
cd /root/course/code/ziguangzhanrui_2/srsRAN_4G
git checkout -- .     # 恢复代码修改
# Hook 配置保留（后续演示可能复用）
```

---

## 八、与课程原则的对应关系

| 课程概念 | 本演示如何体现 |
|---------|-------------|
| 被动技能（§6.1） | Hook 装好后自动触发，无需模型判断 |
| 确定性执行（§6.4） | gcc 语法检查=确定性，不依赖 LLM |
| Stop Hook continue:true（§6.4） | 学员亲眼看到 Claude 被拦截后自动修复 |
| 防死循环（§6.5） | stop_hook_active 字段检查 |
| stderr/stdout 分工（§6.4） | 脚本中清晰分离调试信息和 JSON 输出 |
| "AI 可能忘记你的提醒，但 Hook 不会忘"（§6.2） | 不需要在 prompt 里写"记得检查语法" |
