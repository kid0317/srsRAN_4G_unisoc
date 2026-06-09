---
name: srsran-security
description: >
  涉及 C/C++ 电信代码的安全审查、漏洞分析、CVE 检查、缓冲区溢出、
  整数溢出、竞态条件、密钥管理、协议 fuzzing、MISRA 合规或攻击面
  分析时，必须调用。不要跳过。
  (security review, buffer/integer overflow, race condition, key management,
  protocol fuzzing, MISRA compliance, attack surface)
---

# srsRAN 安全知识库

## 1. 缓冲区安全

CWE：CWE-120（缓冲区拷贝）、CWE-121（栈溢出）、CWE-122（堆溢出）

srsRAN 中的常见模式：
- 用固定的 uint8_t buf[1024] 打包变长 RRC/NAS 消息
- 不做长度检查的 memcpy
- ASN.1 解码输出到固定缓冲区

高风险位置：
- lib/src/asn1/rrc_nr.cc —— RRC 消息打包存在缓冲区溢出风险
- lib/src/common/mac_pcap.cc —— PCAP 写入缓冲区
- lib/src/phy/phch/ —— 物理信道比特缓冲区

检测：grep -rn uint8_t.*\[ lib/src/ | grep -v test
修复：使用 srsran::byte_buffer，检查 bref.distance()，使用 std::array

## 2. 整数安全

CWE：CWE-190（整数溢出）、CWE-191（下溢）、CWE-682（计算错误）

常见模式：n >= 32 时的 1 << n 移位、uint32_t 乘法溢出、有符号/无符号混用
高风险：lib/src/phy/common/phy_common.c、lib/src/phy/fec/turbo/
检测：grep -rn <<\|>> lib/src/phy/
修复：移位前做边界检查、__builtin_mul_overflow、显式类型转换

## 3. 竞态条件

CWE：CWE-362（竞态条件）、CWE-367（TOCTOU）

常见模式：eNB 多线程在无锁情况下共享 UE 上下文
高风险：srsenb/src/stack/mac/scheduler.cc、srsenb/src/stack/rrc/rrc.cc
检测：grep -rn std::mutex srsenb/src/
修复：std::lock_guard，对 UE 上下文使用读写锁

## 4. 密钥管理

CWE：CWE-798（硬编码凭证）、CWE-321（硬编码加密密钥）

常见模式：测试代码中硬编码 IMSI/Ki、mbedTLS 密钥未安全擦除
高风险：srsepc/src/hss/hss.cc、lib/src/common/security.cc
检测：grep -rni imsi\|ki\|opc --include=*.cc
修复：用 memset_s 擦除密钥，文件权限设为 600

## 5. 协议安全

CWE：CWE-20（输入校验不当）

常见模式：不做长度检查的畸形 RRC/NAS、未校验 ASN.1 IE 数量
高风险：lib/src/asn1/、srsenb/src/stack/s1ap/s1ap.cc
检测：grep -rn unpack\|decode lib/src/asn1/
修复：检查 decode 返回值，校验消息长度

## 6. 注入防护

CWE：CWE-78（OS 命令注入）、CWE-89（SQL 注入）

常见模式：用用户输入调用 system()、日志中含未转义的数据
高风险：srsepc/src/mme/、配置文件路径处理
检测：grep -rn system\|popen srsenb/src/ srsepc/src/
修复：禁用 system()，使用 std::filesystem::path，用 %s 格式化日志参数
