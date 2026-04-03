#!/bin/bash
# 自动化持续优化脚本 - 每 5 分钟检查推进

WORKSPACE=/home/cdy/.openclaw/workspace/agent-security-skill-scanner-master
BENCHMARK=$WORKSPACE/benchmark/benchmark_v3.py
RULES=$WORKSPACE/rules/scanner_v3/yara/all_rules_v4.yar
LOG=$WORKSPACE/logs/auto_optimize.log

mkdir -p $WORKSPACE/logs
cd $WORKSPACE

echo "=== $(date '+%Y-%m-%d %H:%M:%S') ===" >> $LOG

# 运行 benchmark
RESULT=$(python3 $BENCHMARK --rules $RULES 2>&1 | grep -E "(Detection Rate|False Positive|F1 Score|credential|persistence|bash|powershell)")

echo "$RESULT" >> $LOG
echo "" >> $LOG

# 提取检测率
DET_RATE=$(echo "$RESULT" | grep "Detection Rate" | awk '{print $3}' | tr -d '%')

if [ -n "$DET_RATE" ]; then
    if (( $(echo "$DET_RATE < 85" | bc -l 2>/dev/null || echo 0) )); then
        echo "⚠️  检测率 ${DET_RATE}% < 85%，需要优化" >> $LOG
    else
        echo "✅ 检测率 ${DET_RATE}% ≥ 85% 达标" >> $LOG
    fi
fi

echo "---" >> $LOG
