# 演示四：Coverity MCP Server 搭建 —— 让 AI 能查外部系统

**对应正文**：第三课 §2.4.2 搭建 Coverity MCP Server
**预计时长**：5 分钟（含讲解）
**所在模块**：第二节「Skill × MCP」→ Coverity 审查辅助完整演示

---

## 一、演示目标

用 FastMCP 搭建 Coverity MCP Server（4 个 Tool），Mock 数据来自真实告警清单。配置 ToolSearch 渐进式披露加载，验证 Claude 能通过 MCP 自主查询 Coverity 数据，并**基于查询结果回到本地代码做二次审查**，产出要修复的清单。

**核心教学点**：
1. `@mcp.tool()` 装饰器——函数加上它就变成 AI 可调用的工具
2. server.py < 120 行——搭建门槛极低
3. Mock 数据 → 真实 API 只需替换 `_load_findings()` 一个函数（注释标注清楚）
4. ToolSearch 渐进式披露——装越多 MCP 不是越慢，而是越强
5. AI 不只拉数据——**拉完数据回到本地代码做二次审查**，产出可执行的修复报告

---

## 二、前置准备

### 2.1 环境要求

| 项目 | 要求 |
|------|------|
| Python | 3.10+（FastMCP 依赖） |
| FastMCP | `pip install mcp` |
| 演示代码 | `/root/course/企业培训/001-紫光展锐/第三课_Skill演示/coverity-mcp-server/` |
| 网络 | 需要访问 Claude API |

### 2.2 确认演示代码就位

```bash
ls -la /root/course/企业培训/001-紫光展锐/第三课_Skill演示/coverity-mcp-server/
# 预期：server.py + mock_findings.json
```

### 2.3 验证 FastMCP 可用

```bash
python3 -c "from mcp.server.fastmcp import FastMCP; print('FastMCP OK')"
```

### 2.4 Mock 数据来源

Mock 数据基于紫光展锐提供的真实告警清单构造：
- 来源：`/root/course/企业培训/001-紫光展锐/案例材料/XX项目告警清单.xlsx`
- 422 条告警，30+ 种 Checker 类型
- 选取了 6 种代表性 Checker（UNINIT、BAD_SHIFT、DEADCODE、NULL_RETURNS、RESOURCE_LEAK、BUFFER_SIZE），构造 10 条 mock finding
- 每条 mock 包含：文件路径、行号、函数名、代码片段、CWE 编号——**均对应 srsRAN 真实代码位置**

> **讲解点**："mock 不是瞎编的——从你们的告警清单提取了典型 Checker 类型和告警模式。演示时 Claude 能找到对应的本地代码。"

---

## 三、演示步骤

### Step 1：展示 server.py 核心结构（1min）

打开 `server.py`，展示四个 `@mcp.tool()` 装饰器：

```python
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("coverity-server")

# ── Mock 数据层 ──────────────────────────────────────────
# 培训演示用本地 JSON 文件模拟 Coverity Connect API。
# 生产环境替换本函数为 REST API 调用：
#   requests.get(f'{COVERITY_URL}/api/v2/issues', params={...})
# 接口签名（入参/返回值）完全不用改。
def _load_findings() -> list[dict]:
    ...

@mcp.tool()
def list_findings(checker: str | None = None, severity: str | None = None) -> str:
    """查询 Coverity 扫描结果列表。可按 checker 类型或严重级别过滤。"""
    ...

@mcp.tool()
def get_finding_detail(finding_id: int) -> str:
    """获取指定 finding 的详细信息，包含代码上下文。"""
    ...

@mcp.tool()
def get_finding_stats() -> str:
    """获取 Coverity 扫描结果统计概要。"""
    ...

@mcp.tool()
def update_finding_status(finding_id: int, status: str, reason: str) -> str:
    """更新 finding 的状态（如 Triaged/Dismissed）和原因。"""
    ...
```

**讲解**：
- "四个工具——增删改查全覆盖。参数类型是参数描述，docstring 是工具说明。"
- "**看注释——Mock → 生产只需要换 `_load_findings()` 一个函数**。接口定义、参数签名完全不动。"

### Step 2：展示 mock_findings.json（30s）

