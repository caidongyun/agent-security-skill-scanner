#!/bin/bash
# agent-security-skill-scanner 安装脚本

set -e

echo "=========================================="
echo "技能安全扫描器 - 安装"
echo "=========================================="
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误：需要 Python 3"
    exit 1
fi

echo "✅ Python 版本：$(python3 --version)"
echo ""

# 创建虚拟环境 (可选)
if [ ! -d ".venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv .venv
    echo "✅ 虚拟环境已创建"
    echo ""
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source .venv/bin/activate

# 安装依赖 (本技能无外部依赖)
echo "检查依赖..."
echo "✅ 本技能无需外部依赖"
echo ""

# 设置执行权限
echo "设置执行权限..."
chmod +x cli.py 2>/dev/null || true
chmod +x scripts/*.sh 2>/dev/null || true
echo "✅ 执行权限已设置"
echo ""

# 验证安装
echo "验证安装..."
if [ -f "cli.py" ] && [ -f "SKILL.md" ] && [ -f "detectors/malware.py" ]; then
    echo "✅ 核心文件完整"
else
    echo "❌ 核心文件缺失"
    exit 1
fi

echo ""
echo "=========================================="
echo "✅ 安装完成！"
echo "=========================================="
echo ""
echo "使用方法:"
echo "  source .venv/bin/activate"
echo "  python cli.py scan <技能目录>"
echo ""
echo "示例:"
echo "  python cli.py scan skills/suspicious-skill/"
echo "  python cli.py scan-all skills/"
echo ""
