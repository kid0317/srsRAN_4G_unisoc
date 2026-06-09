# 演示六：dev-iterate Skill + 环境配置 + 迭代闭环执行日志

**对应正文**：第三课 §3.2 创建 dev-iterate Skill + §3.3 环境配置 + §3.4 课堂演示：看日志
**预计时长**：9 分钟（含讲解）
**所在模块**：第三节「迭代闭环」

---

## 一、演示目标

分三部分展示迭代闭环的完整实现：（1）创建 dev-iterate Skill 定义编译→测试→修复流程；（2）配置 settings.json 权限白名单 + Stop Hook + PostToolUse Hook 构成三层守护；（3）展示完整迭代循环的执行日志，让学员看到三层守护如何协作。

**核心教学点**：
1. 测试映射表是 Skill 核心价值——改了 PHY 跑 PHY 测试，不是全量 1542 个
2. 模板错误只看最后 20 行——领域知识 AI 推导不出来
3. 重试限制（单个 5 轮/全局 10 轮）——不让 AI 死磕
4. 三层守护：PostToolUse Hook（格式化）→ Skill（SOP）→ Stop Hook（强制门禁）
5. "CLAUDE.md 是建议，Skill 是 SOP，Hook 是法律。三层才完整"

---

## 二、前置准备

### 2.1 环境要求

| 项目 | 要求 |
|------|------|
| 代码库 | `/root/course/code/ziguangzhanrui_2/srsRAN_4G`（已构建） |
| 构建 | `cmake --build build` 可执行，增量编译 ~5s |
| 测试 | `ctest --test-dir build` 可执行（1542 个测试） |
| clang-format | 已安装（PostToolUse Hook 使用） |
| 已有 Hook | `hooks/stop_check_syntax.py` 已存在 |

### 2.2 确认构建和测试环境

```bash
cd /root/course/code/ziguangzhanrui_2/srsRAN_4G
# 确认编译可用
cmake --build build -j$(nproc) 2>&1 | tail -3
# 确认冒烟测试可用
ctest --test-dir build -R "thread_pool_test" --output-on-failure 2>&1 | tail -5
```

### 2.3 课前部署 dev-iterate Skill（必做）

```bash
cd /root/course/code/ziguangzhanrui_2/srsRAN_4G
mkdir -p .claude/skills/dev-iterate
# 课前创建 SKILL.md（内容按演示中展示的 Description + 诊断表 + 测试映射表编写）
# 详见本文档 Part A Step 2-5 的完整内容
```

### 2.4 配置 PostToolUse Hook（推荐）

在 `.claude/settings.local.json` 中添加 PostToolUse Hook 以在日志中展示 "clang-format applied"：

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [{
          "type": "command",
          "command": "FILE=$(echo $TOOL_INPUT | jq -r '.file_path // empty'); case \"$FILE\" in *.c|*.cc|*.cpp|*.h|*.hpp) clang-format -i \"$FILE\" && echo 'clang-format applied' >&2 ;; esac; exit 0"
        }]
      }
    ]
  }
}
```

### 2.5 确认 Stop Hook

```bash
cat .claude/settings.local.json | python3 -m json.tool
# 确认 Stop Hook 已配置指向 hooks/stop_check_syntax.py
```

> **Stop Hook 说明**：项目中实际的 `hooks/stop_check_syntax.py` 只做语法检查（gcc -fsyntax-only）。正文 §3.3 展示的 `verify-build.sh` 示例包含编译+冒烟测试，覆盖范围更广。课堂讲解时说明："项目当前配置了语法检查 Hook，正文中的 verify-build.sh 是增强版——加了编译和冒烟测试。讲解以正文增强版为准，演示用项目实际配置。"

### 2.6 提前录制完整迭代日志（推荐）

```bash
# 课前在 srsRAN_4G 上执行一次完整的 dev-iterate 流程并保存日志
# 保存到：演示设计/第三课_演示六_迭代闭环执行日志.md
# 如果无法录制，使用 PPT 展示预期行为序列
```

---

## 三、演示步骤

### Part A：创建 dev-iterate Skill（4min live demo）

#### Step 1：用例规划（30s）

**口头说明**：
> "用例一句话：改了 C/C++ 代码就自动跑编译→测试→修复循环，直到通过。同样的四阶段方法——规划→开发→测试→迭代。"

#### Step 2：展示 Skill Description（30s）

```yaml
---
name: dev-iterate
description: >
  ALWAYS use this workflow after editing C/C++ source files (.c, .cc, .cpp, .h, .hpp).
  Handles the complete build-test-fix cycle. Do NOT skip compilation or testing.
  Do NOT declare task complete without passing verification.