```bash
python3 -c "import json; data=json.load(open('/root/course/企业培训/001-紫光展锐/第三课_Skill演示/coverity-mcp-server/mock_findings.json')); print(json.dumps(data[:2], indent=2, ensure_ascii=False))"
```

重点展示 mock 数据的结构：

```json
{
  "id": 1007,
  "checker": "BAD_SHIFT",
  "file": "lib/src/phy/fec/turbo/tc_interl_lte.c",
  "line": 78,
  "function": "srsran_tc_interl_LTE_gen_interl",
  "code_snippet": "uint32_t mask = (1 << f2);  // f2 range: 0-15 from LTE turbo interleaver table",
  "impact": "False alarm: f2 is bounded by LTE spec table (max 15), shift is always safe for uint32_t"
}
```

**讲解**："**看这条——LTE turbo 交织表的 BAD_SHIFT。直接对应你们告警清单里的同类问题。** 10 条 mock 涵盖六种 Checker——UNINIT、BAD_SHIFT、DEADCODE、NULL_RETURNS、RESOURCE_LEAK、BUFFER_SIZE。每条都有 `code_snippet` 和 `file:line`，Claude 可以回到本地代码验证。"

### Step 3：配置 ToolSearch 渐进式披露加载（1min）

展示 `.claude/settings.local.json` 中的 MCP 配置——**关键区别是 ToolSearch 配置**：

```json
{
  "mcpServers": {
    "coverity-server": {
      "command": "python3",
      "args": ["/root/course/企业培训/001-紫光展锐/第三课_Skill演示/coverity-mcp-server/server.py"],
      "toolSearchConfig": {
        "enabled": true,
        "maxResults": 3
      }
    }
  }
}
```

**讲解**：
- "三行启动配置 + ToolSearch 开关。"
- "**旧范式**：5 个 MCP Server × 11K token/server = 55K token，占 27.5% 窗口。每次对话启动就全加载，不用也要付房租。"
- "**新范式**：ToolSearch 按需加载——`enabled: true` 就行。Claude 需要时才加载工具定义。**dlopen() 而不是静态链接。装越多 MCP 不是越慢，而是越强。**"
- "你们团队有 Coverity + Jenkins + Jira + SonarQube——四个 MCP Server 同时挂着，ToolSearch 保证只加载当前需要的工具。"

### Step 4：快速验证 + 本地代码审查（1.5min）

在 Claude Code 中输入：

```
帮我看看 Coverity 扫描结果，挑出需要关注的 High 级别告警，
然后去本地代码确认一下这些告警是否真的有问题，给我一个要修复的清单。
```

**预期行为**：

```
Claude 行为序列：
  1. 识别 MCP 工具可用
  2. 调用 get_finding_stats() → "10 findings: High 4, Medium 2, Low 4"
  3. 调用 list_findings(severity="High") → 4 个高危
  4. 调用 get_finding_detail(1001) → 获取 UNINIT 详情（含文件路径和代码片段）
  5. ★ 关键步骤：Read 本地文件 srsenb/src/stack/rrc/rrc_ue.cc:245
     → 对比 Coverity 报告的代码片段和实际代码
     → 判断是否真正未初始化
  6. 对每个 High 级别 finding 重复 4-5 步
  7. 产出修复清单：
     ┌─────────┬────────────────┬──────────────┬────────────┐
     │ Finding │ 判定           │ 依据         │ 建议       │
     ├─────────┼────────────────┼──────────────┼────────────┤
     │ 1001    │ TRUE POSITIVE  │ 确实有路径未  │ 加初始化   │
     │         │                │ 初始化       │            │
     │ 1004    │ TRUE POSITIVE  │ find_ue 可能 │ 加 null    │
     │         │                │ 返回 nullptr │ check      │
     │ 1005    │ TRUE POSITIVE  │ 错误路径未   │ 加 fclose  │
     │         │                │ close        │            │
     │ 1009    │ TRUE POSITIVE  │ 大 RRC 消息  │ 改用动态   │
     │         │                │ 可能溢出     │ 分配       │
     └─────────┴────────────────┴──────────────┴────────────┘
```

**讲解**：
- "**注意步骤 5——Claude 不只是拉了数据就给你看。它回到本地代码去验证了。** MCP 拉数据，Read 工具看代码——两个能力组合。"
- "**我没复制任何数据——AI 自己通过 MCP 去查了，然后自己去代码里确认了。**"

