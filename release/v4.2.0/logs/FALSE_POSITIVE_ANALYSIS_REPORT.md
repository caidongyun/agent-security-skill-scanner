# 误报样本共性分析报告

**分析时间**: 2026-04-08T21:40:15.269763
**误报样本数**: 532

## 📊 Skill 名称共性

| 关键词 | 数量 | 占比 |
|--------|------|------|
| skill | 44 | 8.3% |
| agent | 38 | 7.1% |
| security | 12 | 2.3% |
| tool | 8 | 1.5% |
| audit | 4 | 0.8% |
| setup | 3 | 0.6% |
| dev | 3 | 0.6% |
| install | 1 | 0.2% |

## 📊 文件模式

- 包含 .sh 文件：187 个 (35.2%)
- 包含安装脚本：25 个 (4.7%)

## 🎯 优化方案

### 方案 1: 安装脚本白名单

```python
INSTALL_SCRIPTS = ['install.sh', 'setup.sh', 'init.sh']
if file_name in INSTALL_SCRIPTS:
    risk_score *= 0.5  # 降低 50%
```

### 方案 2: 安全审计类白名单

```python
if 'audit' in skill_name or 'security' in skill_name:
    risk_score *= 0.7  # 降低 30%
```

### 方案 3: 组合特征检测

```python
# curl|bash + 安装脚本 → 良性
if has_curl_bash and is_install_script:
    verdict = 'SUSPICIOUS'  # 降级
```

### 方案 4: 提高阈值

```python
# malicious_files >= 3 才判定为 MALICIOUS
if malicious_files >= 3:
    verdict = 'MALICIOUS'
elif malicious_files >= 1:
    verdict = 'SUSPICIOUS'
```

### 方案 5-7: AST + LLM + 领域感知

使用集成扫描器：`integrated_scanner.py`
