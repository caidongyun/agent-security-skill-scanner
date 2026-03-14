# Skill Security Scanner

> 技能安全扫描器 - 检测恶意技能、后门代码、权限滥用

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/openclaw/openclaw/releases)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-8%20passed-green.svg)](tests/)

---

## 快速开始

### 安装

```bash
./install.sh
```

### 使用

```bash
# 扫描单个技能
python cli.py scan skills/suspicious-skill/

# 批量扫描
python cli.py scan-all skills/

# 生成报告
python cli.py report --format json --output report.json
```

---

## 功能特性

- ✅ 恶意代码检测 (eval/exec/system)
- ✅ 后门模式识别
- ✅ 权限审查
- ✅ IOC 检测 (IP/域名/Hash)
- ✅ 威胁情报集成
- ✅ 漏洞探索
- ✅ 趋势分析

---

## 情报探索

### 威胁情报收集

```python
from intelligence import ThreatCollector

collector = ThreatCollector()
threats = collector.collect()
print(f"发现 {len(threats)} 个威胁")
```

### 漏洞探索

```python
from intelligence import VulnExplorer

explorer = VulnExplorer()
vulns = explorer.explore("openclaw")
for vuln in vulns:
    print(f"{vuln['id']}: {vuln['title']}")
```

---

## 测试

```bash
python -m unittest discover -v tests/
```

---

*版本：v1.0.0 | 2026-03-12*
