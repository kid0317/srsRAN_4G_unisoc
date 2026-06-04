# 第二课：用好 Claude Code —— 课堂演示指南

> **课程**：紫光展锐 AI Coding 企业培训 · 第二课
> **代码库**：srsRAN_4G（开源 4G/5G 软件无线电协议栈，C/C++）
> **前置条件**：已安装 Claude Code、GCC/G++、CMake 3.5+、Python 3

本文档包含第二课的 **5 个实机演示**，覆盖 Agent Loop、可观测性、Context 管理、Hooks、Multi-Agent 五大主题。每个演示都可以独立运行，也可以按顺序串联。

---

## 环境准备（所有演示共用）

```bash
# 1. 进入项目目录（替换为你的实际路径）
cd ~/srsRAN_4G

# 2. 安装构建依赖（Ubuntu/Debian，首次需要）
sudo apt install -y build-essential cmake libfftw3-dev libmbedtls-dev \
    libboost-program-options-dev libconfig++-dev libsctp-dev

# 3. 构建项目（首次约 5-10 分钟，后续增量编译很快）
mkdir -p build && cd build
cmake -DCMAKE_BUILD_TYPE=Debug -DCMAKE_EXPORT_COMPILE_COMMANDS=ON ..
make -j$(nproc)
cd ..

# 4. 确认工具可用
gcc --version    # 需要 GCC
g++ --version    # 需要 G++
cmake --version  # 需要 CMake 3.5+
python3 --version  # 需要 Python 3
```

