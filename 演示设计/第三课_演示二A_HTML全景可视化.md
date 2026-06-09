# 演示二A：项目全景 HTML 可视化 —— 给人看的 Layer 2

**对应正文**：第三课 §1.2 Layer 2：基于代码的信息（给人看的部分）
**预计时长**：4 分钟（含讲解）
**所在模块**：第一节「知识建设」

---

## 一、演示目标

让 Claude 扫描项目并生成一个单文件 HTML 全景视图，整合架构分层图、模块依赖图、外部依赖图、接口清单、数据模型等信息。对比传统 SVG 单图方式，展示 HTML 组织方式的信息密度优势。

**核心教学点**：
1. HTML > 独立 SVG——一个文件整合全部可视化信息，浏览器直接打开
2. C/C++ 没有 Swagger——AI 3 分钟梳理完人工需要 1-2 周的接口文档
3. 企业内网可用——不依赖 CDN，纯 CSS + 内嵌 SVG，离线打开
4. 可用 Skill 辅助——Cocoon-AI architecture-diagram-generator 等开源 Skill

---

## 二、前置准备

### 2.1 环境要求

| 项目 | 要求 |
|------|------|
| 代码库 | `/root/course/code/ziguangzhanrui_2/srsRAN_4G` |
| 演示一完成 | CLAUDE.md 已存在（提供项目上下文） |
| 网络 | 需要访问 Claude API |

### 2.2 可选：安装 architecture-diagram Skill

```bash
# Cocoon-AI architecture-diagram-generator（MIT 协议）
mkdir -p ~/.claude/skills/
cd ~/.claude/skills/
git clone https://github.com/Cocoon-AI/architecture-diagram-generator.git
# Skill 路径: architecture-diagram-generator/architecture-diagram/SKILL.md
# 产出：暗色主题单 HTML，内嵌 SVG，自带导出按钮
```

> **备选方案**：不安装 Skill 也可以，直接用 prompt 让 Claude 生成 HTML。Skill 主要提供统一的视觉风格和模板。

### 2.3 确认头文件可扫描

```bash
find lib/include -name "*.h" | wc -l
# 预期 ~41 个公共头文件
```

---

## 三、演示指令

### Step 1：项目分析（让 Claude 先理解项目）

```
扫描 srsRAN_4G 项目，输出以下信息：
1. 目录结构和模块划分
2. 协议栈分层（PHY/MAC/RLC/PDCP/RRC/NAS）及每层核心源文件
3. 模块间依赖关系（lib/include 中的头文件引用）
4. 外部依赖库（CMakeLists.txt 中的 find_package）
5. 关键公共接口（头文件中的核心函数签名，按模块分组）
6. 核心数据结构体（主要 struct/enum 定义）
```

**review 重点**：UE/eNB/EPC 三实体是否准确、协议栈分层是否遗漏、外部依赖是否完整

### Step 2：生成 HTML 全景视图

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

**review 重点**：浏览器打开是否正常渲染、接口清单是否覆盖关键模块、SVG 图是否清晰可读

---

## 四、预期产出

### 产出文件

```
docs/
└── project-overview.html    ← 单文件 HTML 全景视图（~500-800 行）
    ├── 项目概览卡片
    ├── 协议栈分层架构图（内嵌 SVG）
    ├── 模块依赖关系图（内嵌 SVG）
    ├── 外部依赖图（内嵌 SVG）
    ├── 关键接口清单（HTML 表格）
    └── 数据模型概览（HTML 表格）
```

### HTML 结构示意

