#!/bin/bash
# 🚀 P1 增强版启动脚本
# 用法：./start_p1_loop.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "============================================================"
echo "🚀 HROS P1 增强版 - 自动优化循环"
echo "============================================================"
echo ""
echo "📊 P1 优化特性:"
echo "  ✅ 动态间隔调整 (P0)"
echo "  ✅ 增量测试策略 (P0)"
echo "  ✅ 自动化规则优化 (P1)"
echo "  ✅ 并发执行 (P1)"
echo ""
echo "🎯 预期产出:"
echo "  - 日循环轮次：500+ 轮 (vs 24 轮)"
echo "  - 检测率提升：+2-3%/天 (vs +0.5%/周)"
echo "  - 人工干预：全自动 (vs 每轮手动)"
echo ""
echo "📈 当前状态:"
if [ -f "ros_meta/eval_report.md" ]; then
    grep "检测率" ros_meta/eval_report.md | head -1
fi
if [ -f "benchmark_result_v3.json" ]; then
    python3 -c "import json; d=json.load(open('benchmark_result_v3.json')); print(f\"  - 检测率：{d['detection_rate']*100:.1f}%\")"
fi
echo ""
echo "🕐 启动时间：$(date '+%Y-%m-%d %H:%M:%S')"
echo "============================================================"
echo ""

# 检查 Python 依赖
echo "🔍 检查依赖..."
python3 -c "import auto_optimizer" 2>/dev/null && echo "  ✅ auto_optimizer.py" || echo "  ⚠️  auto_optimizer.py 未找到"
python3 -c "import concurrent_executor" 2>/dev/null && echo "  ✅ concurrent_executor.py" || echo "  ⚠️  concurrent_executor.py 未找到"
echo ""

# 启动动态间隔循环（集成 P1 自动优化）
echo "🚀 启动循环..."
echo ""
python3 ros_cycle.py --loop

echo ""
echo "============================================================"
echo "👋 循环已停止"
echo "============================================================"
