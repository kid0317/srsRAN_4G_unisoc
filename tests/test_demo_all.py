"""
第三课全部演示 TDD 测试用例
先写测试（RED），再实现产物（GREEN）
"""
import json
import os
import subprocess
import re

import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLAUDE_DIR = os.path.join(PROJECT_ROOT, ".claude")
SKILLS_DIR = os.path.join(CLAUDE_DIR, "skills")
AGENTS_DIR = os.path.join(CLAUDE_DIR, "agents")
DOCS_DIR = os.path.join(PROJECT_ROOT, "docs")
SETTINGS_FILE = os.path.join(CLAUDE_DIR, "settings.local.json")


# ──────────────────────────────────────────────
# 演示一：CLAUDE.md 初始化
# ──────────────────────────────────────────────
class TestDemo1_ClaudeMD:
    def test_claude_md_exists(self):
        assert os.path.isfile(os.path.join(PROJECT_ROOT, "CLAUDE.md"))

    def test_claude_md_line_count_under_400(self):
        with open(os.path.join(PROJECT_ROOT, "CLAUDE.md")) as f:
            lines = f.readlines()
        assert len(lines) <= 400, f"CLAUDE.md has {len(lines)} lines, exceeds 400 limit"

    def test_claude_md_has_project_description(self):
        content = open(os.path.join(PROJECT_ROOT, "CLAUDE.md")).read()
        assert "srsRAN" in content or "4G" in content

    def test_claude_md_has_build_commands(self):
        content = open(os.path.join(PROJECT_ROOT, "CLAUDE.md")).read()
        assert "cmake" in content.lower() or "make" in content.lower()

    def test_claude_md_has_forbidden_zone(self):
        content = open(os.path.join(PROJECT_ROOT, "CLAUDE.md")).read()
        assert "禁区" in content

    def test_claude_md_has_legacy_section(self):
        content = open(os.path.join(PROJECT_ROOT, "CLAUDE.md")).read()
        assert "历史包袱" in content

    def test_claude_md_has_progressive_disclosure_links(self):
        content = open(os.path.join(PROJECT_ROOT, "CLAUDE.md")).read()
        assert "docs/" in content

    def test_docs_directory_exists(self):
        assert os.path.isdir(DOCS_DIR)

    def test_claude_md_has_codemap_index(self):
        content = open(os.path.join(PROJECT_ROOT, "CLAUDE.md")).read()
        assert "CODEMAP" in content


# ──────────────────────────────────────────────
# 演示二A：HTML 全景可视化
# ──────────────────────────────────────────────
class TestDemo2A_HTMLVisualization:
    @pytest.fixture
    def html_path(self):
        return os.path.join(DOCS_DIR, "project-overview.html")

    def test_html_file_exists(self, html_path):
        assert os.path.isfile(html_path), "docs/project-overview.html not found"

    def test_html_has_dark_theme(self, html_path):
        content = open(html_path).read()
        assert "#1e1e2e" in content or "1e1e2e" in content, "Missing dark theme background"

    def test_html_has_six_panels(self, html_path):
        content = open(html_path).read()
        details_count = content.count("<details")
        assert details_count >= 6, f"Expected >=6 <details> panels, found {details_count}"

    def test_html_no_cdn_dependency(self, html_path):
        content = open(html_path).read()
        assert "cdn." not in content.lower(), "HTML should not depend on CDN"
        assert "unpkg.com" not in content.lower()
        assert "jsdelivr" not in content.lower()

    def test_html_has_inline_svg(self, html_path):
        content = open(html_path).read()
        assert "<svg" in content, "HTML should contain inline SVG"

    def test_html_has_protocol_stack(self, html_path):
        content = open(html_path).read()
        assert "PHY" in content and "MAC" in content and "RLC" in content

    def test_html_has_interface_table(self, html_path):
        content = open(html_path).read()
        assert "<table" in content.lower() or "<th" in content.lower()


