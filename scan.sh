#!/bin/bash
# ==============================================================================
# 🛡️ Agent Security Skill Scanner - 默认扫描入口
# ==============================================================================
# 默认扫描器：Ultimate Scanner V2
# - 支持 8 种编程语言
# - 检测率 100%
# - YARA + AST + JS + 智能模式 + 意图识别
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
DEFAULT_SCANNER="${SCRIPT_DIR}/ultimate_scanner_v2.py"
FALLBACK_SCANNER="${SCRIPT_DIR}/ultimate_scanner.py"
SAMPLES_DIR="${SCRIPT_DIR}/samples"
RULES_DIR="${SCRIPT_DIR}/rules/scanner_v3/yara"
REPORTS_DIR="${SCRIPT_DIR}/reports"

# 显示帮助
show_help() {
    echo -e "${CYAN}============================================================================${NC}"
    echo -e "${CYAN}       🛡️  Agent Security Skill Scanner - 默认扫描器${NC}"
    echo -e "${CYAN}       Ultimate Scanner V2 - 8 种语言 | 100% 检测率${NC}"
    echo -e "${CYAN}============================================================================${NC}"
    echo ""
    echo -e "${YELLOW}用法:${NC}"
    echo "  ./scan.sh [选项] [扫描路径]"
    echo ""
    echo -e "${YELLOW}选项:${NC}"
    echo "  (无参数)           扫描内置样本库 (samples/)"
    echo "  <扫描路径>         扫描指定目录"
    echo "  --fast             快速模式 (禁用 AST/JS/智能模式)"
    echo "  --full             完整模式 (启用所有检测引擎，默认)"
    echo "  --workers N        并发数 (默认：4)"
    echo "  --verbose          详细输出模式"
    echo "  -h, --help         显示此帮助"
    echo ""
    echo -e "${YELLOW}示例:${NC}"
    echo "  ./scan.sh                              # 扫描样本库"
    echo "  ./scan.sh /path/to/code                # 扫描项目目录"
    echo "  ./scan.sh --fast                       # 快速扫描"
    echo "  ./scan.sh --workers 8                  # 8 线程扫描"
    echo "  ./scan.sh ~/.local/lib/python*/site-packages/"
    echo ""
    echo -e "${CYAN}============================================================================${NC}"
    echo -e "${YELLOW}支持的语言 (8 种):${NC}"
    echo "  ✅ Python (.py)      ✅ JavaScript (.js)     ✅ Bash (.sh)"
    echo "  ✅ PowerShell (.ps1) ✅ Batch (.bat, .cmd)   ✅ VBScript (.vbs)"
    echo "  ✅ Lua (.lua)        ✅ 其他文本文件"
    echo -e "${CYAN}============================================================================${NC}"
}

# 默认参数
SCANNER="$DEFAULT_SCANNER"
SCAN_PATH="$SAMPLES_DIR"
WORKERS=4
EXTRA_ARGS=""

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --fast)
            EXTRA_ARGS="$EXTRA_ARGS --no-ast --no-js --no-smart"
            shift
            ;;
        --full)
            shift
            ;;
        --workers)
            WORKERS="$2"
            shift 2
            ;;
        --verbose)
            EXTRA_ARGS="$EXTRA_ARGS --verbose"
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        --*)
            echo -e "${RED}❌ 未知选项：$1${NC}"
            echo "运行 ./scan.sh --help 查看帮助"
            exit 1
            ;;
        *)
            SCAN_PATH="$1"
            shift
            ;;
    esac
done

# 检查扫描器
if [ ! -f "$SCANNER" ]; then
    echo -e "${RED}❌ 主扫描器不存在：$SCANNER${NC}"
    echo -e "${YELLOW}💡 尝试使用备用扫描器...${NC}"
    SCANNER="$FALLBACK_SCANNER"
    if [ ! -f "$SCANNER" ]; then
        echo -e "${RED}❌ 所有扫描器均不可用${NC}"
        exit 1
    fi
fi

# 检查扫描路径
if [ ! -e "$SCAN_PATH" ]; then
    echo -e "${RED}❌ 扫描路径不存在：$SCAN_PATH${NC}"
    exit 1
fi

# 创建报告目录
mkdir -p "$REPORTS_DIR"

# 显示扫描信息
echo -e "${CYAN}============================================================================${NC}"
echo -e "${CYAN}       🛡️  Agent Security Skill Scanner${NC}"
echo -e "${CYAN}       Ultimate Scanner V2 - 默认扫描器${NC}"
echo -e "${CYAN}============================================================================${NC}"
echo ""
echo -e "${BLUE}📍 扫描器:${NC}   $SCANNER"
echo -e "${BLUE}📂 扫描路径:${NC} $SCAN_PATH"
echo -e "${BLUE}📊 报告目录:${NC} $REPORTS_DIR"
echo -e "${BLUE}⚡ 并发数:${NC}   $WORKERS"
if [[ "$EXTRA_ARGS" == *"--no-ast"* ]]; then
    echo -e "${YELLOW}⚡ 模式:${NC}     快速模式 (禁用 AST/JS/智能)"
else
    echo -e "${GREEN}🔬 模式:${NC}     完整模式 (所有检测引擎)"
fi
echo ""

# 构建扫描命令
if [ "$SCANNER" == "$DEFAULT_SCANNER" ]; then
    SCAN_CMD="python3 $SCANNER --samples $SCAN_PATH --rules $RULES_DIR --workers $WORKERS $EXTRA_ARGS"
else
    # 备用扫描器使用不同参数
    SCAN_CMD="python3 $SCANNER --samples $SCAN_PATH --rules $RULES_DIR --workers $WORKERS"
fi

# 执行扫描
echo -e "${GREEN}🚀 开始扫描...${NC}"
echo ""
eval $SCAN_CMD
EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ 扫描完成!${NC}"
    echo ""
    echo -e "${BLUE}📊 最新报告:${NC}"
    ls -lt "${REPORTS_DIR}"/ultimate_v2_*.json 2>/dev/null | head -1 || \
    ls -lt "${REPORTS_DIR}"/ultimate_*.json 2>/dev/null | head -1
else
    echo -e "${RED}❌ 扫描失败，退出码：$EXIT_CODE${NC}"
    echo ""
    echo -e "${YELLOW}💡 请检查日志或使用 --verbose 查看详细输出${NC}"
fi

echo ""
exit $EXIT_CODE
