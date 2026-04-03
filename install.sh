#!/bin/bash
# Agent Security Skill Scanner - 安装脚本

set -e

echo "🚀 Agent Security Skill Scanner - 安装程序"
echo "=========================================="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 检查 Python 版本
echo ""
echo "📋 检查 Python 环境..."
python3 --version || { echo "❌ Python3 未安装"; exit 1; }

# 创建必要目录
echo ""
echo "📁 创建必要目录..."
mkdir -p reports logs models

# 安装 Python 依赖
echo ""
echo "📦 安装 Python 依赖..."
if [ -f "requirements.txt" ]; then
    pip3 install -r requirements.txt -q
    echo "✅ 依赖安装完成"
else
    echo "⚠️  requirements.txt 不存在，跳过依赖安装"
fi

# 创建配置文件
echo ""
echo "⚙️  创建配置文件..."
if [ ! -f "config.yaml" ]; then
    cp config.yaml.template config.yaml
    echo "✅ 配置文件已创建 (config.yaml)"
else
    echo "✅ 配置文件已存在"
fi

# 创建快速启动脚本
echo ""
echo "🔧 创建快速启动脚本..."

cat > scan.sh << 'EOF'
#!/bin/bash
# 快速扫描入口
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
python3 multi_language_scanner.py "$@"
EOF
chmod +x scan.sh

cat > test.sh << 'EOF'
#!/bin/bash
# 测试脚本
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🧪 运行测试套件..."

# 测试恶意样本
if [ -d "samples/malicious" ]; then
    echo ""
    echo "=== 测试恶意样本检测 ==="
    python3 multi_language_scanner.py samples/malicious/ --quick
fi

# 测试良性样本
if [ -d "samples/benign" ]; then
    echo ""
    echo "=== 测试良性样本误报 ==="
    python3 multi_language_scanner.py samples/benign/ --quick
fi

echo ""
echo "✅ 测试完成"
EOF
chmod +x test.sh

echo "✅ 快速启动脚本已创建 (scan.sh, test.sh)"

# 检查 expert_mode
echo ""
echo "🔍 检查增强功能模块..."
if [ -d "expert_mode" ]; then
    echo "✅ expert_mode 目录存在"
    ls expert_mode/ | head -5
else
    echo "⚠️  expert_mode 目录不存在"
fi

# 完成
echo ""
echo "=========================================="
echo "✅ 安装完成！"
echo ""
echo "📖 下一步:"
echo "   1. 查看 README.md 了解使用方法"
echo "   2. 运行 ./scan.sh /path/to/scan 开始扫描"
echo "   3. 运行 ./test.sh 测试检测能力"
echo ""
echo "📚 文档:"
echo "   - README.md              - 使用文档"
echo "   - MERGE_README.md        - 合并说明"
echo "   - ML_TRAINING_PLAN.md    - ML 训练计划"
echo ""
