# 演示七：多 Agent 并行安全审查 —— 产出代码安全

**对应正文**：第三课 §4.1.3 实战演示
**预计时长**：5 分钟（含讲解）
**所在模块**：第四节「安全防护」

---

## 一、演示目标

展示四 Agent 并行审查 security.cc 的完整流程：Agent 定义 → 并行启动 → 汇总去重 → 分级报告。让学员看到 AI 多视角安全审查的实际效果，以及与 cppcheck 的检出率对比。

**核心教学点**：
1. 多 Agent > 单 Agent——组合不同检测模式发现更多 bug（76.1% 检出率）
2. tools 白名单只给 Read/Grep/Glob——安全 Agent 只审查不修改
3. 安全知识库六大领域——知识库质量决定 Agent 专业性
4. cppcheck 0 个 vs AI Agent 7 个——模式匹配 vs 调用上下文追踪
5. 每条发现都有 CWE 编号 + 攻击场景 + 修复建议

---

## 二、前置准备

### 2.1 环境要求

| 项目 | 要求 |
|------|------|
| 代码库 | `/root/course/code/ziguangzhanrui_2/srsRAN_4G` |
| Agent 定义 | `.claude/agents/security-reviewer.md` 已存在 |
| 安全知识库 | 正文引用的 `srsran-security/` Skill（需要创建或准备） |
| 网络 | 需要访问 Claude API |

### 2.2 更新 Agent 定义（课前必做）

项目中已有 `security-reviewer.md`（model: sonnet），需按正文要求更新并新增 Agent：

```bash
cd /root/course/code/ziguangzhanrui_2/srsRAN_4G/.claude/agents/

# 更新安全审查员 Agent（Opus，对齐正文 §4.1.2）
cat > telecom-security-reviewer.md << 'EOF'
---
name: telecom-security-reviewer
description: "C/C++ 电信协议栈安全审查专家。检测内存安全漏洞、密码学缺陷、
  输入验证问题。在审查 C/C++ 代码安全性时 ALWAYS invoke。"
tools: ["Read", "Grep", "Glob"]
model: opus
---
## 审查原则
1. 对抗性视角：假设攻击者能通过空口发送恶意 NAS/RRC 消息
2. 写不出攻击场景就降级：不确定标记 MEDIUM，不标 CRITICAL
3. 零容忍：memcpy 无边界检查 / free 后未置 NULL / 硬编码密钥 / 格式字符串

## 高危文件清单
| 文件 | 不安全函数数 | 优先级 | 已知风险 |
|------|-------------|--------|---------|
| security.cc | 44 (memcpy) | P0 | calloc 无 NULL 检查 |
| nas.cc | 33 | P0 | NAS 消息解析溢出 |
| liblte_security.cc | 9 | P0 | 密钥派生固定长度 |
EOF

# 新增嵌入式特化 Agent
cat > embedded-specialist-reviewer.md << 'EOF'
---
name: embedded-specialist-reviewer
description: "嵌入式系统安全审查专家。检测 ISR/DMA/RTOS 相关安全问题。"
tools: ["Read", "Grep", "Glob"]
model: sonnet
---
## 审查维度
- ISR 中禁止操作（malloc/printf/浮点运算）
- DMA 缓冲区对齐和缓存一致性
- RTOS 优先级反转、死锁
- 硬件寄存器越界访问
EOF

# 新增合规检查 Agent
cat > compliance-reviewer.md << 'EOF'
---
name: compliance-reviewer
description: "C/C++ 编码合规检查专家。检测 MISRA C/CERT C 违规。"
tools: ["Read", "Grep", "Glob"]
model: sonnet
---
## 审查维度
- MISRA C:2025 关键规则违规
- CERT C 安全编码规则（MEM30-C, STR31-C 等）
- 危险函数使用（gets, sprintf, strcpy 等）
EOF
```

### 2.3 确认目标文件

```bash
# 确认目标文件存在且有足够内容
wc -l lib/src/common/security.cc
# 确认 memcpy 调用数量
grep -c "memcpy" lib/src/common/security.cc
```

### 2.3 准备 cppcheck 对比数据（可选）

```bash
# 如果安装了 cppcheck
cppcheck --enable=all --force lib/src/common/security.cc 2>&1 | head -20
```

### 2.4 部署安全知识库 Skill（课前必做）

从已有素材部署到项目中：

