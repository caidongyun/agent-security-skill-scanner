#!/bin/bash
# ==============================================================================
# 🔄 ROS 分批训练提升系统 - 完整版
# ==============================================================================
# 每批都是完整训练循环：扫描 → 分析 → 优化 → 验证 → 记录
# 持续优化扫描器，每批都有提升！
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"
BENCHMARK_DIR="/home/cdy/Desktop/security-benchmark"
SAMPLES_BASE="$BENCHMARK_DIR/samples/from-templates"
RULES_DIR="$PROJECT_DIR/rules/scanner_v3/yara"
TRAINING_DIR="$PROJECT_DIR/training"
LOGS_DIR="$TRAINING_DIR/logs"
REPORTS_DIR="$TRAINING_DIR/reports"
ISSUES_DIR="$TRAINING_DIR/issues"
KB_DIR="$TRAINING_DIR/knowledge-base"

# 批次配置 (按攻击类型)
declare -a BATCHES=(
    "data_exfiltration"
    "prompt_injection"
    "tool_poisoning"
    "credential_theft"
    "memory_pollution"
    "supply_chain_attack"
    "resource_exhaustion"
    "normal_script"
)

# 时间戳
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
ROUND_ID="BATCH-TRAIN-R01"

echo "=============================================================================="
echo "🔄 ROS 分批训练提升系统 - 完整版"
echo "=============================================================================="
echo "会话 ID: $ROUND_ID-$TIMESTAMP"
echo "总批次数：${#BATCHES[@]}"
echo "策略：每批独立训练 + 持续优化"
echo ""

# 创建目录
mkdir -p "$LOGS_DIR" "$REPORTS_DIR" "$ISSUES_DIR" "$KB_DIR"