# ──────────────────────────────────────────────
# 演示二B：CODEMAP + LLM Wiki
# ──────────────────────────────────────────────
class TestDemo2B_Codemap:
    @pytest.fixture
    def codemap_path(self):
        return os.path.join(PROJECT_ROOT, "CODEMAP.md")

    def test_codemap_exists(self, codemap_path):
        assert os.path.isfile(codemap_path)

    def test_codemap_has_index_table(self, codemap_path):
        content = open(codemap_path).read()
        assert "|" in content, "CODEMAP should have index table"
        assert "模块" in content or "Module" in content

    def test_codemap_has_hot_zone(self, codemap_path):
        content = open(codemap_path).read()
        has_hot = "🔥" in content or "热区" in content or "hot" in content.lower()
        assert has_hot, "CODEMAP should have hot zone markers"

    def test_codemap_has_cold_zone(self, codemap_path):
        content = open(codemap_path).read()
        has_cold = "❄️" in content or "冷区" in content or "cold" in content.lower()
        assert has_cold, "CODEMAP should have cold zone markers"

    def test_codemap_has_phy_module(self, codemap_path):
        content = open(codemap_path).read()
        assert "phy" in content.lower() or "PHY" in content

    def test_codemap_has_dependency_info(self, codemap_path):
        content = open(codemap_path).read()
        assert "依赖" in content or "depend" in content.lower()


# ──────────────────────────────────────────────
# 演示三：AST 索引 + clangd LSP
# ──────────────────────────────────────────────
class TestDemo3_AST_LSP:
    def test_compile_commands_exists(self):
        path = os.path.join(PROJECT_ROOT, "build", "compile_commands.json")
        assert os.path.isfile(path)

    def test_compile_commands_valid_json(self):
        path = os.path.join(PROJECT_ROOT, "build", "compile_commands.json")
        with open(path) as f:
            data = json.load(f)
        assert isinstance(data, list)
        assert len(data) > 0

    def test_compile_commands_has_entries(self):
        path = os.path.join(PROJECT_ROOT, "build", "compile_commands.json")
        with open(path) as f:
            data = json.load(f)
        assert len(data) >= 50, f"Expected 50+ entries, got {len(data)}"

    def test_clangd_installed(self):
        result = subprocess.run(["which", "clangd"], capture_output=True, text=True)
        assert result.returncode == 0, "clangd not installed"

    def test_clangd_version(self):
        result = subprocess.run(["clangd", "--version"], capture_output=True, text=True)
        assert result.returncode == 0

    def test_lsp_setup_doc_exists(self):
        path = os.path.join(DOCS_DIR, "lsp-setup.md")
        assert os.path.isfile(path), "LSP setup documentation missing"


# ──────────────────────────────────────────────
# 演示四：Coverity MCP Server
# ──────────────────────────────────────────────
class TestDemo4_MCPServer:
    MCP_DIR = os.path.join(PROJECT_ROOT, "coverity-mcp-server")

    def test_server_py_exists(self):
        assert os.path.isfile(os.path.join(self.MCP_DIR, "server.py"))

    def test_mock_findings_exists(self):
        assert os.path.isfile(os.path.join(self.MCP_DIR, "mock_findings.json"))

    def test_mock_findings_valid_json(self):
        with open(os.path.join(self.MCP_DIR, "mock_findings.json")) as f:
            data = json.load(f)
        assert isinstance(data, list)
        assert len(data) >= 10

    def test_mock_findings_have_required_fields(self):
        with open(os.path.join(self.MCP_DIR, "mock_findings.json")) as f:
            data = json.load(f)
        required = {"id", "checker", "severity", "file", "line", "function", "description", "code_snippet"}
        for finding in data:
            missing = required - set(finding.keys())
            assert not missing, f"Finding {finding.get('id')} missing fields: {missing}"

    def test_mock_findings_cover_six_checkers(self):
        with open(os.path.join(self.MCP_DIR, "mock_findings.json")) as f:
            data = json.load(f)
        checkers = {f["checker"] for f in data}
        expected = {"UNINIT", "BAD_SHIFT", "DEADCODE", "NULL_RETURNS", "RESOURCE_LEAK", "BUFFER_SIZE"}
        assert expected.issubset(checkers), f"Missing checkers: {expected - checkers}"

    def test_server_py_has_mock_comments(self):
        with open(os.path.join(self.MCP_DIR, "server.py")) as f:
            content = f.read()
        assert "Mock" in content or "mock" in content or "生产环境" in content

    def test_server_py_importable(self):
        result = subprocess.run(
            ["python3", "-c", f"import sys; sys.path.insert(0, '{self.MCP_DIR}'); import server"],
            capture_output=True, text=True, timeout=10
        )
        assert result.returncode == 0, f"Import failed: {result.stderr}"

    def test_settings_has_mcp_config(self):
        with open(SETTINGS_FILE) as f:
            settings = json.load(f)
        assert "mcpServers" in settings
        assert "coverity-server" in settings["mcpServers"]

    def test_settings_has_toolsearch_config(self):
        with open(SETTINGS_FILE) as f:
            settings = json.load(f)
        mcp = settings["mcpServers"]["coverity-server"]
        assert "toolSearchConfig" in mcp or "args" in mcp

    def test_mcp_list_findings(self):
        """Test list_findings tool returns data"""
        result = subprocess.run(
            ["python3", "-c", f"""
import sys; sys.path.insert(0, '{self.MCP_DIR}')
from server import _load_findings
findings = _load_findings()
assert len(findings) >= 10
filtered = [f for f in findings if f['checker'] == 'UNINIT']
assert len(filtered) >= 1
print('list_findings OK')
"""],
            capture_output=True, text=True, timeout=10
        )
        assert result.returncode == 0, f"list_findings test failed: {result.stderr}"

    def test_mcp_get_finding_stats(self):
        """Test get_finding_stats logic"""
        result = subprocess.run(
            ["python3", "-c", f"""
import sys; sys.path.insert(0, '{self.MCP_DIR}')
from server import _load_findings
findings = _load_findings()
by_checker = {{}}
by_severity = {{}}
for f in findings:
    by_checker[f['checker']] = by_checker.get(f['checker'], 0) + 1
    by_severity[f['severity']] = by_severity.get(f['severity'], 0) + 1
assert len(by_checker) >= 6
assert 'High' in by_severity
print('stats OK')
"""],
            capture_output=True, text=True, timeout=10
        )
        assert result.returncode == 0, f"stats test failed: {result.stderr}"


