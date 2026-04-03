#!/bin/bash
# 扫描器自治研发系统安装脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_FILE="$SCRIPT_DIR/auto_rd_scanner.service"
SYSTEM_SERVICE="/etc/systemd/system/scanner_auto_rd.service"

echo "🔧 安装扫描器自治研发系统..."

# 创建日志目录
mkdir -p "$SCRIPT_DIR/logs"
chmod 755 "$SCRIPT_DIR/logs"

# 复制服务文件
echo "📋 复制服务文件..."
sudo cp "$SERVICE_FILE" "$SYSTEM_SERVICE"

# 重新加载 systemd
echo "🔄 重新加载 systemd..."
sudo systemctl daemon-reload

# 启用服务
echo "▶️  启用服务..."
sudo systemctl enable scanner_auto_rd

# 启动服务
echo "🚀 启动服务..."
sudo systemctl start scanner_auto_rd

# 检查状态
echo ""
echo "📊 服务状态:"
sudo systemctl status scanner_auto_rd --no-pager

echo ""
echo "✅ 安装完成!"
echo ""
echo "常用命令:"
echo "  查看状态：sudo systemctl status scanner_auto_rd"
echo "  查看日志：sudo journalctl -u scanner_auto_rd -f"
echo "  停止服务：sudo systemctl stop scanner_auto_rd"
echo "  重启服务：sudo systemctl restart scanner_auto_rd"
