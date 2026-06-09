# srsRAN_4G

开源 4G/5G 软件无线电（SDR）协议栈套件——在通用计算机 + SDR 射频前端上完整实现 LTE 终端、基站与核心网，无需专用基带芯片即可搭建可运行的 4G 网络（含实验性 5G NR 功能）。

> 上游项目：[srsran/srsRAN_4G](https://github.com/srsran/srsRAN_4G)（5G O-RAN CU/DU 见 srsRAN Project）。
> 完整可视化概览见 → [`docs/project-overview.html`](docs/project-overview.html)

---

## 核心架构

### 对外接口与系统实体

三个独立可执行程序 + 一个公共库，通过标准 3GPP 接口互联：

| 实体 | 可执行文件 | 角色 | 关键 3GPP 接口 |
|------|-----------|------|---------------|
| srsUE | `srsue` | 全栈 SDR 4G 终端（含实验性 5G） | Uu（空口，对 eNB） |
| srsENB | `srsenb` | 全栈 SDR 4G eNodeB 基站 | Uu、S1（对 EPC） |
| srsGNB | （随 srsenb 构建） | 实验性 5G gNodeB | — |
| srsEPC | `srsepc` | 轻量核心网（MME + HSS + S/P-GW + MBMS-GW） | S1-MME、S1-U |
| 公共库 | `libsrsran_*.so` | PHY/MAC/RLC/PDCP/ASN1 等被三端复用 | — |

- **典型部署**：`srsepc` ←S1→ `srsenb` ←Uu→ `srsue`。射频可用真实 SDR（USRP/BladeRF/Soapy）或 ZeroMQ 虚拟射频做纯软件仿真。
- **配置入口**：各应用读取 `*.conf`（libconfig 格式），样例见 `srsue/`、`srsenb/`、`srsepc/` 各自的 `*.conf.example`。

### 核心模块拓扑

每个应用都是「PHY + Stack」的分层结构，Stack 内自上而下为标准协议栈：

```
应用层    srsue / srsenb / srsgnb / srsepc （main.cc → 应用对象）
  │
Stack    RRC ── NAS         (控制面)
  │       │
  │      PDCP ─ RLC ─ MAC   (用户面/层2)
  │
PHY      OFDM / PDSCH / PUSCH / 信道估计 / 同步  (lib/src/phy，纯 C)
  │
Radio    SDR 抽象层 (UHD / BladeRF / Soapy / ZMQ 插件)
```

→ 分层调用关系与数据流详见 [`docs/project-overview.html`](docs/project-overview.html)

### 关键依赖与技术栈

- **语言**：PHY 层纯 C（C99），协议栈与应用 C++（**C++14**）
- **必需依赖**：FFTW3F（FFT，或 Intel MKL 替代）、mbedTLS（加密）、Boost（program_options）、libsctp（S1 接口）、libconfig++
- **可选依赖**：UHD/BladeRF/SoapySDR（真实 SDR）、ZeroMQ（虚拟射频/仿真）、srsGUI（图形界面）、PCSClite（SIM 卡）
- **日志**：自研 `srslog` 框架（`lib/src/srslog`），禁用 printf/cout
- **构建**：CMake ≥ 3.5；可选 ccache 加速

---

## 关键模块（顶级目录）

| 目录 | 职责 | 核心文件 / 入口 |
|------|------|----------------|
| `lib/` | 公共库：被三端复用的全部协议实现 | 见下方细分 |
| `srsue/` | 4G UE 全协议栈应用 | `src/main.cc`、`src/ue.cc`、`src/phy/`、`src/stack/` |
| `srsenb/` | 4G eNodeB 应用 | `src/main.cc`、`src/enb.cc`、`src/enb_cfg_parser.cc`、`src/stack/`、`src/phy/` |
| `srsgnb/` | 5G gNodeB（实验性） | `srsgnb/` |
| `srsepc/` | 轻量 EPC 核心网 | `src/main.cc`、`src/mme/`、`src/hss/`、`src/spgw/`、`src/mbms-gw/` |
| `lib/include/srsran/` | 全部对外头文件 | `config.h`（错误码/宏）、`srsran.h`、`interfaces/`（跨层接口） |
| `test/`、`tests/` | 集成与端到端测试 | （单元测试就近放在各模块 `test/` 子目录） |
| `cmake/` | CMake 模块（依赖查找、版本、打包） | `cmake/modules/` |
| `docs/` | 项目文档（构建/命名/LSP/概览） | 见文末文档索引 |

### `lib/` 细分

| 子目录 | 职责 |
|--------|------|
| `lib/src/phy/` | 物理层（纯 C）：OFDM、PDSCH/PUSCH、信道编解码（fec）、信道估计、同步（sync） |
| `lib/src/mac/`、`rlc/`、`pdcp/` | 层 2 协议（C++） |
| `lib/src/asn1/` | ASN.1 编解码（RRC、S1AP、LIBLTE 等消息） |
| `lib/src/radio/` | 射频前端抽象层 |
| `lib/src/gtpu/` | GTP-U 用户面隧道 |
| `lib/src/srslog/` | 日志框架 |
| `lib/src/common/`、`support/`、`system/` | 通用工具、缓冲池、线程/任务调度 |
| `lib/include/srsran/adt/` | 抽象数据类型（无锁队列、对象池等） |

---

## 构建命令

```bash
# 推荐开发构建（Debug + 导出 compile_commands.json 供 LSP）
mkdir -p build && cd build
cmake -DCMAKE_BUILD_TYPE=Debug \
      -DENABLE_WERROR=ON \
      -DCMAKE_EXPORT_COMPILE_COMMANDS=ON ..
make -j$(nproc)

# 仅编译单个目标
make srsue        # 或 srsenb / srsepc

# 安装到系统（默认 /usr/local）
sudo make install
```

> 不允许 in-tree 构建（CMake 会报错），必须在独立 `build/` 目录构建。
> 默认 `-Werror` 开启；本地调试可加 `-DENABLE_WERROR=OFF`。
> 完整依赖安装、全部 CMake 选项、交叉编译与常见问题 → [`docs/build-guide.md`](docs/build-guide.md)

```bash
# 测试
cd build
ctest --output-on-failure       # 全部测试
ctest -R rlc -V                  # 按名筛选（如 RLC）
ctest -N                         # 仅列出测试

# 运行（需准备 .conf 配置，详见各应用 *.conf.example）
./srsepc/src/srsepc  epc.conf
./srsenb/src/srsenb  enb.conf
./srsue/src/srsue    ue.conf
```

# 搜索代码
搜索代码或者梳理代码链路时，可以使用clangd-lsp加快进度
---

## 命名约定（速查）

| 类别 | 模式 | 示例 |
|------|------|------|
| C 函数（PHY） | `srsran_<模块>_<动作>()` | `srsran_pdsch_encode()` |
| C 结构体（PHY） | `srsran_<模块>_t` | `srsran_cell_t` |
| C++ 类（协议栈） | 小写 snake_case，**无前缀** | `class rrc` |
| 配置/指标结构体 | `<模块>_cfg_t` / `_args_t` / `_metrics_t` | `rrc_cfg_t`、`mac_metrics_t` |
| 跨层接口 | `<提供方>_interface_<使用方>` | `mac_interface_phy_lte` |
| 错误码 | `SRSRAN_SUCCESS`(0) / `SRSRAN_ERROR_*`(负数) | `SRSRAN_ERROR_TIMEOUT` |
| 宏 | `SRSRAN_<NAME>` 全大写 | `SRSRAN_MAX_TBSIZE_BITS` |
| 文件名 | snake_case；NR 版本加 `_nr`，NB-IoT 加 `_nbiot` | `pdsch_nr.c`、`rlc_am_nr.cc` |
| 命名空间 | 按应用划分 | `srsran` / `srsenb` / `srsue` / `srsepc` |
| 日志 | `srslog::fetch_basic_logger("MAC")` → `.info/.warning/.error/.debug` | logger 名全大写模块名 |

**编码约束（必守）**：
- 错误码统一在 `lib/include/srsran/config.h` 定义，范围 `SRSRAN_SUCCESS`(0) 到 `SRSRAN_ERROR_RX_EOF`(-8)；新增按负数递减分配，**禁止修改已有错误码的编号值**。
- C++ 标准固定为 **C++14**。
- 格式化遵循根目录 `.clang-format`（Google 风格变体），可用 `run-clang-format-diff.sh`。
- 静态分析：Coverity Scan（CI），本地可用 cppcheck / clang-tidy（`-DENABLE_TIDY=ON`）；规范参考 MISRA C:2012（Advisory）。
- **每次改完代码必须本地编译确认通过。**

→ 完整命名规范（含函数生命周期、枚举、头文件布局）详见 [`docs/naming-conventions.md`](docs/naming-conventions.md)

---

## 文档索引

| 文档 | 内容 |
|------|------|
| [`docs/build-guide.md`](docs/build-guide.md) | 依赖安装、全部 CMake 选项、交叉编译、构建问题排查 |
| [`docs/naming-conventions.md`](docs/naming-conventions.md) | 完整命名规范与代码示例 |
| [`docs/lsp-setup.md`](docs/lsp-setup.md) | clangd / LSP 配置（基于 compile_commands.json） |
| [`docs/project-overview.html`](docs/project-overview.html) | 架构全景可视化 |

## Skill 路由

| 场景 | 指向 |
|------|------|
| 编译-测试-修复迭代 | Skill `dev-iterate` |
| Coverity 静态分析三查 | Skill `coverity-triage-sop` |
| 安全审查 / 漏洞分析 | Skill `srsran-security` |
| PHY 层同步问题 | `.claude/skills/phy-sync.md`（待创建） |
| 错误码扩展 | `.claude/skills/error-codes.md`（待创建） |
| 3GPP 规范映射 | `.claude/skills/3gpp-mapping.md`（待创建） |

---

## 禁区

待人工补充。

## 历史包袱

待人工补充。
