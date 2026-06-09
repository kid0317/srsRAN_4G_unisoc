# 演示三：AST 索引与 clangd LSP —— Agent 的搜索基础设施

**对应正文**：第三课 §1.3 Layer 3：AST 索引——Agent 的搜索基础设施
**预计时长**：4 分钟（含讲解）
**所在模块**：第一节「知识建设」

---

## 一、演示目标

展示 compile_commands.json + clangd LSP 如何给 AI 带来编译器级别的代码理解能力。通过**同一个任务、有/无 LSP 两次执行**的实际对比，让学员直观感受效率和精确度的质变。

**核心教学点**：
1. 900 倍速度差距——grep ~45 秒 vs LSP ~50ms，不是优化是质变
2. 一行 CMake 就能拥有——`cmake -DCMAKE_EXPORT_COMPILE_COMMANDS=ON`
3. Claude Code 内置 LSP Tool——安装插件后自动启用 9 种操作
4. 实际任务对比——同一个代码导航问题，有/无 LSP 的 token 消耗和精确度差异

---

## 二、前置准备

### 2.1 环境要求

| 项目 | 要求 |
|------|------|
| 代码库 | `/root/course/code/ziguangzhanrui_2/srsRAN_4G` |
| 已构建 | `build/compile_commands.json` 存在（808KB） |
| clangd | `apt install clangd-18`（或更高版本） |
| Claude Code | v2.1.0+（LSP 稳定支持） |
| clangd LSP 插件 | 已安装（见 2.3） |

### 2.2 确认 compile_commands.json

```bash
cd /root/course/code/ziguangzhanrui_2/srsRAN_4G
ls -lh build/compile_commands.json
# 预期 ~808KB，覆盖所有源文件
wc -l build/compile_commands.json
```

### 2.3 安装 clangd LSP 插件（课前必做）

```bash
# 确认 clangd 已安装
clangd --version
# 如未安装：apt install clangd-18

# 安装 Claude Code 官方 clangd LSP 插件
# 在 Claude Code 中执行：
/plugin install clangd-lsp@claude-plugins-official

# 验证插件已启用
/plugin list
# 应显示 clangd-lsp: enabled
```

**插件安装后 Claude Code 获得的 LSP 操作**：

| LSP 操作 | 功能 | 对应 grep 替代 |
|----------|------|---------------|
| `goToDefinition` | 跳转到定义 | grep 函数名 |
| `findReferences` | 查找所有引用 | grep 函数名（含噪音） |
| `hover` | 获取类型信息 | 手动读头文件 |
| `documentSymbol` | 文件内所有符号 | ctags |
| `workspaceSymbol` | 全局符号搜索 | grep -r |
| `goToImplementation` | 跳转到实现 | 手动追踪 |
| `prepareCallHierarchy` | 调用层次分析 | 多次 grep |
| `incomingCalls` | 谁调用了我 | grep（噪音大） |
| `outgoingCalls` | 我调用了谁 | 读源码 |

### 2.4 课前演练对比数据

提前跑一次对比测试，记录数据：

```bash
# 无 LSP 场景（禁用插件）
# /plugin disable clangd-lsp@claude-plugins-official
# prompt: "找出 srsran_chest_dl_estimate 被哪些函数调用"
# 记录：耗时、token 数、结果数（含噪音数）

# 有 LSP 场景（启用插件）
# /plugin enable clangd-lsp@claude-plugins-official
# /reload-plugins
# 同样 prompt
# 记录：耗时、token 数、结果数
```

---

## 三、演示步骤

### Step 1：展示 compile_commands.json（30s）

```bash
ls -lh build/compile_commands.json
echo "---"
head -20 build/compile_commands.json
```

**讲解**："每个 .c/.cc 文件的完整编译命令都在这里——include 路径、宏定义、编译选项。clangd 读这个文件就拥有了编译器视角。"

### Step 2：无 LSP 场景——Claude 用 grep 导航（1min）

先禁用 LSP 插件（或使用课前录制的数据）：

```
# 如果现场演示：
/plugin disable clangd-lsp@claude-plugins-official
```

然后输入任务：

```
找出 srsran_chest_dl_estimate 这个函数被哪些函数调用了，列出完整的调用链。
```

**预期行为**：
- Claude 使用 Grep 工具搜索 `srsran_chest_dl_estimate`
- 匹配到注释、字符串、头文件声明——噪音大
- 需要多轮 Grep 追踪调用链
- 耗时较长，token 消耗高

**讲解**："看——匹配到注释了，匹配到头文件声明了。它还要多轮搜索才能追出调用链。"

### Step 3：有 LSP 场景——Claude 用 LSP 导航（1min）

启用 LSP 插件：

```
/plugin enable clangd-lsp@claude-plugins-official
/reload-plugins
```

同样的任务：

```
找出 srsran_chest_dl_estimate 这个函数被哪些函数调用了，列出完整的调用链。
```