# ──────────────────────────────────────────────
# 演示五：Coverity Triage Skill
# ──────────────────────────────────────────────
class TestDemo5_CoveritySkill:
    SKILL_DIR = os.path.join(SKILLS_DIR, "coverity-triage-sop")

    def test_skill_dir_exists(self):
        assert os.path.isdir(self.SKILL_DIR)

    def test_skill_md_exists(self):
        assert os.path.isfile(os.path.join(self.SKILL_DIR, "SKILL.md"))

    def test_skill_has_instruction_description(self):
        with open(os.path.join(self.SKILL_DIR, "SKILL.md")) as f:
            content = f.read()
        assert "ALWAYS invoke" in content or "ALWAYS" in content, "Description should be instruction-style"

    def test_skill_has_do_not_skip(self):
        with open(os.path.join(self.SKILL_DIR, "SKILL.md")) as f:
            content = f.read()
        assert "Do NOT skip" in content or "Do not skip" in content

    def test_skill_has_decision_trees(self):
        with open(os.path.join(self.SKILL_DIR, "SKILL.md")) as f:
            content = f.read()
        for checker in ["UNINIT", "BAD_SHIFT", "DEADCODE", "NULL_RETURNS"]:
            assert checker in content, f"Decision tree for {checker} missing"

    def test_skill_has_code_inspection_step(self):
        with open(os.path.join(self.SKILL_DIR, "SKILL.md")) as f:
            content = f.read()
        assert "Read" in content or "打开文件" in content or "Step 0" in content, \
            "Skill should have code inspection step (Step 0)"

    def test_skill_has_report_template(self):
        with open(os.path.join(self.SKILL_DIR, "SKILL.md")) as f:
            content = f.read()
        assert "Report" in content or "报告" in content or "Triage Report" in content

    def test_skill_has_mcp_prereqs(self):
        with open(os.path.join(self.SKILL_DIR, "SKILL.md")) as f:
            content = f.read()
        assert "coverity-server" in content or "list_findings" in content

    def test_evals_dir_exists(self):
        evals_dir = os.path.join(self.SKILL_DIR, "evals")
        assert os.path.isdir(evals_dir)

    def test_trigger_eval_exists(self):
        path = os.path.join(self.SKILL_DIR, "evals", "trigger_eval.json")
        assert os.path.isfile(path)

    def test_trigger_eval_has_positive_and_negative(self):
        path = os.path.join(self.SKILL_DIR, "evals", "trigger_eval.json")
        with open(path) as f:
            data = json.load(f)
        positives = [e for e in data if e.get("expected") is True or e.get("should_trigger") is True]
        negatives = [e for e in data if e.get("expected") is False or e.get("should_trigger") is False]
        assert len(positives) >= 8, f"Expected >=8 positive triggers, got {len(positives)}"
        assert len(negatives) >= 8, f"Expected >=8 negative triggers, got {len(negatives)}"