```html
<!DOCTYPE html>
<html lang="zh">
<head>
  <meta charset="UTF-8">
  <title>srsRAN_4G 项目全景</title>
  <style>
    /* 暗色主题 + 响应式布局 + 内嵌样式 */
    body { background: #1e1e2e; color: #cdd6f4; font-family: monospace; }
    .card { background: #313244; border-radius: 8px; padding: 16px; }
    /* ... */
  </style>
</head>
<body>
  <header>srsRAN_4G 项目全景 | 生成时间: 2026-06-08</header>

  <details open><summary>📊 项目概览</summary>
    <!-- 语言/行数/模块数/构建系统/关键依赖 -->
  </details>

  <details open><summary>🏗️ 协议栈分层架构</summary>
    <svg viewBox="0 0 1000 600"><!-- 内嵌 SVG --></svg>
  </details>

  <details><summary>🔗 模块依赖关系</summary>
    <svg><!-- 模块依赖 SVG --></svg>
  </details>

  <!-- ... 更多板块 -->
</body>
</html>
```

### 参考产出

已有实测 SVG 产出：`/root/course/企业培训/001-紫光展锐/第三课_实测/architecture.svg`
已有接口清单：`/root/course/企业培训/001-紫光展锐/第三课_实测/api-list.md`

---

## 五、演示节奏（课堂）

| 时间点 | 讲师动作 | 讲解要点 |
|--------|---------|---------|
| 0:00 | 展示 PPT（Layer 2 给人看的产出表） | "基于代码的信息——给人看 vs 给 Agent 看" |
| 0:15 | 粘贴 Step 1 分析 prompt | "先让 AI 理解项目" |
| 0:30 | CC 扫描 CMakeLists + 目录 + 头文件 | "它在分析模块依赖关系——跟你们做代码 review 一样" |
| 1:00 | 粘贴 Step 2 生成 prompt | "一个 HTML 整合所有可视化信息" |
| 1:30 | CC 开始生成 HTML | "注意——不依赖任何 CDN，内网直接打开" |
| 2:00 | 在浏览器中打开生成的 HTML | "**一个文件，6 个板块——协议栈、模块依赖、外部依赖、接口清单、数据模型**" |
| 2:30 | 展开/折叠各板块 | "details/summary 标签——零 JavaScript，纯 HTML 交互" |
| 3:00 | 展示接口清单表格 | "**C/C++ 没有 Swagger——AI 3 分钟梳理完人工需要 1-2 周**" |
| 3:30 | 展示 SVG 架构图细节 | "PHY→MAC→RLC→PDCP→RRC，UE/eNB/EPC 三色区分" |

---

## 六、关键讲解点

### 6.1 HTML > 独立 SVG

> "Robert 的方案是三张独立 SVG + 两个 MD 文件——很好，但要在 5 个文件之间切换。我们整合成一个 HTML——浏览器打开就是全景。你们可以两种都试，选适合你们团队的。"

### 6.2 企业内网适配

> "不依赖 CDN，不需要 npm install——纯 CSS + 内嵌 SVG。你们 Simba 项目在隔离网络里，这个方案直接能用。"

### 6.3 Skill 辅助

> "Cocoon-AI 的 architecture-diagram-generator 是现成的 Claude Code Skill——暗色主题、内嵌 SVG、自带导出。你们也可以自己写 Skill 标准化团队的可视化风格。"

---

## 七、失败预案

| 风险 | 概率 | 应对 |
|------|------|------|
| HTML 渲染不正确 | 中 | 切到实测 architecture.svg / .png 展示 |
| SVG 图太复杂不清晰 | 中 | 分步生成：先架构图单独一个 SVG 调好，再整合 |
| 接口数量少于预期 | 低 | 说明"AI 只提取了 public 接口，private 不在此列" |
| 执行时间过长 | 中 | 只演示 Step 2（分析结果口头概述），直接展示生成的 HTML |

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
| Layer 2 给人看（§1.2） | HTML 全景视图整合架构图 + 接口 + 数据模型 |
| C/C++ 没有 Swagger（§1.2） | 接口清单 3 分钟自动生成 |
| Robert 12 讲方法论 | 在 Robert 三张 SVG 基础上整合为单文件 HTML |
| Skill 生态（§2.0） | Cocoon-AI architecture-diagram-generator 示例 |
| 企业内网适配 | 不依赖 CDN，纯 CSS + 内嵌 SVG |
