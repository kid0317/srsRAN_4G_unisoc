# srsRAN_4G Code Map

> 本文档是 srsRAN 4G 代码库的模块级导航地图，用于快速定位代码、理解模块职责与依赖关系。

---

## 模块索引

| 模块 | 路径 | 状态 |
|------|------|------|
| PHY 物理层 | `lib/src/phy/` | 🔥 热区 |
| MAC 媒体访问控制 | `lib/src/mac/`, `srsenb/src/stack/mac/`, `srsue/src/stack/mac/` | 🔥 热区 |
| RLC 无线链路控制 | `lib/src/rlc/` | ❄️ 冷区 |
| PDCP 分组数据汇聚 | `lib/src/pdcp/` | ❄️ 冷区 |
| RRC 无线资源控制 | `srsenb/src/stack/rrc/`, `srsue/src/stack/rrc/` | 🔥 热区 |
| S1AP 信令 | `srsenb/src/stack/s1ap/` | ❄️ 冷区 |
| eNodeB 基站 | `srsenb/` | 🔥 热区 |
| UE 终端 | `srsue/` | ❄️ 冷区 |
| EPC 核心网 | `srsepc/` | ❄️ 冷区 |
| Common 公共工具 | `lib/src/common/` | ❄️ 冷区 |

---

## 1. PHY 物理层 🔥

**路径**: `lib/src/phy/`

**职责**: 实现 LTE/NR 物理层信号处理，包括调制解调、信道编解码、同步、信道估计等底层 DSP 算法。

**核心文件**:
| 文件 | 说明 |
|------|------|
| `lib/src/phy/phch/pdsch.c` | PDSCH 下行共享信道处理（编码、调制、资源映射） |
| `lib/src/phy/phch/pusch_nr.c` | NR PUSCH 上行共享信道处理 |
| `lib/src/phy/sync/sync.c` | LTE 同步信号检测（PSS/SSS 搜索与帧同步） |
| `lib/src/phy/fec/turbo/` | Turbo 编解码器实现 |
| `lib/src/phy/ch_estimation/` | 信道估计（DMRS、CSI-RS 等参考信号处理） |

**子目录结构**:
```
lib/src/phy/
├── agc/          # 自动增益控制
├── cfr/          # 削峰因子降低
├── ch_estimation/ # 信道估计
├── channel/      # 信道模型
├── common/       # PHY 公共工具（序列生成、时间戳等）
├── dft/          # FFT/IFFT 变换
├── enb/          # eNB 侧 PHY（enb_dl.c, enb_ul.c）
├── fec/          # 前向纠错（Turbo、LDPC、Polar、CRC）
├── gnb/          # gNB 侧 PHY（NR）
├── io/           # 射频 I/O
├── mimo/         # MIMO 处理
├── modem/        # 调制解调（QPSK、16QAM、64QAM、256QAM）
├── phch/         # 物理信道（PDSCH、PUSCH、PDCCH、PUCCH 等）
├── resampling/   # 重采样
├── rf/           # 射频前端驱动（UHD、BladeRF、ZeroMQ、File）
├── scrambling/   # 加扰/解扰
├── sync/         # 同步（PSS、SSS、SSB）
├── ue/           # UE 侧 PHY（ue_dl.c, ue_ul.c, ue_sync.c）
└── utils/        # PHY 工具函数
```

**对外接口**:
- `lib/include/srsran/phy/` — PHY 层全部头文件
- `lib/include/srsran/phy/common/phy_common.h` — PHY 公共类型定义
- `lib/include/srsran/phy/phch/` — 各物理信道接口
- `lib/include/srsran/phy/enb/` — eNB PHY 上下行接口
- `lib/include/srsran/phy/ue/` — UE PHY 上下行接口

**依赖关系**: 仅依赖 `lib/src/common/`（基础工具）和系统库（FFTW3、SIMD intrinsics）。被 `srsenb/src/phy/`、`srsue/src/phy/` 上层调用。

---

## 2. MAC 媒体访问控制 🔥

**路径**: `lib/src/mac/`（公共 MAC 库），`srsenb/src/stack/mac/`（eNB 侧），`srsue/src/stack/mac/`（UE 侧）

**职责**: 实现 MAC 层调度、HARQ 管理、随机接入、BSR/PHR 处理，是协议栈中调度决策的核心。

