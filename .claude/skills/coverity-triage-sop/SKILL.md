---
name: coverity-triage-sop
description: >
  涉及 Coverity 发现项、静态分析定级（triage）、误报分析、BAD_SHIFT、
  DEADCODE、UNINIT、NULL_RETURNS、RESOURCE_LEAK、USE_AFTER_FREE 或
  checker 模式分析时，必须调用。处理使用 Coverity MCP Server 的
  C/C++ 嵌入式项目。不要跳过。
---

# Coverity 发现项定级 SOP

针对嵌入式 C/C++ 代码库中 Coverity 静态分析发现项的系统化定级流程。通过 **coverity-server MCP** 拉取发现项数据并回写定级结论。

## 前置条件

必须已连接 `coverity-server` MCP。它提供以下工具：
- `list_findings(checker?, severity?)` —— 查询发现项，可选过滤条件
- `get_finding_detail(finding_id)` —— 获取完整详情，含代码片段
- `get_finding_stats()` —— 汇总统计
- `update_finding_status(finding_id, status, reason)` —— 回写定级结论

## 第 1 步：获取总览

先了解本次扫描的整体范围：

```
使用 MCP 工具：get_finding_stats()
```

它返回按 checker 类型与严重级别的计数。用于排定优先级：
- **优先高严重级别** —— 可能导致崩溃、安全问题
- **按 checker 类型批处理** —— 把同类发现项归批，定级更高效

## 第 2 步：按 checker 类型定级

对每个 checker 类型，拉取其发现项并套用下方决策树。

```
使用 MCP 工具：list_findings(checker="UNINIT")
```

然后对每个需要细看的发现项：

```
使用 MCP 工具：get_finding_detail(finding_id=1001)
```

阅读代码片段，套用对应的决策树。

### 决策树：UNINIT（未初始化变量）

```
发现项：变量 V 的 UNINIT
  |
  第 0 步：用 Read 工具打开发现项所在位置的文件。
          读取报告行号上下各 30 行。
          确认实际代码与发现项描述一致。
  |
  |- Q1：V 是否由 memset/构造函数/聚合初始化完成初始化？
  |   是 -> 误报（批量初始化）
  |
  |- Q2：V 是否在所有可达代码路径上都被初始化？
  |   （在使用前检查 if/else/switch 的每个分支）
  |   是 -> 误报（Coverity 漏掉了路径约束）
  |
  |- Q3：V 是否为在循环头中初始化的循环变量？
  |   是 -> 误报
  |
  +- Q4：在某条路径上确实未初始化？
      -> 真实问题 —— 修复：在声明处初始化
      ```cpp
      int status = SRSRAN_ERROR;  // 安全默认值
      if (condition) status = SRSRAN_SUCCESS;
      return status;
      ```
```

### 决策树：BAD_SHIFT（无效位移）

```
发现项：表达式 E 上的 BAD_SHIFT
  |
  第 0 步：用 Read 工具打开发现项所在位置的文件。
          读取报告行号上下各 30 行。
          确认实际代码与发现项描述一致。
  |
  |- Q1：移位量是否为小于类型位宽的编译期常量？
  |   是 -> 误报（安全的常量移位）
  |
  |- Q2：移位量是否由规范/配置约束（如 LTE 带宽 nof_prb <= 25）？
  |   是 -> 误报（受领域约束，补充注释）
  |
  |- Q3：移位前是否存在边界检查？
  |   是，但 Coverity 标记的是检查之前的那一行
  |   -> 误报（保护已存在，Coverity 路径分析不精确）
  |
  +- Q4：移位量来自运行时变量且无边界检查？
      -> 真实问题 —— 修复：添加边界检查
      ```cpp
      if (bit_width < 32) {
          mask = (1U << bit_width);
      }
      ```
```

### 决策树：DEADCODE（不可达代码）

```
发现项：第 X 行的 DEADCODE
  |
  第 0 步：用 Read 工具打开发现项所在位置的文件。
          读取报告行号上下各 30 行。
          确认实际代码与发现项描述一致。
  |
  |- Q1：是否位于 #ifdef / #if 预处理条件内？
  |   是 -> 误报（针对平台变体的条件编译）
  |
  |- Q2：防御性默认：是否在覆盖所有取值的 enum switch 中？
  |   是 -> 误报（为将来 enum 扩展预留的安全网，有意为之）
  |
  |- Q3：是否带有 "legacy"/"compat"/"do not delete" 注释？
  |   是 -> 误报（有意保留）
  |
  +- Q4：未找到任何理由？
      -> 真实问题 —— 建议删除（先查 git blame）
```

### 决策树：NULL_RETURNS

