#!/bin/bash
# 质量门禁自动化脚本 - 每轮生成后自动执行

set -e

LANGUAGE=${1:-python}
COUNT=${2:-50}
ROUND=${3:-round1}

echo "============================================"
echo "质量门禁系统 v2.0"
echo "============================================"
echo "语言：$LANGUAGE"
echo "数量：$COUNT"
echo "轮次：$ROUND"
echo ""

# Gate 1: 样本生成 + 质量检查
echo "🚪 Gate 1: 样本质量检查"
echo "--------------------------------------------"

echo "[1/4] 生成样本..."
python3 -m generators.cli --language $LANGUAGE --count $COUNT --output output/samples/$LANGUAGE 2>&1 | tail -5

echo "[2/4] 样本质量检查..."
python3 quality_gate/gatekeeper.py \
    --samples output/samples/$LANGUAGE \
    --output reports/${ROUND}_quality_$LANGUAGE.json

# 检查通过率
PASS_RATE=$(python3 -c "
import json
try:
    with open('reports/${ROUND}_quality_$LANGUAGE.json') as f:
        data = json.load(f)
        rate = data.get('pass_rate', 0) * 100
        print('{:.1f}'.format(rate))
except:
    print('0.0')
")

echo "  通过率：${PASS_RATE}%"

if (( $(echo "$PASS_RATE >= 80" | bc -l) )); then
    echo "  ✅ Gate 1 通过 (≥80%)"
else
    echo "  ❌ Gate 1 失败 (<80%)"
    echo "  请检查报告：reports/${ROUND}_quality_$LANGUAGE.json"
    exit 1
fi

echo ""

# Gate 2: 规则生成 + 质量检查
echo "🚪 Gate 2: 规则质量检查"
echo "--------------------------------------------"

echo "[3/4] 生成规则..."
python3 rules/generator.py --samples output/samples/$LANGUAGE --output output/rules 2>&1 | tail -5

echo "[4/4] 规则质量检查..."
python3 quality_gate/gatekeeper.py \
    --rules output/rules \
    --output reports/${ROUND}_quality_rules_$LANGUAGE.json

# 检查规则通过率
RULE_PASS_RATE=$(python3 -c "
import json
try:
    with open('reports/${ROUND}_quality_rules_$LANGUAGE.json') as f:
        data = json.load(f)
        rate = data.get('pass_rate', 0) * 100
        print('{:.1f}'.format(rate))
except:
    print('0.0')
")

echo "  通过率：${RULE_PASS_RATE}%"

if (( $(echo "$RULE_PASS_RATE >= 90" | bc -l) )); then
    echo "  ✅ Gate 2 通过 (≥90%)"
else
    echo "  ❌ Gate 2 失败 (<90%)"
    echo "  请检查报告：reports/${ROUND}_quality_rules_$LANGUAGE.json"
    exit 1
fi

echo ""

# Gate 3: 扫描验证
echo "🚪 Gate 3: 扫描验证"
echo "--------------------------------------------"

echo "[5/5] 扫描验证..."
python3 scanner/integration_scanner.py \
    --rules output/rules \
    --samples output/samples/$LANGUAGE \
    --output reports/${ROUND}_scan_$LANGUAGE 2>&1 | tail -10

# 检查检测率
DETECTION_RATE=$(python3 -c "
import json
try:
    with open('reports/${ROUND}_scan_$LANGUAGE.json') as f:
        data = json.load(f)
        rate = data.get('detection_rate', 0)
        print('{:.1f}'.format(rate))
except:
    print('0.0')
")

echo "  检测率：${DETECTION_RATE}%"

if (( $(echo "$DETECTION_RATE >= 95" | bc -l) )); then
    echo "  ✅ Gate 3 通过 (≥95%)"
else
    echo "  ⚠️  Gate 3 警告 (<95%)"
    echo "  建议优化规则"
fi

echo ""
echo "============================================"
echo "质量门禁完成!"
echo "============================================"
echo ""
echo "📊 汇总:"
echo "  样本通过率：${PASS_RATE}% (目标：≥80%)"
echo "  规则通过率：${RULE_PASS_RATE}% (目标：≥90%)"
echo "  扫描检测率：${DETECTION_RATE}% (目标：≥95%)"
echo ""

# 生成反思报告
echo "📝 生成反思报告..."
python3 << EOF
import json
from datetime import datetime

# 读取数据
try:
    with open('reports/${ROUND}_quality_$LANGUAGE.json') as f:
        sample_data = json.load(f)
except:
    sample_data = {}

try:
    with open('reports/${ROUND}_quality_rules_$LANGUAGE.json') as f:
        rule_data = json.load(f)
except:
    rule_data = {}

try:
    with open('reports/${ROUND}_scan_$LANGUAGE.json') as f:
        scan_data = json.load(f)
except:
    scan_data = {}

# 生成反思报告
report = f"""# 反思报告 - {${LANGUAGE}}

**日期**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
**轮次**: ${ROUND}
**语言**: ${LANGUAGE}

## 质量指标

| 指标 | 目标 | 实际 | 状态 |
|------|------|------|------|
| 样本通过率 | ≥80% | {${PASS_RATE}}% | {'✅' if float(${PASS_RATE}) >= 80 else '❌'} |
| 规则通过率 | ≥90% | {${RULE_PASS_RATE}}% | {'✅' if float(${RULE_PASS_RATE}) >= 90 else '❌'} |
| 扫描检测率 | ≥95% | {${DETECTION_RATE}}% | {'✅' if float(${DETECTION_RATE}) >= 95 else '⚠️'} |

## 样本统计

- 生成数量：{sample_data.get('total_checked', 0)}
- 通过数量：{sample_data.get('passed', 0)}
- 失败数量：{sample_data.get('failed', 0)}
- 待审查：{sample_data.get('review', 0)}

## 规则统计

- 生成数量：{rule_data.get('total_checked', 0)}
- 通过数量：{rule_data.get('passed', 0)}
- 失败数量：{rule_data.get('failed', 0)}

## 扫描统计

- 总样本：{scan_data.get('total', 0)}
- 检出：{scan_data.get('detected', 0)}
- 漏检：{scan_data.get('missed', 0)}
- 检测率：{scan_data.get('detection_rate', 0)}%

## 发现的问题

1. ...

## 改进建议

1. ...

## 下一步行动

1. ...
"""

with open('reports/${ROUND}_reflection_$LANGUAGE.md', 'w') as f:
    f.write(report)

print("  反思报告已保存：reports/${ROUND}_reflection_$LANGUAGE.md")
EOF

echo ""
echo "✅ 质量门禁全部完成！"
