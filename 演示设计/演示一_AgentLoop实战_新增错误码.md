# 演示一：Agent Loop 实战 —— 新增错误码指令

**对应正文**：第二课 §2.1 – §2.4（Agent Loop 的启动 → 实测 25 轮过程）
**预计时长**：5–8 分钟（含讲解）
**所在模块**：第一小节「发出一条消息后，到底发生了什么」

---

## 一、演示目标

让学员亲眼看到：一条指令发出后，Claude Code 在 Agent Loop 中经历"思考→行动→观察"循环，并最终完成跨文件代码修改。

**核心教学点**：
1. Agent 不是"接到指令就改"——前 5 轮全在阅读理解
2. Agent Loop 是循环而非线性——一条指令可能自动跑 25 轮
3. Agent 会自主分析调用链决定"不改也是正确决策"

---

## 二、前置准备

### 2.1 环境要求

| 项目 | 要求 |
|------|------|
| 代码库 | `/root/course/code/ziguangzhanrui_2/srsRAN_4G`（干净 clone，无未提交修改） |
| 构建依赖 | GCC/G++、CMake 3.5+（构建验证需要） |
| Langfuse | 可选，如需演示二衔接则需提前配置 |
| 网络 | 需要访问 Claude API |

### 2.2 预编译（可选，减少等待）

```bash
cd /root/course/code/ziguangzhanrui_2/srsRAN_4G
mkdir -p build && cd build
cmake -DCMAKE_BUILD_TYPE=Debug -DCMAKE_EXPORT_COMPILE_COMMANDS=ON ..
make -j$(nproc)
```

### 2.3 代码库状态确认

演示前确认 config.h 错误码状态正常：

```bash
grep 'SRSRAN_ERROR' lib/include/srsran/config.h
```

预期输出 8 个宏定义（-1 到 -8），无 -9。

### 2.4 Git 状态清洁

```bash
cd /root/course/code/ziguangzhanrui_2/srsRAN_4G
git status  # 确认无未提交修改
git stash   # 如有需先暂存
```

---

## 三、演示指令

### 精简版（推荐课堂使用）

```
srsRAN_4G 的 sync::radio_recv_fnc 在射频接收失败时返回通用的 SRSRAN_ERROR，请新增一个专用错误码 SRSRAN_ERROR_RADIO_RECV_FAIL 并让相关调用点正确处理它。
```

### 完整版（备选，如需更精准控制）

```
在 srsRAN_4G 的 PHY 层同步模块中，radio_recv_fnc 函数在射频接收失败时只返回通用错误码 SRSRAN_ERROR，无法区分是超时还是其他原因。请新增一个 SRSRAN_ERROR_RADIO_RECV_FAIL 错误码，并让 radio_recv_fnc 在接收失败时返回这个新错误码，同时更新 run_camping_state 的 switch 分支对这个新错误码做专门处理。
```

---

## 四、预期执行路径

### 核心 8 轮（课堂讲解用，简化自实测 25 轮）

| 轮次 | Claude 的思考 | 调用工具 | 观察结果 |
|------|-------------|---------|---------|
| 1 | "错误码定义在哪个文件？" | Grep `SRSRAN_ERROR` | 找到 `lib/include/srsran/config.h` |
| 2 | "看看现有错误码体系" | Read `config.h` | 8 个宏定义，-1 到 -8，下一个可用 -9 |
| 3 | "找到 radio_recv_fnc 的实现" | Grep `radio_recv_fnc` | 定位 `sync.cc` 第 981 行 |
| 4 | "看调用方怎么处理返回值" | Read `sync.cc` | `run_idle_state` 第670行用 `== SRSRAN_SUCCESS` 判断，不区分错误类型；`radio_recv_fnc` 还通过回调注册给 `ue_sync`，C 层用 `< 0` 判断 |
| 5 | "搜一下还有没有其他引用" | Grep 全局 | `search.cc` + `test/phy/` |
| 6 | "改头文件" | Edit `config.h` | `#define SRSRAN_ERROR_RADIO_RECV_FAIL -9` |
| 7 | "改实现文件" | Edit `sync.cc` | 替换返回值 + 更新 switch/日志 |
| 8 | "跑构建验证" | Bash `cmake --build` | 编译通过 |

### 实测关键数据（2026-05-28 headless 模式）

| 指标 | 数值 |
|------|------|
| Agent Loop 轮次 | 25 轮 |
| 总耗时 | 257 秒（~4.3 分钟） |
| Token 花费 | $0.58 |
| 缓存命中率 | 95%+ |
| 修改文件 | 2 个（config.h + sync.cc） |
| 代码变更 | +6 行 / -2 行 |
| 构建结果 | 通过 |

