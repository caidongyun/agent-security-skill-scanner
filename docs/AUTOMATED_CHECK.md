# 🔍 自动化 Benchmark 检查

## 📋 概述

v6.1.9+ 提供自动化 Benchmark 检查功能，定期验证扫描器质量和检出率。

---

## 🚀 快速开始

### 手动执行

```bash
# 快速检查 (malicious-new 样本集)
./scripts/auto_benchmark_check.sh quick

# 全量检查 (from-templates 样本集)
./scripts/auto_benchmark_check.sh full
```

### 自动执行 (Cron)

已配置定时任务：
- **每天 09:00** - 快速检查
- **每周日 10:00** - 全量检查

查看 Cron 任务：
```bash
crontab -l | grep benchmark
```

---

## 📊 检查内容

### 1. 检出率验证
- 快速检查：malicious-new 样本集 (560 样本)
- 全量检查：from-templates 样本集 (130,832 样本)

### 2. 质量指标
| 指标 | 阈值 | 说明 |
|------|------|------|
| 检出率 | ≥5% | 过低说明规则库不足 |
| CRITICAL | 0 | 发现 CRITICAL 样本需要审查 |
| 扫描速度 | ≥1000 it/s | 性能退化检测 |

### 3. 误报检测
- CONFIG-MALICIOUS 误报回归测试
- 白名单验证

---

## 📁 输出文件

### 原始数据
```
/home/cdy/Desktop/security-benchmark/BENCHMARK_AUTO_YYYYMMDD_HHMMSS.json
```

### 测试报告
```
/home/cdy/.openclaw/workspace/skill-detect-report/BENCHMARK_AUTO_YYYY-MM-DD.md
```

### 日志
```
/tmp/benchmark_auto.log
```

---

## 🔔 告警通知

### 触发条件
1. 检出率 < 5%
2. 发现 CRITICAL 样本
3. 扫描速度 < 1000 it/s
4. 误报率 > 1%

### 通知方式 (待配置)
- [ ] 飞书 Webhook
- [ ] 邮件通知
- [ ] Telegram Bot

---

## 📈 历史报告

所有自动化检查报告自动同步到 Gitee：
https://gitee.com/caidongyun/skill-detect-report

报告命名：`BENCHMARK_AUTO_YYYY-MM-DD.md`

---

## 🔧 配置选项

### 脚本配置
```bash
# scripts/auto_benchmark_check.sh

# 配置路径
SCANNER_DIR="/home/cdy/.openclaw/workspace/agent-security-skill-scanner-master"
BENCHMARK_DIR="/home/cdy/Desktop/security-benchmark/samples"
OUTPUT_DIR="/home/cdy/Desktop/security-benchmark"
REPORT_DIR="/home/cdy/.openclaw/workspace/skill-detect-report"

# 质量阈值
MIN_DETECTION_RATE=5  # 最低检出率 (%)
MAX_CRITICAL=0        # 最大 CRITICAL 样本数
MIN_SPEED=1000        # 最低扫描速度 (it/s)
```

### Cron 配置
```bash
# 编辑 Cron 任务
crontab -e

# 快速检查 (每天 09:00)
0 9 * * * /path/to/auto_benchmark_check.sh quick

# 全量检查 (每周日 10:00)
0 10 * * 0 /path/to/auto_benchmark_check.sh full

# 禁用任务 (在行首添加 #)
# 0 9 * * * /path/to/auto_benchmark_check.sh quick
```

---

## 🎯 最佳实践

### 1. 定期审查报告
- 每周查看自动化检查报告
- 关注检出率趋势
- 分析新增 CRITICAL 样本

### 2. 规则库更新后
- 手动执行快速检查验证
- 对比历史检出率
- 确保无退化

### 3. 性能优化
- 监控扫描速度趋势
- 发现退化及时优化
- 调整 workers 数量

---

## 📊 示例报告

```markdown
# 自动化 Benchmark 检查报告

**日期**: 2026-04-21  
**模式**: quick  
**时间**: 17:45:30

---

## 📊 测试结果

| 指标 | 值 |
|------|-----|
| 总样本 | 560 |
| 检出 | 558 |
| 检出率 | 99.64% |
| HIGH | 558 |
| CRITICAL | 0 |
| SAFE | 2 |

---

## ✅ 质量检查

**状态**: 通过 ✅

---

## 📁 输出文件

- 原始数据：`/home/cdy/Desktop/security-benchmark/BENCHMARK_AUTO_20260421_174530.json`
- 本报告：`/home/cdy/.openclaw/workspace/skill-detect-report/BENCHMARK_AUTO_2026-04-21.md`
```

---

## 🐛 故障排除

### 问题 1: Cron 任务未执行
```bash
# 检查 Cron 服务状态
systemctl status cron

# 查看 Cron 日志
grep CRON /var/log/syslog | tail -20

# 手动执行测试
./scripts/auto_benchmark_check.sh quick
```

### 问题 2: 推送 Gitee 失败
```bash
# 检查 Git 配置
cd /home/cdy/.openclaw/workspace/skill-detect-report
git remote -v

# 手动推送
git add BENCHMARK_AUTO_*.md
git commit -m "auto: 添加自动化检查报告"
git push origin main
```

### 问题 3: 检出率异常
```bash
# 查看原始数据
python3 -c "
import json
with open('/tmp/latest_benchmark.json') as f:
    data = json.load(f)
print(json.dumps(data.get('summary', {}), indent=2))
"

# 对比历史报告
cd /home/cdy/.openclaw/workspace/skill-detect-report
ls -la BENCHMARK_AUTO_*.md | tail -10
```

---

*最后更新：2026-04-21 (v6.1.9)*
