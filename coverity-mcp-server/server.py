"""
Coverity MCP Server — srsRAN_4G 项目专用
让 Claude Code 通过 MCP 协议查询 Coverity 静态分析结果。

培训演示用：用本地 JSON 文件模拟 Coverity Connect API。
生产环境只需替换 _load_findings()，其余代码零修改。
"""

from mcp.server.fastmcp import FastMCP
import json
import os

mcp = FastMCP("coverity-server")

FINDINGS_PATH = os.path.join(os.path.dirname(__file__), "mock_findings.json")


# ── Mock 数据层 ──────────────────────────────
# 培训演示用本地 JSON 文件模拟 Coverity Connect API。
# 生产环境替换本函数为 REST API 调用：
#   requests.get(f'{COVERITY_URL}/api/v2/issues', params={...})
# 接口签名（入参/返回值）完全不用改。
def _load_findings() -> list[dict]:
    """加载 Coverity 扫描结果。

    当前实现：从本地 mock_findings.json 读取模拟数据。
    生产环境替换示例：
        import requests
        def _load_findings() -> list[dict]:
            resp = requests.get(
                f'{COVERITY_URL}/api/v2/issues',
                params={'project': PROJECT_NAME},
                auth=(USER, PASSWORD),
            )
            resp.raise_for_status()
            return resp.json()['issues']
    """
    with open(FINDINGS_PATH) as f:
        return json.load(f)


@mcp.tool()
def list_findings(checker: str | None = None, severity: str | None = None) -> str:
    """
    查询 Coverity 扫描结果列表。
    可按 checker 类型（如 UNINIT, BAD_SHIFT, DEADCODE）或严重级别（High/Medium/Low）过滤。

    Args:
        checker: 过滤指定 checker 类型，如 "UNINIT"、"BAD_SHIFT"
        severity: 过滤严重级别，如 "High"、"Medium"、"Low"
    """
    findings = _load_findings()
    if checker:
        findings = [f for f in findings if f["checker"] == checker]
    if severity:
        findings = [f for f in findings if f["severity"] == severity]

    if not findings:
        return "No findings match the filter criteria."

    lines = [f"Found {len(findings)} findings:\n"]
    for f in findings:
        lines.append(
            f"[{f['id']}] {f['checker']} | {f['severity']} | "
            f"{f['file']}:{f['line']} | {f['description']}"
        )
    return "\n".join(lines)


@mcp.tool()
def get_finding_detail(finding_id: int) -> str:
    """
    获取单个 Coverity finding 的详细信息，包括代码片段和上下文。

    Args:
        finding_id: Finding 的 ID 编号
    """
    findings = _load_findings()
    for f in findings:
        if f["id"] == finding_id:
            return json.dumps(f, indent=2, ensure_ascii=False)
    return f"Finding {finding_id} not found."


@mcp.tool()
def get_finding_stats() -> str:
    """
    获取 Coverity 扫描结果的统计概要：按 checker 类型和严重级别分组计数。
    """
    findings = _load_findings()
    by_checker: dict[str, int] = {}
    by_severity: dict[str, int] = {}
    for f in findings:
        by_checker[f["checker"]] = by_checker.get(f["checker"], 0) + 1
        by_severity[f["severity"]] = by_severity.get(f["severity"], 0) + 1

    lines = [f"Total findings: {len(findings)}\n"]
    lines.append("By checker:")
    for k, v in sorted(by_checker.items(), key=lambda x: -x[1]):
        lines.append(f"  {k}: {v}")
    lines.append("\nBy severity:")
    for k, v in sorted(by_severity.items(), key=lambda x: -x[1]):
        lines.append(f"  {k}: {v}")
    return "\n".join(lines)


@mcp.tool()
def update_finding_status(
    finding_id: int, status: str, reason: str
) -> str:
    """
    更新 Finding 的处置状态（模拟写回 Coverity Connect）。

    Args:
        finding_id: Finding 的 ID 编号
        status: 新状态，可选值: "Triaged", "Fixed", "False_Positive", "Intentional", "Needs_Review"
        reason: 状态变更原因说明
    """
    valid_statuses = {"Triaged", "Fixed", "False_Positive", "Intentional", "Needs_Review"}
    if status not in valid_statuses:
        return f"Invalid status '{status}'. Valid: {', '.join(sorted(valid_statuses))}"

    findings = _load_findings()
    for f in findings:
        if f["id"] == finding_id:
            return (
                f"Finding {finding_id} ({f['checker']} in {f['file']}:{f['line']}) "
                f"status updated to '{status}'. Reason: {reason}"
            )
    return f"Finding {finding_id} not found."


if __name__ == "__main__":
    mcp.run()
