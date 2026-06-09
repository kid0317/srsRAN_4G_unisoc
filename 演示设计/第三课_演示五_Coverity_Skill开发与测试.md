# 演示五：Coverity Triage Skill 开发 + 测试 + 实际触发

**对应正文**：第三课 §2.4.3 阶段二：开发 Skill + §2.4.4 阶段三：测试
**预计时长**：9 分钟（含讲解）
**所在模块**：第二节「Skill × MCP」→ Coverity 审查辅助完整演示

---

## 一、演示目标

完整走通 Skill 开发四阶段中的「阶段二：开发」和「阶段三：测试」。从指令式 Description 到分流决策树，从触发测试到 with/without 对比，让学员看到 Skill 从"能用"到"好用"的全过程。**重点增强**：Skill 不只做分流判定——还指导 Claude 去本地代码做检查验证。

**核心教学点**：
1. Description 决定触发率——被动式 37% vs 指令式 100%（650 次实验）
2. 决策树是 Skill 的灵魂——老工程师脑子里的经验编码为 SOP
3. 代码检查指令——Skill 里写明"打开文件、看上下文、判断是否真正有问题"
4. 三级加载节省 97% Token——20 个 Skill 未触发仅 2000 token
5. 测试三重验证——触发测试 + 功能测试 + 工具支撑测试
6. with/without 对比——60% vs 90%，Skill 带来 30% 准确率提升

---

## 二、前置准备

### 2.1 环境要求

| 项目 | 要求 |
|------|------|
| 演示四完成 | Coverity MCP Server 已配置并验证通过 |
| Skill 代码 | `/root/course/企业培训/001-紫光展锐/第三课_Skill演示/skills/coverity-triage-sop/` |
| Mock 数据 | `mock_findings.json` 10 条（来源：告警清单 6 种 Checker） |
| 网络 | 需要访问 Claude API |

### 2.2 确认 Skill 文件就位

```bash
ls -la /root/course/企业培训/001-紫光展锐/第三课_Skill演示/skills/coverity-triage-sop/
# 预期：SKILL.md + evals/
cat /root/course/企业培训/001-紫光展锐/第三课_Skill演示/skills/coverity-triage-sop/SKILL.md | head -20
```

### 2.3 Mock 数据与代码检查的对应关系

Skill 演示时 Claude 会根据 mock finding 的文件路径去本地代码做检查。确保以下对应关系成立：

| Mock Finding ID | 文件路径 | 预期 Claude 行为 |
|----------------|---------|-----------------|
| 1001 (UNINIT) | `srsenb/src/stack/rrc/rrc_ue.cc:245` | 读文件 → 检查是否有 memset 或构造函数初始化 |
| 1002 (BAD_SHIFT) | `lib/src/phy/common/phy_common.c:112` | 读文件 → 看 bit_width 有无边界检查 |
| 1004 (NULL_RETURNS) | `srsenb/src/stack/mac/scheduler.cc:334` | 读文件 → 确认 find_ue 返回值无 null check |
| 1005 (RESOURCE_LEAK) | `lib/src/common/mac_pcap.cc:89` | 读文件 → 看错误路径有无 fclose |
| 1007 (BAD_SHIFT) | `lib/src/phy/fec/turbo/tc_interl_lte.c:78` | 读文件 → 确认 f2 范围 0-15，shift 安全 |
| 1010 (UNINIT) | `lib/src/phy/ue/ue_dl.c:156` | 读文件 → 看到 memset → FALSE POSITIVE |

> **课前必做**：手动验证以上文件路径和行号在 srsRAN_4G 代码库中存在且匹配。如有偏移，调整 mock_findings.json 的行号。

---

## 三、演示步骤

### Part A：阶段二——开发 Skill（5min）

#### Step 1：指令式 Description（1min）

展示 SKILL.md 的 frontmatter：

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

**讲解**："三要素看清楚——**ALWAYS invoke 开头**，7+ 触发短语全列出来，**Do NOT skip 收尾**。650 次实验——被动式 37%，指令式 100%，差 20 倍。对比一下：如果我写 'Use when the user mentions Coverity findings'——被动式，加了 Hook 后掉到 37%。"

#### Step 2：MCP 依赖声明（30s）

展示 Prerequisites 章节：

