# 扫描检测报告

**生成时间**: 2026-03-25T18:23:42.256788

## 📊 汇总

- 总样本数：10
- 检出数：0
- 漏检数：10
- **检测率**: 0.0%
- 误报率：0.0%

## 🎯 质量评估

❌ **需改进**: 检测率 <80%

## 🔍 详细结果

| 文件 | 状态 | 匹配规则 | 耗时 (ms) |
|------|------|----------|-----------|

### ❌ 漏检样本

| normal_script_08.py | ❌ | - | 0.0 |
| | | `name 'time' is not defined` | |
| normal_script_05.py | ❌ | - | 0.0 |
| | | `name 'time' is not defined` | |
| normal_script_09.py | ❌ | - | 0.0 |
| | | `name 'time' is not defined` | |
| normal_script_07.py | ❌ | - | 0.0 |
| | | `name 'time' is not defined` | |
| normal_script_10.py | ❌ | - | 0.0 |
| | | `name 'time' is not defined` | |
| normal_script_01.py | ❌ | - | 0.0 |
| | | `name 'time' is not defined` | |
| normal_script_04.py | ❌ | - | 0.0 |
| | | `name 'time' is not defined` | |
| normal_script_02.py | ❌ | - | 0.0 |
| | | `name 'time' is not defined` | |
| normal_script_06.py | ❌ | - | 0.0 |
| | | `name 'time' is not defined` | |
| normal_script_03.py | ❌ | - | 0.0 |
| | | `name 'time' is not defined` | |

## 💡 建议

1. 增加 YARA 规则覆盖范围
2. 优化现有规则的模式匹配
3. 分析漏检样本特征，添加针对性规则
