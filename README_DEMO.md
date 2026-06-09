# 第三课 · 演示环境搭建指南

> **课程**：紫光展锐 AI Coding 企业培训 · 第三课 · 构建 AI 原生代码库
> **演示数量**：7 个（三-1 ～ 三-7）
> **验证报告**：[第三课_演示验证报告.md](../../../企业培训/001-紫光展锐/第三课_演示验证报告.md)

---

## 一、系统依赖

### 1.1 基础工具链

```bash
apt update && apt install -y \
  build-essential cmake git python3 python3-pip \
  clangd clang-format cppcheck
```

| 工具 | 最低版本 | 用途 | 涉及演示 |
|------|---------|------|---------|
| build-essential (gcc/g++) | 13+ | C/C++ 编译、Stop Hook 语法检查 | 全部 |
| cmake | 3.28+ | 项目构建 + 生成 compile_commands.json | 三-3 |
| clangd | 18+ | LSP 语言服务器（跳转/补全） | 三-3 |
| clang-format | 18+ | PostToolUse Hook 自动格式化 | 三-6 |
| cppcheck | 2.13+ | 静态分析对比基准 | 三-7 |

### 1.2 srsRAN 构建依赖

```bash
apt install -y \
  libfftw3-dev libconfig++-dev libmbedtls-dev libsctp-dev \
  libboost-program-options-dev libboost-thread-dev \
  libboost-system-dev libboost-test-dev \
  libfmt-dev libspdlog-dev
```

### 1.3 Python 包

```bash
pip3 install mcp langfuse pytest pytest-asyncio pytest-cov pytest-timeout anthropic httpx
```

| 包 | 用途 | 涉及演示 |
|----|------|---------|
| mcp (FastMCP) | Coverity MCP Server | 三-4, 三-5 |
| langfuse | Trace 捕获与验证 | 全部 |
| pytest + 插件 | 测试套件（76 用例） | 验证 |
| anthropic | Agent API 调用 | 三-7 |
| httpx | LangFuse HTTP 查询 | 验证 |

### 1.4 Claude Code

```bash
claude --version  # 需要 2.1.x+
```

---

## 二、项目构建

```bash
cd /root/course/code/ziguangzhanrui_2/srsRAN_4G

# 构建（首次约 5-10 分钟）
mkdir -p build && cd build
cmake -DCMAKE_BUILD_TYPE=Debug \
      -DENABLE_WERROR=ON \
      -DCMAKE_EXPORT_COMPILE_COMMANDS=ON ..
make -j$(nproc)

# 创建 compile_commands.json 软链接（演示三-3 依赖）
cd ..
ln -sf build/compile_commands.json .
```

验证构建成功：

```bash
cmake --build build -j$(nproc) 2>&1 | tail -3
# 应输出 [100%] Built target ...
```

---

## 三、LangFuse 配置

演示全程使用 LangFuse 捕获 Trace，需要一个运行中的 LangFuse 实例。

### 3.1 LangFuse 服务

确保 `http://localhost:3000` 可访问：

```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/api/public/health
# 应返回 200
```

### 3.2 项目环境变量

已配置在 `.claude/settings.local.json`，无需手动设置：

| 变量 | 值 | 说明 |
|------|-----|------|
| `LANGFUSE_PUBLIC_KEY` | `pk-lf-cc-workspace-bot-local` | LangFuse 公钥 |
| `LANGFUSE_SECRET_KEY` | `sk-lf-cc-workspace-bot-local` | LangFuse 私钥 |
| `LANGFUSE_BASE_URL` | `http://localhost:3000` | LangFuse 地址 |
| `CC_LF_APP_ID` | `srsran-4g-dev` | 应用标识 |

> **注意**：讲师需根据自己的 LangFuse 实例替换密钥。

---

## 四、项目文件清单

### 4.1 Claude Code 配置（`.claude/`）

| 路径 | 用途 | 涉及演示 |
|------|------|---------|
| `settings.local.json` | LangFuse 环境变量 + MCP Server + Hooks | 全部 |
| `agents/security-reviewer.md` | 电信安全 Agent | 三-7 |
| `agents/embedded-specialist-reviewer.md` | 嵌入式专家 Agent | 三-7 |
| `agents/compliance-reviewer.md` | 合规审查 Agent | 三-7 |
| `agents/architecture-reviewer.md` | 架构 Agent | 三-7 |
| `agents/code-quality-reviewer.md` | 代码质量 Agent | 三-7 |
| `agents/telecom-security-reviewer.md` | 电信安全（备用） | 三-7 |
| `skills/coverity-triage-sop/SKILL.md` | Coverity 告警分流决策树 | 三-5 |
| `skills/dev-iterate/SKILL.md` | 编译测试修复闭环 | 三-6 |
| `skills/srsran-security/SKILL.md` | 安全知识库 | 三-7 |