---
```

**讲解**："指令式——ALWAYS、Do NOT。三个 Do NOT 确保 AI 不会跳过任何验证步骤。"

#### Step 3：增量编译 + 诊断表（1min）

展示 Skill 中的编译步骤和诊断表：

```
Step 1：增量编译
  命令：cmake --build build -j$(nproc)
  exit 0 → 进入 Step 2
  非 0   → 查诊断表修复后重新编译，最多 5 轮

错误诊断表：
  语法错误     expected ';'           → 直接修复
  类型不匹配   cannot convert         → 检查 C/C++ 混编
  模板错误     50-500 行展开          → ★ 只看最后 20 行
  链接错误     undefined ref          → 检查 target_link_libraries
  宏展开错误   HAL 宏多层嵌套         → 查看宏定义源头
```

**讲解**："**模板错误——AI 只看最后 20 行。这是领域知识，AI 推导不出来，你得告诉它。**"

#### Step 4：测试映射表（1min）——核心价值

展示测试映射表：

```
修改路径           测试命令
lib/src/phy/      ctest --test-dir build -L phy
lib/src/common/   ctest --test-dir build -R common
lib/src/rlc/pdcp/ ctest --test-dir build -R "rlc|pdcp"
srsenb/           ctest --test-dir build -L lte
srsgnb/           ctest --test-dir build -L nr
srsue/            ctest --test-dir build -R ue
```

**讲解**："**这张表是整个 Skill 的核心价值。** 改了 PHY 跑 PHY 测试，改了 eNodeB 跑 LTE 测试。靠 AI 猜——要么全量 1542 个等半天，要么漏掉关键测试。"

#### Step 5：测试失败诊断 + 重试限制（30s）

```
测试失败三分支判断：
  代码有 bug？    → 改代码
  测试本身过时？  → 改测试
  分不清？       → 停下来问人

重试限制：
  单个错误 ≤ 5 轮
  全局 ≤ 10 轮
  每次重试前必须说明改了什么、为什么改
```

**讲解**："没有重试限制，AI 一个错误来回改 20 次越改越乱。5 次不行——停下来报告。诊断式重试，不是盲目重试。"

#### 快速验证（30s）

口头说明触发测试：
- 正例："帮我加个 verify_mac 函数" → 应触发 dev-iterate
- 负例："帮我查 Coverity 告警" → 不应触发

---

### Part B：环境配置——三层守护（2min）

#### Step 6：settings.json 权限白名单（30s）

展示 permissions 配置：

```json
{
  "permissions": {
    "allow": [
      "Bash(cmake *)", "Bash(ctest *)", "Bash(make *)",
      "Bash(clang-format *)", "Bash(git *)", "Bash(./build/*)"
    ],
    "deny": [
      "Bash(rm -rf *)", "Bash(sudo *)", "Bash(curl *)", "Bash(wget *)"
    ]
  }
}
```

**讲解**："**能编译能测试，不能删文件不能装软件。** allow 是最小权限集，deny 是安全红线。"

#### Step 7：Stop Hook（1min）

展示已有的 `hooks/stop_check_syntax.py` 核心逻辑：

```
三个要点：
1. stop_hook_active 防无限循环——Hook 阻止后 Claude 修复再试，连续修不好就放行
2. exit 2 是 Hook 专用退出码——阻止并把错误信息反馈给 Claude
3. 只检查本次修改的 .c/.h 文件——不是全量扫描
```

**讲解**："Stop Hook 在 Agent 完成时自动运行一次。编译检查 + 冒烟测试——两道门禁。"

#### Step 8：PostToolUse Hook 示意（30s）

```
每次编辑 .c/.h 文件后自动 clang-format，不到 1 秒无感。
```

**讲解**："第一层守护——格式化。确定性 100%，无需 AI 参与。"

#### 三层守护总结

```
Layer 1: PostToolUse Hook — 每次编辑自动格式化（确定性 100%）
Layer 2: dev-iterate Skill — 编译→测试→修复流程（Agent SOP）
Layer 3: Stop Hook — 完成前强制编译+语法检查（确定性 100%）

"CLAUDE.md 是建议，Skill 是 SOP，Hook 是法律。三层才完整。"
```

---

### Part C：看执行日志（3min）

#### Step 9：展示完整迭代循环执行日志

**演示场景**：在 security.cc 增加 `srsran_security_verify_mac` 函数。

**方式**：展示提前跑好的执行日志（或现场演示）。

**预期行为序列**：

```
1. Agent 触发 dev-iterate Skill
2. 写函数 → PostToolUse Hook 自动 clang-format
   ─── Layer 1，日志显示 "clang-format applied" ───
