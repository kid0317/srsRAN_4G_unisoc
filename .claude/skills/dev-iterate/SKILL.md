---
name: dev-iterate
description: >
  涉及代码修改、Bug 修复、功能实现、编译-测试-修复循环、构建错误、
  测试失败或迭代式开发时，必须调用。为 srsRAN_4G C/C++ 代码库管理
  编译-测试-修复循环，带重试上限与针对性测试选择。不要跳过。
  (compile-test-fix, build error, test failure, iterative development)
---

# dev-iterate：编译-测试-修复循环

## 迭代流程

第 1 步：进行代码修改
第 2 步：构建 → `cmake --build build -j$(nproc) 2>&1 | tail -30`
第 3 步：构建失败？→ 分析错误，修复，重试（记录重试次数）
第 4 步：构建成功 → 按映射表运行针对性测试
第 5 步：测试失败？→ 分析失败原因，修复，回到第 2 步
第 6 步：全部通过 → 对修改过的文件执行 clang-format
第 7 步：输出汇总报告

## 测试映射表

| 修改的模块 | 路径模式 | 测试命令 | 预期测试数 |
|----------------|-------------|-------------|---------------|
| PHY | lib/src/phy/ | cd build && ctest -R phy --output-on-failure | ~12 |
| MAC | srsenb/src/stack/mac/ | cd build && ctest -R mac --output-on-failure | ~8 |
| RLC | lib/src/rlc/ | cd build && ctest -R rlc --output-on-failure | ~6 |
| PDCP | lib/src/pdcp/ | cd build && ctest -R pdcp --output-on-failure | ~4 |
| RRC | srsenb/src/stack/rrc/ | cd build && ctest -R rrc --output-on-failure | ~4 |
| Common | lib/src/common/ | cd build && ctest -R common --output-on-failure | ~10 |
| 跨模块 | 多个 | cd build && ctest --output-on-failure | 全量 |

## 重试上限（CRITICAL）

- 单文件重试上限：5 轮
- 整个会话全局重试上限：共 10 轮
- 达到上限后：停止并报告剩余错误

## 构建错误处理

### C++ 模板错误
模板错误输出冗长，只看最后 20 行：
  cmake --build build -j$(nproc) 2>&1 | tail -20

### 链接错误
  nm -C build/lib/libsrsran_phy.a | grep missing_symbol

### 缺少头文件
  grep -r include_directories CMakeLists.txt

## 格式化

所有测试通过后，对修改过的文件运行 clang-format：
  clang-format -i <modified_files>

## 汇总模板

  ## 迭代汇总
  - 修改的文件：{file list}
  - 构建重试：{N} 轮
  - 测试范围：{module}（{M} 个测试）
  - 测试结果：{PASS/FAIL}
  - 是否格式化：{done/skipped}
  - 遗留问题：{none/list}
