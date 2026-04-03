#!/bin/bash
# Agent Security Skill Scanner - 测试脚本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🧪 Agent Security Skill Scanner - 测试套件"
echo "=========================================="

# 创建测试报告目录
mkdir -p reports/test

# 测试统计
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# 测试函数
run_test() {
    local test_name="$1"
    local test_path="$2"
    local expected_result="$3"  # "malicious" or "benign"
    
    echo ""
    echo "📋 测试：$test_name"
    echo "路径：$test_path"
    
    if [ ! -d "$test_path" ] && [ ! -f "$test_path" ]; then
        echo "⚠️  跳过（路径不存在）"
        return
    fi
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    # 运行扫描
    local start_time=$(date +%s.%N)
    local result=$(python3 multi_language_scanner.py "$test_path" --quick --json 2>/dev/null)
    local end_time=$(date +%s.%N)
    local duration=$(echo "$end_time - $start_time" | bc)
    
    # 解析结果
    local detected=$(echo "$result" | grep -o '"threat_level"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1)
    
    if [ "$expected_result" == "malicious" ]; then
        if [[ "$detected" == *"high"* ]] || [[ "$detected" == *"critical"* ]]; then
            echo "✅ 通过（检出恶意）"
            PASSED_TESTS=$((PASSED_TESTS + 1))
        else
            echo "❌ 失败（未检出恶意）"
            FAILED_TESTS=$((FAILED_TESTS + 1))
        fi
    else
        if [[ "$detected" == *"low"* ]] || [[ "$detected" == *"none"* ]] || [ -z "$detected" ]; then
            echo "✅ 通过（无误报）"
            PASSED_TESTS=$((PASSED_TESTS + 1))
        else
            echo "❌ 失败（误报）"
            FAILED_TESTS=$((FAILED_TESTS + 1))
        fi
    fi
    
    echo "耗时：${duration}s"
}

# 测试恶意样本
echo ""
echo "=== 恶意样本检测测试 ==="
if [ -d "samples/malicious" ]; then
    run_test "Python 恶意样本" "samples/malicious/" "malicious"
elif [ -d "samples/python_malicious" ]; then
    run_test "Python 恶意样本" "samples/python_malicious/" "malicious"
fi

# 测试良性样本
echo ""
echo "=== 良性样本误报测试 ==="
if [ -d "samples/benign" ]; then
    run_test "Python 良性样本" "samples/benign/" "benign"
elif [ -d "samples/python_safe" ]; then
    run_test "Python 良性样本" "samples/python_safe/" "benign"
fi

# 测试 JavaScript 样本
echo ""
echo "=== JavaScript 样本测试 ==="
if [ -d "samples/js_malicious" ]; then
    run_test "JS 恶意样本" "samples/js_malicious/" "malicious"
fi

if [ -d "samples/js_safe" ]; then
    run_test "JS 良性样本" "samples/js_safe/" "benign"
fi

# 测试 Shell 样本
echo ""
echo "=== Shell 样本测试 ==="
if [ -d "samples/shell_malicious" ]; then
    run_test "Shell 恶意样本" "samples/shell_malicious/" "malicious"
fi

# 测试 PowerShell 样本
echo ""
echo "=== PowerShell 样本测试 ==="
if [ -d "samples/powershell_malicious" ]; then
    run_test "PowerShell 恶意样本" "samples/powershell_malicious/" "malicious"
fi

# 测试供应链检测
echo ""
echo "=== 供应链安全检测 ==="
if [ -f "expert_mode/litellm_detector.py" ]; then
    echo "✅ LiteLLM 检测器存在"
    PASSED_TESTS=$((PASSED_TESTS + 1))
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
else
    echo "❌ LiteLLM 检测器不存在"
    FAILED_TESTS=$((FAILED_TESTS + 1))
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
fi

if [ -f "expert_mode/exfil_detector.py" ]; then
    echo "✅ 数据外传检测器存在"
    PASSED_TESTS=$((PASSED_TESTS + 1))
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
else
    echo "❌ 数据外传检测器不存在"
    FAILED_TESTS=$((FAILED_TESTS + 1))
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
fi

# 测试规则库
echo ""
echo "=== 规则库检查 ==="
RULE_COUNT=$(find rules/ -name "*.yaml" -o -name "*.json" 2>/dev/null | wc -l)
echo "规则文件数量：$RULE_COUNT"
if [ "$RULE_COUNT" -gt 100 ]; then
    echo "✅ 规则库完整"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo "⚠️  规则库不完整"
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))

# 生成测试报告
echo ""
echo "=========================================="
echo "📊 测试结果汇总"
echo "=========================================="
echo "总测试数：$TOTAL_TESTS"
echo "✅ 通过：$PASSED_TESTS"
echo "❌ 失败：$FAILED_TESTS"

if [ $TOTAL_TESTS -gt 0 ]; then
    PASS_RATE=$(echo "scale=2; $PASSED_TESTS * 100 / $TOTAL_TESTS" | bc)
    echo "通过率：${PASS_RATE}%"
fi

echo ""

# 保存测试报告
cat > reports/test/test_report_$(date +%Y%m%d_%H%M%S).md << EOF
# 测试报告

**时间**: $(date)
**总测试数**: $TOTAL_TESTS
**通过**: $PASSED_TESTS
**失败**: $FAILED_TESTS
**通过率**: ${PASS_RATE}%
EOF

if [ $FAILED_TESTS -eq 0 ]; then
    echo "🎉 所有测试通过！"
    exit 0
else
    echo "⚠️  部分测试失败，请检查报告"
    exit 1
fi