**核心文件（公共库 lib）**:
| 文件 | 说明 |
|------|------|
| `lib/src/mac/pdu.cc` | MAC PDU 组装/解析（eNB 与 UE 共用） |
| `lib/src/mac/mac_sch_pdu_nr.cc` | NR MAC SCH PDU 处理 |

**核心文件（eNB 侧）**:
| 文件 | 说明 |
|------|------|
| `srsenb/src/stack/mac/mac.cc` | eNB MAC 主逻辑（TTI 处理入口） |
| `srsenb/src/stack/mac/sched.cc` | 调度器主框架（资源分配决策） |
| `srsenb/src/stack/mac/sched_grid.cc` | 调度网格（PRB 资源管理） |
| `srsenb/src/stack/mac/sched_ue.cc` | 每 UE 调度状态管理 |
| `srsenb/src/stack/mac/ue.cc` | MAC 层 UE 上下文 |

**核心文件（UE 侧）**:
| 文件 | 说明 |
|------|------|
| `srsue/src/stack/mac/mac.cc` | UE MAC 主逻辑 |
| `srsue/src/stack/mac/proc_ra.cc` | 随机接入过程 |
| `srsue/src/stack/mac/dl_harq.cc` | 下行 HARQ 进程 |
| `srsue/src/stack/mac/ul_harq.cc` | 上行 HARQ 进程 |
| `srsue/src/stack/mac/mux.cc` | 上行复用（MAC PDU 组装） |

**对外接口**:
- `srsenb/hdr/stack/mac/mac.h` — eNB MAC 接口
- `srsenb/hdr/stack/mac/sched_interface.h` — 调度器接口定义
- `srsue/hdr/stack/mac/` — UE MAC 接口
- `lib/include/srsran/interfaces/enb_mac_interfaces.h` — eNB MAC 跨层接口
- `lib/include/srsran/interfaces/ue_mac_interfaces.h` — UE MAC 跨层接口

**依赖关系**: 向下依赖 PHY 层接口；向上为 RLC 提供逻辑信道传输服务；依赖 `lib/include/srsran/mac/pdu.h` 进行 PDU 组装/解析。

---

## 3. RLC 无线链路控制 ❄️

**路径**: `lib/src/rlc/`

**职责**: 实现 RLC 三种传输模式（TM/UM/AM），负责分段、重组、ARQ 重传，保障上层数据可靠传输。

**核心文件**:
| 文件 | 说明 |
|------|------|
| `lib/src/rlc/rlc.cc` | RLC 实体管理（创建/删除 Bearer） |
| `lib/src/rlc/rlc_am_lte.cc` | LTE AM 模式（确认传输，支持 ARQ） |
| `lib/src/rlc/rlc_um_lte.cc` | LTE UM 模式（非确认传输） |
| `lib/src/rlc/rlc_tm.cc` | TM 模式（透明传输，用于 SRB0） |
| `lib/src/rlc/rlc_am_nr.cc` | NR AM 模式实现 |

**对外接口**:
- `lib/include/srsran/rlc/rlc.h` — RLC 主接口
- `lib/include/srsran/rlc/rlc_common.h` — RLC 公共类型与配置
- `lib/include/srsran/rlc/rlc_metrics.h` — RLC 层统计指标
- `lib/include/srsran/interfaces/enb_rlc_interfaces.h` — eNB RLC 跨层接口
- `lib/include/srsran/interfaces/ue_rlc_interfaces.h` — UE RLC 跨层接口

**依赖关系**: 向下依赖 MAC 层逻辑信道；向上为 PDCP 提供 Bearer 级数据传输服务。依赖 `lib/src/rlc/bearer_mem_pool.cc` 管理内存。

---

## 4. PDCP 分组数据汇聚 ❄️

**路径**: `lib/src/pdcp/`

**职责**: 实现 PDCP 层加密/完整性保护、头压缩、序列号管理，是用户面安全的关键层。

**核心文件**:
| 文件 | 说明 |
|------|------|
| `lib/src/pdcp/pdcp.cc` | PDCP 实体管理 |
| `lib/src/pdcp/pdcp_entity_base.cc` | PDCP 实体基类（加密/完保公共逻辑） |
| `lib/src/pdcp/pdcp_entity_lte.cc` | LTE PDCP 实体（12/18 bit SN） |
| `lib/src/pdcp/pdcp_entity_nr.cc` | NR PDCP 实体 |

