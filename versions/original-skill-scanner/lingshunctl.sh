#!/bin/bash
# 🧠 灵顺 V5 快速管理脚本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DAEMON_SCRIPT="$SCRIPT_DIR/lingshun_daemon.py"
SERVICE_FILE="$SCRIPT_DIR/lingshun.service"

show_help() {
    cat << EOF
🧠 灵顺 V5 守护进程管理

用法：$0 <命令> [选项]

命令:
    start       启动守护进程
    stop        停止守护进程
    restart     重启守护进程
    status      查看状态
    logs        查看日志 (最近 50 行)
    follow      实时跟踪日志
    install     安装 systemd 服务
    uninstall   卸载 systemd 服务
    enable      启用开机自启
    disable     禁用开机自启

选项:
    -i, --interval <秒>   设置每轮间隔时间 (默认：300)
    -n, --lines <行数>    查看日志行数 (默认：50)
    -h, --help            显示帮助

示例:
    $0 start                      # 启动
    $0 status                     # 查看状态
    $0 logs -n 100                # 查看最近 100 行日志
    $0 follow                     # 实时跟踪日志
    $0 start -i 600               # 启动，每轮间隔 600 秒
    $0 install && $0 enable       # 安装并启用开机自启

EOF
}

case "$1" in
    start)
        shift
        python3 "$DAEMON_SCRIPT" start "$@"
        ;;
    stop)
        python3 "$DAEMON_SCRIPT" stop
        ;;
    restart)
        python3 "$DAEMON_SCRIPT" restart
        ;;
    status)
        python3 "$DAEMON_SCRIPT" status
        ;;
    logs)
        shift
        python3 "$DAEMON_SCRIPT" logs "$@"
        ;;
    follow)
        python3 "$DAEMON_SCRIPT" logs --follow
        ;;
    install)
        echo "🔧 安装 systemd 服务..."
        if [ "$EUID" -ne 0 ]; then
            echo "⚠️  需要 sudo 权限，请输入密码："
            sudo cp "$SERVICE_FILE" /etc/systemd/system/lingshun.service
        else
            cp "$SERVICE_FILE" /etc/systemd/system/lingshun.service
        fi
        sudo systemctl daemon-reload
        echo "✅ 服务已安装"
        echo ""
        echo "使用以下命令管理:"
        echo "  sudo systemctl start lingshun     # 启动"
        echo "  sudo systemctl stop lingshun      # 停止"
        echo "  sudo systemctl restart lingshun   # 重启"
        echo "  sudo systemctl status lingshun    # 状态"
        ;;
    uninstall)
        echo "🗑️  卸载 systemd 服务..."
        if [ "$EUID" -ne 0 ]; then
            sudo systemctl stop lingshun 2>/dev/null || true
            sudo systemctl disable lingshun 2>/dev/null || true
            sudo rm -f /etc/systemd/system/lingshun.service
        else
            systemctl stop lingshun 2>/dev/null || true
            systemctl disable lingshun 2>/dev/null || true
            rm -f /etc/systemd/system/lingshun.service
        fi
        sudo systemctl daemon-reload
        echo "✅ 服务已卸载"
        ;;
    enable)
        echo "⚙️  启用开机自启..."
        sudo systemctl enable lingshun
        echo "✅ 已启用开机自启"
        ;;
    disable)
        echo "⚙️  禁用开机自启..."
        sudo systemctl disable lingshun
        echo "✅ 已禁用开机自启"
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        if [ -n "$1" ]; then
            echo "❌ 未知命令：$1"
            echo ""
        fi
        show_help
        exit 1
        ;;
esac