```markdown
## Prerequisites
coverity-server MCP provides:
  - list_findings
  - get_finding_detail
  - get_finding_stats
  - update_finding_status
```

**讲解**："Skill 不自己获取数据——它告诉 Claude 用 MCP 工具去获取。没连上时 Claude 提前告知，而不是跑到一半报错。"

#### Step 3：分流决策树 + 代码检查指令（2min）——核心！

展示 SKILL.md 的决策树部分——**每棵树包含代码检查步骤**：

```
Decision Tree: UNINIT
├─ Step 0: 用 Read 工具打开 finding 指向的文件，定位到告警行号
│         的前后 30 行上下文。确认实际代码与 finding 描述一致。
├─ Q1: 被 memset/构造函数/聚合初始化？       → FALSE POSITIVE
│      检查方法：搜索变量声明到使用之间是否有 memset(&var, 0, sizeof(var))
├─ Q2: 所有可达路径都初始化了？               → FALSE POSITIVE
│      检查方法：追踪所有 if/else 分支，确认每条路径都有赋值
├─ Q3: 循环变量在循环头初始化？               → FALSE POSITIVE
│      检查方法：看 for/while 循环头
└─ Q4: 确实有路径未初始化？                   → TRUE POSITIVE → 修复
       修复建议：在声明时初始化，或在条件分支外添加默认值

Decision Tree: BAD_SHIFT
├─ Step 0: 用 Read 工具打开文件，定位移位操作行，
│         查看移位量的来源和类型宽度。
├─ Q1: 移位量是编译期常量且 < 类型宽度？      → FALSE POSITIVE
│      检查方法：看移位量是否为字面量或 #define 常量
├─ Q2: 移位量受规范/表格限定（如 LTE 交织表）？ → FALSE POSITIVE
│      检查方法：追踪变量来源，看是否受 spec 表限定（如 f2 ≤ 15）
├─ Q3: 移位前有 bounds check？                → FALSE POSITIVE
│      检查方法：看上方是否有 if (shift_amount >= 32) 之类的检查
└─ Q4: 运行时变量无边界检查？                  → TRUE POSITIVE → 加检查
       修复建议：添加 assert(shift < sizeof(type)*8) 或 bounds check

Decision Tree: DEADCODE
├─ Step 0: 用 Read 工具打开文件，定位 dead code 块，
│         查看周围的预处理指令和 switch 结构。
├─ Q1: 在 #ifdef / #if 条件编译块内？         → FALSE POSITIVE
│      检查方法：看告警代码上方是否有 #ifdef/#if 指令
├─ Q2: switch 覆盖全部 enum 的防御性 default？ → FALSE POSITIVE
│      检查方法：看 switch 变量的 enum 定义，确认 default 是防御性的
├─ Q3: 带 "legacy"/"compat" 注释？            → FALSE POSITIVE
│      检查方法：看代码块周围注释
└─ Q4: 无正当理由？                           → TRUE POSITIVE → 建议删除
       修复建议：确认无副作用后删除，或加注释说明保留理由
```

**讲解要点**：
- "**看 Step 0——每棵决策树第一步都是'打开文件看代码'。** Skill 不只是判断规则——它告诉 Claude 怎么去验证。"
- "UNINIT Q1——memset 是嵌入式 C 最常见初始化模式，Coverity 经常漏掉。一个问题过滤大量误报"
- "BAD_SHIFT Q2——LTE turbo 交织表 f2 最大 15，uint32_t 移 15 位完全安全。**这条直接对应 mock finding 1007 和你们告警清单的同类问题**"
- "DEADCODE Q1——`#ifdef` 条件编译，展锐项目 DEADCODE 误报的第一大来源"
- "**这些判断规则 + 检查方法，就是你们老工程师脑子里的东西。以前口口相传，现在写进 Skill，AI 每次按标准执行**"

#### Step 4：报告模板（30s）

展示 SKILL.md 的报告模板部分：

```markdown
## 输出格式

### 单条 Finding 报告
| 字段 | 内容 |
|------|------|
| Finding ID | {id} |
| Checker | {checker} |
| 文件 | {file}:{line} |
| 判定 | TRUE POSITIVE / FALSE POSITIVE |
| 依据 | {决策树哪个问题命中，代码检查发现了什么} |
| 修复建议 | {仅 TRUE POSITIVE 填写} |
| 优先级 | {Critical/High/Medium/Low} |
```