> 如果编译过程中报其他依赖缺失，参见 [srsRAN_4G 官方构建文档](https://docs.srsran.com/projects/4g/en/latest/general/source/1_installation.html)。

---

## 演示一：Agent Loop —— 一条指令，25 轮循环

> **对应课程**：第一小节「发出一条消息后，到底发生了什么」
>
> **你将看到**：Claude Code 如何在"思考→行动→观察"循环中，自主完成跨文件代码修改。

### 背景知识

srsRAN_4G 的错误码定义在 `lib/include/srsran/config.h`：

```c
#define SRSRAN_SUCCESS                  0
#define SRSRAN_ERROR                   -1
#define SRSRAN_ERROR_INVALID_INPUTS    -2
#define SRSRAN_ERROR_TIMEOUT           -3
#define SRSRAN_ERROR_INVALID_COMMAND   -4
#define SRSRAN_ERROR_OUT_OF_BOUNDS     -5
#define SRSRAN_ERROR_CANT_START        -6
#define SRSRAN_ERROR_ALREADY_STARTED   -7
#define SRSRAN_ERROR_RX_EOF            -8
```

8 个扁平的宏定义，值从 0 到 -8。`radio_recv_fnc`（`srsue/src/phy/sync.cc:972`）在射频接收失败时返回通用的 `SRSRAN_ERROR`（-1），无法区分具体原因。

### 执行步骤

**Step 1：确认干净状态**

```bash
git status    # 应无未提交修改
grep 'SRSRAN_ERROR_RADIO_RECV_FAIL' lib/include/srsran/config.h
# 应无输出（-9 尚不存在）
```

**Step 2：在 Claude Code 中发送指令**

在项目根目录打开终端，启动 Claude Code：
```bash
cd ~/srsRAN_4G   # 确保在项目根目录
claude            # 启动 Claude Code 交互模式
```

然后发送以下指令：

```
srsRAN_4G 的 sync::radio_recv_fnc 在射频接收失败时返回通用的 SRSRAN_ERROR，
请新增一个专用错误码 SRSRAN_ERROR_RADIO_RECV_FAIL 并让相关调用点正确处理它。
```

**Step 3：观察 Agent Loop 过程**

Claude Code 会自动执行多轮循环（实测约 25 轮），核心路径如下：

| 阶段 | Claude 在做什么 | 使用的工具 | 观察结果 |
|------|---------------|----------|---------|
| 阅读理解 | 搜索错误码定义 | Grep | 找到 `config.h`，8 个宏，-1 到 -8 |
| 阅读理解 | 定位 `radio_recv_fnc` | Grep | 找到 `sync.cc:972`，返回通用 `SRSRAN_ERROR` |
| 阅读理解 | 查看调用方 | Read | `run_idle_state:670` 用 `== SRSRAN_SUCCESS` 判断 |
| 阅读理解 | 搜索全局引用 | Grep | `search.cc` 回调 + `ue_sync.c` 的 `< 0` 检查 |
| 动手修改 | 新增错误码 | Edit | `config.h` 加 `#define SRSRAN_ERROR_RADIO_RECV_FAIL -9` |
| 动手修改 | 替换返回值 + 更新分支 | Edit | `sync.cc` 两处修改 |
| 自我验证 | 构建检查 | Bash | `cmake --build` 编译通过 |

**重点观察**：前 4-5 轮全在"阅读理解"，只有最后 2-3 轮才"动手改"——和优秀工程师的工作方式一样。

**Step 4：验证结果**

```bash
# 查看修改了哪些文件
git diff --stat
# 预期：2 files changed, 6 insertions(+), 2 deletions(-)

# 查看具体变更
git diff

# 构建验证
cd build && make -j$(nproc) && cd ..
# 预期：100% 编译通过
```

### 预期代码变更

**config.h**（新增 1 行）：
```c
#define SRSRAN_ERROR_RX_EOF            -8
#define SRSRAN_ERROR_RADIO_RECV_FAIL   -9   // ← 新增
```

**sync.cc**（修改 2 处）：

修改 1 —— `radio_recv_fnc` 返回专用错误码：
```cpp
// 第 981 行附近
if (not radio_h->rx_now(data, rf_timestamp)) {
    return SRSRAN_ERROR_RADIO_RECV_FAIL;  // 原来是 SRSRAN_ERROR
}
```

修改 2 —— `run_idle_state` 增加专门处理分支：
```cpp
// 第 670 行附近
int ret = radio_recv_fnc(dummy_buffer, &rx_time);
if (ret == SRSRAN_ERROR_RADIO_RECV_FAIL) {
    Warning("SYNC:  Radio receive failed while in IDLE_RX");
} else if (ret >= SRSRAN_SUCCESS) {
    srsran::console("SYNC:  Receiving from radio while in IDLE_RX\n");
}
```

### 设计思路

1. **为什么新增 -9 而不改现有值？** 递减分配保持连续性，不影响已有代码。
2. **为什么只改了 2 个文件？** Claude 分析了 `ue_sync.c` 的调用链，发现 C 层用 `< 0` 判断——`-9 < 0` 天然成立，不需要改。**不改，反而是正确的决策。**
3. **为什么最后要跑构建？** Agent 的自我校验——改完代码必须验证能编译通过。

### 恢复（完成后）

```bash
git restore lib/include/srsran/config.h srsue/src/phy/sync.cc
```

---

## 演示二：Langfuse 可观测性 —— 亲眼看到 Agent 的思考过程

> **对应课程**：第一小节「Langfuse 实证」
>
> **你将看到**：Agent Loop 每一轮的完整执行轨迹——Prompt、工具调用、返回值。

### 背景知识

Langfuse 是开源的 LLM 可观测性平台。配置后，Claude Code 的每条指令都会在 Langfuse 中留下完整的 Trace。

### 前置配置

Langfuse 的连接信息已配置在 `.claude/settings.local.json`：

```json
{
  "env": {
    "LANGFUSE_PUBLIC_KEY": "pk-lf-cc-workspace-bot-local",
    "LANGFUSE_SECRET_KEY": "sk-lf-cc-workspace-bot-local",
    "LANGFUSE_BASE_URL": "http://localhost:3000"
  }
}
```

如果你有自己的 Langfuse 实例，替换上面的 Key 和 URL 即可。没有 Langfuse 的话可以跳过本演示（不影响其他演示）。

### 执行步骤

**Step 1**：确保 Langfuse 服务运行中

```bash
curl -s http://localhost:3000/api/public/health
# 预期：{"status":"OK","version":"3.x.x"}
```

**Step 2**：执行演示一的指令（或任意 Claude Code 指令）

**Step 3**：打开 Langfuse 界面 `http://localhost:3000`

**Step 4**：在 Trace 列表中找到最近的执行记录，点击进入

### 看什么

| 区域 | 要观察的内容 | 教学意义 |
|------|------------|---------|
| Trace 列表 | 执行时间、总耗时、Token 消耗 | 每条指令都可追溯 |
| Span 树 | 多轮嵌套结构 | Agent Loop 循环的可视化 |
| Generation 详情 | prompt 完整内容 | CLAUDE.md 如何被注入上下文 |
| Tool Call 详情 | 工具名 + 输入参数 + 返回结果 | Claude 搜了什么、读了哪些行 |
| Token 统计 | 缓存读/写比例 | 多轮循环的缓存命中率（通常 95%+） |

### 关键认知

CLAUDE.md 的内容被拼装在 prompt 的**稳定段**中——内容不变就能命中 prompt cache，每一轮循环都低成本复用。这就是为什么缓存命中率能到 95% 以上。

---

## 演示三：CLAUDE.md 四层体系 —— Context 管理的核心

> **对应课程**：第二小节「CLAUDE.md 的四层加载优先级」
>
> **你将看到**：企业级、用户级、项目级、本地级四层 CLAUDE.md 各放什么、怎么协作。

### 背景知识

CLAUDE.md 的每一行，都会在每次 Session 中注入上下文。它有四层，从低到高叠加：

```
优先级（从低到高）：
┌────────────────────────────────────┐
│ ④ 本地级：CLAUDE.local.md         │ ← 最高，不入 git
├────────────────────────────────────┤
│ ③ 项目级：CLAUDE.md               │ ← 提交 git，团队共享
├────────────────────────────────────┤
│ ② 用户级：~/.claude/CLAUDE.md      │ ← 跨项目生效
├────────────────────────────────────┤
│ ① 企业级：/etc/claude-code/CLAUDE.md │ ← IT 下发，不可违反
└────────────────────────────────────┘
```

### 查看四层示例

本项目已包含项目级和本地级，另有企业级和用户级的示例文件：

**第三层：项目级** `./CLAUDE.md`（约 50 行，提交 git，团队共享）

```bash
cat CLAUDE.md
```

包含：模块结构表、编码约定、代码质量工具（Coverity/MISRA/clang-format）、构建命令、Skill 路由表。Skill 路由指向的文件标注了"待创建"——这些将在第三课中实际创建。

核心设计原则：
- **Less is More**——每一行都有"房租"，占上下文空间
- **具体优于泛泛**——不写"遵循最佳实践"，写"新增错误码递减分配"
- **渐进式披露**——核心信息在 CLAUDE.md，详细步骤指向 Skill 文件

**第四层：本地级** `./CLAUDE.local.md`（不提交 git，个人便签）

```bash
cat CLAUDE.local.md
```

包含：当前 JIRA 任务号、分支名、交叉编译目标、本地环境信息。**每天开工前花 30 秒更新，任务结束就清空。**

**第一层：企业级**（安全铁律）

```bash
cat examples/CLAUDE_企业级示例.md
```

```markdown
## 安全红线（违反即阻断 CR）
- 禁止使用 gets()/sprintf()/strcpy() → 用 fgets/snprintf/strncpy
- 禁止裸 new/malloc → 使用 RAII 或团队封装的内存池
- 密钥、IMSI/Ki 不得出现在代码或注释中

## 合规要求
- MISRA C:2012 强制规则必须遵守
- Coverity 扫描 Critical/High 告警必须在合入前清零
```

由 IT 统一下发。即使项目层怎么写，也不能违反这些安全红线。

**第二层：用户级**（个人偏好）

```bash
cat examples/CLAUDE_用户级示例.md
```

```markdown
- 所有对话使用中文，commit message 用英文
- 改动超过 3 个文件时，先列出修改计划让我确认
- 遇到不确定的 3GPP 条款，标注 "VERIFY:" 让我人工确认
```

跨项目生效。你的个人舒适区。

### 关键认知

- 四层关系：企业级 = 铁律，用户级 = 偏好，项目级 = 共识，本地级 = 便签
- 后面的覆盖前面的，但**不能违反企业级的安全红线**
- 项目级 CLAUDE.md 40 多行就够——关键是每一行都是 AI **必须知道**的信息

---

## 演示四：Stop Hook —— C 代码语法检查门禁

> **对应课程**：第五小节「Hooks——安装好的被动技能」
>
> **你将看到**：Claude Code 改完代码后，Stop Hook 自动触发语法检查；有错误时 Claude 自动修复。

### 背景知识

Hook 是**被动技能**——装好就永远触发，100% 确定性执行，不需要模型判断。

Stop Hook 在 Claude 说"任务完成"时触发，独有 `continue:true` 能力——可以强制 Claude 继续修复。

Hook 脚本的约定：
- `exit 0` = 检查通过，正常结束
- `exit 2` = 有意阻止，Claude 读取 stdout 中的 JSON 并尝试修复
- `stdout` = 给 Claude 读的 JSON
- `stderr` = 给人看的调试信息（**不要混淆！**）

### 文件说明

**Hook 脚本**：`hooks/stop_check_syntax.py`

```bash
cat hooks/stop_check_syntax.py
```

核心逻辑：
1. `git diff --name-only` 找到本次修改的 C/C++ 文件
2. C 文件用 `gcc -fsyntax-only -std=c11`，C++ 文件用 `g++ -fsyntax-only -std=c++14`
3. 有语法错误 → `exit 2` + stdout JSON 告诉 Claude 去修
4. 全部通过 → `exit 0`

关键设计点：
- **防死循环**：检查 `stop_hook_active` 字段，如果已经重试过就放行
- **stderr/stdout 分离**：调试日志走 stderr，JSON 走 stdout——如果混淆了，Claude 会把调试文本当指令解析
- **语言适配**：脚本用 Python 写只是方便演示，你完全可以用 C、Shell 或任何语言

**Hook 配置**：`.claude/settings.local.json`

```json
{
  "hooks": {
    "Stop": [{
      "matcher": "",
      "hooks": [{
        "type": "command",
        "command": "python3 hooks/stop_check_syntax.py"
      }]
    }]
  }
}
```

### 手动测试 Hook

不需要启动 Claude Code，可以直接测试三种场景：

**场景 1：无 C/C++ 文件修改 → 通过**

```bash
echo '{}' | python3 hooks/stop_check_syntax.py
# stdout: {"decision": "allow"}
# stderr: No C/C++ files modified, skipping syntax check.
# exit code: 0
```

**场景 2：有正确修改 → 通过**

```bash
# 先制造一个正确的修改
echo '#define SRSRAN_ERROR_RADIO_RECV_FAIL -9' >> lib/include/srsran/config.h
echo '{}' | python3 hooks/stop_check_syntax.py
# stdout: {"decision": "allow"}
# stderr: Syntax check passed for 1 file(s).
# exit code: 0

# 恢复
git restore lib/include/srsran/config.h
```

**场景 3：有语法错误 → 阻止**

```bash
# 故意引入语法错误
echo 'int broken syntax here' >> lib/include/srsran/config.h
echo '{}' | python3 hooks/stop_check_syntax.py
# stdout: {"decision": "block", "continue": true, "errors": [...]}
# stderr: Syntax check found 1 error(s)...
# exit code: 2

# 恢复
git restore lib/include/srsran/config.h
```

### 在 Claude Code 中体验

让 Claude 修改 C/C++ 代码，完成后 Stop Hook 会自动触发。如果引入了语法错误，你会看到 Claude **自动修复并重新检查**——整个过程无需人工干预。

### 进阶方向

实际嵌入式项目中，`gcc -fsyntax-only` 可能因缺少外部库头文件而误报。更工业级的做法：

```bash
# 使用 compile_commands.json + clang-tidy
clang-tidy --quiet -p build/ <file>
```

CMake 已配置 `-DCMAKE_EXPORT_COMPILE_COMMANDS=ON`，`build/compile_commands.json` 包含了完整的编译参数。

---

## 演示五：Multi-Agent —— 三个独立视角审查同一份代码

> **对应课程**：第六小节「Multi-Agent——一个人变一支团队」
>
> **你将看到**：3 个 AI Agent 从安全、质量、架构三个角度并行审查同一份代码变更。

### 背景知识

Multi-Agent 的第一价值不是并行，是**上下文隔离**。

> 让写代码的人 Review 自己的代码，就像让厨师品尝自己做了一百次的菜——品不出问题。

每个 SubAgent 启动时上下文是干净的，不带先入为主，只把结论带回来。

### 自定义 Agent 定义

三个只读审查 Agent 已创建在 `.claude/agents/` 下：

**安全审查 Agent** `.claude/agents/security-reviewer.md`：

```bash
cat .claude/agents/security-reviewer.md
```

```yaml
---
name: security-reviewer
description: 审查代码变更的安全性。
tools: Read, Grep, Glob          # 注意：没有 Edit/Write/Bash
model: sonnet                     # 指定用 Sonnet 模型
---
```

审查维度：缓冲区溢出（CWE-120）、MISRA 合规、错误码值域冲突、密钥泄漏。

**代码质量 Agent** `.claude/agents/code-quality-reviewer.md`：

审查维度：命名规范、编号连续性、单元测试覆盖、日志完整性。

**架构兼容性 Agent** `.claude/agents/architecture-reviewer.md`：

审查维度：调用链兼容性（`< 0` 检查）、ABI 兼容、跨模块一致性。

关键设计点：
- **tools 只有 Read/Grep/Glob**——物理上只能看、不能改。比"希望你别改"更可靠。
- **model: sonnet**——审查任务用 Sonnet 就够了，不需要 Opus。省成本。

### 执行步骤

**Step 1：应用演示一的代码变更**

```bash
# 方式一：先跑完演示一，保留修改不恢复（推荐）

# 方式二：手动修改（如果已恢复干净状态）
# 在 lib/include/srsran/config.h 的 #define SRSRAN_ERROR_RX_EOF -8 后面加一行：
#   #define SRSRAN_ERROR_RADIO_RECV_FAIL -9
# 在 srsue/src/phy/sync.cc:981 将 return SRSRAN_ERROR 改为 return SRSRAN_ERROR_RADIO_RECV_FAIL
# 在 srsue/src/phy/sync.cc:670 修改 if 分支（详见演示一的"预期代码变更"）
```

确认修改已应用：
```bash
git diff --stat
# 预期：config.h (+1), sync.cc (+5, -2)
```

**Step 2：在 Claude Code 中启动多 Agent Review**

```
基于当前的 git diff，请并行启动 3 个子 Agent 进行 review：

1. 安全审查 Agent（/security-reviewer）：值域冲突？未处理的错误路径？
2. 代码质量 Agent（/code-quality-reviewer）：命名规范？编号连续？测试覆盖？
3. 架构兼容性 Agent（/architecture-reviewer）：ue_sync.c 的 < 0 检查兼容吗？

请汇总三份报告，标注每个发现的优先级。
```

**Step 3：观察结果**

三个 Agent 会各自独立审查代码。实测中，**所有 3 个 Agent 独立发现了同一个核心问题**：

> C 层 `ue_sync.c:722` 的 `receive_samples()` 函数将所有负返回值统一映射为 `SRSRAN_ERROR`(-1)。新增的 `-9` 在 `< 0` 检查中会被正确拦截（不会崩溃），但错误码的区分信息在这里被吞没了。

这意味着新错误码的区分能力仅在 `run_idle_state` 直接调用路径中生效，在 CAMPING 状态（通过 `srsran_ue_sync_zerocopy` 间接调用）下会被抹成通用 `-1`。

**这个发现是真实的、非平凡的**——人类 Code Review 容易漏掉这种跨 C/C++ 边界的错误码吞没。

### 预期 Review 报告

| Agent | 核心发现 | 级别 |
|-------|---------|------|
| 安全审查 | `ue_sync.c:722` 将 -9 覆写为 -1，CAMPING 路径无法感知新错误码 | Critical |
| 安全审查 | `run_idle_state` 中 -8 到 -1 的负值被静默忽略 | High |
| 代码质量 | 命名和编号均正确（-9 连续递减） | Pass |
| 代码质量 | 缺少对新错误码的单元测试 | Low |
| 架构兼容 | `< 0` 检查天然兼容 -9，无崩溃风险 | Pass |
| 架构兼容 | NR 路径 `sync_sa` 未同步更新 | Low |

### 恢复

```bash
git restore lib/include/srsran/config.h srsue/src/phy/sync.cc
```

---

## 项目文件总览

```
srsRAN_4G/
├── 课堂演示README.md               ← 本文件
│
├── CLAUDE.md                       ← 演示三：项目级 CLAUDE.md
├── CLAUDE.local.md                 ← 演示三：本地级（不入 git）
│
├── .claude/
│   ├── settings.local.json         ← Langfuse 配置 + Hook 配置
│   └── agents/
│       ├── security-reviewer.md    ← 演示五：安全审查 Agent
│       ├── code-quality-reviewer.md
│       └── architecture-reviewer.md
│
├── hooks/
│   └── stop_check_syntax.py        ← 演示四：Stop Hook 脚本
│
├── examples/
│   ├── CLAUDE_企业级示例.md         ← 演示三：企业级 CLAUDE.md 示例
│   └── CLAUDE_用户级示例.md         ← 演示三：用户级 CLAUDE.md 示例
│
├── build/                          ← 构建产出
│
├── lib/include/srsran/config.h     ← 错误码定义（演示一核心文件）
├── srsue/src/phy/sync.cc           ← PHY 同步模块（演示一核心文件）
└── [srsRAN_4G 其他代码...]
```

---

## 速查：课程核心概念与演示映射

| 课程概念 | 一句话 | 哪个演示体现 |
|---------|--------|------------|
| Agent Loop | 思考→行动→观察的循环，一条指令自动跑 25 轮 | 演示一 |
| ReAct 范式 | Reasoning + Acting，所有 Agentic AI 的标准范式 | 演示一 |
| LLM 可观测性 | 每一轮循环的 Prompt 和工具调用都可追溯 | 演示二 |
| Prompt Cache | CLAUDE.md 在稳定段中，缓存命中率 95%+ | 演示二 |
| CLAUDE.md 四层 | 企业级=铁律，用户级=偏好，项目级=共识，本地级=便签 | 演示三 |
| Less is More | CLAUDE.md 每一行都有"房租"，项目级 40 行就够 | 演示三 |
| 渐进式披露 | 核心放 CLAUDE.md，详细步骤指向 Skill 文件 | 演示三 |
| Hook = 被动技能 | 装好就永远触发，100% 确定性，不靠模型自觉 | 演示四 |
| exit 2 + continue:true | Stop Hook 独有能力，强制 Claude 继续修复 | 演示四 |
| 上下文隔离 | 每个 SubAgent 上下文干净，不带先入为主 | 演示五 |
| 物理只读 | tools 不含 Edit/Write/Bash，物理上做不到修改 | 演示五 |
| 多模型分层 | 审查用 Sonnet，架构决策用 Opus，搜索用 Haiku | 演示五 |
