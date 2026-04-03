#!/bin/bash
# ==============================================================================
# 🛡️ Agent Security Skill Scanner - 默认全量扫描入口
# ==============================================================================
# 功能：
#   - 使用最强扫描器 (multi_language_scanner_v4.py)
#   - 支持全量样本扫描
#   - 自动生成详细报告 (JSON + Markdown)
#   - 性能统计与可视化
#
# 用法：
#   ./scan_all.sh                    # 扫描默认样本库
#   ./scan_all.sh /path/to/scan      # 扫描指定目录
#   ./scan_all.sh --quick            # 快速模式
#   ./scan_all.sh --help             # 显示帮助
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 配置
SCANNER="${SCRIPT_DIR}/multi_language_scanner_v4.py"  # 最强扫描器
SAMPLES_DIR="${SCRIPT_DIR}/samples"                   # 默认样本库
REPORTS_DIR="${SCRIPT_DIR}/reports"
QUICK_MODE=false

# 显示帮助
show_help() {
    echo -e "${CYAN}============================================================================${NC}"
    echo -e "${CYAN}       🛡️  Agent Security Skill Scanner - 全量扫描入口${NC}"
    echo -e "${CYAN}============================================================================${NC}"
    echo ""
    echo -e "${YELLOW}用法:${NC}"
    echo "  ./scan_all.sh [选项] [扫描路径]"
    echo ""
    echo -e "${YELLOW}选项:${NC}"
    echo "  --quick          快速模式 (仅关键检测，跳过 AST/ML)"
    echo "  --report         生成详细报告 (默认启用)"
    echo "  --html           生成 HTML 报告"
    echo "  --verbose        详细输出模式"
    echo "  --samples        扫描内置样本库 (默认)"
    echo "  --help, -h       显示此帮助信息"
    echo ""
    echo -e "${YELLOW}示例:${NC}"
    echo "  ./scan_all.sh                              # 扫描内置样本库"
    echo "  ./scan_all.sh --quick                      # 快速扫描样本库"
    echo "  ./scan_all.sh ~/.local/lib/python*/site-packages/"
    echo "  ./scan_all.sh --html ~/projects/my-project/"
    echo ""
    echo -e "${CYAN}============================================================================${NC}"
}

# 解析参数
SCAN_PATH=""
GEN_HTML=false
VERBOSE=""
USE_SAMPLES=true

while [[ $# -gt 0 ]]; do
    case $1 in
        --quick)
            QUICK_MODE=true
            shift
            ;;
        --report)
            shift
            ;;
        --html)
            GEN_HTML=true
            shift
            ;;
        --verbose)
            VERBOSE="--verbose"
            shift
            ;;
        --samples)
            USE_SAMPLES=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            SCAN_PATH="$1"
            USE_SAMPLES=false
            shift
            ;;
    esac
done

# 确定扫描路径
if [ "$USE_SAMPLES" = true ] && [ -z "$SCAN_PATH" ]; then
    SCAN_PATH="$SAMPLES_DIR"
fi

# 检查扫描路径
if [ -z "$SCAN_PATH" ]; then
    echo -e "${RED}❌ 请指定扫描路径或使用 --samples 扫描内置样本库${NC}"
    show_help
    exit 1
fi

if [ ! -e "$SCAN_PATH" ]; then
    echo -e "${RED}❌ 扫描路径不存在：$SCAN_PATH${NC}"
    exit 1
fi

# 检查扫描器
if [ ! -f "$SCANNER" ]; then
    echo -e "${RED}❌ 扫描器不存在：$SCANNER${NC}"
    echo -e "${YELLOW}💡 尝试使用备用扫描器...${NC}"
    SCANNER="${SCRIPT_DIR}/multi_language_scanner.py"
    if [ ! -f "$SCANNER" ]; then
        echo -e "${RED}❌ 所有扫描器均不可用${NC}"
        exit 1
    fi
fi

