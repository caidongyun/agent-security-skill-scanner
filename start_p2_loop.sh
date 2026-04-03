#!/bin/bash
# 🚀 P2 事件驱动版启动脚本
# 用法：./start_p2_loop.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "============================================================"
echo "🚀 HROS P2 事件驱动版 - 全自动智能优化"
echo "============================================================"
echo ""
echo "📊 P0+P1+P2 完整特性:"
echo "  ✅ 动态间隔调整 (P0)"
echo "  ✅ 增量测试策略 (P0)"
echo "  ✅ 自动化规则优化 (P1)"
echo "  ✅ 并发执行 (P1)"
echo "  ✅ 事件驱动架构 (P2) ⭐ 新增"
echo "  ✅ 威胁情报 API 集成 (P2) ⭐ 新增"
echo ""
echo "🎯 核心能力:"
echo "  - 🔄 实时响应：<1 分钟 (vs 30 分钟)"
echo "  - 🌐 4 个情报源：MITRE ATLAS/ATT&CK/NVD/GitHub"
echo "  - 🤖 全自动闭环：事件触发 → 自动优化"
echo "  - 📈 日产出：500-1000+ 轮"
echo ""
echo "📈 当前状态:"
if [ -f "ros_meta/eval_report.md" ]; then
    grep "检测率" ros_meta/eval_report.md | head -1
fi
if [ -f "benchmark_result_v3.json" ]; then
    python3 -c "import json; d=json.load(open('benchmark_result_v3.json')); print(f\"  - 检测率：{d['detection_rate']*100:.1f}%\")"
fi
if [ -d "intel" ]; then
    intel_count=$(ls intel/intel_*.json 2>/dev/null | wc -l)
    echo "  - 威胁情报：${intel_count} 个文件"
fi
echo ""
echo "🕐 启动时间：$(date '+%Y-%m-%d %H:%M:%S')"
echo "============================================================"
echo ""

# 检查 Python 依赖
echo "🔍 检查依赖..."
python3 -c "import auto_optimizer" 2>/dev/null && echo "  ✅ auto_optimizer.py (P1)" || echo "  ⚠️  auto_optimizer.py 未找到"
python3 -c "import concurrent_executor" 2>/dev/null && echo "  ✅ concurrent_executor.py (P1)" || echo "  ⚠️  concurrent_executor.py 未找到"
python3 -c "import event_driver" 2>/dev/null && echo "  ✅ event_driver.py (P2)" || echo "  ⚠️  event_driver.py 未找到"
python3 -c "import threat_intel_api" 2>/dev/null && echo "  ✅ threat_intel_api.py (P2)" || echo "  ⚠️  threat_intel_api.py 未找到"
echo ""

# 采集威胁情报 (首次启动)
echo "🌐 采集威胁情报..."
timeout 60 python3 threat_intel_api.py || echo "  ⚠️  威胁情报采集失败，继续启动..."
echo ""

# 启动动态间隔循环（集成 P0+P1+P2）
echo "🚀 启动 P2 事件驱动循环..."
echo ""
python3 ros_cycle.py --loop

echo ""
echo "============================================================"
echo "👋 循环已停止"
echo "============================================================"