# ==============================================================================
# 分批处理
# ==============================================================================
BATCH_NUM=0
TOTAL_IMPROVEMENTS=0

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
    echo "开始时间：$(date '+%H:%M:%S')"
    echo ""
    
    # -------------------------------------------------------------------------
    # 步骤 1: 基准扫描
    # -------------------------------------------------------------------------
    echo "步骤 1: 基准扫描..."
    SCAN_REPORT="$REPORTS_DIR/batch${BATCH_NUM}_${BATCH_NAME}_scan.json"
    
    python3 "$PROJECT_DIR/ultimate_scanner_v2.py" \
        --samples "$SAMPLES_DIR" \
        --rules "$RULES_DIR" \
        --workers 8 \
        --output "$SCAN_REPORT" \
        2>&1 | tee "$LOGS_DIR/batch${BATCH_NUM}_scan.log"
    
    # 提取检测结果
    if command -v jq &> /dev/null && [ -f "$SCAN_REPORT" ]; then
        DETECTION_RATE=$(jq -r '.summary.detection_rate // "N/A"' "$SCAN_REPORT" 2>/dev/null)
        TOTAL_SAMPLES=$(jq -r '.summary.total // 0' "$SCAN_REPORT" 2>/dev/null)
        echo "  检测率：$DETECTION_RATE"
        echo "  样本数：$TOTAL_SAMPLES"
    fi
    
    # -------------------------------------------------------------------------
    # 步骤 2: 分析问题
    # -------------------------------------------------------------------------
    echo ""
    echo "步骤 2: 分析问题..."
    ANALYSIS_REPORT="$REPORTS_DIR/batch${BATCH_NUM}_analysis.json"
    FAILURES_FILE="$ISSUES_DIR/batch${BATCH_NUM}_failures.json"
    
    python3 "$PROJECT_DIR/analyze_and_identify.py" \
        --scan-report "$SCAN_REPORT" \
        --output-analysis "$ANALYSIS_REPORT" \
        --output-failures "$FAILURES_FILE" \
        2>&1 | tee "$LOGS_DIR/batch${BATCH_NUM}_analysis.log"
    
    # -------------------------------------------------------------------------
    # 步骤 3: 生成优化建议
    # -------------------------------------------------------------------------
    echo ""
    echo "步骤 3: 生成优化建议..."
    OPTIMIZATIONS_FILE="$REPORTS_DIR/batch${BATCH_NUM}_optimizations.json"
    
    python3 "$PROJECT_DIR/generate_optimizations.py" \
        --failures "$FAILURES_FILE" \
        --batch-name "$BATCH_NAME" \
        --output "$OPTIMIZATIONS_FILE" \
        2>&1 | tee "$LOGS_DIR/batch${BATCH_NUM}_optimizations.log"
    
    # -------------------------------------------------------------------------
    # 步骤 4: 执行优化 (如果优化建议数量 > 0)
    # -------------------------------------------------------------------------
    OPT_COUNT=0
    if [ -f "$OPTIMIZATIONS_FILE" ] && command -v jq &> /dev/null; then
        OPT_COUNT=$(jq '.suggestions | length' "$OPTIMIZATIONS_FILE" 2>/dev/null || echo "0")
    fi
    
    if [ "$OPT_COUNT" -gt 0 ]; then
        echo ""
        echo "步骤 4: 执行优化 ($OPT_COUNT 条建议)..."
        
        # 读取优化建议并执行
        python3 "$PROJECT_DIR/apply_optimizations.py" \
            --optimizations "$OPTIMIZATIONS_FILE" \
            --rules-dir "$RULES_DIR" \
            2>&1 | tee "$LOGS_DIR/batch${BATCH_NUM}_apply.log"
        
        TOTAL_IMPROVEMENTS=$((TOTAL_IMPROVEMENTS + OPT_COUNT))
        echo "  ✅ 应用 $OPT_COUNT 条优化建议"
    else
        echo ""
        echo "步骤 4: 无需优化 (检测率达标)"
    fi
    
    # -------------------------------------------------------------------------
    # 步骤 5: 验证优化效果
    # -------------------------------------------------------------------------
    echo ""
    echo "步骤 5: 验证优化效果..."
    VERIFICATION_REPORT="$REPORTS_DIR/batch${BATCH_NUM}_verification.json"
    
    python3 "$PROJECT_DIR/verify_improvements.py" \
        --before "$SCAN_REPORT" \
        --optimizations "$OPTIMIZATIONS_FILE" \
        --output "$VERIFICATION_REPORT" \
        2>&1 | tee "$LOGS_DIR/batch${BATCH_NUM}_verification.log"
    
    # -------------------------------------------------------------------------
    # 步骤 6: 记录知识库
    # -------------------------------------------------------------------------
    echo ""
    echo "步骤 6: 记录知识库..."
    KB_FILE="$KB_DIR/batch${BATCH_NUM}_${BATCH_NAME}.md"
    
    python3 "$PROJECT_DIR/record_knowledge.py" \
        --batch-num "$BATCH_NUM" \
        --batch-name "$BATCH_NAME" \
        --scan-report "$SCAN_REPORT" \
        --failures "$FAILURES_FILE" \
        --optimizations "$OPTIMIZATIONS_FILE" \
        --verification "$VERIFICATION_REPORT" \
        --output "$KB_FILE" \
        2>&1 | tee "$LOGS_DIR/batch${BATCH_NUM}_kb.log"
    
    echo ""
    echo "✅ Batch $BATCH_NUM 完成 (结束时间：$(date '+%H:%M:%S'))"
    echo ""
    
    # 可选：每批后短暂暂停
    sleep 1
done

# ==============================================================================
# 完成总结
# ==============================================================================
echo ""
echo "=============================================================================="
echo "✅ 所有批次完成！"
echo "=============================================================================="
echo ""
echo "📊 训练总结:"
echo "  总批次数：$BATCH_NUM"
echo "  总优化数：$TOTAL_IMPROVEMENTS"
echo "  平均每批优化：$((TOTAL_IMPROVEMENTS / BATCH_NUM)) 条"
echo ""
echo "📁 产出物:"
echo "  扫描报告：$REPORTS_DIR/batch*_scan.json"
echo "  分析报告：$REPORTS_DIR/batch*_analysis.json"
echo "  优化建议：$REPORTS_DIR/batch*_optimizations.json"
echo "  验证报告：$REPORTS_DIR/batch*_verification.json"
echo "  知识库：$KB_DIR/batch*.md"
echo ""
echo "📈 查看最新报告:"
ls -lt "$REPORTS_DIR"/*.json 2>/dev/null | head -5
echo ""
echo "📚 查看知识库:"
ls -lt "$KB_DIR"/*.md 2>/dev/null | head -5
echo ""
echo "🎯 下一步:"
echo "  1. 查看汇总报告：cat $REPORTS_DIR/summary_*.md"
echo "  2. 运行下一轮：./ros-01-batch-train.sh (Round 02)"
echo "  3. 查看优化效果：对比各批次检测率"
echo ""
echo "=============================================================================="
