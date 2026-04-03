#!/bin/bash
# 供应链安全扫描器 - 安装脚本
# 用法：./install_daemon.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_NAME="supply-chain-scanner"
SERVICE_FILE="$SCRIPT_DIR/${SERVICE_NAME}.service"
SYSTEMD_DIR="/etc/systemd/system"

echo "========================================"
echo "供应链安全扫描器 - 安装向导"
echo "========================================"
echo

# 1. 检查依赖
echo "[1/5] 检查依赖..."

check_dep() {
    if command -v "$1" &> /dev/null; then
        echo "  ✅ $1"
    else
        echo "  ❌ $1 (未安装)"
        MISSING_DEPS+=("$1")
    fi
}

MISSING_DEPS=()
check_dep python3
check_dep pip
check_dep git
check_dep systemctl

if [ ${#MISSING_DEPS[@]} -gt 0 ]; then
    echo ""
    echo "⚠️  缺少依赖：${MISSING_DEPS[*]}"
    echo "请先安装缺失的依赖"
    exit 1
fi

# 2. 安装 Python 依赖
echo ""
echo "[2/5] 安装 Python 依赖..."
pip install feedparser requests pyyaml --quiet
echo "  ✅ 依赖已安装"

# 3. 创建目录
echo ""
echo "[3/5] 创建目录..."
mkdir -p "$SCRIPT_DIR/logs"
mkdir -p "$SCRIPT_DIR/intel"
mkdir -p "$SCRIPT_DIR/intel/cache"
echo "  ✅ 目录已创建"

# 4. 安装 systemd 服务
echo ""
echo "[4/5] 安装 systemd 服务..."

if [ -f "$SERVICE_FILE" ]; then
    # 复制服务文件
    sudo cp "$SERVICE_FILE" "$SYSTEMD_DIR/"
    
    # 重新加载 systemd
    sudo systemctl daemon-reload
    
    # 启用服务
    sudo systemctl enable "$SERVICE_NAME"
    
    echo "  ✅ systemd 服务已安装"
else
    echo "  ❌ 服务文件不存在：$SERVICE_FILE"
    exit 1
fi

# 5. 启动服务
echo ""
echo "[5/5] 启动服务..."

sudo systemctl start "$SERVICE_NAME"

if sudo systemctl is-active --quiet "$SERVICE_NAME"; then
    echo "  ✅ 服务已启动"
else
    echo "  ⚠️  服务启动失败，请检查日志"
fi

echo ""
echo "========================================"
echo "安装完成!"
echo "========================================"
echo ""
echo "服务管理:"
echo "  查看状态：sudo systemctl status $SERVICE_NAME"
echo "  停止服务：sudo systemctl stop $SERVICE_NAME"
echo "  重启服务：sudo systemctl restart $SERVICE_NAME"
echo "  查看日志：tail -f $SCRIPT_DIR/logs/daemon.log"
echo ""
echo "手动扫描:"
echo "  cd $SCRIPT_DIR"
echo "  ./supply_chain_daemon.sh scan"
echo ""
echo "威胁情报:"
echo "  查看 IoC: cat $SCRIPT_DIR/intel/ioc.json | jq '.domains'"
echo "  手动更新：python3 $SCRIPT_DIR/expert_mode/intel_fetcher.py"
echo ""
