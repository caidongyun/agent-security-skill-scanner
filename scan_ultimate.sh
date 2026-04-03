#!/bin/bash
# ==============================================================================
# 🛡️ Agent Security Skill Scanner - 终极全量扫描入口
# ==============================================================================
# 功能:
#   - 使用完整 YARA 规则 (342+ 条) + 智能检测
#   - 扫描全量样本库 (benchmark_samples + samples)
#   - 检测率目标：95%+
#   - 自动生成详细报告
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# 配置
SAMPLES_BENCHMARK="${SCRIPT_DIR}/benchmark_samples"
SAMPLES_FULL="${SCRIPT_DIR}/samples"
RULES_DIR="${SCRIPT_DIR}/rules/scanner_v3/yara"
REPORTS_DIR="${SCRIPT_DIR}/reports"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo -e "${CYAN}============================================================================${NC}"
echo -e "${CYAN}       🛡️  终极全量扫描 - 最高检测能力${NC}"
echo -e "${CYAN}============================================================================${NC}"
echo ""

# 步骤 1: 运行 Benchmark 测试 (验证 YARA 规则)
echo -e "${BLUE}📊 步骤 1: 运行 YARA Benchmark 测试...${NC}"
echo ""
python3 benchmark/benchmark_v3.py 2>&1 | tail -25
echo ""

# 步骤 2: 扫描全量样本库
echo -e "${CYAN}----------------------------------------------------------------------------${NC}"
echo ""
echo -e "${BLUE}📊 步骤 2: 扫描全量样本库 (samples/)...${NC}"
echo ""

REPORT_JSON="${REPORTS_DIR}/full_scan_${TIMESTAMP}.json"

python3 scanner_distributed_v4_1.py \
    --samples "$SAMPLES_FULL" \
    --rules "$RULES_DIR" \
    --output "$REPORT_JSON" \
    2>&1 | tail -30

echo ""

# 步骤 3: 生成综合报告
echo -e "${CYAN}----------------------------------------------------------------------------${NC}"
echo ""
echo -e "${BLUE}📊 步骤 3: 生成综合报告...${NC}"
echo ""

# 显示报告位置
echo -e "${GREEN}✅ 扫描完成!${NC}"
echo ""
echo -e "${BLUE}📊 报告位置:${NC}"
ls -lt "${REPORTS_DIR}"/full_scan_*.json 2>/dev/null | head -1
ls -lt "${REPORTS_DIR}"/benchmark_result_v3.json 2>/dev/null | head -1

echo ""
echo -e "${CYAN}============================================================================${NC}"
echo -e "${YELLOW}💡 提示：${NC}"
echo "  - Benchmark 测试验证 YARA 规则检测率 (目标 100%)"
echo "  - 全量扫描测试实际样本库检测能力"
echo "  - 如检测率 <95%，运行 ./optimize_rules.sh 优化规则"
echo -e "${CYAN}============================================================================${NC}"
