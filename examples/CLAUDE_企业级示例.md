# 企业级 CLAUDE.md 示例
# 路径：/etc/claude-code/CLAUDE.md
# 由 IT 统一下发，安全铁律，最低优先级但不可违反

## 安全红线（违反即阻断 CR）

- 禁止使用 gets()/sprintf()/strcpy() → 用 fgets/snprintf/strncpy
- 禁止裸 new/malloc → 使用 RAII 或团队封装的内存池
- 密钥、IMSI/Ki 不得出现在代码或注释中
- 所有函数入口必须校验指针参数非 NULL
- 禁止在中断上下文中使用动态内存分配

## 合规要求

- MISRA C:2012 强制规则必须遵守（Advisory 规则建议遵守）
- Coverity 扫描 Critical/High 级别告警必须在合入前清零
- ISO 26262 安全相关代码必须保留完整审计日志

## 代码提交规范

- commit message 必须用英文
- 每次提交必须关联 JIRA 工单号
- 禁止 force push 到 main/develop 分支
