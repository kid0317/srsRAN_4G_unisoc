# 演示二B：CODEMAP + LLM Wiki —— 给 Agent 看的 Layer 2

**对应正文**：第三课 §1.2 Layer 2（给 Agent 看的部分）+ §1.2.5 LLM Wiki 方法论
**预计时长**：4 分钟（含讲解）
**所在模块**：第一节「知识建设」

---

## 一、演示目标

展示"给 Agent 看的"代码知识地图（CODEMAP）的生成过程，并对接 Karpathy LLM Wiki 方法论。让学员理解：CODEMAP 不是随便写个目录树——而是 Agent 代码导航的核心基础设施，需要用工具 + LLM 编译双层架构来构建和维护。

**核心教学点**：
1. CODEMAP 是 Agent 的代码导航图——改 PHY 代码先查 CODEMAP 定位文件
2. 工具出骨架 + LLM 出语义——Tree-sitter 提取符号关系，LLM 补充业务含义
3. LLM Wiki 三操作：Ingest（摄入）→ Query（查询）→ Lint（健康检查）
4. CLAUDE.md 必须索引 CODEMAP——不索引等于没有
5. Layer 2 vs Layer 3 边界——CODEMAP 是知识层面（模块/接口/数据结构），AST 是编译器层面

---

## 二、前置准备

### 2.1 环境要求

| 项目 | 要求 |
|------|------|
| 代码库 | `/root/course/code/ziguangzhanrui_2/srsRAN_4G` |
| 演示一完成 | CLAUDE.md 已存在 |
| 演示二A完成 | 接口清单和数据模型信息已有 |

### 2.2 可选：安装 CODEMAP 辅助工具

以下工具可在课前安装用于对比演示，非必需：

```bash
# 方案 A：RepoMapper（Aider RepoMap 独立版，推荐）
# Tree-sitter + PageRank 自动生成代码地图
pip install repomapper  # 或 git clone https://github.com/pdavis68/RepoMapper

# 方案 B：Codemap（JordanCoin，Claude Code Skill）
# 实时代码上下文生成
pip install codemap

# 方案 C：karpathy-llm-wiki（LLM Wiki 的 Agent Skill 实现）
# git clone https://github.com/Astro-Han/karpathy-llm-wiki
```

> **课堂推荐**：直接用 Claude prompt 生成 CODEMAP，再讲工具生态作为延伸。

---

## 三、演示指令

### Step 1：生成 CODEMAP.md（给 Agent 看的代码地图）

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

**讲解**："CODEMAP 是给 Agent 看的——不需要好看，需要精确。Agent 改 PHY 代码时先查 CODEMAP 定位文件，不盲目全量扫描。"

### Step 2：在 CLAUDE.md 中添加索引

```
在 CLAUDE.md 中添加 Code Knowledge Map 章节，索引 CODEMAP.md：

## Code Knowledge Map
- 代码地图：`CODEMAP.md` — 按模块组织的核心文件、接口、依赖关系
- 项目全景：`docs/project-overview.html` — 架构图+接口清单+数据模型
- 更新方法：代码结构变更后重新 Ingest CODEMAP
```

**讲解**："**不索引等于没有。** Agent 读 CLAUDE.md 时才知道 CODEMAP 存在。"

### Step 3：讲解 LLM Wiki 三操作（PPT + 口头）

```
LLM Wiki 三操作对接 CODEMAP：

Ingest（摄入）：
  代码变更 → 重新扫描 → 更新 CODEMAP.md
  可用 RepoMapper 自动化：python repomap.py . --map-tokens 4096

Query（查询）：
  Agent 遇到代码导航问题 → 先查 CODEMAP → 定位目标文件
  "srsRAN 的 MAC 层调度器在哪？" → CODEMAP → lib/src/mac/scheduler*.cc

Lint（健康检查）：
  定期检查 CODEMAP 与代码是否漂移
  新增模块没有在 CODEMAP 中？→ 触发 Ingest 更新
```

---

## 四、预期产出

### CODEMAP.md 结构示例

```markdown
# srsRAN_4G Code Map

## 索引
| 模块 | 路径 | 状态 |
|------|------|------|
| PHY 物理层 | lib/src/phy/ | 🔥 热区 |
| MAC 媒体访问控制 | lib/src/mac/ | 🔥 热区 |
| RLC 无线链路控制 | lib/src/rlc/ | ❄️ 冷区 |
| PDCP 分组数据汇聚 | lib/src/pdcp/ | ❄️ 冷区 |
| RRC 无线资源控制 | lib/src/rrc/ | 🔥 热区 |
| eNodeB 基站 | srsenb/ | 🔥 热区 |
| UE 终端 | srsue/ | ❄️ 冷区 |
| EPC 核心网 | srsepc/ | ❄️ 冷区 |

## PHY 物理层
- **路径**: lib/src/phy/
- **职责**: 物理层信号处理——调制解调、信道估计、FFT/IFFT
- **核心文件**:
  - `ch_estimation/chest_dl.c` — 下行信道估计
  - `phch/pdsch.c` — 物理下行共享信道
  - `sync/sync.c` — 同步信号检测
- **对外接口**: `lib/include/srsran/phy/` 下的头文件
- **依赖**: 依赖 common（工具函数），被 MAC 层调用
- **状态**: 🔥 热区——频繁优化 SIMD 和算法

## MAC 媒体访问控制
- **路径**: lib/src/mac/
...
```

