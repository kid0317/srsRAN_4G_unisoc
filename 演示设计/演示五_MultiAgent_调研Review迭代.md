# 演示五：Multi-Agent —— 调研→多角度 Review→迭代

**对应正文**：第二课 §7.4（实战案例：调研→多角度 Review→迭代）
**预计时长**：8–12 分钟（含讲解）
**默认方案**：展示预跑好的 Review 报告（确定性高），现场只跑 1 个 Agent 作演示（加分项）
**所在模块**：第六小节「Multi-Agent——一个人变一支团队」
**前置依赖**：已讲完 §7.1–§7.3（5 种模式 + 自定义 Agent + 主动技能论点）

---

## 一、演示目标

用 srsRAN_4G 错误码需求，走完"调研→设计方案→多 Agent 并行 Review→迭代"的完整流程，展示 Multi-Agent 的核心价值：**上下文隔离带来真正独立的视角**。

**核心教学点**：
1. Multi-Agent 的第一价值是**隔离**，不是并行——"让厨师品尝自己做的菜，品不出问题"
2. Multi-Agent 也是**主动技能**——主动告诉 Claude 启动什么 Agent
3. "调研→Review→迭代"是标准设计评审流程，三个 Reviewer 换成了 AI

---

## 二、前置准备

### 2.1 环境要求

| 项目 | 要求 |
|------|------|
| 代码库 | `/root/course/code/ziguangzhanrui_2/srsRAN_4G`（干净状态） |
| 自定义 Agent | `.claude/agents/security-reviewer.md`（提前创建，演示 §7.3 已展示） |
| 网络 | 需要访问 Claude API（并行 3 个 SubAgent 会同时发请求） |

### 2.2 创建自定义 Agent 文件

确保 `.claude/agents/security-reviewer.md` 已存在：

```markdown
---
name: security-reviewer
description: 审查代码变更的安全性。代码修改后主动使用。
tools: Read, Grep, Glob
model: sonnet
---

你是一个安全审查专家，专注于 C/C++ 通信协议栈代码的安全审查。

## 审查维度
- 缓冲区溢出、use-after-free、整数溢出（CWE-120/416/190）
- MISRA C/C++ 关键规则合规
- 竞态条件、死锁风险
- 错误码值域冲突、未处理的错误路径
- 硬编码密钥、IMSI/Ki 泄漏

## 输出格式
- [文件:行号] 问题描述 → 修复建议
- 按 Critical / High / Medium / Low 分级
```

> ⚠️ 注意：文件必须以 `---` 开头（YAML frontmatter），不要在前面加 markdown heading。

### 2.3 提前跑好演示一

本演示基于演示一的结果进行 Review。如果课堂上没有真实跑演示一，可以用预先准备好的 diff：

```bash
cd /root/course/code/ziguangzhanrui_2/srsRAN_4G
# 手动应用预期的代码变更（模拟演示一的结果）
```

或者直接用 PPT 展示 Review 过程。

---

## 三、演示流程

### Step 1：启动调研 Agent 出设计方案（2min）

**讲师输入**：

```
请启动一个子 Agent 来调研 srsRAN_4G 的错误码改动方案。
调研范围：
1. 读取 config.h，分析现有错误码定义和编号规则
2. 读取 sync.cc，找出 radio_recv_fnc 中的通用错误码使用
3. grep 搜索所有引用，确认影响范围
4. 输出设计方案：新增哪些错误码、编号多少、修改哪些文件、风险点
```

**预期输出**（调研 Agent 返回设计方案）：

```
设计方案：
1. 新增错误码：SRSRAN_ERROR_RADIO_RECV_FAIL = -9
2. 修改文件：
   - config.h（新增定义）
   - sync.cc（替换返回值 + 更新 switch 分支）
3. 不需修改：
   - ue_sync.c（< 0 检查天然兼容 -9）
4. 风险点：
   - search.cc 的 radio_recv_fnc 回调是否需要同步更新
   - 测试文件 dummy_phy_common.h 的兼容性
```

**讲解**：
> "第一步：先让一个 Agent 调研出设计方案。注意，这个调研 Agent 有自己独立的上下文——它从头开始读代码，不带任何先入为主。"

### Step 2：并行启动 3 个 Review Agent（3min）

**讲师输入**：

```
基于上面的设计方案，请并行启动 3 个子 Agent 进行 review：

1. 安全审查 Agent（用 /security-reviewer）：值域冲突？未处理的错误路径？整数溢出风险？
2. 代码质量 Agent：命名规范？编号连续？测试覆盖？
3. 架构兼容性 Agent：ue_sync.c 的 < 0 检查兼容吗？search.cc 的回调需要更新吗？需要更新文档吗？

请汇总三份报告，标注每个发现的优先级。
```

**讲解（等待期间）**：
> "注意我说的是'**并行**启动 3 个子 Agent'——它们同时从不同角度审查同一份方案，互不影响。这就是 Multi-Agent 的核心——**上下文隔离带来真正独立的视角**。"

### Step 3：展示 Review 报告汇总（2min）

**预期输出格式**：