```bash
cd /root/course/code/ziguangzhanrui_2/srsRAN_4G

# 创建 Skill 目录
mkdir -p .claude/skills/srsran-security/references

# 从已有实测素材复制（需检查目录下是否有对应文件）
# 如果 第三课_安全Agent实测/ 下有 security-patterns.md，复制过来：
cp /root/course/企业培训/001-紫光展锐/第三课_安全Agent实测/security-patterns.md \
   .claude/skills/srsran-security/references/ 2>/dev/null || \
   echo "⚠️ 安全知识库文件不存在，需要课前创建"

# 确认 Skill 结构
ls -la .claude/skills/srsran-security/
```

目标结构：
```
.claude/skills/srsran-security/
├── SKILL.md                     ← 安全审查 Skill
└── references/
    └── security-patterns.md     ← 六大领域知识库（~1250 行）
```

> **如果素材不存在**：需要根据正文 §4.1.1 的六大领域描述课前创建 security-patterns.md，至少涵盖内存安全（CWE-787/120/416）、整数安全（CWE-190）、密码学安全（CWE-327/798）的 BAD/GOOD 代码对比。

---

## 三、演示步骤

### Step 1：展示 Agent 定义 + 安全知识库结构（1min）

展示 `security-reviewer.md` Agent 定义：

```yaml
---
name: telecom-security-reviewer
description: "C/C++ 电信协议栈安全审查专家。检测内存安全漏洞、密码学缺陷、
  输入验证问题。在审查 C/C++ 代码安全性时 ALWAYS invoke。"
tools: ["Read", "Grep", "Glob"]
model: opus
---
```

**讲解要点**：
- "tools 白名单只给 Read/Grep/Glob——**纯只读。安全 Agent 只审查不修改**"
- "model: opus——安全审查用最强模型，质量优先"

展示高危文件清单：

```
| 文件 | 不安全函数数 | 优先级 | 已知风险 |
|------|-------------|--------|---------|
| security.cc | 44 (memcpy) | P0 | calloc 无 NULL 检查 |
| nas.cc | 33 | P0 | NAS 消息解析溢出 |
| liblte_security.cc | 9 | P0 | 密钥派生固定长度 |
```

**讲解**："高危文件清单不是通用清单——从 srsRAN 实际代码统计出来。security.cc 有 44 个 memcpy 调用，每一个都是潜在溢出点。"

展示四 Agent 分工架构（PPT）：

```
           待审查代码（security.cc）
     ┌──────────┼──────────┬──────────┐
     ▼          ▼          ▼          ▼
 Agent 1    Agent 2    Agent 3    Agent 4
 安全审查员  质量风险    嵌入式特化  合规检查
 CWE/内存/  复杂度/    ISR/DMA/   MISRA C/
 密码学     技术债     RTOS/硬件   CERT C
 (Opus)     (Sonnet)   (Sonnet)   (Sonnet)
```

**讲解**："为什么多 Agent？单个 Agent 放六领域检查清单，前面查得细后面草率——检查疲劳。Codex-Verify 论文证明：组合不同检测模式 76.1% 检出率。"

### Step 2：启动多 Agent 审查（2min live demo）

在 Claude Code 中输入：

```
用安全审查 Agent 检查 lib/src/common/security.cc
```

**预期行为**：

```
四 Agent 并行启动：
  安全审查员 → memcpy 无边界检查（CWE-120）、calloc 未检查返回值（CWE-252）
  质量风险   → 函数圈复杂度 >15、重复模式未抽象
  嵌入式特化 → MD5 用于安全校验（CWE-327）、密钥材料泄露日志（CWE-200）
  合规检查   → MISRA C:2025 违规 3 项、CERT C MEM30-C 违规

汇总 Agent → 去重 → 交叉验证 → 分级报告
```

> **注意**：如果项目中只有单个 security-reviewer Agent 而非四个独立 Agent，可在 prompt 中指定多视角审查，或使用已有的 security-reviewer + code-quality-reviewer + architecture-reviewer 三个 Agent。

### Step 3：展示审查报告（1min）

展示预期报告格式：

```
[SEC-001] CWE-120: memcpy 无长度校验（security.cc:kdf_common）
  严重性：CRITICAL
  攻击场景：空口发送超长 NAS 消息 → 堆溢出 → 远程代码执行
  修复建议：memcpy 前加 msg_len ≤ sizeof(buffer) 检查

[SEC-002] CWE-252: calloc 返回值未检查（security.cc:kdf_common）
  严重性：CRITICAL
  修复：calloc 后加 if (!ptr) return SRSRAN_ERROR

[SEC-003] CWE-327: MD5 用于安全校验（security.cc）
  严重性：HIGH
  修复：替换为 SHA-256 / HMAC-SHA-256
```

