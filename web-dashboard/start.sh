#!/bin/bash
# Scanner V3 Web Dashboard - 启动脚本
# 用法：
#   ./start.sh          - 本地模式（默认）
#   ./start.sh remote   - 远程模式

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="/tmp/scanner-web.pid"
LOG_FILE="/tmp/scanner-web.log"

MODE="${1:-local}"

stop_service() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        kill $PID 2>/dev/null && echo "✅ 已停止服务 (PID: $PID)" || echo "⚠️  服务未运行"
        rm -f "$PID_FILE"
    else
        pkill -f "server_v3.py" 2>/dev/null && echo "✅ 已停止旧服务" || echo "ℹ️  无旧服务"
    fi
}

start_service() {
    cd "$SCRIPT_DIR"
    
    if [ "$MODE" == "remote" ]; then
        nohup python3 server_v4.py --remote > "$LOG_FILE" 2>&1 &
        echo "🌐 启动远程模式"
    else
        nohup python3 server_v4.py > "$LOG_FILE" 2>&1 &
        echo "🔒 启动本地模式"
    fi
    
    PID=$!
    echo $PID > "$PID_FILE"
    echo "✅ 服务已启动 (PID: $PID)"
    echo "📄 日志：$LOG_FILE"
    
    sleep 2
    
    # 验证
    if ps -p $PID > /dev/null 2>&1; then
        echo "✅ 服务运行正常"
        if [ "$MODE" == "remote" ]; then
            echo "🌐 访问地址：http://localhost:8080 或 http://192.168.0.103:8080"
        else
            echo "🔒 访问地址：http://localhost:8080"
        fi
    else
        echo "❌ 服务启动失败，查看日志：$LOG_FILE"
        exit 1
    fi
}

status_service() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            echo "✅ 服务运行中 (PID: $PID)"
            MODE_STR=$(ps -p $PID -o args= | grep -q "\-\-remote" && echo "远程" || echo "本地")
            echo "📋 模式：$MODE_STR"
            return 0
        fi
    fi
    
    # 尝试通过端口查找
    if ss -tlnp | grep -q ":8080"; then
        echo "⚠️  端口 8080 被占用，但 PID 文件不存在"
        ss -tlnp | grep 8080
        return 1
    fi
    
    echo "❌ 服务未运行"
    return 1
}

case "${2:-start}" in
    start)
        stop_service
        start_service
        ;;
    stop)
        stop_service
        ;;
    restart)
        stop_service
        sleep 2
        start_service
        ;;
    status)
        status_service
        ;;
    *)
        echo "用法：$0 [local|remote] [start|stop|restart|status]"
        echo ""
        echo "模式:"
        echo "  local   - 仅本地监听 (127.0.0.1:8080) - 默认"
        echo "  remote  - 允许远程访问 (0.0.0.0:8080)"
        echo ""
        echo "操作:"
        echo "  start   - 启动服务"
        echo "  stop    - 停止服务"
        echo "  restart - 重启服务"
        echo "  status  - 查看状态"
        echo ""
        echo "示例:"
        echo "  $0              - 本地模式启动"
        echo "  $0 remote       - 远程模式启动"
        echo "  $0 local stop   - 停止服务"
        echo "  $0 status       - 查看状态"
        ;;
esac