**预期行为**：
- Claude 使用 LSP `findReferences` 操作
- 50ms 级响应，只返回真正的调用点
- 可能进一步使用 `incomingCalls` 追踪上层调用
- 结果精确，无噪音

**讲解**："**50 毫秒，只有真正的调用点——编译器语义理解。** 没有注释噪音，没有字符串匹配。"

### Step 4：对比总结 + 生成方式（30s）

展示对比数据（PPT 或口头）：

```
对比项           无 LSP (grep)      有 LSP (clangd)
──────          ──────────        ─────────────
速度            ~2-5 秒（小项目）    ~50ms
                ~45 秒（大项目）
Token 消耗      ~2000+             ~500
精确度          低（含注释/字符串）   高（编译器语义）
宏展开          不支持              支持
条件编译        不理解              理解
调用链追踪      多轮手动            incomingCalls 一步到位

→ 速度差 900 倍，Token 省 75%，精确度质变
```

```bash
# 生成 compile_commands.json 的一行命令
echo "cmake -B build -DCMAKE_EXPORT_COMPILE_COMMANDS=ON"
```

**讲解**："**一行 CMake + 一个插件安装。就这两步，AI 拥有编译器级别理解。**"

---

## 四、演示节奏（课堂）

| 时间点 | 讲师动作 | 讲解要点 |
|--------|---------|---------|
| 0:00 | 展示 compile_commands.json | "808KB，每个源文件的完整编译命令" |
| 0:20 | 展示 LSP 插件和 9 种操作 | "安装方式：`/plugin install clangd-lsp@claude-plugins-official`" |
| 0:40 | 无 LSP：粘贴任务 prompt | "同一个任务——找调用链。先用 grep" |
| 1:00 | 展示 grep 结果 | "注释、字符串、声明——**噪音**" |
| 1:20 | 有 LSP：启用插件，同一个 prompt | "同一个任务——现在有 LSP" |
| 1:40 | 展示 LSP 结果 | "**50ms，精确调用点——质变**" |
| 2:00 | 展示对比数据 | "速度差 900 倍，Token 省 75%" |
| 2:30 | 展示生成命令 | "**一行 CMake + 一个插件——就这两步**" |
| 3:00 | 展示工具生态表（PPT） | "clangd 最低配置。Aider RepoMap、Repomix 是进阶" |
| 3:30 | 衔接 Layer 2 vs Layer 3 | "CODEMAP 是知识层，AST 是编译器层——两者互补" |

---

## 五、关键讲解点

### 5.1 同一个任务的质变

> "注意——我没有换任务。同一个问题'谁调用了这个函数'，grep 要多轮搜索、结果有噪音；LSP 一步到位、结果精确。这不是优化——是质变。"

### 5.2 LSP 插件安装

> "Claude Code v2.0.74 开始支持 LSP。一行命令安装：`/plugin install clangd-lsp@claude-plugins-official`。安装后 Claude 自动获得 9 种 LSP 操作——goToDefinition、findReferences、incomingCalls 等。"

### 5.3 C/C++ 特殊性

> "宏展开、条件编译、模板实例化——grep 全都理解不了。clangd 基于 LLVM 前端，跟你们编译器用的同一个前端。"

### 5.4 企业环境注意事项

> "LSP 集成还在快速迭代，部分环境可能遇到稳定性问题。如果插件不工作——退回 grep 方案不影响功能，只是慢一些。保底方案永远在。"

---

## 六、失败预案

| 风险 | 概率 | 应对 |
|------|------|------|
| clangd 未安装 | 低 | 课前已检查；用 PPT 展示对比数据 |
| LSP 插件报 "No LSP server available" | 中 | 已知 bug（GitHub #14803）；用 PPT 展示对比 + 说明社区修复进度 |
| compile_commands.json 不存在 | 低 | 现场 `cmake -DCMAKE_EXPORT_COMPILE_COMMANDS=ON` 生成 |
| LSP 首次索引慢 | 中 | 课前启动一次让索引完成；说明"首次需要索引，后续都是 50ms" |
| 现场演示时间不够 | 高 | 只演示有 LSP 场景，无 LSP 用课前录制的数据/PPT 对比 |

---

## 七、演示后恢复

无代码修改，无需恢复。

如果演示中禁用了插件，重新启用：
```
/plugin enable clangd-lsp@claude-plugins-official
```

---

## 八、与课程原则的对应关系

| 课程概念 | 本演示如何体现 |
|---------|-------------|
| Layer 3 AST 索引（§1.3） | compile_commands.json + clangd 是 AST 索引基础 |
| 900 倍速度差距（§1.3） | 同一任务 grep vs LSP 实际对比 |
| Agent 搜索基础设施（§1.0） | LSP 让 Agent 工作效率质变 |
| 工具生态（§1.3） | clangd / Aider RepoMap / Repomix / libclang |
| Token 节省（§1.3） | 75% token 节省——从 2000+ 降到 500 |
| Claude Code LSP 插件 | `/plugin install clangd-lsp@claude-plugins-official` |