---

## 四、演示节奏（课堂）

| 时间点 | 讲师动作 | 讲解要点 |
|--------|---------|---------|
| 0:00 | 打开 server.py | "看代码量——< 120 行" |
| 0:15 | 逐个指出 @mcp.tool() | "Python 函数加装饰器就变成 AI 工具" |
| 0:30 | 指出 _load_findings 注释 | "**Mock → 生产只需换这一个函数**" |
| 0:45 | 展示 mock 数据 1007 BAD_SHIFT | "**直接对应你们告警清单里的同类问题**" |
| 1:10 | 展示 settings.json + ToolSearch | "ToolSearch 渐进式披露——装越多 MCP 不是越慢" |
| 1:40 | 对比旧范式 vs 新范式 | "55K token 全加载 vs 按需加载" |
| 2:00 | 粘贴验证 prompt | "注意——我要 Claude 去本地代码确认" |
| 2:30 | Claude 调用 MCP 拉数据 | "MCP 的本质是三个字：**别复制**" |
| 3:00 | Claude Read 本地代码审查 | "**看——它回到代码里确认了，不是只拉数据**" |
| 3:30 | Claude 产出修复清单 | "4 个 High 全审完，每个有判定依据和修复建议" |
| 4:00 | 回到 PPT | "MCP 管数据拉取，Skill 管分流流程——下一个演示" |

---

## 五、关键讲解点

### 5.1 Mock → 生产只需换一个函数

> "server.py 里的 `_load_findings()` 读的是 JSON 文件。生产环境把它换成 Coverity Connect REST API 调用——`requests.get(f'{coverity_url}/api/v2/issues')`。接口定义不用改。**注释里写得清清楚楚——下次来的人也知道怎么换。**"

### 5.2 Mock 数据不是瞎编的

> "10 条 mock 来自你们提供的告警清单——422 条告警，30+ 种 Checker。我们挑了最有代表性的 6 种 Checker 各取 1-3 条。**每条都有真实的文件路径和代码片段——Claude 可以回到本地代码验证。**"

### 5.3 ToolSearch 渐进式披露

> "旧范式 5 个 Server 55K token 占掉 27.5% 窗口。新范式 ToolSearch 按需加载——`toolSearchConfig: { enabled: true }` 就行。**dlopen() 而不是静态链接。装越多 MCP 不是越慢，而是越强。**"

### 5.4 AI 不只拉数据——还审代码

> "传统工具链：Coverity 输出告警 → 人去看代码。现在：AI 通过 MCP 拉告警 → **自己去看代码** → 产出修复清单。人只需要看清单决策。"

---

## 六、失败预案

| 风险 | 概率 | 应对 |
|------|------|------|
| FastMCP 未安装 | 低 | 现场 `pip install mcp`（~10 秒） |
| MCP Server 启动报错 | 低 | 检查 Python 版本 ≥ 3.10 |
| Claude 未识别 MCP 工具 | 中 | 重启 Claude Code 让 settings.json 生效 |
| Claude 没有回到本地代码审查 | 中 | 说明"prompt 要求了'去本地代码确认'——如果没做，再追问一句" |
| ToolSearch 不生效 | 中 | 说明"v2.1.0+ 支持——老版本需更新" |
| 验证执行时间过长 | 中 | 只验证 get_finding_stats，代码审查用 PPT 数据展示 |

---

## 七、演示后恢复

MCP Server 无状态副作用，无需特殊恢复。如果修改了 settings.local.json，恢复原始内容。

---

## 八、与课程原则的对应关系

| 课程概念 | 本演示如何体现 |
|---------|-------------|
| MCP 构建方法（§2.2） | FastMCP 快速搭建 < 120 行 Python |
| ToolSearch 动态加载（§2.2.2） | `toolSearchConfig` 配置 + Token 节省 85% |
| "别复制"（§2.4.2 金句） | AI 自主通过 MCP 查数据 |
| AI 代码审查（新增教学点） | Claude 拉完数据回到本地代码做二次确认 |
| Mock 数据来源（§2.4.2） | 基于真实告警清单构造，非臆造 |
| Skill + MCP 组合（§2.0） | MCP 管数据，为后续 Skill 管流程做铺垫 |