# ──────────────────────────────────────────────
# 演示六：dev-iterate Skill + 迭代闭环
# ──────────────────────────────────────────────
class TestDemo6_DevIterate:
    SKILL_DIR = os.path.join(SKILLS_DIR, "dev-iterate")

    def test_skill_dir_exists(self):
        assert os.path.isdir(self.SKILL_DIR)

    def test_skill_md_exists(self):
        assert os.path.isfile(os.path.join(self.SKILL_DIR, "SKILL.md"))

    def test_skill_has_instruction_description(self):
        with open(os.path.join(self.SKILL_DIR, "SKILL.md")) as f:
            content = f.read()
        assert "ALWAYS" in content

    def test_skill_has_test_mapping(self):
        with open(os.path.join(self.SKILL_DIR, "SKILL.md")) as f:
            content = f.read()
        assert "PHY" in content or "测试映射" in content or "test_mapping" in content.lower()

    def test_skill_has_retry_limits(self):
        with open(os.path.join(self.SKILL_DIR, "SKILL.md")) as f:
            content = f.read()
        has_limit = ("5" in content and ("重试" in content or "retry" in content.lower())) or "轮" in content
        assert has_limit, "Skill should have retry limits"

    def test_skill_has_build_command(self):
        with open(os.path.join(self.SKILL_DIR, "SKILL.md")) as f:
            content = f.read()
        assert "make" in content.lower() or "cmake" in content.lower() or "build" in content.lower()

    def test_settings_has_post_tool_use_hook(self):
        with open(SETTINGS_FILE) as f:
            settings = json.load(f)
        assert "hooks" in settings
        assert "PostToolUse" in settings["hooks"]

    def test_settings_has_stop_hook(self):
        with open(SETTINGS_FILE) as f:
            settings = json.load(f)
        assert "Stop" in settings["hooks"]

    def test_stop_hook_script_exists(self):
        assert os.path.isfile(os.path.join(PROJECT_ROOT, "hooks", "stop_check_syntax.py"))


# ──────────────────────────────────────────────
# 演示七：多 Agent 安全审查
# ──────────────────────────────────────────────
class TestDemo7_SecurityAgents:
    AGENT_FILES = [
        "security-reviewer.md",
        "telecom-security-reviewer.md",
        "embedded-specialist-reviewer.md",
        "compliance-reviewer.md",
    ]

    def test_agents_dir_exists(self):
        assert os.path.isdir(AGENTS_DIR)

    @pytest.mark.parametrize("agent_file", AGENT_FILES)
    def test_agent_file_exists(self, agent_file):
        path = os.path.join(AGENTS_DIR, agent_file)
        assert os.path.isfile(path), f"Agent file {agent_file} not found"

    @pytest.mark.parametrize("agent_file", AGENT_FILES)
    def test_agent_has_tools_restriction(self, agent_file):
        path = os.path.join(AGENTS_DIR, agent_file)
        content = open(path).read()
        assert "Read" in content and "Grep" in content and "Glob" in content

    @pytest.mark.parametrize("agent_file", AGENT_FILES)
    def test_agent_has_name_and_description(self, agent_file):
        path = os.path.join(AGENTS_DIR, agent_file)
        content = open(path).read()
        assert "name:" in content
        assert "description:" in content

    def test_security_knowledge_skill_exists(self):
        skill_dir = os.path.join(SKILLS_DIR, "srsran-security")
        assert os.path.isdir(skill_dir), "Security knowledge base skill not found"

    def test_security_knowledge_has_skill_md(self):
        path = os.path.join(SKILLS_DIR, "srsran-security", "SKILL.md")
        assert os.path.isfile(path)

    def test_security_knowledge_has_cwe(self):
        path = os.path.join(SKILLS_DIR, "srsran-security", "SKILL.md")
        content = open(path).read()
        assert "CWE" in content, "Security skill should reference CWE identifiers"

    def test_security_knowledge_has_domains(self):
        path = os.path.join(SKILLS_DIR, "srsran-security", "SKILL.md")
        content = open(path).read().lower()
        domains = ["buffer", "integer", "race", "key", "protocol", "injection",
                   "缓冲区", "整数", "竞态", "密钥", "协议", "注入"]
        found = sum(1 for d in domains if d in content)
        assert found >= 3, f"Security skill should cover multiple domains, found {found}/12"