**讲解**："True Positive 有修复建议和优先级，False Positive 有审计理由——**包含代码检查发现了什么**。Claude 每次产出格式一致。不写模板——第一次 Markdown，第二次纯文本，第三次 JSON。"

---

### Part B：阶段三——测试（4min）

#### Step 5：触发测试——8 正例 + 8 负例（1min）

展示触发测试列表：

```
✅ 正例（应该触发）：
  "刚跑完 Coverity，出来 47 个 findings，帮我看看"
  "BAD_SHIFT 在 modulator.c，是不是误报"
  "帮我分流 Coverity 告警"
  "这个 UNINIT 是真的还是假的"

❌ 负例（不应该触发）：
  "帮我写 Python 脚本解析 Coverity JSON"        ← 开发任务
  "帮我配置 Coverity Connect 的 LDAP"            ← 运维
  "帮我写单元测试"                                ← 测试
  "帮我看看这段 C 代码有没有 bug"                  ← 通用 CR
```

**讲解**："负例覆盖近似但不应触发的场景——'配置 Coverity 服务器'是运维不是分流。如果负例也触发了，Description 太宽——回去收窄。"

#### Step 6：实际触发 Live Demo（2min）——整个演示的高潮

在 Claude Code 中输入：

```
帮我把 Coverity 扫描结果分流一下
```

**预期行为序列**：

```
Claude 行为序列：
  1. 匹配 description → 加载 coverity-triage-sop Skill
  2. get_finding_stats() → "10 findings: High 4, Medium 2, Low 4"
  3. list_findings(severity="High") → 4 个高危先处理
  4. get_finding_detail(1001) → 获取 UNINIT 详情
  5. ★ Read srsenb/src/stack/rrc/rrc_ue.cc:245（Skill Step 0 指导）
     → 查看上下文，没找到 memset → Q4 命中 → TRUE POSITIVE
  6. get_finding_detail(1004) → 获取 NULL_RETURNS 详情
  7. ★ Read srsenb/src/stack/mac/scheduler.cc:334
     → 确认 find_ue 返回值没有 null check → TRUE POSITIVE
  8. ... 处理全部 10 个 findings
  9. 产出标准分流报告（含代码检查依据）
```

**讲解**：
- "Claude 自动加载 Skill，按步骤执行。"
- "**看步骤 5 和 7——它不只是看了 Coverity 的描述就下判断。它打开了本地代码文件去验证。** 这就是 Skill 里 Step 0 的作用。"
- "整个过程没问我'怎么判断 BAD_SHIFT'——Skill 里写得清清楚楚。"

#### Step 7：with/without 对比数据（1min）

展示 PPT 对比表：

```
┌──────────────┬──────────────┬────────────┐
│ 指标         │ with Skill   │ without    │
├──────────────┼──────────────┼────────────┤
│ 分类准确率   │ ~90%         │ ~60%       │
│ 代码检查     │ 每条都打开   │ 随机跳过   │
│              │ 文件验证     │            │
│ 报告格式     │ 每次一致     │ 每次不同   │
│ MCP 调用     │ 有序完整     │ 可能遗漏   │
│ 判定依据     │ 引用代码行   │ 凭描述猜   │
└──────────────┴──────────────┴────────────┘
```

**讲解**：
- "差 30%：没有 Skill 的 Claude 不知道 #ifdef 是嵌入式常见误报模式。**你们团队的经验，就是这 30% 的来源。**"
- "**注意'代码检查'这一行——有 Skill 时每条都去看了文件，没 Skill 时经常跳过。** Skill 里的 Step 0 保证了这个行为。"

**反问**："**这 10 个 findings 我们 5 分钟分完了。你们上周花了多久？**"

---

## 四、演示节奏总览

