# 演示二：Langfuse 可观测性 —— 查看完整执行轨迹

**对应正文**：第二课 §2.5（Langfuse 实证：亲眼看到 Agent 的思考过程）
**预计时长**：3–5 分钟
**所在模块**：第一小节「发出一条消息后，到底发生了什么」
**前置依赖**：紧接演示一（Agent Loop 实战）完成后进行

---

## 一、演示目标

让学员在 Langfuse 界面中看到 Agent Loop 的**完整执行轨迹**——每一轮的 Prompt、工具调用、参数、返回值，将 Agent Loop 从概念变成可观测的事实。

**核心教学点**：
1. LLM 可观测性不是黑盒——每一轮循环都有完整记录
2. System Prompt 的注入方式可视化（CLAUDE.md 如何被加载）
3. 工具调用的输入/输出全透明——Claude 搜了什么、读了哪些行、改了什么

---

## 二、前置准备

### 2.1 Langfuse 服务

| 项目 | 要求 |
|------|------|
| Langfuse 实例 | 本地 Docker 或云端实例 |
| 访问地址 | `http://localhost:3000`（本地）或 `https://langfuse.xxx.com`（云端） |
| Public/Secret Key | 已创建项目并获取 API Key |

### 2.2 Claude Code 配置

在 srsRAN_4G 项目目录下配置 Langfuse 环境变量：

```bash
# /root/course/code/ziguangzhanrui_2/srsRAN_4G/.claude/settings.local.json
{
  "env": {
    "LANGFUSE_PUBLIC_KEY": "<your-public-key>",
    "LANGFUSE_SECRET_KEY": "<your-secret-key>",
    "LANGFUSE_BASE_URL": "http://localhost:3000"
  }
}
```

### 2.3 预跑一次（推荐）

为确保 Langfuse 中有数据可看，建议课前用 headless 模式跑一次演示一的指令：

```bash
cd /root/course/code/ziguangzhanrui_2/srsRAN_4G
claude -p "srsRAN_4G 的 sync::radio_recv_fnc 在射频接收失败时返回通用的 SRSRAN_ERROR，请新增一个专用错误码 SRSRAN_ERROR_RADIO_RECV_FAIL 并让相关调用点正确处理它。"
```

跑完后恢复 git 状态：
```bash
git checkout -- .
```

---

## 三、演示流程

### Step 1：打开 Langfuse 界面（30s）

> "刚才的表格是我简化过的。如果你想看 25 轮的**完整**执行过程，可以用 Langfuse。"

打开浏览器 → 进入 Langfuse Dashboard → 找到最近的 Trace

### Step 2：展示 Trace 总览（1min）

展示 Trace 列表页：
- 指出 Trace 名称、时间戳、耗时
- 点击进入 Trace 详情

**讲解**：
> "每一条 Claude Code 指令，都会在 Langfuse 里留下完整的执行轨迹。"

### Step 3：展示嵌套 Span 结构（1.5min）

在 Trace 详情中展示：
1. **每一轮 Loop 是一个独立 span**——嵌套关系清晰
2. 点开第 1 轮，展示完整的 prompt 结构
3. 找到 CLAUDE.md 内容的注入位置——**注意：具体位置以 Langfuse 实际展示为准**（课前需截图确认）

**讲解**：
> "注意看——CLAUDE.md 的内容被拼装在 prompt 的**稳定段**中。为什么这很重要？因为 prompt cache 的机制是：前缀不变就能命中缓存。CLAUDE.md 的内容不常变化，放在稳定段中，每一轮 Agent Loop 循环都能低成本复用——这就是 95% 缓存命中率的来源。具体怎么拼装，Context 管理那一节详细讲。"

> ⚠️ **讲师注意**：正文 §3.2 描述为"走 User Content 路径"。实际 Langfuse trace 中 CLAUDE.md 可能出现在 system prompt 静态段或独立的 user message 中——**以课前实际截图为准**，讲解时聚焦"稳定段命中缓存"的核心论点，不要硬绑定具体位置。

### Step 4：展示工具调用详情（1.5min）

点开中间某一轮（如第 3 轮 Grep），展示：
1. 工具名称（Grep）
2. 输入参数（搜索关键词 `radio_recv_fnc`）
3. 返回结果（匹配的文件和行号）

**讲解**：
> "Claude 搜了什么关键词、读了哪几行代码、改了哪些文件——全都有记录。这不是看 PPT 上的概念图，这是**一个真实指令的完整执行轨迹**。"

---

## 四、界面要展示的关键区域

| Langfuse 区域 | 要指出的内容 | 教学意义 |
|-------------|------------|---------|
| Trace 列表 | 本次执行的时间/耗时/Token | 每条指令都可追溯 |
| Span 树 | 25 轮嵌套结构 | Agent Loop 循环可视化 |
| Generation 详情 | prompt 结构（CLAUDE.md 在稳定段中） | 稳定段命中 prompt cache |
| Tool Call 详情 | 工具名 + 输入 + 输出 | 透明化 Agent 行为 |
| Token 统计 | 输入/缓存读/缓存写/输出 | 解释 95% 缓存命中率 |

---

## 五、讲解要点

### 5.1 为什么需要可观测性

> "AI Agent 不再是一问一答——它可能自己跑 25 轮。如果没有可观测性，你不知道它在中间做了什么。Langfuse 让这个黑盒变成了玻璃盒。"

**课程原则映射**：Agent Loop 每轮结果追加到消息列表（§2.3 最后一段）

### 5.2 Token 缓存命中率

> "注意看 Token 统计——缓存读 567,991，缓存写才 31,285。命中率 95% 以上。为什么？因为多轮循环中，前面的上下文（CLAUDE.md + 之前轮次的结果）都被缓存了。这就是 CLAUDE.md 放在独立 User Message 中的效果。"

**课程原则映射**：CLAUDE.md 放 User Content 稳定命中缓存（§3.2 Bootstrap 详解）

### 5.3 衔接下一节

> "你们亲眼看到 Claude 在一轮一轮地'想、做、看'——这就是 Agent Loop。那什么决定了它能不能解决任务？不光在循环本身，更在于你给它提供了什么信息。这就是下一节——Context 管理。"

---

## 六、失败预案

| 风险 | 概率 | 应对 |
|------|------|------|
| Langfuse 无数据 | 中 | 使用提前截好的界面截图（PPT 备份） |
| Langfuse 服务挂了 | 低 | 切 PPT 截图讲解，说明"课后大家自己配置后可以看到" |
| Trace 加载太慢 | 低 | 先讲解 PPT 上的概念图，Trace 在后台加载 |
| Span 结构非嵌套 | 中 | 课前验证实际 Trace 结构，如扁平则调整讲解措辞或用截图替代 |

**PPT 备份截图清单**：
1. Trace 列表页（含时间/耗时/Token）
2. Span 树展开视图（25 轮嵌套）
3. 单轮 Generation 详情（**标注 System Prompt 与 User Message 分区**）
4. Tool Call 详情（Grep 输入/输出）
5. Token 统计面板（**箭头标注缓存读/写数字位置**）

---

## 七、与课程原则的对应关系

| 课程概念 | 本演示如何体现 |
|---------|-------------|
| Agent Loop 可追溯（§2.3） | 每轮 Loop 的输入输出都记录在 Langfuse |
| System Prompt 结构（§3.2） | 亲眼看到 CLAUDE.md 在 System Prompt 中的位置 |
| Token 缓存策略（§3.2） | 95% 缓存命中率可视化 |
| "亲眼看到 Agent 的思考过程"（§2.5 标题） | Langfuse 将概念变为可观测事实 |
