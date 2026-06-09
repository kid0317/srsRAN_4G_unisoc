# srsRAN_4G Naming Conventions

本文档总结 srsRAN 4G 代码库中的命名规范，用于代码阅读和贡献时保持一致性。

---

## 错误码

所有错误码定义在 `lib/include/srsran/config.h`，统一使用 `SRSRAN_` 前缀：

| 错误码 | 值 | 说明 |
|--------|-----|------|
| `SRSRAN_SUCCESS` | 0 | 操作成功 |
| `SRSRAN_ERROR` | -1 | 通用错误 |
| `SRSRAN_ERROR_INVALID_INPUTS` | -2 | 输入参数无效 |
| `SRSRAN_ERROR_TIMEOUT` | -3 | 操作超时 |
| `SRSRAN_ERROR_INVALID_COMMAND` | -4 | 无效命令 |
| `SRSRAN_ERROR_OUT_OF_BOUNDS` | -5 | 索引越界 |
| `SRSRAN_ERROR_CANT_START` | -6 | 无法启动 |
| `SRSRAN_ERROR_ALREADY_STARTED` | -7 | 已在运行 |
| `SRSRAN_ERROR_RX_EOF` | -8 | 接收到 EOF |

**使用模式**：

```c
// C 函数返回值约定
int srsran_pdsch_encode(...) {
  if (input == NULL) {
    return SRSRAN_ERROR_INVALID_INPUTS;
  }
  // ... 处理逻辑
  return SRSRAN_SUCCESS;
}

// 调用侧检查
if (srsran_pdsch_encode(...) != SRSRAN_SUCCESS) {
  // 错误处理
}
```

---

## 日志宏

srsRAN 使用自研的 `srslog` 日志框架（`lib/include/srsran/srslog/`），不使用 printf 或 std::cout。

### 获取 Logger

```cpp
#include "srsran/srslog/srslog.h"

// 获取 logger 实例（按模块名）
srslog::basic_logger& logger = srslog::fetch_basic_logger("MAC");

// 使用
logger.info("DL grant rnti=0x%x, tbs=%d", rnti, tbs);
logger.warning("HARQ retx exceeded max=%d", max_retx);
logger.error("Failed to decode PDSCH");
logger.debug("Buffer pool status: %d/%d", used, total);
```

### 日志级别

| 级别 | 方法 | 用途 |
|------|------|------|
| ERROR | `logger.error(...)` | 不可恢复的错误 |
| WARNING | `logger.warning(...)` | 可恢复但需关注的异常 |
| INFO | `logger.info(...)` | 关键操作状态变更 |
| DEBUG | `logger.debug(...)` | 调试级详细信息 |

### Logger 命名约定

Logger 名称对应协议栈模块，全大写：

```
"PHY", "MAC", "RLC", "PDCP", "RRC", "NAS", "GW", "S1AP", "GTPU"
```

---

## 文件命名

### C 源文件（PHY 层）

PHY 层为纯 C 实现，文件名使用模块前缀 + 下划线分隔：

```
srsran_pdsch.c       -> 不使用（前缀已在路径中体现）
pdsch.c              -> lib/src/phy/phch/pdsch.c
pdsch_nr.c           -> lib/src/phy/phch/pdsch_nr.c（NR 版本加 _nr 后缀）
enb_dl.c             -> lib/src/phy/enb/enb_dl.c
ue_sync.c            -> lib/src/phy/ue/ue_sync.c
```

**规律**：
- 按功能域组织到子目录（`phch/`, `sync/`, `fec/`, `ch_estimation/`）
- NR（5G）版本在文件名末尾加 `_nr` 后缀
- NB-IoT 版本加 `_nbiot` 后缀

### C++ 源文件（协议栈）

协议栈为 C++ 实现，文件名使用模块名 + 下划线分隔：

```
rrc.cc                -> 模块主文件
rrc_ue.cc             -> 每 UE 逻辑
rrc_mobility.cc       -> 子功能（切换）
rrc_bearer_cfg.cc     -> 子功能（承载配置）
sched.cc              -> 调度器主框架
sched_grid.cc         -> 调度器子模块
sched_ue.cc           -> 调度器 UE 管理
```

**规律**：
- 模块主文件直接以模块名命名（`mac.cc`, `rrc.cc`, `rlc.cc`）
- 子功能用 `模块_子功能.cc` 格式
- LTE 版本无后缀，NR 版本加 `_nr` 后缀（如 `rlc_am_nr.cc`）

### 头文件

头文件与源文件同名，扩展名为 `.h`：

```
srsenb/hdr/stack/rrc/rrc.h
srsenb/hdr/stack/mac/mac.h
lib/include/srsran/rlc/rlc.h
lib/include/srsran/upper/pdcp.h
```

**注意**：eNB/UE 的头文件在各自的 `hdr/` 目录下，公共库的头文件在 `lib/include/srsran/` 下。

---

## 函数命名

### C 函数（PHY 层）

使用 `srsran_` 前缀 + 模块名 + 动作，全小写下划线分隔：

