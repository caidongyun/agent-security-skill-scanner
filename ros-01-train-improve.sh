#!/bin/bash
# ==============================================================================
# 🔄 ROS 训练提升编排系统 - 简化版 (直接使用 Benchmark)
# ==============================================================================
# 流程:
# 1. 基准扫描 (使用现有 benchmark 样本)
# 2. 问题识别与分析
# 3. 优化提升
# 4. 知识沉淀
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"
BENCHMARK_DIR="/home/cdy/Desktop/security-benchmark"
SAMPLES_DIR="$BENCHMARK_DIR/samples/from-templates"
RULES_DIR="$PROJECT_DIR/rules/scanner_v3/yara"
TRAINING_DIR="$PROJECT_DIR/training"
LOGS_DIR="$TRAINING_DIR/logs"
REPORTS_DIR="$TRAINING_DIR/reports"

# 创建目录
mkdir -p "$LOGS_DIR" "$REPORTS_DIR" "$TRAINING_DIR/issues" "$TRAINING_DIR/knowledge-base"

# 时间戳
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
ROUND_ID="TRAIN-R01"

echo "=============================================================================="
echo "🔄 ROS 训练提升编排系统 - 简化版"
echo "=============================================================================="
echo "会话 ID: $ROUND_ID-$TIMESTAMP"
echo "Benchmark 目录：$BENCHMARK_DIR"
echo "样本目录：$SAMPLES_DIR"
echo "规则目录：$RULES_DIR"
echo ""

# ==============================================================================
# 步骤 1: 运行基准扫描
# ==============================================================================
echo "=============================================================================="
echo "🎯 步骤 1: 基准扫描 (55,000+ 样本)"
echo "=============================================================================="

echo ""
echo "运行扫描器..."
python3 "$PROJECT_DIR/ultimate_scanner_v2.py" \
    --samples "$SAMPLES_DIR" \
    --rules "$RULES_DIR" \
    --workers 8 \
    --output "$REPORTS_DIR/benchmark_scan_$TIMESTAMP.json" \
    2>&1 | tee "$LOGS_DIR/scanning_$TIMESTAMP.log"

echo ""
echo "✅ 步骤 1 完成"

# ==============================================================================
# 步骤 2: 分析问题
# ==============================================================================
echo ""
echo "=============================================================================="
echo "🔍 步骤 2: 分析问题"
echo "=============================================================================="

echo ""
echo "分析扫描结果..."
python3 "$PROJECT_DIR/analyze_scan_results.py" \
    --input "$REPORTS_DIR/benchmark_scan_$TIMESTAMP.json" \
    --output "$REPORTS_DIR/analysis_$TIMESTAMP.json" \
    2>&1 | tee "$LOGS_DIR/analysis_$TIMESTAMP.log"

echo ""
echo "识别检测失败案例..."
python3 "$PROJECT_DIR/identify_failures.py" \
    --scan-report "$REPORTS_DIR/benchmark_scan_$TIMESTAMP.json" \
    --analysis "$REPORTS_DIR/analysis_$TIMESTAMP.json" \
    --output "$TRAINING_DIR/issues/failures_$TIMESTAMP.json" \
    2>&1 | tee "$LOGS_DIR/identify_$TIMESTAMP.log"

echo ""
echo "✅ 步骤 2 完成"

# ==============================================================================
# 步骤 3: 生成优化建议
# ==============================================================================
echo ""
echo "=============================================================================="
echo "🚀 步骤 3: 生成优化建议"
echo "=============================================================================="

echo ""
python3 "$PROJECT_DIR/generate_optimizations.py" \
    --failures "$TRAINING_DIR/issues/failures_$TIMESTAMP.json" \
    --output "$REPORTS_DIR/optimizations_$TIMESTAMP.json" \
    2>&1 | tee "$LOGS_DIR/optimizations_$TIMESTAMP.log"

echo ""
echo "✅ 步骤 3 完成"

# ==============================================================================
# 步骤 4: 生成报告并更新知识库
# ==============================================================================
echo ""
echo "=============================================================================="
echo "📚 步骤 4: 生成报告 & 知识库"
echo "=============================================================================="

echo ""
echo "生成训练报告..."
python3 "$PROJECT_DIR/generate_training_report.py" \
    --session-id "$ROUND_ID-$TIMESTAMP" \
    --scan-report "$REPORTS_DIR/benchmark_scan_$TIMESTAMP.json" \
    --analysis "$REPORTS_DIR/analysis_$TIMESTAMP.json" \
    --optimizations "$REPORTS_DIR/optimizations_$TIMESTAMP.json" \
    --output "$REPORTS_DIR/training_report_$ROUND_ID_$TIMESTAMP.md" \
    2>&1 | tee "$LOGS_DIR/report_$TIMESTAMP.log"

echo ""
echo "更新知识库..."
python3 "$PROJECT_DIR/update_knowledge_base.py" \
    --session-id "$ROUND_ID-$TIMESTAMP" \
    --issues "$TRAINING_DIR/issues/failures_$TIMESTAMP.json" \
    --optimizations "$REPORTS_DIR/optimizations_$TIMESTAMP.json" \
    --report "$REPORTS_DIR/training_report_$ROUND_ID_$TIMESTAMP.md" \
    --output "$TRAINING_DIR/knowledge-base/session_$TIMESTAMP.md" \
    2>&1 | tee "$LOGS_DIR/kb_$TIMESTAMP.log"

echo ""
echo "✅ 步骤 4 完成"

# ==============================================================================
# 完成总结
# ==============================================================================
echo ""
echo "=============================================================================="
echo "✅ ROS 训练提升完成!"
echo "=============================================================================="
echo ""
echo "📊 产出物:"
echo "  - 扫描报告：$REPORTS_DIR/benchmark_scan_$TIMESTAMP.json"
echo "  - 分析报告：$REPORTS_DIR/analysis_$TIMESTAMP.json"
echo "  - 问题记录：$TRAINING_DIR/issues/failures_$TIMESTAMP.json"
echo "  - 优化建议：$REPORTS_DIR/optimizations_$TIMESTAMP.json"
echo "  - 训练报告：$REPORTS_DIR/training_report_$ROUND_ID_$TIMESTAMP.md"
echo "  - 知识库：$TRAINING_DIR/knowledge-base/session_$TIMESTAMP.md"
echo ""
echo "📁 日志目录：$LOGS_DIR"
echo ""
echo "🎯 下一步:"
echo "  1. 查看训练报告: cat $REPORTS_DIR/training_report_$ROUND_ID_$TIMESTAMP.md"
echo "  2. 执行优化建议：参考 $REPORTS_DIR/optimizations_$TIMESTAMP.json"
echo "  3. 运行下一轮：./ros-01-train-improve.sh"
echo ""
echo "=============================================================================="