**对外接口**:
- `lib/include/srsran/upper/pdcp.h` — PDCP 主接口
- `lib/include/srsran/upper/pdcp_entity_base.h` — PDCP 实体基类
- `lib/include/srsran/upper/pdcp_metrics.h` — PDCP 层统计指标
- `lib/include/srsran/interfaces/enb_pdcp_interfaces.h` — eNB PDCP 跨层接口
- `lib/include/srsran/interfaces/ue_pdcp_interfaces.h` — UE PDCP 跨层接口

**依赖关系**: 向下依赖 RLC 层；向上为 RRC（控制面）和 GW/SDAP（用户面）提供安全数据传输。依赖 `lib/src/common/security.cc` 进行加密运算。

---

## 5. RRC 无线资源控制 🔥

**路径**:
- eNB 侧: `srsenb/src/stack/rrc/`
- UE 侧: `srsue/src/stack/rrc/`

**职责**: 实现 RRC 连接管理、小区配置、测量上报、切换控制，是无线接入网的"大脑"。

**核心文件（eNB 侧）**:
| 文件 | 说明 |
|------|------|
| `srsenb/src/stack/rrc/rrc.cc` | eNB RRC 主逻辑（连接建立/释放、系统消息广播） |
| `srsenb/src/stack/rrc/rrc_ue.cc` | 每 UE RRC 状态机 |
| `srsenb/src/stack/rrc/rrc_mobility.cc` | 切换管理（S1/X2 切换） |
| `srsenb/src/stack/rrc/rrc_bearer_cfg.cc` | 承载配置（SRB/DRB 建立） |
| `srsenb/src/stack/rrc/rrc_cell_cfg.cc` | 小区参数配置 |

**核心文件（UE 侧）**:
| 文件 | 说明 |
|------|------|
| `srsue/src/stack/rrc/rrc.cc` | UE RRC 主逻辑（小区搜索、连接建立） |
| `srsue/src/stack/rrc/rrc_procedures.cc` | RRC 过程（连接建立、重配置、重建立） |
| `srsue/src/stack/rrc/rrc_meas.cc` | 测量配置与上报 |
| `srsue/src/stack/rrc/rrc_cell.cc` | 小区信息管理 |
| `srsue/src/stack/rrc/phy_controller.cc` | PHY 层控制（频率/定时调整） |

**对外接口**:
- `srsenb/hdr/stack/rrc/rrc.h` — eNB RRC 主接口
- `srsenb/hdr/stack/rrc/rrc_config.h` — eNB RRC 配置结构
- `srsue/hdr/stack/rrc/rrc.h` — UE RRC 主接口
- `lib/include/srsran/interfaces/enb_rrc_interface_*.h` — eNB RRC 与各层的跨层接口
- `lib/include/srsran/interfaces/ue_rrc_interfaces.h` — UE RRC 跨层接口
- `lib/include/srsran/rrc/` — ASN.1 RRC 消息定义

**依赖关系**: 向下依赖 PDCP（控制面消息传输）、MAC（调度配置）、PHY（物理层配置）；向上通过 S1AP 与 EPC 交互。RRC 是协议栈中依赖关系最复杂的模块。

---

## 6. S1AP 信令 ❄️

**路径**: `srsenb/src/stack/s1ap/`

**职责**: 实现 eNB 与 EPC（MME）之间的 S1 接口信令，负责 UE 上下文管理、E-RAB 管理、寻呼等。

**核心文件**:
| 文件 | 说明 |
|------|------|
| `srsenb/src/stack/s1ap/s1ap.cc` | S1AP 完整实现（SCTP 连接、消息编解码、过程处理） |

**对外接口**:
- `srsenb/hdr/stack/s1ap/s1ap.h` — S1AP 主接口
- `srsenb/hdr/stack/s1ap/s1ap_metrics.h` — S1AP 统计指标
- `lib/include/srsran/interfaces/enb_s1ap_interfaces.h` — S1AP 跨层接口
- `lib/include/srsran/interfaces/enb_rrc_interface_s1ap.h` — RRC-S1AP 接口

**依赖关系**: 向下依赖 SCTP socket（网络传输）；向上为 RRC 提供 NAS 消息转发和 EPC 信令交互。依赖 ASN.1 编解码库。

---

## 7. eNodeB 基站 🔥

**路径**: `srsenb/`

