#!/bin/bash
# 灵顺守护进程安装脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_FILE="$SCRIPT_DIR/lingshun.service"
SYSTEMD_DIR="/etc/systemd/system"

echo "========================================"
echo "🔧 灵顺守护进程安装"
echo "========================================"

# 检查权限
if [ "$EUID" -ne 0 ]; then
    echo "⚠️  需要 sudo 权限"
    echo "请使用：sudo $0"
    exit 1
fi

# 复制服务文件
echo "📄 复制服务文件..."
cp "$SERVICE_FILE" "$SYSTEMD_DIR/lingshun.service"

# 重载 systemd
echo "🔄 重载 systemd..."
systemctl daemon-reload

# 启用服务
echo "✅ 启用服务..."
systemctl enable lingshun

# 启动服务
echo "🚀 启动服务..."
systemctl start lingshun

# 显示状态
echo ""
echo "========================================"
echo "📊 服务状态"
echo "========================================"
systemctl status lingshun --no-pager

echo ""
echo "========================================"
echo "✅ 安装完成!"
echo "========================================"
echo ""
echo "常用命令:"
echo "  sudo systemctl start lingshun    # 启动"
echo "  sudo systemctl stop lingshun     # 停止"
echo "  sudo systemctl restart lingshun  # 重启"
echo "  sudo systemctl status lingshun   # 状态"
echo "  journalctl -u lingshun -f        # 查看日志"
echo ""