---

## 五、演示节奏（课堂）

| 时间点 | 讲师动作 | 讲解要点 |
|--------|---------|---------|
| 0:00 | 展示 config.h 错误码定义（PPT） | "8 个扁平宏定义，你们 Simba 里一眼就能认出来" |
| 0:30 | 粘贴指令，按回车 | "就一句话，大家猜它先做什么？" |
| 0:40 | CC 开始读 config.h | "它在理解错误码体系——**思考阶段**" |
| 1:00 | CC 搜索 radio_recv_fnc | "它在定位目标代码——**行动阶段**" |
| 1:30 | CC 读 sync.cc 上下文 | "追踪调用链——**观察+再思考**" |
| 2:00 | CC 搜索其他引用 | "注意：它**自己想到了**要检查影响范围" |
| 2:30 | CC 改 config.h | "终于动手了，先改定义" |
| 3:00 | CC 改 sync.cc | "替换返回值+加了更详细的日志" |
| 3:30 | CC 跑构建 | "改完必须验证——这是 Agent 的自我校验" |
| 4:00 | CC 输出总结 | 展示关键数据卡片 |

---

## 六、关键讲解点

### 6.1 为什么前 5 轮不动手改代码

> "前 5 轮全在'阅读理解'，只有后 3 轮才动手。这跟优秀工程师的工作方式一模一样——先搞清楚上下文，再动手。"

**课程原则映射**：Agent Loop 的"思考→行动→观察"循环（正文 §2.3）

### 6.2 为什么只改了 2 个文件而非 3 个

> "AI 分析了 ue_sync.c 的调用链，发现里面用的是 `< 0` 判断——-9 天然被覆盖，不需要改。**不改，反而是正确的决策。**"

**课程原则映射**：Agent 会自主分析调用链做出"不改"的判断（正文 §2.4）

### 6.3 为什么 25 轮而不是 8 轮

> "真实工程任务比理想路径复杂——AI 做了大量确认性阅读。它还读了 CMakeLists.txt、确认 C 层兼容性、尝试构建验证。"

---

## 七、预期代码变更

### config.h

```diff
 #define SRSRAN_ERROR_RX_EOF            -8
+#define SRSRAN_ERROR_RADIO_RECV_FAIL   -9
```

### sync.cc（两处）

**返回值细化**：
```diff
   if (not radio_h->rx_now(data, rf_timestamp)) {
-    return SRSRAN_ERROR;
+    return SRSRAN_ERROR_RADIO_RECV_FAIL;
   }
```

**调用方处理**：
```diff
     dummy_buffer.set_nof_samples(nsamples);
-    if (radio_recv_fnc(dummy_buffer, &rx_time) == SRSRAN_SUCCESS) {
+    int ret = radio_recv_fnc(dummy_buffer, &rx_time);
+    if (ret == SRSRAN_ERROR_RADIO_RECV_FAIL) {
+      Warning("SYNC:  Radio receive failed while in IDLE_RX");
+    } else if (ret >= SRSRAN_SUCCESS) {
       srsran::console("SYNC:  Receiving from radio while in IDLE_RX\n");
     }
```

---

## 八、失败预案

| 风险 | 概率 | 应对 |
|------|------|------|
| CC 执行时间过长（>5min） | 中 | 切换到提前跑好的 headless 模式录屏/截图 |
| CC 改了不同的文件 | 低 | 用 PPT 展示实测结果，说明"AI 每次执行路径可能略有不同" |
| CC 改了更多文件（3-4个） | 中 | 说明"AI 比预期更保守/更激进都正常，关键是构建通过+逻辑正确" |
| 构建失败 | 低 | 说明"这就是为什么需要 Stop Hook 做门禁"，衔接第五小节 |
| API 超时/网络问题 | 低 | 切换到 PPT 讲解实测数据 + Langfuse 截图 |

---

## 九、演示后恢复

```bash
cd /root/course/code/ziguangzhanrui_2/srsRAN_4G
git checkout -- .     # 恢复所有修改
git clean -fd         # 清理新增文件
```

---

## 十、与课程原则的对应关系

| 课程概念 | 本演示如何体现 |
|---------|-------------|
| Agent Loop 六步循环（§2.3） | 学员亲眼看到 CC 在循环中思考→行动→观察 |
| ReAct 范式（§2.6） | 一条指令自动跑 25 轮，不是一问一答 |
| 基础工具组合（§2.3） | 只用 Read/Edit/Grep/Bash 完成所有工作 |
| Bootstrap + Context（§2.2） | CC 启动时先拼装上下文再开始循环 |
| "改完必须验证"（§2.4） | 最后一轮跑 cmake --build 做自我校验 |
