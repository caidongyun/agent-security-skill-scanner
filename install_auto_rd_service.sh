#!/bin/bash
# ==============================================================================
# 安装自治研发系统 systemd 服务
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_FILE="$SCRIPT_DIR/auto_rd_scanner.service"
SYSTEM_SERVICE="/etc/systemd/system/auto_rd_scanner.service"

echo "=============================================================================="
echo "       🛡️  安装自治研发系统服务"
echo "=============================================================================="
echo ""

# 1. 停止所有冲突进程
echo "🛑 步骤 1: 停止所有冲突进程..."
pkill -f "auto_rd_scanner.py" 2>/dev/null || true
pkill -f "enhanced_orchestrator" 2>/dev/null || true
pkill -f "progress_reporter" 2>/dev/null || true
pkill -f "ros_" 2>/dev/null || true
sleep 2
echo "✅ 冲突进程已停止"
echo ""

# 2. 清理锁文件
echo "🧹 步骤 2: 清理锁文件..."
rm -f /tmp/auto_rd_scanner.lock
echo "✅ 锁文件已清理"
echo ""

# 3. 清理规则目录
echo "🔒 步骤 3: 清理规则目录..."
cd "$SCRIPT_DIR"
./protect_rules.sh --clean
./protect_rules.sh --lock
echo ""

# 4. 复制服务文件
echo "📋 步骤 4: 安装 systemd 服务..."
sudo cp "$SERVICE_FILE" "$SYSTEM_SERVICE"
sudo systemctl daemon-reload
echo "✅ 服务已安装"
echo ""

# 5. 启用服务
echo "▶️  步骤 5: 启用服务..."
sudo systemctl enable auto_rd_scanner
echo "✅ 服务已启用 (开机自启)"
echo ""

# 6. 显示状态
echo "📊 服务状态:"
sudo systemctl status auto_rd_scanner --no-pager
echo ""

echo "=============================================================================="
echo "✅ 安装完成!"
echo "=============================================================================="
echo ""
echo "常用命令:"
echo "  启动服务：sudo systemctl start auto_rd_scanner"
echo "  停止服务：sudo systemctl stop auto_rd_scanner"
echo "  查看状态：sudo systemctl status auto_rd_scanner"
echo "  查看日志：sudo journalctl -u auto_rd_scanner -f"
echo "  禁用服务：sudo systemctl disable auto_rd_scanner"
echo ""
echo "=============================================================================="
