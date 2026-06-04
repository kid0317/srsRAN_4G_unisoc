# 演示三：CLAUDE.md Live Demo —— 为 srsRAN_4G 写四层 CLAUDE.md

**对应正文**：第二课 §3.5（实战演示：为 srsRAN_4G 写 CLAUDE.md）
**预计时长**：5–8 分钟
**所在模块**：第二小节「Context 管理——决定 AI 能力上限的关键」
**前置依赖**：已讲完 §3.3 四层加载优先级 + §3.4 四条编写原则

---

## 一、演示目标

现场从零撰写 srsRAN_4G 的项目级 CLAUDE.md，并展示四层完整示例，让学员掌握"写什么、不写什么、怎么组织"的实操能力。

**核心教学点**：
1. CLAUDE.md 的每一行都有"房租"——Less is More
2. 项目级 ~40 行就够——关键是模块结构表 + Skill 路由
3. 四层各有分工：企业级=铁律、用户级=偏好、项目级=共识、本地级=便签

---

## 二、前置准备

### 2.1 srsRAN_4G 项目目录

```
/root/course/code/ziguangzhanrui_2/srsRAN_4G/
```

确认目录下**没有**已有的 CLAUDE.md（或提前备份）：
```bash
ls /root/course/code/ziguangzhanrui_2/srsRAN_4G/CLAUDE.md 2>/dev/null || echo "OK: 无已有文件"
```

### 2.2 PPT 准备

需要 4 张 PPT（或 4 个代码块）分别展示四层 CLAUDE.md 的完整内容：
- Slide A：企业级 `/etc/claude-code/CLAUDE.md`
- Slide B：用户级 `~/.claude/CLAUDE.md`
- Slide C：项目级 `./CLAUDE.md`（现场编写这一层）
- Slide D：本地级 `./CLAUDE.local.md`

---

## 三、演示流程

### Step 1：引入（30s）

**讲述**：
> "光说不练假把式。我们现场来写一个。"

### Step 2：展示并讲解项目级 CLAUDE.md（3min）

**推荐方式**：打开预写好的文件，逐段展示并讲解（比从零敲更紧凑）。
**增强方式**：如果时间充裕，可在编辑器中从零编写。

预写文件内容：

```markdown
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

## 构建命令

cmake .. -DCMAKE_BUILD_TYPE=Debug -DENABLE_WERROR=ON && make -j$(nproc)
ctest --output-on-failure

## Skill 路由

| 场景 | 指向 |
|------|------|
| PHY 层同步问题 | → .claude/skills/phy-sync.md |
| 错误码扩展 | → .claude/skills/error-codes.md |
| 3GPP 规范映射 | → .claude/skills/3gpp-mapping.md |
```

**边写边讲解**：
- "模块结构表让 AI 一眼知道代码在哪里，不需要每次从头探索"
- "Skill 路由表是重点——详细步骤不在 CLAUDE.md 里写死，指向 Skill 文件"
- "注意，项目级也就 40 行。**关键不是写得多，而是每一行都是 AI 必须知道的。**"

### Step 3：展示四层完整示例（3min）

按加载优先级从低到高，PPT 逐层展示：

**第一层：企业级**（安全铁律）
```markdown
## 安全红线（违反即阻断 CR）
- 禁止使用 gets()/sprintf()/strcpy() → 用 fgets/snprintf/strncpy
- 禁止裸 new/malloc → 使用 RAII 或团队封装的内存池
- 密钥、IMSI/Ki 不得出现在代码或注释中
```

> "企业级是 IT 统一下发的铁律——即使项目层怎么写也不能违反。对你们来说，这里放 MISRA C/C++ 标准、Coverity 规则集。"

**第二层：用户级**（个人偏好）
```markdown
- 所有对话使用中文，commit message 用英文
- 改动超过 3 个文件时，先列出修改计划让我确认
- 遇到不确定的 3GPP 条款，标注 "VERIFY:" 让我人工确认
```

> "用户级是你的个人舒适区，跨项目都生效。"

**第三层：项目级**（团队共享）
> "就是我们刚才写的那 40 行——提交 git，团队共享。"

**第四层：本地级**（便签纸）
```markdown
## 当前任务
- JIRA: SIMBA-4521 — 为 radio_recv_fnc 新增专用错误码
- 分支: feature/radio-recv-error-code
- 交叉编译目标: aarch64-linux-gnu（Simba 平台）
```

> "本地级是便签纸——每天开工前花 30 秒更新当前任务，任务结束就清空。不入 git。"

### Step 4：弹幕互动（1min）

> "回忆一下你上周写的 CLAUDE.md，现在看觉得缺了什么？弹幕说说。"

---

## 四、关键讲解点

### 4.1 Less is More 原则

> "CLAUDE.md 的每一行都有房租——写进去就永远占着上下文空间。'请写高质量代码'——这种话 Claude 本来就知道，写了只会浪费 Token。"

**课程原则映射**：§3.4 原则一

### 4.2 模块结构表的价值

> "这张表让 AI 在 Agent Loop 第 1 轮就知道去 `config.h` 找错误码、去 `sync.cc` 找同步逻辑——不需要像我们刚才演示的那样花 5 轮去探索。Context 好 → 轮次少 → 效率高。"

**课程原则映射**：§3.1 "你写了什么，AI 就知道什么"

### 4.3 Skill 路由表

> "详细的操作步骤不在 CLAUDE.md 里写死，指向 Skill 文件。CLAUDE.md 保持轻量，AI 按需读取——这就是**渐进式披露**的思路。"

**课程原则映射**：§3.4 原则四

### 4.4 四层协作关系

> "企业级是铁律。用户级是个人舒适区。项目级是团队共识。本地级是便签纸。后面的覆盖前面的，但不能违反企业级的安全红线。"

**课程原则映射**：§3.3 四层加载优先级

---

## 五、演示后操作

如果是现场真实写入了文件：
```bash
# 保留 CLAUDE.md 供后续演示使用
cat /root/course/code/ziguangzhanrui_2/srsRAN_4G/CLAUDE.md
```

或者用 PPT 展示，不实际写入文件（避免影响后续演示）。

---

## 六、失败预案

| 风险 | 概率 | 应对 |
|------|------|------|
| 现场手写太慢 | 中 | 已将"打开预写文件"设为主推方案 |
| 演示三写入 CLAUDE.md 后影响其他演示 | 中 | 如需重跑演示一，先 `rm CLAUDE.md`；或演示三仅在 PPT 展示不写入文件 |
| 学员对模块结构不熟 | 低 | 类比展锐 Simba 的模块划分，说"你们的 PHY 层对应这里的 lib/src/phy/" |
| 弹幕冷场 | 中 | 自己举例"比如构建命令没写、Skill 路由没有" |

---

## 七、与课程原则的对应关系

| 课程概念 | 本演示如何体现 |
|---------|-------------|
| Less is More（§3.4） | 项目级只有 40 行，每行都是必要信息 |
| 具体优于泛泛（§3.4） | "错误码递减分配"而非"遵循最佳实践" |
| WHY/WHAT/HOW（§3.4） | 编码约定包含 what（格式）和 how（构建命令） |
| 渐进式披露（§3.4） | Skill 路由表指向外部文件 |
| 四层优先级（§3.3） | 四层示例完整展示 |
| CLAUDE.md 在 Bootstrap 中的位置（§3.2） | 学员理解"这些内容每一轮循环都带着" |
