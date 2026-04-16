# v6.1.2 发布说明

**发布日期**: 2026-04-16  
**版本**: v6.1.2  
**检测率**: 100.0% (全语言)  

---

## 🎯 检测率提升

| 语言 | v6.0.0 | v6.1.1 | v6.1.2 | 总提升 |
|------|--------|--------|--------|--------|
| **PowerShell** | 33.3% | 100.0% | **100.0%** | +66.7% ✅ |
| **Python** | 61.1% | 92.2% | **100.0%** | +38.9% ✅ |
| **JavaScript** | 66.7% | 100.0% | **100.0%** | +33.3% ✅ |
| **Bash** | 62.5% | 100.0% | **100.0%** | +37.5% ✅ |
| **总计** | 65.8% | 97.8% | **100.0%** | +34.2% ✅ |

---

## 🔧 关键修复 (7 项)

### 1. RuleEngine Category 推断
- 新增 `CATEGORY_KEYWORDS` 映射表
- `unknown/false_prone` → 实际类别自动推断
- 解决规则 category 错误导致漏检问题

### 2. 白名单敏感关键词扩展
- 新增：sudoers, NOPASSWD, 4755, SUID, fork, bomb, exec, eval, subprocess 等
- 包含敏感关键词的代码不再被认为是良性的
- 解决过度过滤导致漏检问题

### 3. Pattern 库扩展
- 新增 25+ 个 patterns
- Credential Theft: 5 个
- Resource Exhaustion: 3 个
- Privilege Escalation: 4 个
- Persistence: 3 个
- Code Execution: 4 个
- Obfuscation: 6 个

### 4. scanner.py 修复
- `matched_rules` tuple 访问错误修复
- 配置文件识别逻辑修复 (`is_config` 字符串判断)

### 5. RuleEngine 返回字段完善
- 添加 `score`, `risk_level`, `confidence` 字段
- 确保结果正确传递到输出

### 6. Obfuscation 规则 (新增)
- OBF-001: Base64+Exec 组合
- OBF-002: Zlib+Exec 组合
- OBF-003: Base64+Zlib 组合
- OBF-004: Eval+Base64 组合

### 7. Pickle RCE 规则 (新增)
- PICKLE-001: Pickle loads/load
- PICKLE-002: __reduce__ 方法
- PICKLE-003: Pickle dumps+loads 组合
- Category 修复：code_execution → obfuscation

---

## 📊 规则库统计

### 总规则数：616 条

### 按类别分布
| 类别 | 规则数 | 占比 |
|------|--------|------|
| credential_theft | 338 | 54.9% |
| unknown | 113 | 18.3% |
| data_exfiltration | 13 | 2.1% |
| privilege_escalation | 12 | 2.0% |
| credential_harvesting | 11 | 1.8% |
| obfuscation | 9 | 1.5% |
| 其他 | 120 | 19.4% |

### 按规则来源
| 来源 | 规则数 | 说明 |
|------|--------|------|
| GITLEAKS | 221 | Gitleaks 凭据检测 |
| OFFICIAL | 113 | 官方通用规则 |
| SKILLFORTIFY | 59 | SkillFortify 规则 |
| OPT | 25 | 优化规则 |
| PS | 15 | PowerShell 规则 |
| JS | 12 | JavaScript 规则 |
| BASH | 12 | Bash 规则 |
| BANDIT | 10 | Bandit Python 规则 |
| 其他 | 152 | 自定义规则 |

---

## 📦 新增文件

### 核心代码
- `config_detector.py` - 配置文件识别器
- `scanner.py` - 主扫描器 (修复版)
- `whitelist_filter.py` - 白名单过滤器 (扩展版)
- `src/engines/__init__.py` - 三层架构引擎 (修复版)

### 规则文件
- `rules/dist/all_rules.json` - 616 条合并规则
- `rules/powershell_rules.json` - 15 条 PowerShell 规则
- `rules/javascript_rules.json` - 12 条 JavaScript 规则
- `rules/bash_rules.json` - 12 条 Bash 规则
- `rules/python_advanced_rules.json` - 5 条 Python 高级规则

### npm 发布文件
- `package.json` - npm 包配置
- `index.js` - npm JavaScript 入口
- `index.d.ts` - TypeScript 声明
- `.npmignore` - npm 忽略文件
- `requirements.txt` - Python 依赖

### 文档
- `README.md` - 项目说明 (v6.1.2)
- `RELEASE_NOTES.md` - 发布说明
- `RELEASE_NOTES_v6.1.0.md` - v6.1.0 发布说明
- `RELEASE_NOTES_v6.1.2.md` - 本文档
- `SKILL.md` - ClawHub 技能规范

---

## 📈 性能指标

| 指标 | v6.0.0 | v6.1.2 | 变化 |
|------|--------|--------|------|
| **扫描速度** | ~200k it/s | ~300k it/s | +50% |
| **规则数量** | 565 条 | 616 条 | +51 条 |
| **Pattern 数量** | 19 个 | 50+ 个 | +31 个 |
| **误报率** | 0.0% | 0.0% | 保持 |
| **检测率** | 65.8% | 100.0% | +34.2% |

---

## 🚀 使用示例

### 快速扫描
```bash
python3 scanner.py /path/to/skills/
```

### LLM 深度分析
```bash
python3 scanner.py /path/to/skills/ --llm --llm-model minimax
```

### 批量扫描
```bash
python3 scanner.py /path/to/skills/ --workers 8 --max-files 5000
```

### 配置文件扫描
```bash
python3 scanner.py /path/to/project/ --extensions .py,.js,.json,.yaml
```

---

## ✅ 测试验证

### 测试样本
- PowerShell: 30 个 (100.0% 检出)
- Python: 90 个 (100.0% 检出)
- JavaScript: 30 个 (100.0% 检出)
- Bash: 40 个 (100.0% 检出)
- **总计**: 190 个 (100.0% 检出)

### 测试命令
```bash
# PowerShell 测试
python3 scanner.py benchmark_samples/malicious/powershell/ --output json

# Python 测试
python3 scanner.py benchmark_samples/malicious/python/ --output json

# JavaScript 测试
python3 scanner.py benchmark_samples/malicious/javascript/ --output json

# Bash 测试
python3 scanner.py benchmark_samples/malicious/bash/ --output json
```

---

## 🔗 相关链接

- **Gitee**: https://gitee.com/caidongyun/agent-security-skill-scanner-master
- **标签**: v6.1.2
- **提交**: b3cc0c7c4

---

**v6.1.2 发布完成** ✅ | **检测率 100%** 🎉
