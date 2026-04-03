# 行业常见易误报样本集

**创建日期**: 2026-04-01  
**用途**: 测试安全扫描器的误报率  
**样本数**: 8 个  

## 📋 样本列表

| 文件名 | 场景 | 易误报点 |
|--------|------|----------|
| `devops_deploy.py` | DevOps/K8s 部署 | subprocess, base64, kubectl, rm -rf |
| `security_scanner.py` | 安全扫描工具 | nmap, socket, eval, requests |
| `system_monitor.py` | 系统监控 | subprocess, base64, rm -rf, SSH |
| `crypto_utils.py` | 加密工具库 | base64, hashlib, cryptography |
| `cicd_pipeline.py` | CI/CD 流水线 | git, docker, AWS credentials, SSH |
| `network_tools.py` | 网络工具 | socket, ping, traceroute, DNS |
| `db_admin.py` | 数据库管理 | mysqldump, psql, 密码操作 |
| `log_analyzer.py` | 日志分析 | grep, regex, SIEM 集成 |

## 🎯 测试目的

1. **DevOps 场景** - 部署脚本中的敏感操作（kubectl, docker, SSH）
2. **安全工具** - 扫描器/渗透测试工具的合法使用
3. **系统管理** - 运维脚本中的命令执行
4. **加密操作** - 合法的加解密函数
5. **CI/CD** - 自动化流水线中的凭证使用
6. **网络管理** - 网络诊断和管理工具
7. **数据库** - DBA 日常运维操作
8. **日志分析** - SIEM/日志处理系统

## 📊 测试结果

### 初始测试（优化前）

| 样本 | 误报规则数 | 主要误报规则 |
|------|-----------|-------------|
| devops_deploy.py | 1 | Malicious_Credential_Theft |
| security_scanner.py | 6 | Remote_Code_Execution, Shell_ReverseShell |
| system_monitor.py | 4 | Data_Exfiltration, Credential_Theft |
| crypto_utils.py | 1 | Credential_Theft |
| cicd_pipeline.py | 5 | Data_Exfiltration, EnvVarTheft |
| network_tools.py | 4 | Socket_Exfil, ReverseShell |
| db_admin.py | 5 | Remote_Code_Execution, Eval |
| log_analyzer.py | 6 | Code_Injection, Data_Exfil |

### 优化方向

1. **上下文检测** - 单一关键词不报警，需要组合模式
2. **意图识别** - 区分合法运维 vs 恶意操作
3. **白名单机制** - 常见工具命令（kubectl, docker, git）
4. **凭证使用场景** - 区分读取 vs 窃取 vs 正常使用

## 📁 样本位置

```
/home/cdy/Desktop/security-benchmark/samples/industry_false_prone/
```

## 🔧 使用方法

```bash
cd /home/cdy/.openclaw/workspace/agent-security-skill-scanner-master
./scanner-master/scan /path/to/industry_false_prone/ full
```