# 显示扫描信息
echo -e "${CYAN}============================================================================${NC}"
echo -e "${CYAN}       🛡️  Agent Security Skill Scanner - 全量扫描${NC}"
echo -e "${CYAN}============================================================================${NC}"
echo ""
echo -e "${BLUE}📍 扫描器:${NC}   $SCANNER"
echo -e "${BLUE}📂 扫描路径:${NC} $SCAN_PATH"
echo -e "${BLUE}📊 报告目录:${NC} $REPORTS_DIR"
if [ "$QUICK_MODE" = true ]; then
    echo -e "${YELLOW}⚡ 模式:${NC}     快速模式 (跳过 AST/ML)"
else
    echo -e "${GREEN}🔬 模式:${NC}     完整模式 (AST+JS+YARA+ 智能评分)"
fi
echo ""

# 创建报告目录
mkdir -p "$REPORTS_DIR"

# 生成时间戳
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REPORT_JSON="${REPORTS_DIR}/scan_result_${TIMESTAMP}.json"
REPORT_MD="${REPORTS_DIR}/scan_result_${TIMESTAMP}.md"

# 构建扫描命令
SCAN_CMD="python3 $SCANNER $SCAN_PATH -r -o $REPORT_JSON"

if [ "$QUICK_MODE" = true ]; then
    SCAN_CMD="$SCAN_CMD --no-smart"  # 跳过智能评分
fi

if [ "$GEN_HTML" = true ]; then
    # HTML 生成需要扫描器支持
    SCAN_CMD="$SCAN_CMD"
fi

if [ -n "$VERBOSE" ]; then
    SCAN_CMD="$SCAN_CMD $VERBOSE"
fi

# 执行扫描
echo -e "${GREEN}🚀 开始扫描...${NC}"
echo ""
echo -e "${BLUE}命令:${NC} $SCAN_CMD"
echo ""
echo -e "${CYAN}----------------------------------------------------------------------------${NC}"

eval $SCAN_CMD
EXIT_CODE=$?

echo -e "${CYAN}----------------------------------------------------------------------------${NC}"
echo ""

# 显示结果
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ 扫描完成!${NC}"
    echo ""
    echo -e "${BLUE}📊 报告位置:${NC}"
    echo "  JSON: $REPORT_JSON"
    echo "  Markdown: $REPORT_MD"
    if [ -f "${REPORTS_DIR}/scan_result_${TIMESTAMP}.html" ]; then
        echo "  HTML: ${REPORTS_DIR}/scan_result_${TIMESTAMP}.html"
    fi
    echo ""
    
    # 显示摘要 (如果报告存在)
    if [ -f "$REPORT_JSON" ]; then
        echo -e "${CYAN}============================================================================${NC}"
        echo -e "${CYAN}📈 扫描摘要${NC}"
        echo -e "${CYAN}============================================================================${NC}"
        
        # 尝试解析 JSON 报告
        if command -v jq &> /dev/null; then
            TOTAL=$(jq -r '.total_files // 0' "$REPORT_JSON" 2>/dev/null)
            MALICIOUS=$(jq -r '.malicious_files // 0' "$REPORT_JSON" 2>/dev/null)
            BENIGN=$(jq -r '.safe_files // 0' "$REPORT_JSON" 2>/dev/null)
            DURATION=$(jq -r '.scan_time_seconds // 0' "$REPORT_JSON" 2>/dev/null)
            DETECTION_RATE=$(jq -r '.detection_rate * 100 | floor' "$REPORT_JSON" 2>/dev/null)
            
            echo -e "${BLUE}总扫描数:${NC}   $TOTAL"
            echo -e "${RED}恶意样本:${NC}   $MALICIOUS"
            echo -e "${GREEN}安全样本:${NC}   $BENIGN"
            echo -e "${GREEN}检测率:${NC}   ${DETECTION_RATE}%"
            echo -e "${YELLOW}扫描耗时:${NC}   ${DURATION}s"
        else
            echo -e "${YELLOW}💡 安装 jq 可获得更详细的摘要 (apt install jq)${NC}"
        fi
    fi
else
    echo -e "${RED}❌ 扫描失败，退出码：$EXIT_CODE${NC}"
    echo ""
    echo -e "${YELLOW}💡 请检查日志或运行 ./scan_all.sh --verbose 查看详细输出${NC}"
fi

echo ""
exit $EXIT_CODE