```c
// 格式：srsran_<模块>_<动作>()
int  srsran_pdsch_init_enb(srsran_pdsch_t* q, uint32_t max_prb);
int  srsran_pdsch_encode(srsran_pdsch_t* q, ...);
void srsran_pdsch_free(srsran_pdsch_t* q);

int  srsran_chest_dl_init(srsran_chest_dl_t* q, ...);
int  srsran_sync_find(srsran_sync_t* q, ...);
int  srsran_ofdm_tx_sf(srsran_ofdm_t* q);

// 生命周期函数统一模式
srsran_<模块>_init()    // 初始化
srsran_<模块>_free()    // 释放
srsran_<模块>_set_*()   // 设置参数
srsran_<模块>_get_*()   // 获取参数
```

### C++ 方法（协议栈）

C++ 类的方法不使用 `srsran_` 前缀，使用 snake_case：

```cpp
class mac {
public:
  int  init(const mac_args_t& args);
  void stop();
  void reset();
  int  ue_cfg(uint16_t rnti, const sched_interface::ue_cfg_t& cfg);
  void process_pdus();
};

class rrc {
public:
  void init(const rrc_cfg_t& cfg);
  void setup_release(uint16_t rnti);
  void handle_rrc_setup_request(uint16_t rnti, ...);
};
```

---

## 类命名

### C 结构体（PHY 层）

使用 `srsran_` 前缀 + 模块名 + `_t` 后缀：

```c
typedef struct {
  // ...
} srsran_pdsch_t;

typedef struct {
  // ...
} srsran_cell_t;

typedef struct {
  // ...
} srsran_chest_dl_t;

typedef struct {
  // ...
} srsran_ofdm_t;
```

### C++ 类（协议栈）

**不使用 `srsran_` 前缀**，直接使用有意义的类名，小写 snake_case：

```cpp
// 协议栈实体类
class mac;
class rrc;
class rlc;
class pdcp;
class s1ap;

// 子功能类
class sched;            // 调度器
class sched_ue;         // 调度器 UE 管理
class ue;               // UE 上下文
class mac_controller;   // MAC 控制器
class phy_controller;   // PHY 控制器
```

### 配置结构体

配置类使用 `_cfg_t`、`_args_t` 后缀：

```cpp
struct rrc_cfg_t { ... };
struct mac_args_t { ... };
struct phy_args_t { ... };
struct sched_interface::ue_cfg_t { ... };
```

### 指标结构体

指标类使用 `_metrics_t` 后缀：

```cpp
struct mac_metrics_t { ... };
struct rlc_metrics_t { ... };
struct rrc_metrics_t { ... };
```

---

## 接口命名

跨层接口使用 `_interface_` 命名模式：

```cpp
// 格式：<提供方>_interface_<使用方>
class mac_interface_phy_lte;    // MAC 提供给 PHY 的接口
class rrc_interface_mac;        // RRC 提供给 MAC 的接口
class pdcp_interface_rlc;       // PDCP 提供给 RLC 的接口
class rrc_interface_s1ap;       // RRC 提供给 S1AP 的接口
```

头文件位于 `lib/include/srsran/interfaces/`：

```
enb_mac_interfaces.h       # eNB MAC 接口
enb_rrc_interface_mac.h    # eNB RRC-MAC 接口
ue_phy_interfaces.h        # UE PHY 接口
```

---

## 命名空间

- 公共库代码使用 `srsran` 命名空间
- eNB 代码使用 `srsenb` 命名空间
- UE 代码使用 `srsue` 命名空间
- EPC 代码使用 `srsepc` 命名空间

```cpp
namespace srsran { ... }   // lib/
namespace srsenb { ... }   // srsenb/
namespace srsue  { ... }   // srsue/
namespace srsepc { ... }   // srsepc/
```

---

## 宏命名

全大写 + `SRSRAN_` 前缀：

```c
#define SRSRAN_SUCCESS 0
#define SRSRAN_MAX_TBSIZE_BITS 97896
#define SRSRAN_N_SRB 3
#define SRSRAN_N_DRB 8
#define SRSRAN_API __attribute__((visibility("default")))
```

---

## 枚举命名

C 枚举使用 `srsran_` 前缀 + 全小写：

```c
typedef enum {
  SRSRAN_MOD_BPSK = 0,
  SRSRAN_MOD_QPSK,
  SRSRAN_MOD_16QAM,
  SRSRAN_MOD_64QAM,
  SRSRAN_MOD_256QAM,
} srsran_mod_t;
```

C++ 枚举使用 scoped enum：

```cpp
enum class srsran_rat_t { lte, nr, nulltype };
```

---

## 速查表

| 类别 | 模式 | 示例 |
|------|------|------|
| C 函数 | `srsran_<模块>_<动作>()` | `srsran_pdsch_encode()` |
| C 结构体 | `srsran_<模块>_t` | `srsran_cell_t` |
| C++ 类 | 小写 snake_case，无前缀 | `class rrc` |
| 配置结构体 | `<模块>_cfg_t` / `<模块>_args_t` | `rrc_cfg_t` |
| 指标结构体 | `<模块>_metrics_t` | `mac_metrics_t` |
| 跨层接口 | `<提供方>_interface_<使用方>` | `mac_interface_phy_lte` |
| 错误码 | `SRSRAN_ERROR_*` / `SRSRAN_SUCCESS` | `SRSRAN_ERROR_TIMEOUT` |
| 宏 | `SRSRAN_<NAME>` | `SRSRAN_MAX_TBSIZE_BITS` |
| 命名空间 | 按应用划分 | `srsran`, `srsenb`, `srsue`, `srsepc` |
| 文件名 | snake_case，NR 加 `_nr` 后缀 | `pdsch_nr.c`, `rlc_am_nr.cc` |