### 产出文件清单

```
Layer 2 给 Agent 看的产出：
├── CODEMAP.md         → 模块拓扑 + 核心文件 + 接口 + 热区/冷区
└── CLAUDE.md          → 新增 Code Knowledge Map 索引章节
```

### 参考产出

已有实测 CODEMAP：`/root/course/企业培训/001-紫光展锐/第三课_实测/CODEMAP.md`（359 行）

---

## 五、演示节奏（课堂）

| 时间点 | 讲师动作 | 讲解要点 |
|--------|---------|---------|
| 0:00 | 展示 PPT（Layer 2 给人 vs 给 Agent） | "SVG 给人看全局，CODEMAP 给 Agent 看精确位置" |
| 0:15 | 粘贴 Step 1 prompt | "生成给 Agent 看的代码地图" |
| 0:30 | CC 开始扫描和生成 | "它在分析每个模块的核心文件和接口" |
| 1:00 | 展示 CODEMAP.md 索引表 | "**热区🔥冷区❄️——Agent 优先更新热区**" |
| 1:20 | 展示 PHY 模块详情 | "核心文件、对外接口、依赖关系——Agent 改代码时的导航图" |
| 1:40 | 粘贴 Step 2 索引 prompt | "**不索引等于没有——CLAUDE.md 必须知道 CODEMAP 存在**" |
| 2:00 | 展示 CLAUDE.md 新增章节 | "现在 Agent 读 CLAUDE.md 就知道去查 CODEMAP" |
| 2:20 | 展示 LLM Wiki 三操作（PPT） | "Ingest 摄入、Query 查询、Lint 健康检查" |
| 2:40 | 讲工具生态 | "RepoMapper 用 Tree-sitter + PageRank 自动排序关键符号" |
| 3:00 | 对比 Layer 2 vs Layer 3 | "CODEMAP 是知识层面——模块/接口/数据结构。AST 是编译器层面——下一个演示" |
| 3:30 | 展示 LLM Wiki 目录结构 | "raw/ → LLM 编译 → wiki/——Karpathy 的范式" |

---

## 六、关键讲解点

### 6.1 CODEMAP 的核心价值

> "Agent 改代码时先查 CODEMAP 定位文件，不盲目全量扫描。改 PHY 代码——CODEMAP 告诉它看 `lib/src/phy/ch_estimation/`。没有 CODEMAP——Agent 用 grep 在几十万行代码里搜。"

### 6.2 工具 + LLM 双层架构

> "Tree-sitter + PageRank 出骨架——确定性的、可复现的。LLM 补充业务语义——'这个模块负责什么'、'这组错误码含义'。**工具出骨架，LLM 出语义，Wiki 持久化。**"

### 6.3 Layer 2 vs Layer 3 边界

> "CODEMAP 是 Layer 2——知识层面：哪个模块在哪里、做什么、接口是什么。AST 索引是 Layer 3——编译器层面：函数调用关系、类型推断、宏展开。CODEMAP 用静态文件扫描就能做，AST 需要 compile_commands.json + clangd。"

### 6.4 工具生态速览

> "RepoMapper（Aider RepoMap 独立版）：Tree-sitter 解析 → PageRank 排序 → Token 预算裁剪。Repomix（22k stars）：`--compress` 用 Tree-sitter 剥离函数体，70% 压缩。karpathy-llm-wiki：Karpathy 的 raw/ → wiki/ 编译模式的 Agent Skill 实现。你们可以按需选择。"

---

## 七、失败预案

| 风险 | 概率 | 应对 |
|------|------|------|
| CODEMAP 未包含热区/冷区 | 中 | 手动指出"热区/冷区需要团队补充——AI 无法从代码推断修改频率" |
| 执行时间过长 | 中 | 直接展示实测产出 CODEMAP.md（359 行） |
| Claude 生成的内容太详细 | 中 | 说明"CODEMAP 需要精简——只列关键文件，不是全部文件" |
| 工具安装失败 | 低 | 跳过工具演示，直接用 prompt 生成 |

---

## 八、演示后恢复

```bash
cd /root/course/code/ziguangzhanrui_2/srsRAN_4G
git checkout -- .
git clean -fd
```

---

## 九、与课程原则的对应关系

| 课程概念 | 本演示如何体现 |
|---------|-------------|
| Layer 2 给 Agent 看（§1.2） | CODEMAP.md — 代码导航图 |
| LLM Wiki 三操作（§1.2.5） | Ingest / Query / Lint 与 CODEMAP 维护 |
| Karpathy "编译" 范式（§1.0） | raw/ → LLM 编译 → wiki/ 结构化知识页 |
| CLAUDE.md 索引（§1.1） | 不索引等于没有——必须在 CLAUDE.md 中引用 |
| 热区/冷区标注（§1.2） | 修改频率决定维护优先级 |
| 工具生态（§1.3） | RepoMapper / Repomix / karpathy-llm-wiki |
| Layer 2 vs Layer 3 边界 | CODEMAP（知识层）vs AST（编译器层） |