```
═══ 多 Agent Review 汇总报告 ═══

安全审查 Agent：
  ✅ 编号 -9 无冲突（现有 -1 到 -8，-9 连续）
  ✅ 无整数溢出风险（负整数在 int 范围内）
  ⚠️ [Medium] sync.cc 的 default 分支处理逻辑建议细化

代码质量 Agent：
  ✅ 命名符合 SRSRAN_ERROR_<描述> 规范
  ✅ 编号连续递减
  ❌ [High] 缺少 SRSRAN_ERROR_RADIO_RECV_FAIL 的单元测试

架构兼容性 Agent：
  ✅ ue_sync.c 的 < 0 检查天然兼容 -9
  ⚠️ [Medium] search.cc 的 radio_recv_fnc 回调建议同步处理
  ⚠️ [Low] 建议更新 API 文档说明新错误码
```

**讲解**：
> "三个 Agent 各自独立审查——安全角度、质量角度、架构角度。这跟你们团队做设计评审的标准流程一模一样，只不过 Reviewer 换成了 AI。"

### Step 4：基于 Review 迭代（1–2min）

**讲师输入**：

```
请基于 Review 报告迭代方案：
1. 修复 [High]：补充单元测试
2. 处理 [Medium]：更新 sync.cc default 分支 + search.cc 回调
3. 重新运行质量 Agent 确认修复
```

**讲解**：
> "调研→方案→多角度 Review→迭代。这不是 AI 独有的——这就是标准的设计评审流程。Multi-Agent 让你一个人就能运转这个流程。"

---

## 四、关键讲解点

### 4.1 上下文隔离的价值

> "让写代码的人 Review 自己的代码，就像让厨师品尝自己做了一百次的菜——他已经习惯了那个味道。每个 Worker 启动时上下文是干净的，不带先入为主。**Multi-Agent 的第一价值不是并行，是隔离。**"

**课程原则映射**：§7.1 上下文污染问题

### 4.2 工具权限约束

> "注意 security-reviewer 的定义里——tools 只有 Read、Grep、Glob、Bash，**没有 Edit 和 Write**。它**物理上**只能看、不能改。'物理上做不到'比'希望你别做'更可靠。"

**课程原则映射**：§7.3 自定义 Agent 的 tools 字段

### 4.3 主动技能使用方式

> "我刚才的指令里明确说了'并行启动 3 个子 Agent'——不是等 Claude 自己判断要不要用。**Multi-Agent 也是主动技能**。"

**课程原则映射**：§7.4 "主动告诉 Claude 启动什么 Agent"

### 4.4 并行 vs 链式

> "今天展示的是**并行 Review 模式**——多个 Agent 同时从不同角度审查。还有一种是**链式调用**——Agent A 的输出喂给 Agent B。可靠性保障原则相同：每个节点的输出都要有验收标准。"

**课程原则映射**：§7.4 最后一段

---

## 五、自定义 Agent 文件位置

```
/root/course/code/ziguangzhanrui_2/srsRAN_4G/
├── .claude/
│   └── agents/
│       └── security-reviewer.md     ← 自定义安全审查 Agent
```

---

## 六、失败预案

| 风险 | 概率 | 应对 |
|------|------|------|
| SubAgent 启动太慢 | 中 | 说明"并行 Agent 需要同时发多个 API 请求" |
| Claude 不启动并行 Agent | 中 | 手动分步发指令，一个一个启动；至少让学员看到一个 SubAgent 的启动和返回 |
| Claude 在主对话直接分析不用 SubAgent | 高 | 明确追加指令"请确认启动独立子代理，不要在主对话中回答"；或切换到 PPT 备份 |
| Review 结果太浅 | 中 | 用 PPT 展示预期的 Review 报告（提前准备好） |
| 总时间超 12min | 中 | 切换到 PPT 备份讲解，口述迭代流程 |
| API 并发限流（429） | 中 | 改为顺序启动，每个间隔 10 秒；或切 PPT |
| SubAgent 返回空/无关内容 | 低 | 话术："这说明 Agent 的 System Prompt 需要优化——第三课讲 Skill 创建技巧时会解决" |

**PPT 备份**：
提前准备一份完整的 Review 汇总报告 PPT，如果现场执行时间太长可切换到 PPT 讲解。

---

## 七、弹幕互动

演示结束后：
> "你们团队的 Code Review，通常从哪几个角度审查？"

预期回答：功能正确性、安全合规（MISRA）、性能、可维护性、测试覆盖等。

**衔接**：
> "你们提到的每一个角度，都可以变成一个自定义 Agent。配置一次，团队共享。"

---

## 八、与课程原则的对应关系

| 课程概念 | 本演示如何体现 |
|---------|-------------|
| 上下文隔离（§7.1） | 3 个 Review Agent 各自独立，不带先入为主 |
| 约束（§7.1） | security-reviewer 只有只读工具 |
| 复用（§7.1） | Agent 定义是 .md 文件，提交 git 团队共享 |
| Coordinator-Worker 模式（§7.2） | 主 Agent 编排，Worker 并行执行 |
| 主动技能（§7.3+§7.4） | 明确指令启动 SubAgent |
| "调研→Review→迭代"（§7.4） | 完整走通标准设计评审流程 |
| 多模型分层（§7.3） | security-reviewer 用 Sonnet，调研用默认模型 |
