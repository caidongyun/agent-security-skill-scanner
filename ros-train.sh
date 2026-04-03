#!/bin/bash
# 🔄 ROS 训练提升系统 - 快速入口

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=============================================================================="
echo "       🔄 ROS 训练提升系统 v3.0"
echo "=============================================================================="
echo ""
echo "用法:"
echo "  ./ros-train.sh <攻击类型>     # 扫描单个类型"
echo "  ./ros-train.sh all            # 扫描所有待优化类型"
echo "  ./ros-train.sh check          # 仅检查样本结构"
echo ""
echo "示例:"
echo "  ./ros-train.sh evasion"
echo "  ./ros-train.sh prompt_injection"
echo "  ./ros-train.sh all"
echo ""
echo "=============================================================================="

if [ "$1" == "all" ]; then
    python3 ros-train-v3.py --all
elif [ "$1" == "check" ]; then
    for attack in evasion prompt_injection memory_pollution false_prone; do
        echo ""
        python3 ros-train-v3.py --attack-type $attack --check-only
    done
elif [ -n "$1" ]; then
    python3 ros-train-v3.py --attack-type "$1"
else
    echo "❌ 请指定攻击类型或使用 'all'"
    exit 1
fi
