# clangd LSP Setup Guide

本指南帮助你在 Claude Code 中配置 clangd LSP 插件，实现对 srsRAN_4G C/C++ 代码库的精确导航与分析。

---

## 前提条件

1. **clangd 已安装**（版本 >= 14 推荐）
2. **compile_commands.json 已生成**（见下一节）
3. Claude Code CLI 已安装并可正常运行

验证 clangd 安装：

```bash
clangd --version
```

如未安装：

```bash
# Ubuntu/Debian
sudo apt install clangd

# macOS
brew install llvm
```

---

## 生成 compile_commands.json

clangd 需要 `compile_commands.json` 来理解项目的编译参数（头文件路径、宏定义、编译选项等）。

```bash
cd /root/course/code/ziguangzhanrui_2/srsRAN_4G

# 创建构建目录
mkdir -p build && cd build

# 使用 cmake 生成，关键参数：CMAKE_EXPORT_COMPILE_COMMANDS=ON
cmake .. \
  -DCMAKE_BUILD_TYPE=Debug \
  -DCMAKE_EXPORT_COMPILE_COMMANDS=ON

# 将 compile_commands.json 软链接到项目根目录（clangd 默认在根目录查找）
ln -sf build/compile_commands.json ../compile_commands.json
```

生成后验证文件存在：

```bash
ls -la compile_commands.json
# 应显示指向 build/compile_commands.json 的软链接
```

---

## 安装 clangd LSP 插件

在 Claude Code 中执行：

```
/plugin install clangd-lsp@claude-plugins-official
```

---

## 验证安装

```
/plugin list
```

输出中应包含：

```
clangd-lsp: enabled
```

---

## LSP 操作一览

安装并启用后，以下 LSP 操作可用于代码导航和分析：

| 操作 | 说明 | 用途示例 |
|------|------|---------|
| `goToDefinition` | 跳转到符号定义 | 查看 `srsran_pdsch_encode()` 的实现位置 |
| `findReferences` | 查找所有引用 | 找出 `mac_interface_phy_lte` 在哪些文件中被使用 |
| `hover` | 悬停查看类型信息 | 查看变量/函数的类型签名和文档注释 |
| `documentSymbol` | 列出文件中所有符号 | 快速浏览 `rrc.cc` 中定义的所有函数和类 |
| `workspaceSymbol` | 全工作区符号搜索 | 搜索名为 `sched_` 开头的所有类 |
| `goToImplementation` | 跳转到接口实现 | 从虚函数声明跳转到具体实现类 |
| `prepareCallHierarchy` | 准备调用层次 | 分析 `process_tti()` 的调用树 |
| `incomingCalls` | 查看谁调用了此函数 | 追踪 `dl_grant()` 被哪些调度器调用 |
| `outgoingCalls` | 查看此函数调用了谁 | 分析 `rrc_setup()` 内部调用了哪些子函数 |

---

## 启用/禁用插件（A/B 对比）

在调试或性能对比时，可临时启用或禁用 clangd LSP 插件：

```bash
# 禁用插件（回退到纯文本搜索）
/plugin disable clangd-lsp@claude-plugins-official

# 重新启用插件
/plugin enable clangd-lsp@claude-plugins-official
```

**对比场景**：
- **启用 LSP**：精确跳转定义、类型推断、跨文件引用追踪，适合深度代码分析
- **禁用 LSP**：依赖 grep/glob 文本搜索，适合简单查找或 LSP 索引未就绪时

---

## 故障排除

### 首次索引较慢

clangd 首次打开项目时需要解析所有编译单元，对于 srsRAN_4G 这样的大型 C/C++ 项目，**首次索引可能需要数分钟**。

- 索引进度会生成 `.cache/clangd/index/` 目录
- 后续启动会使用缓存，速度显著加快
- 索引期间 LSP 功能可能不完整或响应较慢

### 重启 clangd

如果 LSP 出现异常（符号找不到、跳转错误、索引卡住），尝试重启：

```bash
# 方法 1：通过插件命令重启
/plugin restart clangd-lsp@claude-plugins-official

# 方法 2：手动终止 clangd 进程
pkill clangd

# 方法 3：清除索引缓存后重启
rm -rf .cache/clangd/
# 然后重新启用插件
```

### compile_commands.json 找不到

clangd 按以下顺序查找 `compile_commands.json`：

1. 项目根目录
2. `build/` 子目录

确保软链接正确：

```bash
ls -la compile_commands.json
# 应指向 build/compile_commands.json
```

### 头文件报错（红色波浪线）

常见原因：
- 未安装依赖库（FFTW3、UHD 等），cmake 阶段会报错
- `compile_commands.json` 过期，需重新运行 cmake 生成
- 系统头文件路径不在 clangd 搜索范围内

解决：

```bash
cd build && cmake .. -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
```

---

## 交叉编译环境配置

紫光展锐等芯片公司的项目通常需要交叉编译到 ARM 目标板。交叉编译生成的 `compile_commands.json` 中编译器路径指向交叉编译工具链，本机 clangd 需要额外配置才能正确解析。

### 配置 .clangd 文件

在项目根目录创建 `.clangd` 配置文件：

```yaml
CompileFlags:
  # 告诉 clangd 识别交叉编译器的内置头文件路径
  Compiler: /opt/toolchain/bin/aarch64-linux-gnu-gcc
  Add:
    - --query-driver=/opt/toolchain/bin/aarch64-linux-gnu-*
    - -I/opt/toolchain/aarch64-linux-gnu/include
  Remove:
    # 移除 clangd 不支持的交叉编译器特有选项
    - -mfloat-abi=*
    - -march=*
```

### 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 找不到 `arm_neon.h` | 交叉编译器内置头文件未映射 | 在 `.clangd` 的 Add 中添加工具链 include 路径 |
| 宏 `__ARM_NEON__` 未定义 | clangd 用本机编译器，不定义 ARM 宏 | 在 Add 中添加 `-D__ARM_NEON__=1` |
| sysroot 路径不对 | cmake 用了 `--sysroot` 但 clangd 找不到 | 添加 `--sysroot=/opt/toolchain/sysroot` |

### Bear 工具（非 CMake 项目）

如果项目不使用 CMake，可用 Bear 工具从 Make 构建中捕获编译命令：

```bash
# 安装
sudo apt install bear

# 生成 compile_commands.json
bear -- make -j$(nproc)
```
