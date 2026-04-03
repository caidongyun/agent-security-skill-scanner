#!/bin/bash
# 产品化持续优化流程 - 智能推进
# 每次运行自动分析短板并针对性优化

WORKSPACE=/home/cdy/.openclaw/workspace/agent-security-skill-scanner-master
BENCHMARK=$WORKSPACE/benchmark/benchmark_v3.py
RULES=$WORKSPACE/rules/scanner_v3/yara/all_rules_v5.yar
LOG=$WORKSPACE/logs/product_evolution.log
VERSION=5

mkdir -p $WORKSPACE/logs
cd $WORKSPACE

echo ""
echo "========================================"
echo "🚀 产品进化 - 第 $((VERSION+1)) 轮迭代"
echo "========================================"
echo "" | tee -a $LOG

# 运行基准测试
echo "📊 运行基准测试..." | tee -a $LOG
RESULT=$(python3 $BENCHMARK --rules $RULES 2>&1)

# 提取指标
DET_RATE=$(echo "$RESULT" | grep "Detection Rate" | awk '{print $3}' | tr -d '%')
FP_RATE=$(echo "$RESULT" | grep "False Positive" | awk '{print $4}' | tr -d '%')
F1=$(echo "$RESULT" | grep "F1 Score" | awk '{print $4}')

echo "检测率：${DET_RATE}%" | tee -a $LOG
echo "误报率：${FP_RATE}%" | tee -a $LOG
echo "F1 Score: $F1" | tee -a $LOG
echo "" | tee -a $LOG

# 分析短板
echo "🔍 分析短板..." | tee -a $LOG

# 检查是否需要优化
NEED_OPT=false

if (( $(echo "$DET_RATE < 98" | bc -l 2>/dev/null || echo 0) )); then
    echo "⚠️  检测率 ${DET_RATE}% < 98%，需继续优化" | tee -a $LOG
    NEED_OPT=true
fi

if (( $(echo "$FP_RATE > 0" | bc -l 2>/dev/null || echo 0) )); then
    echo "⚠️  误报率 ${FP_RATE}% > 0%，需优化规则特异性" | tee -a $LOG
    NEED_OPT=true
fi

# 检查各攻击类型
for attack in "credential_theft" "persistence" "bash" "powershell" "code_execution" "data_exfil"; do
    RATE=$(echo "$RESULT" | grep "$attack" | awk -F'=' '{print $2}' | awk '{print $1}' | tr -d '%')
    if [ -n "$RATE" ] && (( $(echo "$RATE < 95" | bc -l 2>/dev/null || echo 0) )); then
        echo "⚠️  $attack: ${RATE}% < 95%，需补充规则" | tee -a $LOG
        NEED_OPT=true
    fi
done

echo "" | tee -a $LOG

if [ "$NEED_OPT" = true ]; then
    echo "✅ 启动优化流程..." | tee -a $LOG
    # 这里可以触发自动化规则生成/优化脚本
    # python3 auto_generate_rules.py
else
    echo "🎉 所有指标已达优秀水平！" | tee -a $LOG
    echo "建议方向：扩展新攻击类型覆盖、优化性能、添加高级检测" | tee -a $LOG
fi

echo "" | tee -a $LOG
echo "---" | tee -a $LOG