3. 增量编译 — Skill Step 1
   cmake --build build -j$(nproc)
   → ~5 秒通过
4. 跑 common 测试 — Skill Step 2
   ctest --test-dir build -R common
   → 测试映射表匹配 lib/src/common/ → common 测试
   → 通过
5. Agent 宣布完成 → Stop Hook 触发
   ─── Layer 3，再验编译+语法检查 ───
   → hooks/stop_check_syntax.py 运行
   → 通过，放行
```

**讲解要点**：
- "每一步对应 Skill 的哪个 Step，三层守护分别在哪里介入——日志里都能看到"
- "如果编译失败？更好——Claude 查诊断表，按策略修复，最多 5 次"
- "诊断式重试，不是盲目重试——每次重试前说明改了什么"

---

## 四、演示节奏总览

| 时间点 | 部分 | 讲师动作 | 讲解要点 |
|--------|------|---------|---------|
| 0:00 | Skill | 用例规划一句话 | "改了代码就自动跑编译→测试→修复" |
| 0:30 | Skill | 展示 Description | "ALWAYS、Do NOT——指令式" |
| 1:00 | Skill | 展示诊断表 | "**模板错误只看最后 20 行**" |
| 2:00 | Skill | 展示测试映射表 | "**核心价值——改 PHY 跑 PHY 测试**" |
| 3:00 | Skill | 重试限制 | "5 次不行就停——诊断式重试" |
| 3:30 | 环境 | 展示权限白名单 | "能编译能测试，不能删不能 sudo" |
| 4:00 | 环境 | 展示 Stop Hook | "exit 2 阻止 + 防无限循环" |
| 4:30 | 环境 | 三层守护总结 | "建议/SOP/法律——三层才完整" |
| 5:00 | 日志 | 展示演示场景 | "在 security.cc 加 verify_mac 函数" |
| 5:30 | 日志 | 展示执行日志 | "格式化 → 编译 → 测试 → Stop Hook" |
| 7:00 | 日志 | 指出三层介入点 | "Layer 1 / Layer 2 / Layer 3 分别在哪" |
| 8:00 | 日志 | 失败场景说明 | "编译失败→查诊断表→修复→重试" |

---

## 五、关键讲解点

### 5.1 测试映射表

> "这张表是整个 Skill 的核心价值。改了 PHY 跑 PHY 测试，改了 eNodeB 跑 LTE 测试。靠 AI 猜——要么全量 1542 个等半天，要么漏掉关键测试。映射表是你们的领域知识。"

### 5.2 三层守护

> "CLAUDE.md 是建议，Skill 是 SOP，Hook 是法律。三层才完整。把'编译能过、测试能过'从口头约定变成机器强制。"

### 5.3 Boris Cherny 引言

> "Claude Code 创造者说：'Give Claude a way to verify its work — it will 2-3x the quality.' 编译器就是 AI 的眼睛——没有眼睛的 AI 写代码，跟蒙眼开车一个道理。"

---

## 六、失败预案

| 风险 | 概率 | 应对 |
|------|------|------|
| dev-iterate Skill 未触发 | 低 | 检查 Description 指令式格式 |
| 编译失败（真实错误） | 中 | 正好展示"编译失败子循环"的实际运行 |
| 测试超时（全量跑了 1542 个） | 中 | 说明"测试映射表没配对——这就是映射表的价值" |
| Stop Hook 阻止后死循环 | 低 | 展示 stop_hook_active 防循环机制 |
| 现场演示时间过长 | 高 | 改用提前录制的日志/截图展示 |

---

## 七、演示后恢复

```bash
cd /root/course/code/ziguangzhanrui_2/srsRAN_4G
git checkout -- .
git clean -fd
```

---

## 八、与课程原则的对应关系

| 课程概念 | 本演示如何体现 |
|---------|-------------|
| 迭代闭环五步（§3.1） | 开发→编译→测试→收集日志→反思迭代 |
| 编译错误诊断表（§3.1.1） | 五类错误 + AI 处理策略 |
| 测试四层（§3.1.2） | L1-L2 AI 完全自主，L4 是 AI 边界 |
| 四阶段方法 阶段二（§3.2） | dev-iterate Skill 开发全过程 |
| 三层守护（§3.3） | PostToolUse + Skill + Stop Hook |
| Boris Cherny 引言（§3.0） | "2-3x the quality" |
| Carlini 引言（§3.0） | "编译器是 AI 的眼睛" |
