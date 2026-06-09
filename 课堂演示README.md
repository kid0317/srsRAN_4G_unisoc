# 紫光展锐 AI Coding 企业培训 —— 课堂演示手册

> **培训**：紫光展锐 AI Coding 企业落地培训（5 课 × 2 小时）
> **代码库**：srsRAN_4G（开源 4G/5G 软件无线电协议栈，C/C++）
> **演示代码根目录**：`/root/course/code/ziguangzhanrui_2/srsRAN_4G/`
> **版本**：v1（2026-06-08）

---

## 目录

- [第一课：AI Coding 企业落地全景](#第一课ai-coding-企业落地全景)
- [第二课：Claude Code 深度解析](#第二课claude-code-深度解析)
- [第三课：构建 AI 原生代码库](#第三课构建-ai-原生代码库)（✅ 完整演示步骤）
- [第四课：AI 原生开发工作流](#第四课ai-原生开发工作流)
- [第五课：全自动化与组织治理](#第五课全自动化与组织治理)

---

## 全局课前准备

每次上课前确认：

```bash
# 1. Claude Code 可用
claude --version

# 2. 代码库可构建
cd /root/course/code/ziguangzhanrui_2/srsRAN_4G
cmake --build build -j$(nproc) 2>&1 | tail -5

# 3. 测试可运行
cd build && ctest -R common --output-on-failure | tail -5

# 4. Python 环境
python3 -c "from mcp.server.fastmcp import FastMCP; print('FastMCP OK')"

# 5. 格式化工具
clang-format --version
```

---

## 第一课：AI Coding 企业落地全景

> **主题**：AI Coding 行业趋势、标杆案例、三层体系（工具/流程/组织）、成熟度模型
> **演示时长**：约 15min（以 PPT 讲解为主）
> **PPTX**：`AI Coding企业落地培训-第一课.pptx`

### 演示概览

| 编号 | 演示名称 | 时长 | 说明 |
|------|---------|------|------|
| 1-1 | Claude Code 基础操作演示 | 5min | 打开项目、提问、代码导航 |
| 1-2 | Cursor/Copilot/Claude Code 对比 | 5min | 三工具同一任务对比 |
| 1-3 | 成熟度自评表填写 | 5min | 引导学员定位当前水平 |

> 📝 第一课以理论认知为主，演示步骤待补充。

---

## 第二课：Claude Code 深度解析

> **主题**：ReAct 范式、Harness 五层架构、记忆系统、Sub-Agent、Skills/Hooks/Rules、Headless + MCP
> **演示时长**：约 45min（5 个实机演示）
> **PPTX**：`AI Coding企业落地培训-第二课_终版.pptx`
> **代码库**：srsRAN_4G（开源 4G/5G 软件无线电协议栈，C/C++）
> **前置条件**：已安装 Claude Code、GCC/G++、CMake 3.5+、Python 3

### 演示概览

| 编号 | 演示名称 | 时长 | 说明 |
|------|---------|------|------|
| 2-1 | Agent Loop | 10min | 一条指令，25 轮循环 |
| 2-2 | Langfuse 可观测性 | 5min | 亲眼看到 Agent 的思考过程 |
| 2-3 | CLAUDE.md 四层体系 | 10min | Context 管理的核心 |
| 2-4 | Stop Hook 语法守护 | 10min | C 代码语法检查门禁 |
| 2-5 | Multi-Agent 并行审查 | 10min | 三个独立视角审查同一份代码 |

### 环境准备（所有演示共用）

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

### 演示 2-1：Agent Loop —— 一条指令，25 轮循环

> **对应课程**：第一小节「发出一条消息后，到底发生了什么」
>
> **你将看到**：Claude Code 如何在"思考→行动→观察"循环中，自主完成跨文件代码修改。

#### 背景知识

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

#### 执行步骤

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
# 预期：2 files changed, 7 insertions(+), 2 deletions(-)

# 查看具体变更
git diff

# 构建验证
cd build && make -j$(nproc) && cd ..
# 预期：100% 编译通过
```

#### 预期代码变更

**config.h**（新增 1 行）：
```c
#define SRSRAN_ERROR_RX_EOF            -8
#define SRSRAN_ERROR_RADIO_RECV_FAIL   -9   // ← 新增
```

**sync.cc**（修改 2 处）：

修改 1 —— `radio_recv_fnc` 返回专用错误码（并补一行日志）：
```cpp
// 第 981 行附近
if (not radio_h->rx_now(data, rf_timestamp)) {
    phy_logger.error("SYNC:  radio reception failed");
    return SRSRAN_ERROR_RADIO_RECV_FAIL;  // 原来是 SRSRAN_ERROR
}
```

修改 2 —— `run_idle_state` 增加专门处理分支：
```cpp
// 第 670 行附近
int recv_ret = radio_recv_fnc(dummy_buffer, &rx_time);
if (recv_ret == SRSRAN_ERROR_RADIO_RECV_FAIL) {
    Error("SYNC:  Radio reception failed while in IDLE_RX");
} else if (recv_ret > SRSRAN_SUCCESS) {
    srsran::console("SYNC:  Receiving from radio while in IDLE_RX\n");
}
```

#### 设计思路

1. **为什么新增 -9 而不改现有值？** 递减分配保持连续性，不影响已有代码。
2. **为什么只改了 2 个文件？** Claude 分析了 `ue_sync.c` 的调用链，发现 C 层用 `< 0` 判断——`-9 < 0` 天然成立，不需要改。**不改，反而是正确的决策。**
3. **为什么最后要跑构建？** Agent 的自我校验——改完代码必须验证能编译通过。

#### 恢复（完成后）

```bash
git restore lib/include/srsran/config.h srsue/src/phy/sync.cc
```

---

### 演示 2-2：Langfuse 可观测性 —— 亲眼看到 Agent 的思考过程

> **对应课程**：第一小节「Langfuse 实证」
>
> **你将看到**：Agent Loop 每一轮的完整执行轨迹——Prompt、工具调用、返回值。

#### 背景知识

Langfuse 是开源的 LLM 可观测性平台。配置后，Claude Code 的每条指令都会在 Langfuse 中留下完整的 Trace。

#### 前置配置

Langfuse 的连接信息已配置在 `.claude/settings.local.json`：

```json
{
  "env": {
    "LANGFUSE_PUBLIC_KEY": "pk-lf-cc-workspace-bot-local",
    "LANGFUSE_SECRET_KEY": "sk-lf-cc-workspace-bot-local",
    "LANGFUSE_BASE_URL": "http://localhost:3000",
    "CC_LF_APP_ID": "srsran-4g-dev",
    "CC_LF_FRAMEWORK_SESSION_ID": "srsran-4g-interactive",
    "CC_LF_CHANNEL_KEY": "claude-code-cli",
    "CC_LF_USER_OPEN_ID": "BennieWoodcec@greenmail.net"
  }
}
```

前 3 个是 Langfuse 的连接凭证；后 4 个 `CC_LF_*` 是上报维度标签——`APP_ID` 区分应用、`FRAMEWORK_SESSION_ID` 串起同一会话的多条 Trace、`CHANNEL_KEY` 标记来源渠道、`USER_OPEN_ID` 关联用户。配好后在 Langfuse 里可以按这些维度筛选。

如果你有自己的 Langfuse 实例，替换上面的 Key 和 URL 即可。没有 Langfuse 的话可以跳过本演示（不影响其他演示）。

#### 执行步骤

**Step 1**：确保 Langfuse 服务运行中

```bash
curl -s http://localhost:3000/api/public/health
# 预期：{"status":"OK","version":"3.x.x"}
```

**Step 2**：执行演示一的指令（或任意 Claude Code 指令）

**Step 3**：打开 Langfuse 界面 `http://localhost:3000`

**Step 4**：在 Trace 列表中找到最近的执行记录，点击进入

#### 看什么

| 区域 | 要观察的内容 | 教学意义 |
|------|------------|---------|
| Trace 列表 | 执行时间、总耗时、Token 消耗 | 每条指令都可追溯 |
| Span 树 | 多轮嵌套结构 | Agent Loop 循环的可视化 |
| Generation 详情 | prompt 完整内容 | CLAUDE.md 如何被注入上下文 |
| Tool Call 详情 | 工具名 + 输入参数 + 返回结果 | Claude 搜了什么、读了哪些行 |
| Token 统计 | 缓存读/写比例 | 多轮循环的缓存命中率（通常 95%+） |

#### 关键认知

CLAUDE.md 的内容被拼装在 prompt 的**稳定段**中——内容不变就能命中 prompt cache，每一轮循环都低成本复用。这就是为什么缓存命中率能到 95% 以上。

---

### 演示 2-3：CLAUDE.md 四层体系 —— Context 管理的核心

> **对应课程**：第二小节「CLAUDE.md 的四层加载优先级」
>
> **你将看到**：企业级、用户级、项目级、本地级四层 CLAUDE.md 各放什么、怎么协作。

#### 背景知识

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

#### 查看四层示例

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
### 安全红线（违反即阻断 CR）
- 禁止使用 gets()/sprintf()/strcpy() → 用 fgets/snprintf/strncpy
- 禁止裸 new/malloc → 使用 RAII 或团队封装的内存池
- 密钥、IMSI/Ki 不得出现在代码或注释中

### 合规要求
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

#### 关键认知

- 四层关系：企业级 = 铁律，用户级 = 偏好，项目级 = 共识，本地级 = 便签
- 后面的覆盖前面的，但**不能违反企业级的安全红线**
- 项目级 CLAUDE.md 40 多行就够——关键是每一行都是 AI **必须知道**的信息

---

### 演示 2-4：Stop Hook —— C 代码语法检查门禁

> **对应课程**：第五小节「Hooks——安装好的被动技能」
>
> **你将看到**：Claude Code 改完代码后，Stop Hook 自动触发语法检查；有错误时 Claude 自动修复。

#### 背景知识

Hook 是**被动技能**——装好就永远触发，100% 确定性执行，不需要模型判断。

Stop Hook 在 Claude 说"任务完成"时触发，独有 `continue:true` 能力——可以强制 Claude 继续修复。

Hook 脚本的约定：
- `exit 0` = 检查通过，正常结束
- `exit 2` = 有意阻止，Claude 读取 stdout 中的 JSON 并尝试修复
- `stdout` = 给 Claude 读的 JSON
- `stderr` = 给人看的调试信息（**不要混淆！**）

#### 文件说明

**Hook 脚本**：`hooks/stop_check_syntax.py`

```bash
cat hooks/stop_check_syntax.py
```

核心逻辑：
1. `git diff --name-only` 找到本次修改的 C/C++ 文件（`.c/.cc/.cpp/.h/.hpp`）
2. C 文件用 `gcc -fsyntax-only -std=c11`，C++ 文件用 `g++ -fsyntax-only -std=c++14`
3. 有语法错误 → `exit 2` + stdout JSON 告诉 Claude 去修
4. 全部通过 → `exit 0`（仅在 stderr 打印一行汇总，stdout 不输出 JSON）

关键设计点：
- **防死循环**：检查 `stop_hook_active` 字段，如果已经重试过就放行
- **stderr/stdout 分离**：调试日志走 stderr，阻断 JSON 才走 stdout——如果混淆了，Claude 会把调试文本当指令解析
- **include 路径对齐真实构建**：srsRAN 的 `#include` 以仓库根为基准（如 `srsue/hdr/phy/sync.h`），脚本把仓库根、`lib/include`、`srsue/hdr`、`srsenb/hdr` 都加进 `-I`；若 `build/` 存在还会补上生成头文件目录（`build/lib/include`），尽量贴近 `compile_commands.json` 的真实编译环境
- **语言适配**：脚本用 Python 写只是方便演示，你完全可以用 C、Shell 或任何语言

**Hook 配置**：`.claude/settings.local.json`（与演示二的 `env` 同处一个文件）

```json
{
  "hooks": {
    "Stop": [{
      "matcher": "",
      "hooks": [{
        "type": "command",
        "command": "python3 \"$CLAUDE_PROJECT_DIR/hooks/stop_check_syntax.py\""
      }]
    }]
  }
}
```

> `$CLAUDE_PROJECT_DIR` 是 Claude Code 注入的环境变量，指向项目根目录。用它拼绝对路径，无论从哪个工作目录触发 Hook 都能正确定位脚本——比相对路径 `hooks/stop_check_syntax.py` 更稳健。

#### 手动测试 Hook

不需要启动 Claude Code，可以直接测试三种场景：

**场景 1：无 C/C++ 文件修改 → 通过**

```bash
echo '{}' | python3 hooks/stop_check_syntax.py
# stdout:（无）
# stderr: No C/C++ files modified, skipping syntax check.
# exit code: 0
```

**场景 2：有正确修改 → 通过**

```bash
# 先制造一个正确的修改
echo '#define SRSRAN_ERROR_RADIO_RECV_FAIL -9' >> lib/include/srsran/config.h
echo '{}' | python3 hooks/stop_check_syntax.py
# stdout:（无，放行时不输出 JSON）
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
# stdout: {"decision": "block", "reason": "Syntax errors in 1 file(s)...", "continue": true}
# stderr: Syntax check found 1 error(s) in N file(s): ...
# exit code: 2

# 恢复
git restore lib/include/srsran/config.h
```

> 放行（exit 0）时脚本只往 stderr 写一行汇总、**stdout 不输出任何 JSON**；只有阻断（exit 2）时才往 stdout 写 `{"decision":"block","reason":...,"continue":true}`。Claude 读 stdout 的 JSON 来决定是否继续修复。

#### 在 Claude Code 中体验

让 Claude 修改 C/C++ 代码，完成后 Stop Hook 会自动触发。如果引入了语法错误，你会看到 Claude **自动修复并重新检查**——整个过程无需人工干预。

#### 进阶方向

实际嵌入式项目中，`gcc -fsyntax-only` 可能因缺少外部库头文件而误报。更工业级的做法：

```bash
# 使用 compile_commands.json + clang-tidy
clang-tidy --quiet -p build/ <file>
```

CMake 已配置 `-DCMAKE_EXPORT_COMPILE_COMMANDS=ON`，`build/compile_commands.json` 包含了完整的编译参数。

---

### 演示 2-5：Multi-Agent —— 三个独立视角审查同一份代码

> **对应课程**：第六小节「Multi-Agent——一个人变一支团队」
>
> **你将看到**：3 个 AI Agent 从安全、质量、架构三个角度并行审查同一份代码变更。

#### 背景知识

Multi-Agent 的第一价值不是并行，是**上下文隔离**。

> 让写代码的人 Review 自己的代码，就像让厨师品尝自己做了一百次的菜——品不出问题。

每个 SubAgent 启动时上下文是干净的，不带先入为主，只把结论带回来。

#### 自定义 Agent 定义

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

#### 执行步骤

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
# 预期：config.h (+1), sync.cc (+6, -2)
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

#### 预期 Review 报告

| Agent | 核心发现 | 级别 |
|-------|---------|------|
| 安全审查 | `ue_sync.c:722` 将 -9 覆写为 -1，CAMPING 路径无法感知新错误码 | Critical |
| 安全审查 | `run_idle_state` 中 -8 到 -1 的负值被静默忽略 | High |
| 代码质量 | 命名和编号均正确（-9 连续递减） | Pass |
| 代码质量 | 缺少对新错误码的单元测试 | Low |
| 架构兼容 | `< 0` 检查天然兼容 -9，无崩溃风险 | Pass |
| 架构兼容 | NR 路径 `sync_sa` 未同步更新 | Low |

#### 恢复

```bash
git restore lib/include/srsran/config.h srsue/src/phy/sync.cc
```

---

### 项目文件总览

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

### 速查：课程核心概念与演示映射

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


---

## 第三课：构建 AI 原生代码库

> **主题**：AI 原生代码库四大支柱——知识建设、Skill × MCP、迭代闭环、安全防护
> **演示时长**：约 44min（8 个演示）
> **正文**：`正文/第三课_完整正文_v5.md`
> **演示设计**：`/root/course/code/ziguangzhanrui_2/srsRAN_4G/演示设计/`

### 演示总览

| 编号 | 演示名称 | 时长 | 模块 | 对应正文 |
|------|---------|------|------|---------|
| 三-1 | CLAUDE.md 初始化 | 4min | 知识建设 | §1.2 |
| 三-2A | HTML 全景可视化 | 4min | 知识建设 | §1.3（给人看） |
| 三-2B | CODEMAP 生成 + LLM Wiki 回扣 | 4min | 知识建设 | §1.3（给 Agent 看）+ §1.0 回扣 |
| 三-3 | AST 索引与 clangd LSP | 4min | 知识建设 | §1.4 |
| 三-4 | Coverity MCP Server 搭建 | 5min | Skill × MCP | §2.4.2 |
| 三-5 | Coverity Skill 开发+测试 | 9min | Skill × MCP | §2.4.3-2.4.4 |
| 三-6 | dev-iterate Skill + 迭代闭环 | 9min | 迭代闭环 | §3.2-3.4 |
| 三-7 | 多 Agent 并行安全审查 | 5min | 安全防护 | §4.1.3 |

### 课前准备清单（CRITICAL）

```bash
# ===== P0 必做 =====

# 演示三-1: 备份 CLAUDE.md
ls /root/course/code/ziguangzhanrui_2/srsRAN_4G/CLAUDE.md

# 演示三-3: clangd + LSP 插件
clangd --version
ls /root/course/code/ziguangzhanrui_2/srsRAN_4G/build/compile_commands.json
# 课前在 Claude Code 中执行:
# /plugin install clangd-lsp@claude-plugins-official
# /plugin list  → 确认 clangd-lsp: enabled
# 启动一次让索引完成

# 演示三-4: FastMCP + mock 数据
python3 -c "from mcp.server.fastmcp import FastMCP; print('OK')"
python3 -c "import json; d=json.load(open('/root/course/code/ziguangzhanrui_2/srsRAN_4G/coverity-mcp-server/mock_findings.json')); print(f'{len(d)} findings loaded')"

# 演示三-6: dev-iterate Skill + clang-format + Stop Hook
ls /root/course/code/ziguangzhanrui_2/srsRAN_4G/.claude/skills/dev-iterate/SKILL.md
clang-format --version
ls /root/course/code/ziguangzhanrui_2/srsRAN_4G/hooks/stop_check_syntax.py

# 演示三-7: Agent 定义文件
ls /root/course/code/ziguangzhanrui_2/srsRAN_4G/.claude/agents/*.md

# ===== P1 推荐 =====

# 演示三-7: cppcheck 对比数据
which cppcheck || echo "建议安装: apt install cppcheck"

# 演示三-3: 提前跑无 LSP 对比数据
```

### 演示逻辑递进

```
第一节：知识建设（16min 演示 + 8min PPT）
  [PPT] §1.0 LLM Wiki 方法论（Karpathy 推文引入，三实体/三操作/两文件/chip-wiki/RAG 决策）
  [PPT] §1.1 四层知识全景图（LLM Wiki → 四层结构过渡）
  演示三-1 → CLAUDE.md（§1.2 Layer 1）—— AI 认识项目基础信息
  演示三-2A → HTML 全景视图（§1.3 Layer 2 给人看）—— 团队成员理解项目
  演示三-2B → CODEMAP 生成（§1.3 Layer 2 给 Agent 看）—— AI 理解代码结构（回扣 §1.0 三操作）
  演示三-3 → AST 索引 + LSP（§1.4 Layer 3）—— AI 拥有编译器级搜索
  [PPT] §1.5 增量维护 —— 知识保持新鲜

第二节：Skill × MCP（14min 演示 + 20min PPT + 2min 休息）
  [PPT] Skill/MCP 判断标准 + 场景全景 + 四阶段理论
  演示三-4 → MCP 搭建 + ToolSearch —— 给 AI "手"
  演示三-5 → Skill 开发+测试 —— 给 AI "脑"

第三节：迭代闭环（9min 演示 + 8min PPT）
  [PPT] 效益对比 + 完整流程
  演示三-6 → dev-iterate Skill + 三层守护 —— AI 自主编译测试修复

第四节：安全防护（5min 演示 + 14min PPT）
  [PPT] CVE 冲击 + 安全知识库 + 架构
  演示三-7 → 多 Agent 安全审查 —— AI 受控安全运行
  [PPT] PreToolUse Hook 过程安全
```

### 各演示间串联要点

| 衔接点 | 前→后 | 讲师串场词 |
|--------|-------|----------|
| Layer 1→2（人） | 三-1→三-2A | "CLAUDE.md 是给 AI 的入口——但团队成员也需要全景理解" |
| Layer 2（人→Agent） | 三-2A→三-2B | "HTML 给人看全局——CODEMAP 给 Agent 看精确位置。还记得刚才讲的 LLM Wiki 三操作？CODEMAP 就是 Ingest 的产物" |
| Layer 2→3 | 三-2B→三-3 | "CODEMAP 是知识层——AST 是编译器层，两者互补" |
| 知识→工具 | 三-3→三-4 | "知识建设让 AI 理解代码——MCP 让 AI 连接外部系统" |
| 工具→流程 | 三-4→三-5 | "MCP 管数据拉取——Skill 管分流流程" |
| Skill→闭环 | 三-5→三-6 | "分流出 TRUE POSITIVE——然后 AI 进入修复闭环" |
| 闭环→安全 | 三-6→三-7 | "AI 能自主修复——但修复的安全性谁来保证？" |

---

### 演示三-1：CLAUDE.md 初始化（4min）

> **模块**：知识建设 · §1.2 Layer 1 基础信息
> **目标**：从零生成 CLAUDE.md，演示渐进式披露和 Review 流程

#### 前置准备

```bash
cd /root/course/code/ziguangzhanrui_2/srsRAN_4G

# 备份现有 CLAUDE.md，模拟从零开始
cp CLAUDE.md CLAUDE.md.bak
mv CLAUDE.md CLAUDE.md.bak_demo
mkdir -p docs
```

#### 关键文件

| 文件 | 用途 |
|------|------|
| `CLAUDE.md` | 生成产物（Layer 1 基础信息） |
| `README.md` / `CMakeLists.txt` | 输入源 |
| `docs/build-guide.md` | 渐进式披露目标（详细构建说明） |
| `docs/naming-conventions.md` | 渐进式披露目标（命名规范） |
| 参考产物 | `企业培训/001-紫光展锐/第三课_实测/CLAUDE_md_demo.md`（161 行） |

#### 演示步骤

**Step 1：生成 CLAUDE.md（~1.5min）**

在 Claude Code 中粘贴：

```
读一下这个项目的 README、顶层目录结构、CMakeLists.txt 和主要源文件，
生成 CLAUDE.md 初稿。要求：

1. 项目定位：一句话说明项目是什么、解决什么问题
2. 核心架构：
   - 对外接口和系统实体（如独立的可执行程序、库、协议实体等）
   - 核心模块拓扑和职责
   - 关键依赖和技术栈
3. 关键模块：每个顶级目录的职责和核心文件
4. 构建命令：完整的构建、测试、运行命令
5. 命名约定：函数、宏、文件的命名规范
6. "禁区"章节留空，写"待人工补充"
7. "历史包袱"章节留空，写"待人工补充"

约束：
- 总行数控制在 300 行以内（硬上限 400 行）
- 架构图、接口清单、数据模型的详细内容不要写进来，
  用 `→ 详见 docs/xxx` 链接指向 docs/ 子文档
- 保留项目中已有的 CLAUDE.md 内容（如果存在的话），
  在此基础上补充和优化
```

**讲师口述**："注意这个 prompt——不限定项目类型。你们的项目可能不是协议栈，可能不是 C。这个 prompt 对任何项目都适用。"

**预期行为**：Claude 扫描目录结构（Bash ls/find）、读 CMakeLists.txt 和 README.md、扫描核心头文件，然后生成 ~200 行的 CLAUDE.md。

**Step 2：Review 生成结果（~1min）**

```
检查刚才生成的 CLAUDE.md：
1. 统计总行数，报告是否超过 400 行
2. 如果超过 400 行：
   - 找出可以提取到 docs/ 子文档的章节（如详细构建说明、完整接口列表等）
   - 把这些内容移到对应的 docs/ 文件中
   - 在 CLAUDE.md 中用 `→ 详见 docs/xxx.md` 链接替代
   - 重新统计行数，确保 ≤ 400 行
3. 检查"禁区"和"历史包袱"章节是否留空（不能让 AI 编造）
4. 检查架构描述是否准确反映项目实际结构
```

**讲师口述**："生成后必须 Review——查行数、查准确性。超了就渐进式披露：详细内容移到 docs/，CLAUDE.md 只留链接。"

**Step 3：展示渐进式披露结构（~30s）**

如果 Review 触发了内容拆分，展示输出结构：

```
CLAUDE.md (≤ 400 行，核心信息)
  ├── "→ 详见 docs/build-guide.md"
  ├── "→ 详见 docs/architecture.md"
  └── "→ 详见 docs/naming-conventions.md"

docs/ (详细内容)
  ├── build-guide.md
  ├── architecture.md
  └── naming-conventions.md
```

**讲师口述**：
- 滚动到"禁区"和"历史包袱"章节——"留空。AI 不知道你的历史决策，这 20% 必须人工补充。"
- "超过 800 行 Skill 触发率降 40%。"
- "Robert 的方法是反过来：先生成 docs/ 五份资产，再基于 docs/ 生成 CLAUDE.md。"

#### 时间节奏

| 时刻 | 动作 | 要点 |
|------|------|------|
| 0:00 | PPT 展示 CLAUDE.md 结构图 | "刚才讲了 LLM Wiki 和四层结构——现在从最底层 Layer 1 开始动手" |
| 0:15 | 粘贴 Step 1 prompt | "不限项目类型，通用" |
| 0:30 | Claude 开始扫描目录 | "和你入职第一天做的事一样" |
| 1:00 | Claude 生成 CLAUDE.md | 展示生成结果 |
| 1:20 | 滚动到"禁区""历史包袱" | "留空。AI 不知道历史决策" |
| 1:40 | 展示行数 | "400 行硬上限" |
| 2:00 | 粘贴 Step 2 Review prompt | "生成后必须 Review" |
| 2:20 | Claude 执行 Review | "超了就渐进式披露" |
| 2:40 | 展示渐进式披露结构 | "CLAUDE.md 保留链接，docs/ 保留详情" |
| 3:00 | 口述禁区示例 | "PHY 层 SIMD——AI 碰了可能毁性能" |
| 3:30 | 关联 Robert 12 讲 | "Robert 的方法：先 docs/ 再 CLAUDE.md" |

#### 应急预案

| 风险 | 概率 | 应对 |
|------|------|------|
| 生成超 400 行 | 中 | 正好演示渐进式披露 |
| "禁区"未留空 | 低 | 指出"AI 猜了一些禁区，但不一定对——必须人工确认" |
| 执行超 4min | 中 | 切换到参考产物文件展示 |

#### 演示后恢复

```bash
mv CLAUDE.md.bak_demo CLAUDE.md
rm -f CLAUDE.md.bak
```

---

### 演示三-2A：HTML 全景可视化（4min）

> **模块**：知识建设 · §1.3 Layer 2（给人看）
> **目标**：生成单文件 HTML 全景视图，6 板块整合项目架构/接口/数据模型

#### 前置准备

```bash
# 确认头文件可扫描
find /root/course/code/ziguangzhanrui_2/srsRAN_4G/lib/include -name "*.h" | wc -l
# 预期 ~41 个公共头文件

# 可选：安装 Cocoon-AI 架构图 Skill
# mkdir -p ~/.claude/skills/ && cd ~/.claude/skills/
# git clone https://github.com/Cocoon-AI/architecture-diagram-generator.git
```

#### 关键文件

| 文件 | 用途 |
|------|------|
| `docs/project-overview.html` | 生成产物（~500-800 行 HTML） |
| `CMakeLists.txt` | 外部依赖源 |
| `lib/include/` | 公共接口扫描源 |
| 参考产物 | `第三课_实测/architecture.svg`、`第三课_实测/api-list.md` |

#### 演示步骤

**Step 1：项目分析（~1min）**

```
扫描 srsRAN_4G 项目，输出以下信息：
1. 目录结构和模块划分
2. 协议栈分层（PHY/MAC/RLC/PDCP/RRC/NAS）及每层核心源文件
3. 模块间依赖关系（lib/include 中的头文件引用）
4. 外部依赖库（CMakeLists.txt 中的 find_package）
5. 关键公共接口（头文件中的核心函数签名，按模块分组）
6. 核心数据结构体（主要 struct/enum 定义）
```

**Step 2：生成 HTML 全景视图（~2min）**

```
基于上述分析，生成一个单文件 HTML 全景视图，保存到 docs/project-overview.html。要求：

1. 暗色主题（背景 #1e1e2e，文字白色，模块用不同颜色区分）
2. 包含 6 个板块，每个板块用 <details>/<summary> 可折叠：
   - 项目概览卡片：语言/行数/模块数/构建系统/关键依赖
   - 协议栈分层架构图：内嵌 SVG，PHY→MAC→RLC→PDCP→RRC 分层，UE/eNB/EPC 三色区分
   - 模块依赖关系图：内嵌 SVG，模块间调用方向
   - 外部依赖图：内嵌 SVG，分类标注（必选/可选）
   - 关键接口清单：HTML 表格，函数签名 + 模块 + 一句话说明
   - 数据模型概览：HTML 表格，核心 struct/enum + 字段 + 用途
3. 不依赖任何 CDN 或外部资源（企业内网可直接打开）
4. 所有 SVG 内嵌在 HTML 中，不使用外部图片
5. 用系统 monospace 字体（JetBrains Mono, Fira Code, monospace）
6. 页面顶部加项目名称和生成时间
```

**Step 3：浏览器展示（~1min）**

在浏览器中打开 `docs/project-overview.html`：
- 展开/折叠各板块（`<details>/<summary>` 交互）
- 展示接口清单表格
- 展示 SVG 架构图细节

**讲师口述**：
- "一个文件，6 板块——协议栈、模块依赖、外部依赖、接口清单、数据模型"
- "不依赖 CDN——企业内网直接打开"
- "C/C++ 没有 Swagger——AI 3 分钟整理出的接口清单，人工要 1-2 周"

#### 时间节奏

| 时刻 | 动作 | 要点 |
|------|------|------|
| 0:00 | PPT 展示 Layer 2（给人看 vs 给 Agent 看） | "代码级信息——人看全景，Agent 看精确位置" |
| 0:15 | 粘贴 Step 1 分析 prompt | "先让 AI 理解项目" |
| 1:00 | 粘贴 Step 2 生成 prompt | "一个 HTML 整合所有可视化" |
| 2:00 | 浏览器打开 HTML | "暗色主题，6 板块" |
| 2:30 | 展开/折叠各板块 | "details/summary 标签——零 JavaScript" |
| 3:00 | 展示接口清单表 | "AI 3 分钟 vs 人工 1-2 周" |
| 3:30 | 展示 SVG 架构细节 | "UE/eNB/EPC 三色区分" |

#### 应急预案

| 风险 | 概率 | 应对 |
|------|------|------|
| HTML 渲染异常 | 中 | 切换到参考 architecture.svg/.png |
| SVG 太复杂/不清晰 | 中 | 分步生成：先架构 SVG，再整合 |
| 执行时间过长 | 中 | 只演示 Step 2，Step 1 口述总结，直接展示已生成 HTML |

#### 演示后恢复

```bash
git checkout -- docs/project-overview.html 2>/dev/null
```

---

### 演示三-2B：CODEMAP 生成 + LLM Wiki 回扣（4min）

> **模块**：知识建设 · §1.3 Layer 2（给 Agent 看）
> **目标**：生成 Agent 可消费的代码地图，含热区/冷区标注；回扣 §1.0 LLM Wiki 三操作在 CODEMAP 上的体现

#### 前置准备

```bash
# 可选：安装 RepoMapper
# pip install repomapper
```

#### 关键文件

| 文件 | 用途 |
|------|------|
| `CODEMAP.md` | 生成产物（按模块组织的代码地图） |
| `CLAUDE.md` | 更新：增加 Code Knowledge Map 索引章节 |
| 参考产物 | `第三课_实测/CODEMAP.md`（359 行） |

#### 演示步骤

**Step 1：生成 CODEMAP.md（~1.5min）**

```
基于 CLAUDE.md 和项目目录结构，生成 CODEMAP.md。要求：

按模块组织，每个模块包含：
- 目录路径
- 核心源文件列表（只列关键文件，不是全部文件）
- 模块职责（一句话）
- 对外接口（公共函数/头文件）
- 热区标注（经常修改的模块标 🔥）
- 冷区标注（稳定不动的模块标 ❄️）
- 与其他模块的依赖关系

在文件开头加索引表，方便 Agent 快速定位。
保存到 CODEMAP.md。
```

**讲师口述**："CODEMAP 是给 Agent 看的——不需要好看，需要精准。Agent 修改 PHY 代码时通过 CODEMAP 导航，不用盲目扫描全部文件。"

**预期产出**：CODEMAP.md 包含索引表（模块/路径/状态），各模块分节包含：路径、核心文件、职责、公共接口、依赖关系、热区/冷区状态。模块包括 PHY（🔥）、MAC（🔥）、RLC（❄️）、PDCP（❄️）、RRC（🔥）、eNodeB（🔥）、UE（❄️）、EPC（❄️）。

**Step 2：在 CLAUDE.md 中添加索引（~30s）**

```
在 CLAUDE.md 中添加 Code Knowledge Map 章节，索引 CODEMAP.md：

## Code Knowledge Map
- 代码地图：`CODEMAP.md` — 按模块组织的核心文件、接口、依赖关系
- 项目全景：`docs/project-overview.html` — 架构图+接口清单+数据模型
- 更新方法：代码结构变更后重新 Ingest CODEMAP
```

**讲师口述**："不索引就不存在。Agent 只有在读 CLAUDE.md 时看到 CODEMAP 才知道去查。"

**Step 3：回扣 §1.0 LLM Wiki 三操作——以 CODEMAP 为例（PPT + 口述，~1min）**

**讲师口述**："还记得开头讲的 Karpathy LLM Wiki 三操作吗？刚才做的就是 Ingest——代码就是 raw，CODEMAP 就是 wiki 产物。"

| 操作 | CODEMAP 上的体现 |
|------|-----------------|
| **Ingest** | 刚才做的事——扫描代码（raw）→ 生成 CODEMAP.md（wiki）。代码结构变更后重新 Ingest 更新。可用 RepoMapper：`python repomap.py . --map-tokens 4096` |
| **Query** | Agent 遇到代码导航问题 → 先查 CODEMAP → 定位目标文件（比盲目 grep 快、准） |
| **Lint** | 定期检查 CODEMAP 是否与代码偏移。新模块不在 CODEMAP？→ 触发 Ingest。就像 Coverity 扫代码 |

**讲师口述**：
- "RepoMapper 用 Tree-sitter + PageRank 自动排名关键符号"
- "CODEMAP 是知识层——模块/接口/数据结构。AST 是编译器层——下一个演示"

#### 时间节奏

| 时刻 | 动作 | 要点 |
|------|------|------|
| 0:00 | PPT 展示 Layer 2（人 vs Agent） | "SVG 给人看全局，CODEMAP 给 Agent 看精确位置" |
| 0:15 | 粘贴 Step 1 prompt | "生成 Agent 视角的代码地图" |
| 1:00 | 展示 CODEMAP 索引表 | "热区 🔥 / 冷区 ❄️——Agent 优先更新热区" |
| 1:40 | 粘贴 Step 2 索引 prompt | "不索引就不存在" |
| 2:20 | 回扣 §1.0 三操作 | "刚才做的就是 Ingest——代码是 raw，CODEMAP 是 wiki 产物" |
| 2:40 | 讨论工具生态 | "RepoMapper: Tree-sitter + PageRank" |
| 3:00 | 对比 Layer 2 vs Layer 3 | "CODEMAP 知识层 vs AST 编译器层" |

#### 演示后恢复

```bash
git checkout -- CODEMAP.md CLAUDE.md 2>/dev/null
```

---

### 演示三-3：AST 索引与 clangd LSP（4min）

> **模块**：知识建设 · §1.4 Layer 3 AST 索引
> **目标**：同一任务有/无 LSP 对比，展示编译器级搜索的质变

#### 前置准备

```bash
# 确认 clangd 安装
clangd --version

# 确认 compile_commands.json 存在
ls -lh /root/course/code/ziguangzhanrui_2/srsRAN_4G/build/compile_commands.json
# 预期 808KB

# 在 Claude Code 中安装 LSP 插件（课前完成）
# /plugin install clangd-lsp@claude-plugins-official
# /plugin list  → clangd-lsp: enabled
# 启动一次让索引完成（首次需数分钟）
```

#### 关键文件

| 文件 | 用途 |
|------|------|
| `build/compile_commands.json` | 808KB，每个源文件的完整编译命令 |
| LSP 配置 | `docs/lsp-setup.md`（含交叉编译配置） |

#### 演示步骤

**Step 1：展示 compile_commands.json（~30s）**

```bash
ls -lh build/compile_commands.json
echo "---"
head -20 build/compile_commands.json
```

**讲师口述**："每个 .c/.cc 文件的完整编译命令都在这里——include 路径、宏定义、编译选项。clangd 读这个文件就获得了编译器视角。"

**Step 2：无 LSP —— grep 导航（~1min）**

先禁用 LSP 插件：
```
/plugin disable clangd-lsp@claude-plugins-official
```

输入任务：
```
找出 srsran_chest_dl_estimate 这个函数被哪些函数调用了，列出完整的调用链。
```

**预期行为**：
- Claude 使用 Grep 工具搜索 `srsran_chest_dl_estimate`
- 匹配到注释、字符串、头文件声明——噪声多
- 需要多轮 Grep 才能追踪调用链
- 执行时间长、token 消耗高

**讲师口述**："看——它匹配到了注释，匹配到了头文件声明。还得多轮搜索才能追踪调用链。"

**Step 3：有 LSP —— LSP 导航（~1min）**

启用 LSP 插件：
```
/plugin enable clangd-lsp@claude-plugins-official
/reload-plugins
```

同一任务：
```
找出 srsran_chest_dl_estimate 这个函数被哪些函数调用了，列出完整的调用链。
```

**预期行为**：
- Claude 使用 LSP `findReferences` 操作
- 50ms 级响应，只返回真实调用点
- 进一步用 `incomingCalls` 追踪上层调用者
- 结果精准、无噪声

**讲师口述**："50 毫秒，只有真实调用点——编译器语义理解。没有注释噪声，没有字符串匹配。"

**Step 4：对比总结 + 生成方法（~30s）**

| 指标 | 无 LSP（grep） | 有 LSP（clangd） |
|------|---------------|-----------------|
| 速度 | ~2-5s（小）/ ~45s（大） | ~50ms |
| Token 消耗 | ~2000+ | ~500 |
| 精度 | 低（注释/字符串混入） | 高（编译器语义） |
| 宏展开 | 不支持 | 支持 |
| 条件编译 | 不理解 | 理解 |
| 调用链 | 多轮手动追踪 | incomingCalls 一步到位 |

→ **900 倍速度差异，75% token 节省，精度质变**

展示一行生成命令：
```bash
cmake -B build -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
```

**讲师口述**："一行 CMake + 一个插件安装。就这两步，AI 获得编译器级理解。"

#### LSP 操作一览

| LSP 操作 | 功能 | Grep 等价物 |
|----------|------|------------|
| `goToDefinition` | 跳转到定义 | grep 函数名 |
| `findReferences` | 查找所有引用 | grep 函数名（有噪声） |
| `hover` | 获取类型信息 | 手动读头文件 |
| `documentSymbol` | 文件内所有符号 | ctags |
| `workspaceSymbol` | 全工作区符号搜索 | grep -r |
| `goToImplementation` | 跳转到实现 | 手动追踪 |
| `prepareCallHierarchy` | 调用层次分析 | 多轮 grep |
| `incomingCalls` | 谁调用了我 | grep（高噪声） |
| `outgoingCalls` | 我调用了谁 | 读源代码 |

#### 应急预案

| 风险 | 概率 | 应对 |
|------|------|------|
| LSP 插件报 "No LSP server available" | 中 | 已知 bug（GitHub #14803），用 PPT 数据对比 |
| 首次索引慢 | 中 | 课前启动完成索引；说明"第一次需索引，之后都是 50ms" |
| 时间不够完整对比 | 高 | 只演示有 LSP 场景，无 LSP 用预录数据/PPT |

#### 演示后恢复

无代码修改，无需恢复。如插件被禁用，重新启用：
```
/plugin enable clangd-lsp@claude-plugins-official
```

---

### 演示三-4：Coverity MCP Server 搭建（5min）

> **模块**：Skill × MCP · 给 AI "手"
> **目标**：展示 FastMCP 搭建 Coverity MCP Server + ToolSearch 渐进式披露 + Claude 回到本地代码审查

#### 前置准备

```bash
# FastMCP
python3 -c "from mcp.server.fastmcp import FastMCP; print('FastMCP OK')"

# Mock 数据
python3 -c "import json; d=json.load(open('coverity-mcp-server/mock_findings.json')); print(f'{len(d)} findings')"
# 预期：10 findings

# Mock 数据来源：基于真实告警清单（422 条，30+ Checker 类型），
# 选取 6 种代表性 Checker 构造 10 条 mock：
# UNINIT, BAD_SHIFT, DEADCODE, NULL_RETURNS, RESOURCE_LEAK, BUFFER_SIZE
```

#### 关键文件

| 文件 | 路径 | 用途 |
|------|------|------|
| `server.py` | `coverity-mcp-server/server.py` | MCP Server（< 120 行） |
| `mock_findings.json` | `coverity-mcp-server/mock_findings.json` | 10 条 mock 数据 |
| `settings.local.json` | `.claude/settings.local.json` | MCP + ToolSearch 配置 |

#### 演示步骤

**Step 1：展示 server.py 核心结构（~1min）**

打开 `coverity-mcp-server/server.py`，展示四个 `@mcp.tool()` 装饰器：

| 工具函数 | 用途 |
|---------|------|
| `list_findings(checker, severity)` | 查询扫描结果，按 checker/severity 过滤 |
| `get_finding_detail(finding_id)` | 获取告警详情（含代码上下文） |
| `get_finding_stats()` | 获取扫描结果统计摘要 |
| `update_finding_status(finding_id, status, reason)` | 更新告警状态 |
| `_load_findings()` | Mock 数据层（注释：生产替换这一个函数为 REST API 调用） |

**讲师口述**：
- "四个工具——完整 CRUD 覆盖。参数类型即描述，docstring 即工具说明。"
- "看注释——Mock 到生产只需改 `_load_findings()` 一个函数。接口定义、参数签名不变。"

**Step 2：展示 mock_findings.json（~30s）**

```bash
python3 -c "import json; data=json.load(open('coverity-mcp-server/mock_findings.json')); print(json.dumps(data[:2], indent=2, ensure_ascii=False))"
```

**讲师口述**："看这条——DCI 解包 BAD_SHIFT。直接对应你们告警清单中同类型问题。10 条 mock 覆盖六种 Checker。每条都有 `code_snippet` 和 `file:line`，Claude 可以回到本地代码核实。"

**Step 3：配置 ToolSearch 渐进式披露（~1min）**

展示 `.claude/settings.local.json` 中的 MCP 配置：

```json
{
  "mcpServers": {
    "coverity-server": {
      "command": "python3",
      "args": ["coverity-mcp-server/server.py"],
      "toolSearchConfig": {
        "enabled": true,
        "maxResults": 3
      }
    }
  }
}
```

**讲师口述**：
- "三行启动配置 + ToolSearch 开关。"
- "旧范式：5 个 MCP Server × 11K token/server = 55K token，占窗口 27.5%。每次对话启动全量加载，不用也交租。"
- "新范式：ToolSearch 按需加载——`enabled: true` 就够了。dlopen() 而不是静态链接。MCP 装得越多越强，不是越慢。"

**Step 4：快速验证 + 本地代码审查（~1.5min）**

在 Claude Code 中输入：

```
帮我看看 Coverity 扫描结果，挑出需要关注的 High 级别告警，
然后去本地代码确认一下这些告警是否真的有问题，给我一个要修复的清单。
```

**预期行为序列**：
1. 识别 MCP 工具可用
2. 调用 `get_finding_stats()` → "10 findings: High 4, Medium 2, Low 4"
3. 调用 `list_findings(severity="High")` → 4 条高危
4. 调用 `get_finding_detail(1001)` → 获取 UNINIT 详情
5. **关键步骤**：Read 本地文件 `srsenb/src/stack/rrc/rrc_ue.cc:245` → 对比代码 → 判断是否真未初始化
6. 对每个 High 告警重复 4-5 步
7. 输出修复清单

**讲师口述**：
- "注意第 5 步——Claude 没有拉完数据就给你看。它回到本地代码核实了。MCP 拉数据，Read 工具看代码——两种能力组合。"
- "我没有复制任何数据——AI 自己通过 MCP 查询，自己在代码里确认。"

#### 应急预案

| 风险 | 概率 | 应对 |
|------|------|------|
| FastMCP 未安装 | 低 | 现场 `pip install mcp`（~10s） |
| Claude 没回到本地代码审查 | 中 | 说明"prompt 要求了'去本地代码确认'——如果没做，追问一句" |
| ToolSearch 不工作 | 中 | 说明"v2.1.0+ 支持——旧版本需更新" |
| 执行时间过长 | 中 | 只验证 get_finding_stats，代码审查用 PPT 数据展示 |

#### 演示后恢复

MCP Server 无状态，无需特殊恢复。

---

### 演示三-5：Coverity Skill 开发 + 测试 + 实际触发（9min）

> **模块**：Skill × MCP · 给 AI "脑"
> **目标**：展示 Skill 四阶段中的 Stage 2（开发）+ Stage 3（测试），含指令式 Description、决策树、触发测试、实际运行

#### 关键文件

| 文件 | 路径 | 用途 |
|------|------|------|
| `SKILL.md` | `.claude/skills/coverity-triage-sop/SKILL.md` | Skill 定义（Description + 决策树 + 报告模板） |
| `evals/` | `.claude/skills/coverity-triage-sop/evals/` | 触发测试用例 |
| `mock_findings.json` | `coverity-mcp-server/mock_findings.json` | 10 条 mock 数据 |

#### 演示步骤

##### Part A：Stage 2 —— 开发 Skill（5min）

**Step 1：指令式 Description（~1min）**

展示 SKILL.md frontmatter：

```yaml
---
name: coverity-triage-sop
description: >
  ALWAYS invoke when Coverity findings, static analysis triage,
  false positive analysis, BAD_SHIFT, DEADCODE, UNINIT,
  NULL_RETURNS, RESOURCE_LEAK, USE_AFTER_FREE, or checker
  pattern analysis is mentioned. Handles C/C++ embedded
  projects using the Coverity MCP Server. Do NOT skip.
---
```

**讲师口述**："三要素清晰可见——开头 ALWAYS invoke，7+ 触发短语全列，末尾 Do NOT skip。650 次实验——被动式 37%，指令式 100%，20 倍差距。"

**Step 2：MCP 依赖声明（~30s）**

展示 Prerequisites 章节：

```markdown
## Prerequisites
coverity-server MCP provides:
  - list_findings
  - get_finding_detail
  - get_finding_stats
  - update_finding_status
```

**讲师口述**："Skill 自己不拉数据——告诉 Claude 用 MCP 工具。没连上时 Claude 提前通知，而不是做到一半报错。"

**Step 3：决策树 + 代码检查指令（~2min）—— 核心**

展示三棵决策树（每棵都有 Step 0 代码检查）：

**UNINIT 决策树**：
- **Step 0**：用 Read 工具打开 finding 所在文件和行号，看前后 30 行上下文。确认实际代码与告警描述一致。
- Q1：memset/constructor/aggregate 初始化？→ FALSE POSITIVE
- Q2：所有可达路径都初始化？→ FALSE POSITIVE
- Q3：循环变量在循环头部初始化？→ FALSE POSITIVE
- Q4：路径确实未初始化？→ TRUE POSITIVE → 修复

**BAD_SHIFT 决策树**：
- **Step 0**：用 Read 打开文件，定位移位操作行，检查移位量来源和类型宽度。
- Q1：移位量是编译时常量且 < 类型宽度？→ FALSE POSITIVE
- Q2：移位量受 spec/config 约束（如 LTE 带宽 nof_prb <= 25）？→ FALSE POSITIVE
- Q3：移位前有边界检查？→ FALSE POSITIVE
- Q4：运行时变量无边界检查？→ TRUE POSITIVE → 加 assert

**DEADCODE 决策树**：
- **Step 0**：用 Read 打开文件，定位死代码块，检查周围预处理指令和 switch 结构。
- Q1：在 `#ifdef`/`#if` 条件编译块内？→ FALSE POSITIVE
- Q2：switch 的防御性 default（已覆盖所有 enum）？→ FALSE POSITIVE
- Q3：有 "legacy"/"compat" 注释？→ FALSE POSITIVE
- Q4：无合理原因？→ TRUE POSITIVE → 建议删除

**讲师口述**：
- "看 Step 0——每棵决策树第一步都是'打开文件看代码'。Skill 不只是判断规则——它告诉 Claude 怎么验证。"
- "UNINIT Q1——memset 是嵌入式 C 最常见的初始化方式，Coverity 经常漏看。一个问题过滤大量误报。"
- "BAD_SHIFT Q2——LTE 带宽配置 nof_prb ≤ 25，移 uint32_t 25 位完全安全。直接对应 mock finding 1007。"
- "这些判断规则 + 检查方法就是你们资深工程师脑子里的东西。以前口口相传，现在写进 Skill，AI 每次执行到位。"

**Step 4：报告模板（~30s）**

```markdown
## 输出格式
### 单条 Finding 报告
| 字段 | 内容 |
|------|------|
| Finding ID | {id} |
| Checker | {checker} |
| 文件 | {file}:{line} |
| 判定 | TRUE POSITIVE / FALSE POSITIVE |
| 依据 | {匹配决策树哪个问题，代码检查发现了什么} |
| 修复建议 | {仅 TRUE POSITIVE} |
| 优先级 | {Critical/High/Medium/Low} |
```

##### Part B：Stage 3 —— 测试（4min）

**Step 5：触发测试（~1min）**

✅ 正向（应该触发）：
- "刚跑完 Coverity，出来 47 个 findings，帮我看看"
- "BAD_SHIFT 在 modulator.c，是不是误报"
- "帮我分流 Coverity 告警"
- "这个 UNINIT 是真的还是假的"

❌ 反向（不应该触发）：
- "帮我写 Python 脚本解析 Coverity JSON"（开发任务）
- "帮我配置 Coverity Connect 的 LDAP"（运维）
- "帮我写单元测试"（测试）
- "帮我看看这段 C 代码有没有 bug"（通用 CR）

**讲师口述**："反向覆盖相似但不应触发的场景——'配置 Coverity 服务器'是运维不是分流。如果反向也触发，说明 Description 太宽——回去收窄。"

**Step 6：实际触发 Live Demo（~2min）—— 整个演示高潮**

在 Claude Code 中输入：

```
帮我把 Coverity 扫描结果分流一下
```

**预期行为序列**：
1. 匹配 description → 加载 coverity-triage-sop Skill
2. `get_finding_stats()` → "10 findings: High 4, Medium 2, Low 4"
3. `list_findings(severity="High")` → 先处理 4 条高危
4. `get_finding_detail(1001)` → 获取 UNINIT 详情
5. **Read** `srsenb/src/stack/rrc/rrc_ue.cc:245`（Skill Step 0 引导）→ 检查上下文，无 memset → Q4 命中 → TRUE POSITIVE
6. `get_finding_detail(1004)` → 获取 NULL_RETURNS 详情
7. **Read** `sched.cc:334` → 确认 find_ue 返回值未做 null 检查 → TRUE POSITIVE
8. ... 处理全部 10 条 findings
9. 输出标准分流报告（含代码检查证据）

**讲师口述**：
- "Claude 自动加载了 Skill，一步步执行。"
- "看第 5、7 步——它不是只看 Coverity 的描述就判断。它打开了本地代码文件核实。那是 Skill 里 Step 0 的效果。"
- "全程没问过我'BAD_SHIFT 怎么判断'——Skill 里写得清清楚楚。"

**Step 7：with/without 对比数据（~1min）**

| 指标 | 有 Skill | 无 Skill |
|------|---------|---------|
| 分类准确率 | ~90% | ~60% |
| 代码检查 | 每条都打开文件核实 | 随机跳过 |
| 报告格式 | 每次一致 | 每次不同 |
| MCP 调用 | 有序完整 | 可能遗漏 |
| 判断依据 | 引用代码行 | 靠描述猜 |

**讲师口述**：
- "30% 差距：Claude 没有 Skill 不知道 #ifdef 是嵌入式常见误报模式。你们团队的经验就是那 30% 的来源。"
- "注意'代码检查'行——有 Skill 每条都检查文件，无 Skill 经常跳过。Step 0 保证了这个行为。"

收尾提问："这 10 条 findings 我们 5 分钟分流完。你们上周花了多长时间？"

#### 应急预案

| 风险 | 概率 | 应对 |
|------|------|------|
| Skill 未触发 | 低 | 检查 Description 指令式格式；重启 Claude Code |
| Claude 没回到本地代码核实 | 中 | 说明"Skill 是 SOP 不是强制——Step 0 写了但 Claude 可能跳过。多跑几次验证" |
| 执行时间过长 | 中 | 说明"课堂只跑 3-4 条，不够时间全跑" |

#### 演示后恢复

```bash
cd /root/course/code/ziguangzhanrui_2/srsRAN_4G
git checkout -- coverity-mcp-server/mock_findings.json 2>/dev/null
```

---

### 演示三-6：dev-iterate Skill + 迭代闭环（9min）

> **模块**：迭代闭环 · AI 自主编译测试修复
> **目标**：展示 dev-iterate Skill 创建、三层守护配置、完整迭代闭环日志

#### 关键文件

| 文件 | 路径 | 用途 |
|------|------|------|
| `SKILL.md` | `.claude/skills/dev-iterate/SKILL.md` | 编译-测试-修复循环 Skill |
| `settings.local.json` | `.claude/settings.local.json` | 权限白名单 + PostToolUse Hook + Stop Hook 配置 |
| `stop_check_syntax.py` | `hooks/stop_check_syntax.py` | Stop Hook（语法检查） |
| `security.cc` | `lib/src/common/security.cc` | 演示目标文件 |

#### 演示步骤

##### Part A：创建 dev-iterate Skill（4min live demo）

**Step 1：展示 Skill Description（~30s）**

```yaml
---
name: dev-iterate
description: >
  ALWAYS invoke when code modification, bug fix, feature implementation,
  compile-test-fix cycle, build error, test failure, or iterative development
  is mentioned. Manages the compile-test-fix loop with retry limits and
  targeted test selection for srsRAN_4G C/C++ codebase. Do NOT skip.
---
```

**讲师口述**："指令式——ALWAYS，Do NOT。三个 Do NOT 确保 AI 不跳过任何验证步骤。"

**Step 2：增量编译 + 错误诊断表（~1min）**

```
Step 1: 增量编译
  命令: cmake --build build -j$(nproc)
  exit 0 → 进入 Step 2
  非 0 → 查诊断表, 修复, 重编译, 最多 5 轮

错误诊断表:
  语法错误     expected ';'           → 直接修复
  类型不匹配   cannot convert         → 检查 C/C++ 混编
  模板错误     50-500 行展开          → ★ 只看最后 20 行
  链接错误     undefined ref          → 检查 target_link_libraries
  宏展开       HAL 宏多层嵌套         → 检查宏定义来源
```

**讲师口述**："模板错误——AI 只看最后 20 行。这是领域知识，AI 推导不出来，你必须告诉它。"

**Step 3：测试映射表（~1min）—— 核心价值**

| 修改路径 | 测试命令 |
|---------|---------|
| `lib/src/phy/` | `ctest --test-dir build -R phy` |
| `lib/src/common/` | `ctest --test-dir build -R common` |
| `lib/src/rlc/` / `lib/src/pdcp/` | `ctest --test-dir build -R "rlc\|pdcp"` |
| `srsenb/` | `ctest --test-dir build -L lte` |
| `srsgnb/` | `ctest --test-dir build -L nr` |
| `srsue/` | `ctest --test-dir build -R ue` |

**讲师口述**："这张表是整个 Skill 的核心价值。改了 PHY 就跑 PHY 测试，改了 eNodeB 就跑 LTE 测试。让 AI 猜——要么全跑 1542 个等半天，要么漏掉关键测试。"

**Step 4：测试失败诊断 + 重试上限（~30s）**

```
测试失败三分支判断：
  代码有 bug？     → 修代码
  测试本身过时？   → 修测试
  判断不了？       → 停下来问人

重试上限：
  单个错误 ≤ 5 轮
  全局 ≤ 10 轮
  每次重试前必须说明改了什么、为什么改
```

**讲师口述**："没有重试上限，AI 在一个错误上来回 20 次越改越糟。5 次改不好——停下来报告。诊断式重试，不是盲目重试。"

##### Part B：环境配置 —— 三层守护（2min）

**Step 5：权限白名单（~30s）**

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

**讲师口述**："能编译，能测试，不能删文件，不能装软件。allow 是最小权限集，deny 是安全红线。"

**Step 6：Stop Hook 机制（~1min）**

展示 `hooks/stop_check_syntax.py` 核心逻辑：
- `stop_hook_active` 防死循环——Hook 拦截后 Claude 修复重试，反复失败则放行
- `exit 2` 是 Hook 专用退出码——拦截并将错误信息回传 Claude
- 只检查当前 session 修改的 .c/.h 文件——不全量扫描

**Step 7：三层守护总结（~30s）**

```
Layer 1: PostToolUse Hook — 每次编辑后自动格式化（100% 确定性）
Layer 2: dev-iterate Skill — 编译→测试→修复流程（Agent SOP）
Layer 3: Stop Hook — 完成前强制编译+语法检查（100% 确定性）

"CLAUDE.md 是建议，Skill 是 SOP，Hook 是法律。三层才完整。"
```

##### Part C：查看执行日志（3min）

**Step 8：展示完整迭代循环执行日志**

演示场景：在 security.cc 中添加 `srsran_security_verify_mac` 函数。

**预期行为序列**：
1. Agent 触发 dev-iterate Skill
2. 写函数 → PostToolUse Hook 自动 clang-format → 日志显示 "clang-format applied"（Layer 1）
3. 增量编译——Skill Step 1：`cmake --build build -j$(nproc)` → ~5s 通过
4. 跑 common 测试——Skill Step 2：`ctest --test-dir build -R common` → 测试映射表匹配 → 通过
5. Agent 声明完成 → Stop Hook 触发（Layer 3）→ `hooks/stop_check_syntax.py` → 通过放行

**讲师口述**：
- "每步对应 Skill 的哪个 Step，三层守护各在哪里介入——日志里都看得到"
- "如果编译失败呢？更好——Claude 查诊断表，按策略修复，最多 5 次"
- "诊断式重试，不是盲目重试——每次重试前必须说明改了什么"

#### 时间节奏

| 时刻 | 部分 | 动作 | 要点 |
|------|------|------|------|
| 0:00 | Skill | 展示 Description | "ALWAYS, Do NOT——指令式" |
| 1:00 | Skill | 展示诊断表 | "模板错误只看最后 20 行" |
| 2:00 | Skill | 展示测试映射表 | "核心价值——改 PHY 跑 PHY" |
| 3:00 | Skill | 重试上限 | "5 次改不好就停——诊断式重试" |
| 3:30 | 配置 | 展示权限白名单 | "能编译，能测试，不能删，不能 sudo" |
| 4:00 | 配置 | 展示 Stop Hook | "exit 2 拦截 + 防死循环" |
| 4:30 | 配置 | 三层守护总结 | "建议/SOP/法律——三层完整" |
| 5:00 | 日志 | 展示演示场景 | "在 security.cc 添加 verify_mac 函数" |
| 5:30 | 日志 | 展示执行日志 | "格式化→编译→测试→Stop Hook" |
| 7:00 | 日志 | 标注三层介入点 | "Layer 1 / Layer 2 / Layer 3" |
| 8:00 | 日志 | 失败场景说明 | "编译失败→诊断表→修复→重试" |

#### 应急预案

| 风险 | 概率 | 应对 |
|------|------|------|
| 编译真的失败 | 中 | 正好展示"编译失败子循环" |
| 测试超时（跑了全部 1542 个） | 中 | 说明"测试映射表配错了——这就是映射表的价值" |
| Live demo 时间过长 | 高 | 切换到预录日志/截图 |

#### 演示后恢复

```bash
git checkout -- .
git clean -fd
```

---

### 演示三-7：多 Agent 并行安全审查（5min）

> **模块**：安全防护 · AI 受控安全运行
> **目标**：展示四 Agent 并行安全审查 + cppcheck 对比，证明 AI Agent 在安全审查的精度优势

#### 前置准备

```bash
# 确认 Agent 定义文件存在
ls .claude/agents/*.md
# 预期：security-reviewer.md, telecom-security-reviewer.md,
#       embedded-specialist-reviewer.md, compliance-reviewer.md,
#       architecture-reviewer.md, code-quality-reviewer.md

# 确认安全知识库 Skill
ls .claude/skills/srsran-security/SKILL.md

# 确认目标文件
wc -l lib/src/common/security.cc
grep -c "memcpy" lib/src/common/security.cc
# 预期 44 个 memcpy 调用

# 可选：安装 cppcheck 对比
which cppcheck || echo "建议: apt install cppcheck"
```

#### 关键文件

| 文件 | 路径 | 用途 |
|------|------|------|
| Agent 定义 | `.claude/agents/telecom-security-reviewer.md` | Opus 模型，读只权限 |
| Agent 定义 | `.claude/agents/embedded-specialist-reviewer.md` | Sonnet 模型，ISR/DMA/RTOS 焦点 |
| Agent 定义 | `.claude/agents/compliance-reviewer.md` | Sonnet 模型，MISRA C/CERT C |
| 安全知识库 | `.claude/skills/srsran-security/SKILL.md` | 6 领域安全模式知识库 |
| 审查目标 | `lib/src/common/security.cc` | 44 个 memcpy 调用 |

#### 演示步骤

**Step 1：展示 Agent 定义 + 安全知识库结构（~1min）**

展示 `telecom-security-reviewer.md`：

```yaml
---
name: telecom-security-reviewer
description: "C/C++ 电信协议栈安全审查专家。..."
tools: ["Read", "Grep", "Glob"]
model: opus
---
```

展示四 Agent 架构：

```
           待审查代码 (security.cc)
     ┌──────────┼──────────┬──────────┐
     v          v          v          v
 Agent 1    Agent 2    Agent 3    Agent 4
 Security   Quality    Embedded   Compliance
 CWE/内存   复杂度     ISR/DMA    MISRA C/
 密码学     技术债     RTOS/HW    CERT C
 (Opus)     (Sonnet)   (Sonnet)   (Sonnet)
```

**讲师口述**：
- "tools 白名单只给 Read/Grep/Glob——纯只读。安全 Agent 只审查，绝不修改。"
- "model: opus——安全审查用最强模型，质量优先。"
- "为什么多 Agent？单 Agent 带 6 维清单，前几项检查仔细，后面越来越潦草——检查疲劳。Codex-Verify 论文证明：组合不同检测模式达到 76.1% 检出率。"

展示高优先级文件列表：

| 文件 | 不安全函数数 | 优先级 | 已知风险 |
|------|------------|--------|---------|
| security.cc | 44 (memcpy) | P0 | calloc 无 NULL 检查 |
| nas.cc | 33 | P0 | NAS 消息解析溢出 |
| liblte_security.cc | 9 | P0 | 密钥推导固定长度 |

**Step 2：启动多 Agent 审查（~2min live demo）**

在 Claude Code 中输入：

```
用安全审查 Agent 检查 lib/src/common/security.cc
```

**预期行为**：
- 四个 Agent 并行启动：
  - Security reviewer → memcpy 无边界检查（CWE-120），calloc 返回值未检查（CWE-252）
  - Quality reviewer → 函数圈复杂度 >15，重复模式未抽象
  - Embedded specialist → MD5 用于安全验证（CWE-327），密钥材料泄露到日志（CWE-200）
  - Compliance reviewer → MISRA C:2012/2023 违规 ×3，CERT C MEM30-C 违规
- 聚合 Agent → 去重 → 交叉验证 → 严重性分级报告

**Step 3：展示审查报告（~1min）**

```
[SEC-001] CWE-120: memcpy 无长度检查 (security.cc:kdf_common)
  Severity: CRITICAL
  攻击场景: 空口发送超长 NAS 消息 → 堆溢出 → 远程代码执行
  修复: 在 memcpy 前添加 msg_len <= sizeof(buffer) 检查

[SEC-002] CWE-252: calloc 返回值未检查 (security.cc:kdf_common)
  Severity: CRITICAL
  修复: calloc 后添加 if (!ptr) return SRSRAN_ERROR

[SEC-003] CWE-327: MD5 用于安全验证 (security.cc)
  Severity: HIGH
  修复: 替换为 SHA-256 / HMAC-SHA-256
```

**讲师口述**："每条都有 CWE 编号、攻击场景、具体修复建议。不是'可能有问题'——是'攻击者从空口发超长 NAS 消息，触发堆溢出。'"

**Step 4：cppcheck 对比数据（~1min）**

| 对比 | cppcheck | AI Agent |
|------|----------|---------|
| 7 个已知漏洞 | 检出 0 | 检出 7（100%） |
| 原因 | 模式匹配 → 不追踪 msg_len 来源 | 追踪调用上下文 → msg_len 来自外部输入 |

**讲师口述**：
- "cppcheck 扫 7 个已知漏洞——检出 0。AI Agent 同一文件——全部 7 个。"
- "cppcheck 做模式匹配，Agent 追踪调用上下文——`msg_len` 来自外部输入可能大于 256，cppcheck 不追踪，Agent 追踪。"
- "新来的安全审查员培训三个月——Agent 读完知识库马上上岗，而且永远不会漏查清单项。"

#### 应急预案

| 风险 | 概率 | 应对 |
|------|------|------|
| Agent 执行过长 | 高 | 只跑 1-2 个 Agent，或用预跑结果 |
| Agent 未找到已知漏洞 | 低 | 说明"知识库需要持续补充——Stage 4 迭代" |
| cppcheck 未安装 | 中 | 用 PPT 展示对比数据 |

#### 演示后恢复

安全审查纯只读，无代码修改，无需恢复。

---

## 第四课：AI 原生开发工作流

> **主题**：需求→代码→CR→测试的完整 AI 原生工作流 + Coverity 深讲
> **演示时长**：待规划
> **正文大纲**：`正文大纲/第四课大纲_v2_2026-05-09.md`

### 演示概览

| 编号 | 演示名称 | 时长 | 说明 |
|------|---------|------|------|
| 4-1 | 需求到代码：AI 辅助编码完整流程 | TBD | 从需求描述到代码生成 |
| 4-2 | AI Code Review 实战 | TBD | 多维度自动代码审查 |
| 4-3 | AI 辅助测试用例生成 | TBD | 单元测试 + 边界测试 |
| 4-4 | Coverity 深度集成 | TBD | 生产环境 Coverity 对接 |

> 📝 第四课演示步骤待补充。

---

## 第五课：全自动化与组织治理

> **主题**：全自动无人值守流水线 + 组织治理 + L5 治理飞轮
> **演示时长**：待规划
> **正文大纲**：`正文大纲/第五课大纲_v2_2026-05-09.md`

### 演示概览

| 编号 | 演示名称 | 时长 | 说明 |
|------|---------|------|------|
| 5-1 | Headless 模式 CI/CD 集成 | TBD | Claude Code 嵌入 GitLab Pipeline |
| 5-2 | 全自动扫描修复流水线 | TBD | Coverity 扫描 → AI 分流 → 自动修复 → PR |
| 5-3 | 成熟度评估与路线图 | TBD | 从 L2 到 L5 的升级路径 |

> 📝 第五课演示步骤待补充。

---

## 已有素材清单

### 第二课素材（`srsRAN_4G/`）

| 路径 | 用途 | 对应演示 |
|------|------|---------|
| `CLAUDE.md` | 项目级 CLAUDE.md | 2-3 |
| `CLAUDE.local.md` | 本地级 CLAUDE.md（不入 git） | 2-3 |
| `.claude/settings.local.json` | Langfuse 配置 + Hook 配置 | 2-2 / 2-4 |
| `.claude/agents/security-reviewer.md` | 安全审查 Agent | 2-5 |
| `.claude/agents/code-quality-reviewer.md` | 代码质量 Agent | 2-5 |
| `.claude/agents/architecture-reviewer.md` | 架构兼容性 Agent | 2-5 |
| `hooks/stop_check_syntax.py` | Stop Hook 脚本（语法检查） | 2-4 |
| `examples/CLAUDE_企业级示例.md` | 企业级 CLAUDE.md 示例 | 2-3 |
| `examples/CLAUDE_用户级示例.md` | 用户级 CLAUDE.md 示例 | 2-3 |

### 第三课实测产出（`企业培训/001-紫光展锐/第三课_实测/`）

| 文件 | 用途 | 对应演示 |
|------|------|---------|
| `CLAUDE_md_demo.md`（161 行） | CLAUDE.md 实测生成结果 | 三-1 |
| `architecture.svg` / `.png` | 协议栈分层架构图 | 三-2A |
| `api-list.md` | 8 模块 50+ 公共接口 | 三-2A |
| `data-model.md` | 13 模块 30+ struct/enum | 三-2A |
| `CODEMAP.md`（359 行） | Agent 代码地图 | 三-2B |

### 第三课项目内配置（`srsRAN_4G/`）

| 路径 | 用途 | 对应演示 |
|------|------|---------|
| `CLAUDE.md`（109 行） | 项目基础信息 | 三-1 |
| `CODEMAP.md`（430+ 行） | 代码地图（热区/冷区） | 三-2B |
| `docs/project-overview.html`（741 行） | HTML 全景视图 | 三-2A |
| `docs/build-guide.md`（213 行） | 构建指南 | 三-1 |
| `docs/naming-conventions.md`（335 行） | 命名规范 | 三-1 |
| `docs/lsp-setup.md`（210+ 行） | clangd LSP 配置（含交叉编译） | 三-3 |
| `coverity-mcp-server/server.py`（134 行） | MCP Server | 三-4 |
| `coverity-mcp-server/mock_findings.json`（132 行） | 10 条 mock 告警 | 三-4/5 |
| `.claude/settings.local.json`（45 行） | MCP + ToolSearch + Hook 配置 | 三-4/6 |
| `.claude/skills/coverity-triage-sop/SKILL.md` | 分流决策树 Skill | 三-5 |
| `.claude/skills/dev-iterate/SKILL.md` | 编译-测试-修复 Skill | 三-6 |
| `.claude/skills/srsran-security/SKILL.md` | 安全知识库 Skill | 三-7 |
| `.claude/agents/security-reviewer.md` | 安全审查 Agent | 三-7 |
| `.claude/agents/telecom-security-reviewer.md` | 电信协议栈安全 Agent | 三-7 |
| `.claude/agents/embedded-specialist-reviewer.md` | 嵌入式专家 Agent | 三-7 |
| `.claude/agents/compliance-reviewer.md` | 合规审查 Agent | 三-7 |
| `hooks/stop_check_syntax.py` | Stop Hook（语法检查） | 三-6 |
| `tests/test_demo_all.py`（76 测试） | 全部演示验证测试 | — |

---

## 测试验证

```bash
# 运行全部 76 个演示验证测试
cd /root/course/code/ziguangzhanrui_2/srsRAN_4G
python3 -m pytest tests/test_demo_all.py -v

# 预期输出：
# TestDemo1_ClaudeMD           9/9   PASSED ✅
# TestDemo2A_HTMLVisualization  7/7   PASSED ✅
# TestDemo2B_Codemap           6/6   PASSED ✅
# TestDemo3_AST_LSP            6/6   PASSED ✅
# TestDemo4_MCPServer         11/11  PASSED ✅
# TestDemo5_CoveritySkill     11/11  PASSED ✅
# TestDemo6_DevIterate         9/9   PASSED ✅
# TestDemo7_SecurityAgents    17/17  PASSED ✅
# ========================== 76 passed ===========================
```

---

## Review 记录

| 轮次 | 日期 | 内容 |
|------|------|------|
| 第一轮 | 2026-06-08 | 正文对齐、可执行性、教学节奏审查，10 项修复 |
| 第二轮 | 2026-06-08 | 用户反馈修订——演示一重写、演示二拆分、LSP 实际对比等 |
| 四角度 Review | 2026-06-08 | 课程讲师/学员/AI专家/嵌入式专家并行审查 → P0×5 + P1×6 修复 |

- 四角度 Review 汇总：[飞书文档](https://www.feishu.cn/docx/J7O2dpkg8olyajxFuwtcE3qdnxf)
- 迭代结果报告：[飞书文档](https://www.feishu.cn/docx/VC07dn3fCocARAxCRf6cLCcKnYc)

---

## 联系讲师

如果在操作过程中有任何疑问，欢迎添加讲师微信咨询：**xiaohan_chat**

---

*版本：v2（2026-06-09）| 第二课 5 个演示 + 第三课 8 个演示完整步骤 | 76/76 测试通过*