| 时间点 | 阶段 | 讲师动作 | 讲解要点 |
|--------|------|---------|---------|
| 0:00 | 开发 | 展示 Description | "三要素：ALWAYS invoke、7+ 触发词、Do NOT skip" |
| 0:45 | 开发 | 展示 MCP 依赖 | "Skill 管流程，MCP 管数据" |
| 1:15 | 开发 | 展示决策树 | "**Step 0 先看代码，再做判断——老工程师脑子里的东西**" |
| 3:00 | 开发 | 展示报告模板 | "没模板——每次格式都不同" |
| 3:30 | 测试 | 展示触发测试列表 | "8 正 + 8 反是底线" |
| 4:30 | 测试 | 输入触发 prompt | "帮我把 Coverity 扫描结果分流一下" |
| 5:00 | 测试 | Claude 开始执行 | "看 MCP 调用序列——自动加载 Skill，按步骤走" |
| 6:00 | 测试 | Claude 打开本地代码 | "**Step 0 起作用了——它在验证代码**" |
| 6:30 | 测试 | Claude 输出报告 | 展示分流报告格式（含代码检查依据） |
| 7:00 | 测试 | 展示对比数据 | "with 90% vs without 60%，**经验就是这 30%**" |
| 8:00 | 收尾 | 反问 | "**10 个 findings 5 分钟。你们上周花了多久？**" |

---

## 五、关键讲解点

### 5.1 决策树 + 代码检查是 Skill 的灵魂

> "看 UNINIT——**第一步不是直接判断，是打开文件看代码。** Q1 问'memset 初始化了吗？'怎么确认？去文件里搜 memset。嵌入式 C 代码里 memset 是最常见的初始化模式，Coverity 经常漏掉。一个问题过滤大量误报。"

### 5.2 领域知识编码

> "BAD_SHIFT Q2——LTE turbo 交织表 f2 最大 15，uint32_t 移 15 位完全安全。Coverity 不知道这个领域约束。**这些判断规则，就是你们老工程师脑子里的东西。** mock finding 1007 就是这个场景——Claude 打开 `tc_interl_lte.c` 看到 f2 来自 LTE 规范表，直接判 FALSE POSITIVE。"

### 5.3 代码检查让判定有据可依

> "without Skill 时 Claude 看到'variable may contain garbage value'就判 TRUE POSITIVE——但它没去看代码，没发现下面就有 memset。**Skill 里写了 Step 0 '先看代码'——这一步让准确率从 60% 到 90%。** 不是 AI 变聪明了，是 SOP 让它做了该做的事。"

### 5.4 from 60% to 90%

> "没有 Skill 的 Claude 不知道 #ifdef 是嵌入式常见误报模式。你们团队的经验，就是这 30% 的来源。"

---

## 六、失败预案

| 风险 | 概率 | 应对 |
|------|------|------|
| Skill 未触发 | 低 | 检查 Description 是否为指令式；重启 Claude Code |
| MCP 连接失败 | 中 | 检查 settings.json 中 MCP 配置路径 |
| Claude 没有打开本地代码验证 | 中 | 说明"Skill 是 SOP 不是强制——Step 0 写了但 Claude 可能跳过。多跑几次验证" |
| 分流结果不准确 | 中 | 说明"这就是阶段四迭代的意义——收集 bad case 更新决策树" |
| 执行时间过长（10 个 findings） | 中 | 提前说明"课堂只跑 3-4 个，剩下的时间不够" |
| Mock 文件路径与实际代码不匹配 | 中 | 课前验证文件路径；不匹配则说明"mock 路径偏移不影响逻辑演示" |

---

## 七、演示后恢复

```bash
# 如果 update_finding_status 修改了 mock 数据
cd /root/course/企业培训/001-紫光展锐/第三课_Skill演示/coverity-mcp-server
git checkout -- mock_findings.json
```

---

## 八、与课程原则的对应关系

| 课程概念 | 本演示如何体现 |
|---------|-------------|
| 四阶段方法论 阶段二（§2.3） | 完整走通 Description→决策树→报告模板 |
| 四阶段方法论 阶段三（§2.3） | 触发测试 + with/without 对比 |
| 650 次实验（§2.3） | 指令式 100% vs 被动式 37% |
| 三级加载（§2.3） | Frontmatter ~100 token，SKILL.md ~5K token |
| Skill + MCP 组合（§2.0） | Skill 管流程（决策树+代码检查），MCP 管数据（findings） |
| 代码检查指令（新增教学点） | 决策树 Step 0——先读文件再判断 |
| Mock 数据来源 | 基于真实告警清单构造，文件路径对应本地代码 |
| "没测过的 Skill 和没测过的代码一样"（§2.3） | 三重验证体现测试重要性 |
