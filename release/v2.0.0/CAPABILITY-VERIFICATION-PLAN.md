# 扫描器 v2.0.0 能力验证方案

> **创建日期**: 2026-03-13  
> **版本**: v2.0.0  
> **目的**: 系统验证待发布扫描器的各项能力

---

## 🎯 验证目标

验证 **v2.0.0 扫描器** 的核心能力：
1. ✅ 恶意代码检出能力
2. ✅ 误报率控制
3. ✅ 性能表现
4. ✅ 并发扫描能力
5. ✅ 稳定性

---

## 📊 测试样本集

| 样本集 | 位置 | 文件数 | 用途 |
|--------|------|--------|------|
| **恶意技能** | `scripts/samples/standard_malicious_skills/` | ~600 | 检出率测试 |
| **真实技能** | `scripts/samples/real_skills/` | 63 | 误报测试 |
| **代码安全** | `scripts/samples/code_security/` | ~500 | 分类测试 |
| **测试样本** | `tests/samples/` | 3,200 | 性能测试 |
| **全量样本** | `scripts/samples/` | 229,529 | 压力测试 |

---

## 🧪 测试用例

### 测试 1: 恶意代码检出能力

**目标**: 验证恶意代码检出率

**命令**:
```bash
python3 release/v2.0.0/scanner_cli.py scan \
  scripts/samples/standard_malicious_skills/ \
  --threads 8 \
  --output test-results/malicious-detection.json
```

**预期结果**:
- 检出率 >95%
- 严重/高危问题占比 >80%

**通过标准**:
- ✅ 检出率 ≥95%
- ✅ 无漏报关键恶意代码

---

### 测试 2: 误报率测试

**目标**: 验证真实技能无误报

**命令**:
```bash
python3 release/v2.0.0/scanner_cli.py scan \
  scripts/samples/real_skills/ \
  --threads 8 \
  --output test-results/false-positive-test.json
```

**预期结果**:
- 误报率 <1%
- 严重/高危误报 = 0

**通过标准**:
- ✅ 误报率 <1%
- ✅ 无严重/高危误报

---

### 测试 3: 代码安全测试

**目标**: 验证各类漏洞检出能力

**命令**:
```bash
python3 release/v2.0.0/scanner_cli.py scan \
  scripts/samples/code_security/ \
  --threads 8 \
  --output test-results/code-security-test.json
```

**预期结果**:
- 各类漏洞正确分类
- 严重程度准确

**通过标准**:
- ✅ 分类准确率 >90%
- ✅ 严重程度准确

---

### 测试 4: 并发性能测试

**目标**: 验证多线程性能

**命令**:
```bash
# 4 线程
python3 release/v2.0.0/scanner_cli.py scan tests/samples/ --threads 4

# 8 线程
python3 release/v2.0.0/scanner_cli.py scan tests/samples/ --threads 8

# 16 线程
python3 release/v2.0.0/scanner_cli.py scan tests/samples/ --threads 16
```

**预期结果**:
- 4 线程：>2,000 文件/秒
- 8 线程：>4,000 文件/秒
- 16 线程：>6,000 文件/秒

**通过标准**:
- ✅ 线性扩展比 >70%
- ✅ 最高速度 >5,000 文件/秒

---

### 测试 5: 压力测试

**目标**: 验证大样本量稳定性

**命令**:
```bash
python3 release/v2.0.0/scanner_cli.py scan \
  scripts/samples/ \
  --threads 16 \
  --output test-results/full-stress-test.json
```

**预期结果**:
- 无崩溃
- 内存占用 <1GB
- 速度稳定

**通过标准**:
- ✅ 完成扫描
- ✅ 无崩溃
- ✅ 速度 >5,000 文件/秒

---

## 📈 能力评估矩阵

| 能力 | 权重 | 目标值 | 测试方法 |
|------|------|--------|----------|
| **检出率** | 30% | >95% | 恶意样本测试 |
| **准确率** | 25% | >99% | 真实技能测试 |
| **性能** | 20% | >5,000 文件/秒 | 性能测试 |
| **并发** | 15% | 线性扩展 | 多线程测试 |
| **稳定性** | 10% | 无崩溃 | 压力测试 |

**总分**: ≥90 分即可发布

---

## 🚀 快速执行

### 一键测试

```bash
cd /home/cdy/.openclaw/workspace/skills/agent-security-skill-scanner/
./release/v2.0.0/run-capability-tests.sh
```

### 查看结果

```bash
# 查看测试结果
ls -lh release/v2.0.0/test-results/

# 查看测试报告
cat release/v2.0.0/test-results/CAPABILITY-TEST-REPORT.md
```

---

## 📝 测试报告

测试完成后自动生成：
- `test-results/malicious-detection.json` - 恶意检出结果
- `test-results/false-positive-test.json` - 误报测试结果
- `test-results/code-security-test.json` - 代码安全结果
- `test-results/perf-4threads.json` - 4 线程性能
- `test-results/perf-8threads.json` - 8 线程性能
- `test-results/perf-16threads.json` - 16 线程性能
- `test-results/full-stress-test.json` - 压力测试
- `test-results/CAPABILITY-TEST-REPORT.md` - 综合报告

---

## ✅ 发布决策

### 通过标准

| 指标 | 通过 | 警告 | 失败 |
|------|------|------|------|
| 检出率 | ≥95% | 90-95% | <90% |
| 误报率 | <1% | 1-3% | >3% |
| 性能 | >5,000 | 3,000-5,000 | <3,000 |
| 稳定性 | 无崩溃 | 偶发错误 | 频繁崩溃 |

### 决策规则

- **全部通过** → ✅ 批准发布
- **1-2 个警告** → ⚠️ 有条件发布
- **≥3 个警告或 1 个失败** → ❌ 不发布

---

*方案创建：2026-03-13*  
*维护人：Security Team*