**职责**: eNB 应用程序顶层，集成 PHY、MAC、RLC、PDCP、RRC、S1AP 形成完整的 4G 基站。

**核心文件**:
| 文件 | 说明 |
|------|------|
| `srsenb/src/main.cc` | 程序入口（配置解析、信号处理） |
| `srsenb/src/enb.cc` | eNB 主类（初始化各层、启停控制） |
| `srsenb/src/enb_cfg_parser.cc` | 配置文件解析（enb.conf） |
| `srsenb/src/stack/enb_stack_lte.cc` | LTE 协议栈集成（MAC+RLC+PDCP+RRC+S1AP） |
| `srsenb/src/metrics_stdout.cc` | 终端指标输出 |

**目录结构**:
```
srsenb/
├── hdr/           # 头文件
│   ├── common/    # eNB 公共定义
│   ├── phy/       # eNB PHY 层
│   └── stack/     # 协议栈（mac/, rrc/, s1ap/）
├── src/
│   ├── main.cc    # 入口
│   ├── enb.cc     # 主控
│   ├── phy/       # eNB PHY 工作线程
│   └── stack/     # 协议栈实现
└── test/          # 单元测试
```

**对外接口**:
- `srsenb/hdr/enb.h` — eNB 主接口
- `lib/include/srsran/interfaces/enb_interfaces.h` — eNB 全部跨层接口汇总
- `lib/include/srsran/interfaces/enb_metrics_interface.h` — 指标采集接口

**依赖关系**: 依赖 `lib/`（PHY、RLC、PDCP、Common）中的公共库实现；依赖射频驱动（UHD/BladeRF/ZeroMQ）。

---

## 8. UE 终端 ❄️

**路径**: `srsue/`

**职责**: UE 应用程序顶层，实现完整的 4G/5G NSA 终端功能，包括小区搜索、附着、数据收发。

**核心文件**:
| 文件 | 说明 |
|------|------|
| `srsue/src/main.cc` | 程序入口 |
| `srsue/src/ue.cc` | UE 主类（初始化各层） |
| `srsue/src/phy/phy.cc` | UE PHY 层管理 |
| `srsue/src/stack/ue_stack_lte.cc` | LTE 协议栈集成 |
| `srsue/src/stack/mac/proc_ra.cc` | 随机接入过程 |

**目录结构**:
```
srsue/
├── hdr/           # 头文件
│   ├── phy/       # UE PHY 层
│   └── stack/     # 协议栈（mac/, rrc/）
├── src/
│   ├── main.cc    # 入口
│   ├── ue.cc      # 主控
│   ├── phy/       # UE PHY（同步、搜索、收发）
│   └── stack/     # 协议栈（mac/, rrc/, upper/）
└── test/          # 单元测试
```

**对外接口**:
- `srsue/hdr/ue.h` — UE 主接口
- `lib/include/srsran/interfaces/ue_interfaces.h` — UE 全部跨层接口汇总
- `lib/include/srsran/interfaces/ue_*_interfaces.h` — 各层跨层接口

**依赖关系**: 依赖 `lib/`（PHY、RLC、PDCP、Common）；依赖射频驱动。UE 侧 NAS 层实现在 `srsue/src/stack/upper/`。

---

## 9. EPC 核心网 ❄️

**路径**: `srsepc/`

**职责**: 轻量级 EPC 实现（MME + HSS + S-GW/P-GW），用于测试和开发环境。

**核心文件**:
| 文件 | 说明 |
|------|------|
| `srsepc/src/main.cc` | 程序入口 |
| `srsepc/src/mme/mme.cc` | MME 主逻辑（S1AP 连接管理） |
| `srsepc/src/mme/s1ap.cc` | EPC 侧 S1AP 实现 |
| `srsepc/src/mme/nas.cc` | NAS 层（鉴权、附着、安全模式） |
| `srsepc/src/spgw/spgw.cc` | S-GW/P-GW 合设（GTP-U 隧道、IP 分配） |

**目录结构**:
```
srsepc/
├── hdr/
│   ├── hss/       # 归属用户服务器（用户数据库）
│   ├── mme/       # 移动管理实体
│   ├── mbms-gw/   # MBMS 网关
│   └── spgw/      # 服务网关/PDN 网关
├── src/
│   ├── hss/       # hss.cc
│   ├── mme/       # mme.cc, s1ap.cc, nas.cc 等
│   ├── mbms-gw/   # MBMS 网关实现
│   └── spgw/      # spgw.cc, gtpc.cc, gtpu.cc
└── epc.conf.example  # 配置示例
```

