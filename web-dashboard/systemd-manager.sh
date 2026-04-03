#!/bin/bash
# Scanner V3 Web Dashboard - systemd 管理脚本

SERVICE_NAME="scanner-web"
SERVICE_FILE="/home/cdy/.openclaw/workspace/agent-security-skill-scanner-V3/web-dashboard/scanner-web.service"
SYSTEMD_DIR="/etc/systemd/system"

install_service() {
    echo "📦 安装 systemd 服务..."
    
    # 复制服务文件
    sudo cp "$SERVICE_FILE" "$SYSTEMD_DIR/"
    
    # 重载 systemd
    sudo systemctl daemon-reload
    
    echo "✅ 服务已安装"
    echo ""
    echo "使用命令:"
    echo "  sudo systemctl start $SERVICE_NAME     - 启动"
    echo "  sudo systemctl stop $SERVICE_NAME      - 停止"
    echo "  sudo systemctl restart $SERVICE_NAME   - 重启"
    echo "  sudo systemctl status $SERVICE_NAME    - 状态"
    echo "  sudo systemctl enable $SERVICE_NAME    - 开机启动"
}

start_local() {
    echo "🔒 启动本地模式..."
    # 修改服务文件为本地模式
    sed -i 's/--remote//' "$SERVICE_FILE"
    sudo cp "$SERVICE_FILE" "$SYSTEMD_DIR/$SERVICE_NAME.service"
    sudo systemctl daemon-reload
    sudo systemctl start $SERVICE_NAME
    sudo systemctl status $SERVICE_NAME
}

start_remote() {
    echo "🌐 启动远程模式..."
    # 修改服务文件为远程模式
    sed -i 's|ExecStart=.*server_v3.py|ExecStart=/usr/bin/python3 /home/cdy/.openclaw/workspace/agent-security-skill-scanner-V3/web-dashboard/server_v3.py --remote|' "$SERVICE_FILE"
    sudo cp "$SERVICE_FILE" "$SYSTEMD_DIR/$SERVICE_NAME.service"
    sudo systemctl daemon-reload
    sudo systemctl start $SERVICE_NAME
    sudo systemctl status $SERVICE_NAME
}

case "$1" in
    install)
        install_service
        ;;
    local)
        start_local
        ;;
    remote)
        start_remote
        ;;
    status)
        sudo systemctl status $SERVICE_NAME
        ;;
    stop)
        sudo systemctl stop $SERVICE_NAME
        ;;
    restart)
        sudo systemctl restart $SERVICE_NAME
        ;;
    *)
        echo "Scanner V3 Web Dashboard - systemd 管理"
        echo ""
        echo "用法：$0 {install|local|remote|status|stop|restart}"
        echo ""
        echo "命令:"
        echo "  install  - 安装 systemd 服务"
        echo "  local    - 启动本地模式 (127.0.0.1:8080)"
        echo "  remote   - 启动远程模式 (0.0.0.0:8080)"
        echo "  status   - 查看状态"
        echo "  stop     - 停止服务"
        echo "  restart  - 重启服务"
        ;;
esac