### 4.2 MCP Server

| 路径 | 用途 | 涉及演示 |
|------|------|---------|
| `coverity-mcp-server/server.py` | FastMCP Server，4 个工具 | 三-4 |
| `coverity-mcp-server/mock_findings.json` | Mock Coverity 告警数据 | 三-4, 三-5 |

### 4.3 Hook 脚本

| 路径 | 触发时机 | 用途 | 涉及演示 |
|------|---------|------|---------|
| `hooks/stop_check_syntax.py` | Stop Hook | 会话结束前 C/C++ 语法检查 | 三-6 |
| PostToolUse (settings.local.json) | Write/Edit 后 | clang-format 自动格式化 | 三-6 |

### 4.4 知识文件（演示中生成/恢复）

| 路径 | 行数 | 用途 | 涉及演示 |
|------|------|------|---------|
| `CLAUDE.md` | 108 | 项目知识库 | 三-1（生成并恢复） |
| `CODEMAP.md` | 436 | 代码地图 + 热区/冷区 | 三-2B（生成并恢复） |
| `docs/project-overview.html` | ~740 | 6 面板暗色主题全景图 | 三-2A（生成并恢复） |
| `docs/build-guide.md` | — | 构建指南 | 参考 |
| `docs/lsp-setup.md` | — | LSP 配置指南 | 三-3 参考 |
| `docs/naming-conventions.md` | — | 命名规范 | 参考 |

### 4.5 测试

| 路径 | 用例数 | 用途 |
|------|--------|------|
| `tests/test_demo_all.py` | 76 | 全部 7 个演示的端到端验证 |

### 4.6 构建产物

| 路径 | 大小 | 用途 |
|------|------|------|
| `build/` | ~2GB | cmake 构建输出 |
| `compile_commands.json` | 865KB | 软链接 → `build/compile_commands.json` |

---

## 五、课前检查（5 分钟）

```bash
cd /root/course/code/ziguangzhanrui_2/srsRAN_4G

# 1. 工具链
claude --version
which clangd clang-format cppcheck cmake

# 2. 构建
cmake --build build -j$(nproc) 2>&1 | tail -5

# 3. compile_commands.json
ls -la compile_commands.json
# 应为软链接 → build/compile_commands.json

# 4. LangFuse
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/api/public/health
# 应返回 200

# 5. MCP Server
python3 -c "import json; d=json.load(open('coverity-mcp-server/mock_findings.json')); print(f'{len(d)} findings loaded')"

# 6. 测试套件
python3 -m pytest tests/test_demo_all.py -v
# 应输出 76 passed

# 7. CLAUDE.md 原始状态（演示三-1 会修改并恢复）
wc -l CLAUDE.md
# 应为 108 行
```

---

## 六、演示一览

| # | 演示 | 核心操作 | 产物 |
|---|------|---------|------|
| 三-1 | CLAUDE.md 初始化 | AI 生成项目知识库 | CLAUDE.md（108→扩展→恢复 108） |
| 三-2A | HTML 全景可视化 | 生成暗色主题 6 面板架构图 | docs/project-overview.html |
| 三-2B | CODEMAP + LLM Wiki | 生成代码地图（热区/冷区/依赖） | CODEMAP.md |
| 三-3 | AST 索引 + clangd LSP | cmake 生成 compile_commands.json | compile_commands.json |
| 三-4 | Coverity MCP Server | FastMCP Server + 4 工具 | coverity-mcp-server/ |
| 三-5 | Coverity Skill 分流 | 决策树 Step0→Q1-Q4 | .claude/skills/coverity-triage-sop/ |
| 三-6 | dev-iterate 迭代闭环 | PostToolUse + Stop Hook 三层守卫 | .claude/skills/dev-iterate/ + hooks/ |
| 三-7 | 多 Agent 并行安全审查 | 3 Agent 并行审查 security.cc | .claude/agents/ (6 个) |

---

## 七、注意事项

1. **演示三-1/三-2A/三-2B 会修改文件**：CLAUDE.md、CODEMAP.md、project-overview.html 在演示中会被 AI 重新生成。演示结束后需恢复原始版本（测试套件会验证）。
2. **LangFuse 密钥**：`settings.local.json` 中的密钥为开发环境值，讲师需替换为自己的实例。
3. **构建耗时**：首次 `make -j$(nproc)` 约 5-10 分钟，后续增量构建很快。
4. **磁盘空间**：`build/` 目录约 2GB，确保磁盘充足。
