#!/bin/bash
#
# 🔍 自动化 Benchmark 检查脚本
# 用途：定期执行 Benchmark 测试，验证扫描器质量
#

set -e

# 配置
SCANNER_DIR="/home/cdy/.openclaw/workspace/agent-security-skill-scanner-master"
BENCHMARK_DIR="/home/cdy/Desktop/security-benchmark/samples"
OUTPUT_DIR="/home/cdy/Desktop/security-benchmark"
REPORT_DIR="/home/cdy/.openclaw/workspace/skill-detect-report"

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 主函数
main() {
    local test_mode="${1:-quick}"  # quick | full
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local output_file="${OUTPUT_DIR}/BENCHMARK_AUTO_${timestamp}.json"
    local report_file="${REPORT_DIR}/BENCHMARK_AUTO_$(date +%Y-%m-%d).md"
    
    log_info "🚀 开始自动化 Benchmark 检查"
    log_info "   模式：${test_mode}"
    log_info "   输出：${output_file}"
    
    cd "${SCANNER_DIR}"
    
    # 执行扫描
    if [ "${test_mode}" == "quick" ]; then
        log_info "📊 执行快速测试 (malicious-new 样本集)"
        python3 scanner.py "${BENCHMARK_DIR}/malicious-new/" \
            --extensions ".py,.python,.js,.javascript,.sh,.bash,.yaml,.yml,.json,.go,.rb,.php" \
            --output json \
            --output-file "${output_file}" \
            --workers 8 \
            2>&1 | tail -5
        
    elif [ "${test_mode}" == "full" ]; then
        log_info "📊 执行全量测试 (from-templates 样本集)"
        python3 scanner.py "${BENCHMARK_DIR}/from-templates/" \
            --extensions ".py,.python,.js,.javascript,.sh,.bash,.yaml,.yml,.json,.go,.rb,.php" \
            --output json \
            --output-file "${output_file}" \
            --workers 16 \
            2>&1 | tail -5
    fi
    
    # 分析结果
    log_info "📈 分析测试结果..."
    python3 << EOF
import json
import sys
from datetime import datetime

with open('${output_file}', 'r') as f:
    data = json.load(f)

results = data.get('results', [])
total = len(results)
safe = sum(1 for r in results if r.get('risk_level') == 'SAFE')
high = sum(1 for r in results if r.get('risk_level') == 'HIGH')
critical = sum(1 for r in results if r.get('risk_level') == 'CRITICAL')
detected = total - safe

detection_rate = (detected / total * 100) if total > 0 else 0

print(f"\n{'='*60}")
print(f"📊 Benchmark 测试结果")
print(f"{'='*60}")
print(f"总样本：{total}")
print(f"检出：{detected} ({detection_rate:.2f}%)")
print(f"HIGH: {high}")
print(f"CRITICAL: {critical}")
print(f"SAFE: {safe}")
print(f"{'='*60}")

# 质量检查
issues = []
if detection_rate < 5:
    issues.append(f"检出率过低 ({detection_rate:.2f}% < 5%)")
if critical > 0:
    issues.append(f"发现 {critical} 个 CRITICAL 样本需要审查")

if issues:
    print(f"\n⚠️  质量问题:")
    for issue in issues:
        print(f"  - {issue}")
    sys.exit(1)
else:
    print(f"\n✅ 质量检查通过")
    sys.exit(0)
EOF
    
    local check_result=$?
    
    # 生成报告
    log_info "📝 生成测试报告..."
    cat > "${report_file}" << REPORT
# 自动化 Benchmark 检查报告

**日期**: $(date +%Y-%m-%d)  
**模式**: ${test_mode}  
**时间**: $(date +%H:%M:%S)

---

## 📊 测试结果

| 指标 | 值 |
|------|-----|
| 总样本 | ${total} |
| 检出 | ${detected} |
| 检出率 | ${detection_rate:.2f}% |
| HIGH | ${high} |
| CRITICAL | ${critical} |
| SAFE | ${safe} |

---

## ✅ 质量检查

$(if [ $check_result -eq 0 ]; then echo "**状态**: 通过 ✅"; else echo "**状态**: 失败 ❌"; fi)

---

## 📁 输出文件

- 原始数据：\`${output_file}\`
- 本报告：\`${report_file}\`

---

*自动生成于 $(date)*
REPORT
    
    # 同步到 Gitee
    log_info "📡 同步报告到 Gitee..."
    cd "${REPORT_DIR}"
    git add "${report_file}" 2>/dev/null || true
    git commit -m "auto: 添加自动化 Benchmark 检查报告 ($(date +%Y-%m-%d))" 2>/dev/null || true
    git push origin main 2>&1 | head -5 || log_warn "推送失败，请手动同步"
    
    log_info "✅ 自动化检查完成"
    log_info "   报告：${report_file}"
    
    return $check_result
}

# 执行
main "$@"
