#!/bin/bash
# Round 8 完整验证流程脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
FRAMEWORK_DIR="$BASE_DIR/framework"
REPORTS_DIR="$BASE_DIR/reports"

echo "============================================================"
echo "Round 8 规则验证流程"
echo "============================================================"
echo ""
echo "工作目录：$BASE_DIR"
echo "开始时间：$(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 创建必要目录
echo "[1/6] 创建目录结构..."
mkdir -p "$REPORTS_DIR"
mkdir -p "$BASE_DIR/results"
echo "✅ 目录准备完成"
echo ""

# 生成测试用例
echo "[2/6] 生成测试用例..."
cd "$BASE_DIR"
python3 "$FRAMEWORK_DIR/generate_test_cases.py"
echo ""

# 执行规则检测
echo "[3/6] 执行规则检测..."
python3 "$FRAMEWORK_DIR/rule_executor.py"
echo ""

# 分析结果
echo "[4/6] 分析执行结果..."
python3 "$FRAMEWORK_DIR/result_analyzer.py"
echo ""

# 生成报告
echo "[5/6] 生成报告..."
python3 "$FRAMEWORK_DIR/report_generator.py"
echo ""

# 生成完成报告
echo "[6/6] 生成完成报告..."
python3 "$BASE_DIR/generate_completion_report.py"
echo ""

echo "============================================================"
echo "✅ 验证流程完成!"
echo "============================================================"
echo ""
echo "结束时间：$(date '+%Y-%m-%d %H:%M:%S')"
echo ""
echo "报告位置:"
echo "  - JSON 报告：$REPORTS_DIR/report.json"
echo "  - Markdown 报告：$REPORTS_DIR/report.md"
echo "  - 完成报告：$BASE_DIR/ROUND8_COMPLETION_REPORT.md"
echo ""
