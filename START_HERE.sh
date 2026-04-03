#!/bin/bash
# ==============================================================================
# 🚪 项目入口脚本 - 从这里开始！
# ==============================================================================
# 用法：./START_HERE.sh
#
# 这个脚本会：
# 1. 显示项目状态
# 2. 显示当前任务
# 3. 显示重要文档
# 4. 提供快速导航
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

# 显示横幅
echo -e "${CYAN}"
echo "==============================================================================="
echo "       🚪 安全扫描器自治研发系统 - 项目入口"
echo "==============================================================================="
echo -e "${NC}"
echo ""

# 显示当前时间
echo "📅 当前时间：$(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 显示系统状态
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}       📊 系统状态${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# 检查进程
if ps aux | grep "auto_rd_scanner.py" | grep -v grep > /dev/null; then
    PID=$(ps aux | grep "auto_rd_scanner.py" | grep -v grep | awk '{print $2}')
    echo -e "自治研发系统：${GREEN}✅ 运行中${NC} (PID: $PID)"
else
    echo -e "自治研发系统：${YELLOW}⚠️  未运行${NC}"
fi

# 检查 systemd 服务
if sudo systemctl is-active auto_rd_scanner > /dev/null 2>&1; then
    echo -e "systemd 服务：   ${GREEN}✅ 运行中${NC}"
else
    echo -e "systemd 服务：   ${YELLOW}⚠️  未运行${NC}"
fi

# 显示规则目录状态
echo ""
echo -e "${YELLOW}规则目录:${NC}"
if [ -f "rules/scanner_v3/yara/scanner_rules.yar" ]; then
    RULE_COUNT=$(grep -c "^rule " rules/scanner_v3/yara/scanner_rules.yar 2>/dev/null || echo "0")
    PERM=$(ls -l rules/scanner_v3/yara/scanner_rules.yar 2>/dev/null | awk '{print $1}')
    echo "  规则数：$RULE_COUNT 条"
    echo "  权限：$PERM"
else
    echo "  ${RED}❌ 规则文件不存在${NC}"
fi

echo ""

# 显示当前任务
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}       📋 当前任务${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

if [ -f "TODO_AND_PROGRESS.md" ]; then
    echo "查看 TODO_AND_PROGRESS.md 获取详细任务列表"
    echo ""
    grep -A5 "### 任务 1:" TODO_AND_PROGRESS.md | head -6
else
    echo "⚠️  TODO_AND_PROGRESS.md 不存在"
fi

echo ""

# 显示重要文档
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}       📚 重要文档${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

DOCS=(
    "PROJECT_ENTRY_POINT.md:项目入口和导航"
    "HISTORY_AND_LESSONS.md:历史经验教训"
    "TODO_AND_PROGRESS.md:当前待办和进展"
    "MULTI_LAYER_INTEGRATION_STATUS.md:多层架构状态"
    "SETUP_GUIDE.md:安装和使用指南"
)

for i in "${!DOCS[@]}"; do
    DOC="${DOCS[$i]}"
    FILE="${DOC%%:*}"
    DESC="${DOC##*:}"
    
    if [ -f "$FILE" ]; then
        echo -e "$((i+1)). ${GREEN}✅${NC} $FILE - $DESC"
    else
        echo -e "$((i+1)). ${RED}❌${NC} $FILE - $DESC (不存在)"
    fi
done

echo ""

# 显示快速命令
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}       ⚡ 快速命令${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

echo "查看系统状态：  ./manage_auto_rd.sh status"
echo "查看实时日志：  ./manage_auto_rd.sh logs -f"
echo "查看规则目录：  ./protect_rules.sh --status"
echo "查看 systemd:   sudo systemctl status auto_rd_scanner"
echo ""

echo "阅读文档：      cat PROJECT_ENTRY_POINT.md"
echo "查看历史：      cat HISTORY_AND_LESSONS.md"
echo "查看待办：      cat TODO_AND_PROGRESS.md"
echo ""

# 显示菜单
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}       🎯 下一步操作${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

echo "请选择操作:"
echo ""
echo "  1) 查看系统详细状态"
echo "  2) 查看实时日志"
echo "  3) 阅读项目入口文档"
echo "  4) 阅读历史经验教训"
echo "  5) 阅读当前待办进展"
echo "  6) 启动自治研发系统"
echo "  7) 退出"
echo ""

read -p "请输入选项 [1-7]: " choice

case $choice in
    1)
        ./manage_auto_rd.sh status
        ;;
    2)
        ./manage_auto_rd.sh logs -f
        ;;
    3)
        cat PROJECT_ENTRY_POINT.md | less
        ;;
    4)
        cat HISTORY_AND_LESSONS.md | less
        ;;
    5)
        cat TODO_AND_PROGRESS.md | less
        ;;
    6)
        ./manage_auto_rd.sh start
        ;;
    7)
        echo "👋 再见!"
        exit 0
        ;;
    *)
        echo "❌ 无效选项"
        exit 1
        ;;
esac

echo ""
echo "==============================================================================="
echo ""
