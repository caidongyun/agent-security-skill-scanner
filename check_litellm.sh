#!/bin/bash
# LiteLLM 供应链投毒快速排查脚本
# 用法：./check_litellm.sh

set -e

echo "========================================"
echo "LiteLLM 供应链投毒快速排查"
echo "========================================"
echo

# 1. 检查版本
echo "[1/6] 检查 LiteLLM 版本..."
if command -v pip &> /dev/null; then
    VERSION=$(pip show litellm 2>/dev/null | grep "^Version:" | cut -d' ' -f2)
    if [ -z "$VERSION" ]; then
        echo "  ✅ 未安装 litellm"
    elif [ "$VERSION" = "1.82.7" ] || [ "$VERSION" = "1.82.8" ]; then
        echo "  🔴 已安装投毒版本：$VERSION"
        echo "     立即执行：pip install litellm==1.82.6"
    else
        echo "  ✅ 版本安全：$VERSION"
    fi
else
    echo "  ⚠️ pip 未安装，跳过检查"
fi
echo

# 2. 检查 .pth 文件
echo "[2/6] 检查恶意 .pth 文件..."
PTH_FILES=$(find ~/.local/lib/python* /usr/local/lib/python* /opt/homebrew/lib/python* \
    -name "litellm_init.pth" 2>/dev/null || true)
if [ -n "$PTH_FILES" ]; then
    echo "  🔴 发现恶意文件:"
    echo "$PTH_FILES"
    echo "     执行：rm -f $PTH_FILES"
else
    echo "  ✅ 未发现 litellm_init.pth"
fi
echo

# 3. 检查持久化后门
echo "[3/6] 检查 systemd 后门..."
if [ -d ~/.config/sysmon ]; then
    echo "  🔴 发现可疑目录：~/.config/sysmon/"
    echo "     执行：rm -rf ~/.config/sysmon/"
else
    echo "  ✅ 未发现 sysmon 目录"
fi

if systemctl list-unit-files 2>/dev/null | grep -q "sysmon"; then
    echo "  🔴 发现可疑服务：sysmon.service"
    echo "     执行：sudo systemctl disable --now sysmon"
else
    echo "  ✅ 未发现 sysmon.service"
fi
echo

# 4. 检查 C2 通信
echo "[4/6] 检查 C2 域名连接..."
if netstat -an 2>/dev/null | grep -qE "models\.litellm\.cloud|checkmarx\.zone"; then
    echo "  🔴 发现可疑 C2 连接!"
    echo "     立即断网并溯源"
else
    echo "  ✅ 未发现 C2 通信"
fi
echo

# 5. 检查 K8s 异常 Pod
echo "[5/6] 检查 Kubernetes 异常 Pod..."
if command -v kubectl &> /dev/null; then
    SUSPICIOUS_PODS=$(kubectl get pods -A -o jsonpath='{range .items[*]}{.metadata.name}{"\n"}{end}' 2>/dev/null | \
        grep -E "node-setup-" || true)
    if [ -n "$SUSPICIOUS_PODS" ]; then
        echo "  🔴 发现可疑 Pod:"
        echo "$SUSPICIOUS_PODS"
        echo "     执行：kubectl delete pod $SUSPICIOUS_PODS -n kube-system"
    else
        echo "  ✅ 未发现异常 Pod"
    fi
else
    echo "  ⚠️ kubectl 未安装，跳过检查"
fi
echo

# 6. 检查敏感文件访问
echo "[6/6] 检查敏感文件最近访问..."
SUSPICIOUS_ACCESS=false
for file in ~/.ssh/id_rsa ~/.aws/credentials ~/.kube/config; do
    if [ -f "$file" ]; then
        ATIME=$(stat -c %Y "$file" 2>/dev/null || stat -f %m "$file" 2>/dev/null)
        NOW=$(date +%s)
        HOURS=$(( (NOW - ATIME) / 3600 ))
        if [ "$HOURS" -lt 24 ]; then
            echo "  ⚠️ $file 在 24 小时内被访问 (${HOURS}小时前)"
            SUSPICIOUS_ACCESS=true
        fi
    fi
done

if [ "$SUSPICIOUS_ACCESS" = true ]; then
    echo "     建议：检查系统日志，确认是否有异常进程"
else
    echo "  ✅ 敏感文件无异常访问"
fi
echo

# 总结
echo "========================================"
echo "排查完成"
echo "========================================"
echo
echo "处置建议:"
echo "  1. 如发现投毒版本，立即回滚：pip install litellm==1.82.6"
echo "  2. 删除恶意文件：rm -f ~/.local/lib/python*/site-packages/litellm_init.pth"
echo "  3. 更换所有凭据：SSH/AWS/Azure/K8s/数据库/钱包"
echo "  4. 检查系统日志：journalctl -xe | grep -i sysmon"
echo "  5. 运行完整扫描：python3 expert_mode/litellm_detector.py ~/.local/lib/python*/site-packages/"
echo
