#!/bin/bash
# ==============================================================================
# 自治研发系统统一管理脚本
# ==============================================================================

SERVICE="auto_rd_scanner"
LOCK_FILE="/tmp/auto_rd_scanner.lock"
LOG_FILE="logs/auto_rd_scanner.log"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

show_status() {
    echo -e "${BLUE}══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}       🤖  自治研发系统状态${NC}"
    echo -e "${BLUE}══════════════════════════════════════════════════════════════${NC}"
    echo ""
    
    # 系统服务状态
    echo -e "${YELLOW}Systemd 服务状态:${NC}"
    sudo systemctl status $SERVICE --no-pager | head -10
    echo ""
    
    # 进程状态
    echo -e "${YELLOW}进程状态:${NC}"
    if [ -f "$LOCK_FILE" ]; then
        PID=$(cat "$LOCK_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            echo -e "  ${GREEN}✅ 运行中 (PID: $PID)${NC}"
        else
            echo -e "  ${RED}❌ 锁文件存在但进程已停止${NC}"
        fi
    else
        echo -e "  ${YELLOW}⚠️  未运行${NC}"
    fi
    echo ""
    
    # 规则目录状态
    echo -e "${YELLOW}规则目录状态:${NC}"
    ls -la rules/scanner_v3/yara/scanner_rules.yar 2>/dev/null | awk '{print "  权限:", $1, "大小:", $5, "字节"}'
    grep -c "^rule " rules/scanner_v3/yara/scanner_rules.yar 2>/dev/null | awk '{print "  规则数:", $1, "条"}'
    echo ""
    
    # 日志状态
    echo -e "${YELLOW}最近日志:${NC}"
    tail -5 "$LOG_FILE" 2>/dev/null || echo "  无日志"
    echo ""
}

start_service() {
    echo -e "${BLUE}══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}       🚀  启动自治研发系统${NC}"
    echo -e "${BLUE}══════════════════════════════════════════════════════════════${NC}"
    echo ""
    
    # 检查是否已有进程
    if [ -f "$LOCK_FILE" ]; then
        PID=$(cat "$LOCK_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            echo -e "${RED}❌ 已有进程运行中 (PID: $PID)${NC}"
            echo "请先停止：$0 stop"
            exit 1
        else
            echo -e "${YELLOW}⚠️  清理旧锁文件...${NC}"
            rm -f "$LOCK_FILE"
        fi
    fi
    
    # 启动服务
    echo -e "${GREEN}▶️  启动服务...${NC}"
    sudo systemctl start $SERVICE
    
    sleep 5
    show_status
}

stop_service() {
    echo -e "${BLUE}══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}       🛑  停止自治研发系统${NC}"
    echo -e "${BLUE}══════════════════════════════════════════════════════════════${NC}"
    echo ""
    
    echo -e "${YELLOW}⏹️  停止服务...${NC}"
    sudo systemctl stop $SERVICE
    
    # 清理锁文件
    rm -f "$LOCK_FILE"
    echo -e "${GREEN}✅ 锁文件已清理${NC}"
    echo ""
    
    show_status
}

restart_service() {
    echo -e "${BLUE}══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}       🔄  重启自治研发系统${NC}"
    echo -e "${BLUE}══════════════════════════════════════════════════════════════${NC}"
    echo ""
    
    stop_service
    sleep 2
    start_service
}

view_logs() {
    echo -e "${BLUE}══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}       📜  查看日志${NC}"
    echo -e "${BLUE}══════════════════════════════════════════════════════════════${NC}"
    echo ""
    
    if [ "$1" == "-f" ]; then
        echo -e "${YELLOW}实时日志 (Ctrl+C 停止):${NC}"
        sudo journalctl -u $SERVICE -f
    else
        echo -e "${YELLOW}最近 50 行日志:${NC}"
        sudo journalctl -u $SERVICE -n 50 --no-pager
    fi
}

show_help() {
    echo -e "${BLUE}══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}       📖  自治研发系统管理脚本${NC}"
    echo -e "${BLUE}══════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "用法：$0 <命令> [选项]"
    echo ""
    echo "命令:"
    echo "  start           启动服务"
    echo "  stop            停止服务"
    echo "  restart         重启服务"
    echo "  status          查看状态"
    echo "  logs [-f]       查看日志 (-f 实时跟踪)"
    echo "  install         安装服务"
    echo "  help            显示帮助"
    echo ""
    echo "示例:"
    echo "  $0 start        # 启动服务"
    echo "  $0 logs -f      # 实时查看日志"
    echo "  $0 status       # 查看状态"
    echo ""
    echo -e "${BLUE}══════════════════════════════════════════════════════════════${NC}"
}

# 主程序
case "${1:-status}" in
    start)
        start_service
        ;;
    stop)
        stop_service
        ;;
    restart)
        restart_service
        ;;
    status)
        show_status
        ;;
    logs)
        view_logs "$2"
        ;;
    install)
        sudo ./install_auto_rd_service.sh
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}❌ 未知命令：$1${NC}"
        show_help
        exit 1
        ;;
esac
