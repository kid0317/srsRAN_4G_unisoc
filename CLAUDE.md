# srsRAN_4G

开源 4G/5G 软件无线电协议栈。包含 UE、eNodeB、EPC 三个完整实现。

## 模块结构

| 目录 | 功能 | 关键文件 |
|------|------|---------|
| lib/ | 公共库（PHY/MAC/RLC/PDCP/ASN1） | lib/include/srsran/config.h（错误码） |
| srsue/ | 4G UE 全协议栈 | srsue/src/phy/sync.cc（同步模块） |
| srsenb/ | 4G eNodeB | srsenb/src/enb.cc（基站入口） |
| srsepc/ | 轻量级 EPC | srsepc/src/ |
| srsgnb/ | 5G gNodeB（实验性） | srsgnb/src/ |

## 编码约定

- 错误码在 config.h 定义，SRSRAN_SUCCESS(0) 到 SRSRAN_ERROR_RX_EOF(-8)
- 新增错误码递减分配，格式：#define SRSRAN_ERROR_<描述> <负整数>
- 日志宏：Error/Warning/Info/Debug(fmt, ...)
- C++ 标准：C++14
- 禁止修改已有错误码的编号值
- 每次改完代码，必须进行编译确认通过

## 代码质量

- 静态分析：Coverity Scan（CI 集成），本地可用 cppcheck / clang-tidy
- 编码规范参考：MISRA C:2012（Advisory 级别建议遵守）
- 格式化：项目根目录 .clang-format（Google 风格变体）

## 构建命令

```bash
mkdir -p build && cd build
cmake -DCMAKE_BUILD_TYPE=Debug -DENABLE_WERROR=ON -DCMAKE_EXPORT_COMPILE_COMMANDS=ON ..
make -j$(nproc)
ctest --output-on-failure
```

## Skill 路由（第三课创建）

| 场景 | 指向 | 状态 |
|------|------|------|
| PHY 层同步问题 | .claude/skills/phy-sync.md | 待创建 |
| 错误码扩展 | .claude/skills/error-codes.md | 待创建 |
| 3GPP 规范映射 | .claude/skills/3gpp-mapping.md | 待创建 |

> 以上 Skill 文件将在第三课「如何创建 Skill」中创建。此处为路由占位，展示 CLAUDE.md 的渐进式披露设计——核心信息在 CLAUDE.md，详细步骤指向 Skill 文件。
