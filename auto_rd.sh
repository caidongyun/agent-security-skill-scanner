#!/bin/bash
# 🚀 自动化研发系统 - 主入口
# 一键执行完整的自动化研发流程

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "============================================================"
echo "🚀 Agent Security Skill Scanner V3"
echo "   自动化研发系统"
echo "============================================================"
echo ""
echo "📍 项目根目录：$PROJECT_ROOT"
echo "📅 日期：$(date +%Y-%m-%d)"
echo ""

# 显示菜单
show_menu() {
    echo "请选择要执行的任务:"
    echo ""
    echo "  1) Round 15: 规则扩充 (16 → 50+)"
    echo "  2) Round 16: 样本扩充 (48 → 500+)"
    echo "  3) 质量评估 (检测率/误报率/性能)"
    echo "  4) 完整流程 (Round 15 + 16 + 质量评估)"
    echo "  5) 集成到 agent-defender"
    echo "  0) 退出"
    echo ""
}

# Round 15: 规则扩充
run_round15() {
    echo ""
    echo "============================================================"
    echo "🚀 Round 15: 规则扩充"
    echo "============================================================"
    
    if [ -f "$PROJECT_ROOT/scripts/ros-15-rule-expansion.sh" ]; then
        bash "$PROJECT_ROOT/scripts/ros-15-rule-expansion.sh"
    else
        echo "❌ 脚本不存在：ros-15-rule-expansion.sh"
    fi
}

# Round 16: 样本扩充
run_round16() {
    echo ""
    echo "============================================================"
    echo "🧬 Round 16: 样本扩充"
    echo "============================================================"
    
    if [ -f "$PROJECT_ROOT/scripts/ros-16-sample-expansion.sh" ]; then
        bash "$PROJECT_ROOT/scripts/ros-16-sample-expansion.sh"
    else
        echo "❌ 脚本不存在：ros-16-sample-expansion.sh"
    fi
}

# 质量评估
run_quality_gate() {
    echo ""
    echo "============================================================"
    echo "🎯 质量评估"
    echo "============================================================"
    
    if [ -f "$PROJECT_ROOT/tools/quality_gate.py" ]; then
        cd "$PROJECT_ROOT"
        python3 tools/quality_gate.py
    else
        echo "❌ 工具不存在：quality_gate.py"
    fi
}

# 集成到 agent-defender
run_integration() {
    echo ""
    echo "============================================================"
    echo "🔗 集成到 agent-defender"
    echo "============================================================"
    
    DEFENDER_DIR="$PROJECT_ROOT/../agent-defender"
    if [ -d "$DEFENDER_DIR" ] && [ -f "$DEFENDER_DIR/integrate_sigma_yara.py" ]; then
        cd "$DEFENDER_DIR"
        python3 integrate_sigma_yara.py
    else
        echo "❌ agent-defender 未找到"
    fi
}

# 完整流程
run_full_pipeline() {
    echo ""
    echo "============================================================"
    echo "🚀 完整自动化研发流程"
    echo "============================================================"
    
    run_round15
    echo ""
    read -p "按回车继续到 Round 16..."
    
    run_round16
    echo ""
    read -p "按回车继续到质量评估..."
    
    run_quality_gate
    echo ""
    read -p "按回车继续到集成..."
    
    run_integration
    
    echo ""
    echo "============================================================"
    echo "✅ 完整流程执行完成!"
    echo "============================================================"
}

# 主循环
while true; do
    show_menu
    read -p "请输入选项 (0-5): " choice
    
    case $choice in
        1)
            run_round15
            ;;
        2)
            run_round16
            ;;
        3)
            run_quality_gate
            ;;
        4)
            run_full_pipeline
            ;;
        5)
            run_integration
            ;;
        0)
            echo "👋 退出"
            exit 0
            ;;
        *)
            echo "❌ 无效选项，请重新选择"
            ;;
    esac
    
    echo ""
    read -p "按回车继续..."
done