**讲解**："每条发现都有 CWE 编号、攻击场景、具体修复建议。不是'可能有问题'——是'攻击者通过空口发超长 NAS 消息，触发堆溢出'。"

### Step 4：cppcheck 对比数据（1min）

```
对比：cppcheck vs AI Agent（同一文件 security.cc）

cppcheck：故意漏洞 7 个 → 检出 0 个
AI Agent：故意漏洞 7 个 → 检出 7 个（100%）

原因：
  cppcheck 做模式匹配 → 不追踪 msg_len 来源
  AI Agent 追踪调用上下文 → msg_len 来自外部输入，可能 > 256
```

**讲解**：
- "cppcheck 扫 7 个故意漏洞——检出 **0 个**。AI Agent 同一文件——**7 个全部找到**"
- "cppcheck 做模式匹配，Agent 追踪调用上下文——`msg_len` 来自外部输入可能大于 256，cppcheck 不追踪，Agent 追踪"
- "**新安全审查员培训三个月——Agent 读完知识库立即上岗，而且不会遗漏检查项**"

---

## 四、演示节奏总览

| 时间点 | 讲师动作 | 讲解要点 |
|--------|---------|---------|
| 0:00 | 展示 Agent 定义 | "tools 只读——安全 Agent 只审查不修改" |
| 0:20 | 展示高危文件清单 | "44 个 memcpy，每一个都是溢出点" |
| 0:40 | 展示四 Agent 架构图 | "多 Agent 避免检查疲劳，76.1% 检出率" |
| 1:00 | 粘贴 prompt 启动审查 | "用安全审查 Agent 检查 security.cc" |
| 1:30 | 四 Agent 并行运行 | "注意——四个同时在跑，不是串行" |
| 2:30 | 汇总 Agent 输出报告 | "去重 → 交叉验证 → 分级" |
| 3:00 | 展示报告前三条 | "CWE 编号 + 攻击场景 + 修复建议" |
| 3:30 | 展示 cppcheck 对比 | "**cppcheck 0 个，Agent 7 个全部找到**" |
| 4:00 | 解释差异原因 | "模式匹配 vs 调用上下文追踪" |
| 4:30 | 总结 | "**新安全审查员培训三个月，Agent 读完知识库立即上岗**" |

---

## 五、关键讲解点

### 5.1 多 Agent 的必要性

> "一个审查员看不全——单个 Agent 放六领域检查清单，前面查得细后面草率，检查疲劳。Codex-Verify 论文证明：组合不同检测模式的 Agent 比单 Agent 能发现更多 bug——76.1% 检出率。"

### 5.2 纯只读设计

> "关键设计——tools 白名单只给 Read/Grep/Glob，纯只读。安全 Agent 只审查不修改，发现问题报告给人，由人决定修复。"

### 5.3 CVE 实例连接

> "security.cc 的 memcpy 无边界检查——跟你们 CVE-2022-20210 一个类型。NAS 消息解析堆缓冲区溢出。Agent 能发现，cppcheck 发现不了。"

---

## 六、失败预案

| 风险 | 概率 | 应对 |
|------|------|------|
| Agent 执行时间过长 | 高 | 只运行 1-2 个 Agent 而非四个并行；或用提前跑好的结果 |
| Agent 未发现已知漏洞 | 低 | 说明"知识库需要不断补充——阶段四迭代" |
| 报告格式不一致 | 中 | 说明"报告模板在 Skill 中定义，确保一致性" |
| cppcheck 未安装 | 中 | 用 PPT 展示对比数据 |
| 四 Agent 结果太多无法在课上全展示 | 中 | 只展示 Top 3 CRITICAL 发现 |

---

## 七、演示后恢复

安全审查为只读操作，无代码修改，无需恢复。

---

## 八、与课程原则的对应关系

| 课程概念 | 本演示如何体现 |
|---------|-------------|
| 两层安全逻辑 Layer A（§4.0） | 产出的代码安全——多 Agent 审查 |
| 安全知识库六大领域（§4.1.1） | 内存/整数/密码学/并发/协议/输入验证 |
| 多 Agent 审查架构（§4.1.2） | 四 Agent 并行 → 汇总去重 → 分级报告 |
| cppcheck 对比（§4.1.3） | 0 vs 7，模式匹配 vs 上下文追踪 |
| CVE 案例连接（§4.0） | CVE-2022-20210 同类问题 |
| Codex-Verify 论文（§4.1.2） | 76.1% 检出率数据支撑 |
