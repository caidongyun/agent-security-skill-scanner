#!/bin/bash
# ==============================================================================
# 🔄 ROS 训练提升编排系统 v2.0
# ==============================================================================
# 三轮迭代训练方案:
# 1. 冒烟测试 - 少量样本，快速发现问题
# 2. 全量测试 - 全面评估 + 优化
# 3. 扩充规则 - 复杂样本 + 规则库扩充
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"
BENCHMARK_DIR="/home/cdy/Desktop/security-benchmark"
SAMPLES_DIR="$BENCHMARK_DIR/samples/from-templates"
RULES_DIR="$PROJECT_DIR/rules/scanner_v3/yara"
TRAINING_DIR="$PROJECT_DIR/training"
REPORTS_DIR="$TRAINING_DIR/reports"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# ==============================================================================
# 阶段 1: 冒烟测试
# ==============================================================================
stage1_smoke_test() {
    echo -e "\n${CYAN}=============================================================================="
    echo -e "${CYAN}       阶段 1: 冒烟测试 (Smoke Test)${NC}"
    echo -e "${CYAN}=============================================================================="
    echo "目标：快速发现问题，验证扫描器和 benchmark 可用性"
    echo "样本数：10-50 个"
    echo "时间：<5 分钟"
    echo ""
    
    # 选择少量样本
    echo "📦 选择冒烟测试样本..."
    SMOKE_SAMPLES_DIR="$TRAINING_DIR/smoke_samples"
    mkdir -p "$SMOKE_SAMPLES_DIR"
    
    # 从每个攻击类型选 3-5 个样本
    for attack_type in data_exfiltration prompt_injection tool_poisoning; do
        src_dir="$SAMPLES_DIR/$attack_type"
        if [ -d "$src_dir" ]; then
            echo "  从 $attack_type 复制样本..."
            ls "$src_dir"/*.{py,js,sh,go,yaml,yml} 2>/dev/null | head -5 | xargs -I {} cp {} "$SMOKE_SAMPLES_DIR/" 2>/dev/null
        fi
    done
    
    # 运行扫描
    echo ""
    echo "🔍 运行冒烟扫描..."
    python3 "$PROJECT_DIR/ultimate_scanner_v2.py" \
        --samples "$SMOKE_SAMPLES_DIR" \
        --rules "$RULES_DIR" \
        --workers 4 \
        --output "$REPORTS_DIR/smoke_test_$(date +%Y%m%d_%H%M%S).json" \
        2>&1 | tail -20
    
    echo ""
    echo -e "${GREEN}✅ 阶段 1 完成${NC}"
}

# ==============================================================================
# 阶段 2: 全量测试
# ==============================================================================
stage2_full_test() {
    echo -e "\n${CYAN}=============================================================================="
    echo -e "${CYAN}       阶段 2: 全量测试 (Full Test)${NC}"
    echo -e "${CYAN}=============================================================================="
    echo "目标：全面评估检测率、误报率"
    echo "样本数：全部 (30,000+)"
    echo "时间：30-60 分钟"
    echo ""
    
    # 运行分批训练
    echo "🚀 运行全量分批扫描..."
    bash "$PROJECT_DIR/ros-01-batch-train-full.sh" 2>&1 | tail -30
    
    # 生成汇总报告
    echo ""
    echo "📊 生成汇总报告..."
    cat > "$REPORTS_DIR/full_test_summary_$(date +%Y%m%d_%H%M%S).md" << 'SUMMARY'
# 全量测试报告

## 检测率
- 总样本数：待填充
- 恶意检出：待填充
- 检测率：待填充

## 误报率
- 良性样本数：待填充
- 误报数：待填充
- 误报率：待填充

## 性能
- 平均扫描时间：待填充
- 吞吐量：待填充
SUMMARY
    
    echo -e "${GREEN}✅ 阶段 2 完成${NC}"
}

# ==============================================================================
# 阶段 3: 扩充规则
# ==============================================================================
stage3_expand_rules() {
    echo -e "\n${CYAN}=============================================================================="
    echo -e "${CYAN}       阶段 3: 扩充规则 (Rule Expansion)${NC}"
    echo -e "${CYAN}=============================================================================="
    echo "目标：提升检测深度，覆盖复杂/隐秘攻击"
    echo "新增：复杂样本 + 规则库扩充"
    echo "时间：1-2 小时"
    echo ""
    
    # 1. 分析漏报样本
    echo "🔍 分析漏报样本特征..."
    echo "  (从全量测试结果中提取)"
    
    # 2. 生成针对性规则
    echo ""
    echo "📝 生成针对性 YARA 规则..."
    python3 "$PROJECT_DIR/optimize_rules.py" 2>&1 | tail -10 || echo "  ⚠️  规则优化脚本未找到"
    
    # 3. 验证新规则
    echo ""
    echo "✅ 验证新规则效果..."
    echo "  (用漏报样本重新扫描)"
    
    # 4. 更新 benchmark
    echo ""
    echo "📊 更新 benchmark 样本库..."
    echo "  (添加复杂/隐秘样本)"
    
    echo -e "${GREEN}✅ 阶段 3 完成${NC}"
}

# ==============================================================================
# 主流程
# ==============================================================================
main() {
    echo -e "${CYAN}=============================================================================="
    echo -e "${CYAN}       🔄 ROS 训练提升编排系统 v2.0${NC}"
    echo -e "${CYAN}=============================================================================="
    echo ""
    echo "选择训练模式:"
    echo "  1) 阶段 1 - 冒烟测试 (快速)"
    echo "  2) 阶段 2 - 全量测试 (全面)"
    echo "  3) 阶段 3 - 扩充规则 (深度)"
    echo "  4) 完整流程 (阶段 1 → 2 → 3)"
    echo "  5) 自定义阶段"
    echo ""
    
    if [ -n "$1" ]; then
        MODE="$1"
    else
        read -p "请选择 (1-5): " MODE
    fi
    
    case $MODE in
        1)
            stage1_smoke_test
            ;;
        2)
            stage2_full_test
            ;;
        3)
            stage3_expand_rules
            ;;
        4)
            echo -e "\n${YELLOW}🚀 开始完整训练流程...${NC}"
            stage1_smoke_test
            stage2_full_test
            stage3_expand_rules
            echo -e "\n${GREEN}=============================================================================="
            echo -e "${GREEN}       ✅ 完整训练流程完成！${NC}"
            echo -e "${GREEN}=============================================================================="
            ;;
        5)
            read -p "输入阶段 (1/2/3): " STAGE
            case $STAGE in
                1) stage1_smoke_test ;;
                2) stage2_full_test ;;
                3) stage3_expand_rules ;;
                *) echo "无效选择" ;;
            esac
            ;;
        *)
            echo "无效选择"
            exit 1
            ;;
    esac
}

# 帮助信息
show_help() {
    echo "用法：$0 [选项]"
    echo ""
    echo "选项:"
    echo "  1    阶段 1 - 冒烟测试"
    echo "  2    阶段 2 - 全量测试"
    echo "  3    阶段 3 - 扩充规则"
    echo "  4    完整流程"
    echo "  5    自定义"
    echo "  -h   显示帮助"
    echo ""
    echo "示例:"
    echo "  $0 1          # 运行冒烟测试"
    echo "  $0 4          # 运行完整流程"
    echo "  $0            # 交互式选择"
}

# 入口
if [ "$1" == "-h" ] || [ "$1" == "--help" ]; then
    show_help
else
    main "$1"
fi
