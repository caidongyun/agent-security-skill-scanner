#!/bin/bash
# ==============================================================================
# 🔄 ROS 训练提升编排系统 - 分批训练版
# ==============================================================================
# 策略:
# - 将 55,000 样本分成多个批次
# - 每批独立扫描、分析、优化
# - 快速反馈，可中断续传
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"
BENCHMARK_DIR="/home/cdy/Desktop/security-benchmark"
SAMPLES_BASE="$BENCHMARK_DIR/samples/from-templates"
RULES_DIR="$PROJECT_DIR/rules/scanner_v3/yara"
TRAINING_DIR="$PROJECT_DIR/training"
LOGS_DIR="$TRAINING_DIR/logs"
REPORTS_DIR="$TRAINING_DIR/reports"

# 批次配置 (按攻击类型目录)
declare -a BATCHES=(
    "prompt_injection"
    "tool_poisoning"
    "credential_theft"
    "memory_pollution"
    "supply_chain_attack"
    "resource_exhaustion"
    "data_exfiltration"
    "normal_script"
    "benign"
)

# 时间戳
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
ROUND_ID="TRAIN-R01"

echo "=============================================================================="
echo "🔄 ROS 训练提升编排系统 - 分批训练版"
echo "=============================================================================="
echo "会话 ID: $ROUND_ID-$TIMESTAMP"
echo "总批次数：${#BATCHES[@]}"
echo ""

# 创建目录
mkdir -p "$LOGS_DIR" "$REPORTS_DIR" "$TRAINING_DIR/issues" "$TRAINING_DIR/knowledge-base"

# ==============================================================================
# 分批处理
# ==============================================================================
BATCH_NUM=0
for BATCH_NAME in "${BATCHES[@]}"; do
    BATCH_NUM=$((BATCH_NUM + 1))
    SAMPLES_DIR="$SAMPLES_BASE/$BATCH_NAME"
    
    # 检查目录是否存在
    if [ ! -d "$SAMPLES_DIR" ]; then
        echo "⚠️  跳过 $BATCH_NAME (目录不存在)"
        continue
    fi
    
    echo ""
    echo "=============================================================================="
    echo "📦 Batch $BATCH_NUM/${#BATCHES[@]}: $BATCH_NAME"
    echo "=============================================================================="
    echo "样本目录：$SAMPLES_DIR"
    echo ""
    
    # 步骤 1: 扫描
    echo "步骤 1: 扫描..."
    python3 "$PROJECT_DIR/ultimate_scanner_v2.py" \
        --samples "$SAMPLES_DIR" \
        --rules "$RULES_DIR" \
        --workers 8 \
        --output "$REPORTS_DIR/batch_${BATCH_NUM}_${BATCH_NAME}_$TIMESTAMP.json" \
        2>&1 | tee "$LOGS_DIR/batch_${BATCH_NUM}_scan_$TIMESTAMP.log"
    
    echo "✅ Batch $BATCH_NUM 完成"
    echo ""
    
    # 可选：每批后暂停
    # sleep 1
done

echo ""
echo "=============================================================================="
echo "✅ 所有批次完成！"
echo "=============================================================================="
echo ""
echo "📊 产出物:"
ls -lt "$REPORTS_DIR"/*.json 2>/dev/null | head -10
echo ""
echo "📁 日志目录：$LOGS_DIR"
echo ""
echo "=============================================================================="