**对外接口**:
- `srsepc/hdr/mme/mme.h` — MME 主接口
- `srsepc/hdr/mme/s1ap.h` — EPC 侧 S1AP
- `srsepc/hdr/spgw/` — S/P-GW 接口
- `lib/include/srsran/interfaces/epc_interfaces.h` — EPC 跨层接口

**依赖关系**: 依赖 `lib/src/common/`（安全算法、网络工具）；通过 SCTP 与 eNB S1AP 通信；通过 GTP-U 隧道转发用户面数据。

---

## 10. Common 公共工具 ❄️

**路径**: `lib/src/common/`

**职责**: 提供跨模块的基础设施：安全算法、字节缓冲区、线程池、PCAP 抓包、网络工具等。

**核心文件**:
| 文件 | 说明 |
|------|------|
| `lib/src/common/security.cc` | AES/SNOW3G/ZUC 安全算法 |
| `lib/src/common/byte_buffer.cc` | 零拷贝字节缓冲区 |
| `lib/src/common/thread_pool.cc` | 任务线程池 |
| `lib/src/common/network_utils.cc` | Socket/SCTP 网络工具 |
| `lib/src/common/mac_pcap.cc` | MAC 层 PCAP 抓包 |

**对外接口**:
- `lib/include/srsran/common/common.h` — 全局常量与类型定义
- `lib/include/srsran/common/byte_buffer.h` — 字节缓冲区
- `lib/include/srsran/common/threads.h` — 线程抽象
- `lib/include/srsran/common/security.h` — 安全算法接口
- `lib/include/srsran/common/buffer_pool.h` — 内存池
- `lib/include/srsran/config.h` — 错误码与导出宏定义

**依赖关系**: 被所有模块依赖，是代码库的基础层。自身仅依赖系统库（pthread、OpenSSL/mbedTLS 等）。

---

## 跨层接口总览

所有跨层接口定义集中在 `lib/include/srsran/interfaces/`：

```
interfaces/
├── enb_interfaces.h           # eNB 接口汇总
├── enb_mac_interfaces.h       # PHY ↔ MAC
├── enb_rlc_interfaces.h       # MAC ↔ RLC
├── enb_pdcp_interfaces.h      # RLC ↔ PDCP
├── enb_rrc_interface_mac.h    # RRC ↔ MAC
├── enb_rrc_interface_pdcp.h   # RRC ↔ PDCP
├── enb_rrc_interface_rlc.h    # RRC ↔ RLC
├── enb_rrc_interface_s1ap.h   # RRC ↔ S1AP
├── enb_s1ap_interfaces.h      # S1AP 接口
├── enb_phy_interfaces.h       # PHY 接口
├── ue_interfaces.h            # UE 接口汇总
├── ue_mac_interfaces.h        # UE MAC 接口
├── ue_phy_interfaces.h        # UE PHY 接口
├── ue_rlc_interfaces.h        # UE RLC 接口
├── ue_pdcp_interfaces.h       # UE PDCP 接口
├── ue_rrc_interfaces.h        # UE RRC 接口
├── ue_nas_interfaces.h        # UE NAS 接口
├── ue_gw_interfaces.h         # UE GW 接口
└── epc_interfaces.h           # EPC 接口
```

## 协议栈数据流（下行）

```
EPC (S-GW)
  │ GTP-U
  ▼
S1AP ──→ RRC (控制面)
  │
  ▼
PDCP (加密/完保)
  │
  ▼
RLC (分段/ARQ)
  │
  ▼
MAC (调度/HARQ)
  │
  ▼
PHY (编码/调制/OFDM)
  │
  ▼
RF (射频发射)
```

## 日志系统

日志基础设施位于 `lib/include/srsran/srslog/`，使用 `srslog` 框架：
- `srslog.h` — 日志 API 入口
- `logger.h` — Logger 类定义
- `log_channel.h` — 日志通道
- `sink.h` — 日志输出目标（文件、stdout）

## 测试目录

| 路径 | 说明 |
|------|------|
| `lib/test/` | 公共库单元测试 |
| `srsenb/test/` | eNB 测试（MAC 调度器测试等） |
| `srsue/test/` | UE 测试 |
| `test/` | 集成测试 |
