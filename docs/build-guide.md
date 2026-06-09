# srsRAN_4G Build Guide

---

## 依赖安装

```bash
# Ubuntu/Debian
sudo apt install -y \
  cmake build-essential \
  libfftw3-dev libmbedtls-dev libsctp-dev \
  libconfig++-dev libzmq3-dev \
  libyaml-cpp-dev libpcsclite-dev

# 可选：UHD 驱动（用于 USRP 硬件）
sudo apt install -y libuhd-dev uhd-host
```

---

## CMake 配置选项

### 基础构建

```bash
mkdir -p build && cd build

# Debug 构建（含调试符号，无优化）
cmake .. -DCMAKE_BUILD_TYPE=Debug

# Release 构建（开启优化，默认）
cmake .. -DCMAKE_BUILD_TYPE=Release

# RelWithDebInfo（优化 + 调试符号，推荐用于性能分析）
cmake .. -DCMAKE_BUILD_TYPE=RelWithDebInfo
```

### 完整 CMake 选项参考

| 选项 | 默认值 | 说明 |
|------|--------|------|
| `CMAKE_BUILD_TYPE` | Release | 构建类型：Debug / Release / RelWithDebInfo |
| `CMAKE_EXPORT_COMPILE_COMMANDS` | OFF | 生成 compile_commands.json（LSP 需要） |
| `ENABLE_SRSUE` | ON | 构建 srsUE 终端应用 |
| `ENABLE_SRSENB` | ON | 构建 srsENB 基站应用 |
| `ENABLE_SRSEPC` | ON | 构建 srsEPC 核心网应用 |
| `ENABLE_WERROR` | ON | 将编译警告视为错误 |
| `ENABLE_UHD` | ON | 启用 UHD（USRP）射频驱动 |
| `ENABLE_BLADERF` | ON | 启用 BladeRF 射频驱动 |
| `ENABLE_SOAPYSDR` | ON | 启用 SoapySDR 射频驱动 |
| `ENABLE_ZEROMQ` | ON | 启用 ZeroMQ 虚拟射频（仿真必需） |
| `ENABLE_GUI` | ON | 启用 srsGUI 图形界面 |
| `ENABLE_RF_PLUGINS` | ON | 启用射频插件动态加载 |
| `ENABLE_HARDSIM` | ON | 启用 SIM 卡支持 |
| `ENABLE_ASAN` | OFF | 启用 AddressSanitizer 内存检测 |
| `ENABLE_MSAN` | OFF | 启用 MemorySanitizer |
| `ENABLE_TSAN` | OFF | 启用 ThreadSanitizer 线程检测 |
| `ENABLE_GCOV` | OFF | 启用 gcov 代码覆盖率 |
| `ENABLE_TIDY` | OFF | 启用 clang-tidy 静态分析 |
| `ENABLE_TTCN3` | OFF | 启用 TTCN-3 测试二进制 |
| `ENABLE_ZMQ_TEST` | OFF | 启用 ZeroMQ 端到端测试 |
| `ENABLE_SRSLOG_TRACING` | OFF | 启用 srslog 事件追踪 |
| `ENABLE_TIMEPROF` | ON | 启用时间性能分析 |
| `ASSERTS_ENABLED` | ON | 启用 srsRAN 断言 |
| `STOP_ON_WARNING` | OFF | 遇到日志 WARNING 时中断程序 |
| `BUILD_STATIC` | OFF | 静态链接外部依赖 |
| `BUILD_WITH_LTO` | OFF | 启用链接时优化（实验性） |
| `DISABLE_SIMD` | OFF | 禁用 SIMD 指令（调试用） |
| `AUTO_DETECT_ISA` | ON | 自动检测 ISA 扩展 |
| `USE_LTE_RATES` | OFF | 使用标准 LTE 采样率 |
| `USE_MKL` | OFF | 使用 Intel MKL 替代 FFTW3 |
| `FORCE_32BIT` | OFF | 强制 32 位编译 |
| `GCC_ARCH` | native | GCC 目标架构（aarch64 自动设为 armv8-a） |
| `PARALLEL_COMPILE_JOBS` | - | 限制并行编译任务数（嵌入式系统内存受限时使用） |

### 推荐开发构建命令

```bash
cmake .. \
  -DCMAKE_BUILD_TYPE=Debug \
  -DCMAKE_EXPORT_COMPILE_COMMANDS=ON \
  -DENABLE_WERROR=OFF \
  -DENABLE_ZEROMQ=ON \
  -DENABLE_ASAN=ON
```

---

## 编译

```bash
# 全量编译（使用所有 CPU 核心）
make -j$(nproc)

# 仅编译特定目标
make srsue        # 仅编译 UE
make srsenb       # 仅编译 eNB
make srsepc       # 仅编译 EPC

# 安装到系统（默认 /usr/local/）
sudo make install
```

---

## 常见构建问题

### 1. FFTW3 找不到

```
CMake Error: Could NOT find FFTW3F
```

**解决**：

```bash
sudo apt install libfftw3-dev
```

### 2. mbedTLS 找不到

```
CMake Error: Could NOT find MbedTLS
```

**解决**：

```bash
sudo apt install libmbedtls-dev
```

### 3. UHD 找不到（可忽略，非必需）

```
CMake Warning: Could NOT find UHD
```

如不使用 USRP 硬件，可安全忽略。或手动禁用：

```bash
cmake .. -DENABLE_UHD=OFF
```

### 4. SCTP 找不到

```
CMake Error: Could NOT find SCTP
```

**解决**：

```bash
sudo apt install libsctp-dev
```

### 5. 编译警告导致失败（WERROR）

默认开启 `-Werror`，编译器警告会被视为错误。开发调试时可关闭：

```bash
cmake .. -DENABLE_WERROR=OFF
```

### 6. 内存不足（嵌入式 / 小内存机器）

并行编译占用大量内存。限制并行数：

```bash
make -j2
# 或通过 cmake 选项
cmake .. -DPARALLEL_COMPILE_JOBS=2
```

### 7. aarch64 / ARM 平台编译

CMake 会自动检测 aarch64 并设置 `GCC_ARCH=armv8-a`。如需手动指定：

```bash
cmake .. -DGCC_ARCH=armv8-a
```

---

## 运行测试

```bash
cd build

# 运行所有测试
make test
# 或
ctest

# 运行特定测试（带详细输出）
ctest -R rlc -V          # 运行所有 RLC 相关测试
ctest -R pdsch -V         # 运行 PDSCH 相关测试

# 启用所有测试（默认部分测试关闭）
cmake .. -DENABLE_ALL_TEST=ON
make -j$(nproc)
ctest

# 查看测试列表
ctest -N
```

### ZeroMQ 端到端测试

```bash
cmake .. -DENABLE_ZMQ_TEST=ON -DENABLE_ZEROMQ=ON
make -j$(nproc)
ctest -R zmq -V
```