```
发现项：调用 F() 的 NULL_RETURNS
  |
  第 0 步：用 Read 工具打开发现项所在位置的文件。
          读取报告行号上下各 30 行。
          确认实际代码与发现项描述一致。
  |
  |- Q1：解引用前是否有空指针检查？
  |   是 -> 误报（Coverity 漏掉了保护）
  |
  |- Q2：在本项目配置下 F() 是否真的可能返回 null？
  |   否（如对合法 RNTI 总是成功）-> 误报
  |
  +- Q3：无空指针检查且 null 确有可能？
      -> 真实问题 —— 修复：添加空指针检查
      ```cpp
      auto* ptr = find_ue(rnti);
      if (ptr == nullptr) {
          logger.error("UE %x not found", rnti);
          return SRSRAN_ERROR;
      }
      ptr->set_cfg(cfg);
      ```
```

### 决策树：RESOURCE_LEAK

```
发现项：资源 R 的 RESOURCE_LEAK
  |
  第 0 步：用 Read 工具打开发现项所在位置的文件。
          读取报告行号上下各 30 行。
          确认实际代码与发现项描述一致。
  |
  |- Q1：R 是否由 RAII 管理（unique_ptr、作用域守卫）？
  |   是 -> 误报
  |
  |- Q2：R 是否在包括错误返回在内的所有路径上都被清理？
  |   是 -> 误报（Coverity 漏掉了某条清理路径）
  |
  +- Q3：错误路径跳过了清理？
      -> 真实问题 —— 修复：补充清理或改用 RAII
      ```cpp
      FILE* f = fopen(path, "wb");
      if (!write_header(f)) {
          fclose(f);  // <-- 原先缺失
          return SRSRAN_ERROR;
      }
      ```
```

### 决策树：BUFFER_SIZE

```
发现项：缓冲区 B 的 BUFFER_SIZE
  |
  第 0 步：用 Read 工具打开发现项所在位置的文件。
          读取报告行号上下各 30 行。
          确认实际代码与发现项描述一致。
  |
  |- Q1：缓冲区是否按规范的最坏情况进行了尺寸设计？
  |   是 -> 误报（缓冲区符合规范）
  |
  |- Q2：写入前是否有长度检查？
  |   是 -> 误报
  |
  +- Q3：合法输入下缓冲区也可能溢出？
      -> 真实问题（嵌入式场景属 CRITICAL —— 可能被利用）
      修复：使用动态分配或增大静态尺寸
```

## 第 3 步：记录结论

对每个已定级的发现项，回写结论：

```
使用 MCP 工具：update_finding_status(
    finding_id=1003,
    status="False_Positive",
    reason="位于已禁用的 #ifdef ENABLE_5G_NR_RLC 内的死代码 —— 属条件编译，并非死代码"
)
```

合法的 status 取值：
- `False_Positive` —— 发现项并非真实问题
- `Intentional` —— 代码按设计即如此，正确
- `Fixed` —— 代码已修复
- `Needs_Review` —— 需人工专家复核
- `Triaged` —— 已确认，后续修复

## 第 4 步：生成定级报告

处理完所有发现项后，输出汇总：

```markdown
## Coverity 定级报告 —— [项目] [日期]

### 统计
- 发现项总数：N
- 真实问题：X（Y% —— 需修复）
- 误报：X（Y%）
- 待复核：X（Y%）

### 行动项（真实问题）

| # | ID | Checker | 文件:行 | 修复说明 | 优先级 |
|---|-----|---------|-----------|-----------------|----------|
| 1 | 1001 | UNINIT | rrc_ue.cc:245 | 在声明处初始化 erab_status | P0 |
| 2 | 1004 | NULL_RETURNS | scheduler.cc:334 | 为 find_ue() 添加空指针检查 | P0 |

### 误报（用于审计留痕）

| # | ID | Checker | 理由 |
|---|-----|---------|--------|
| 1 | 1003 | DEADCODE | 条件编译（#ifdef） |
| 2 | 1007 | BAD_SHIFT | 移位量受 LTE 带宽配置约束（nof_prb <= 25，已有保护） |
```

## 嵌入式专项说明

1. **平台条件编译代码**：针对不同 SoC 变体的 `#ifdef` 块是 DEADCODE 误报的首要来源。
2. **内存映射寄存器**：`*(volatile uint32_t*)ADDR` 模式会触发误报。若地址来自硬件数据手册则有效。
3. **ISR 变量**：在 ISR 中修改的变量在 Coverity 看来像未初始化。检查是否有 `volatile` 限定符。
4. **位域操作**：硬件寄存器位域会导致大量 BAD_SHIFT 误报 —— 核对寄存器规范。
5. **静态缓冲池**：srsRAN 使用 `byte_buffer_pool` —— 池管理缓冲区上的 RESOURCE_LEAK 发现项通常是误报。
