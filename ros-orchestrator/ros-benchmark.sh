#!/bin/bash
# ROS Benchmark - 核心性能基线测试
# 只测 3 个核心指标：吞吐量、延迟、重试成功率

set -o pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROS_SCRIPT="$SCRIPT_DIR/ros-taskmaster.sh"
RESULTS_DIR="$SCRIPT_DIR/benchmark-results"
mkdir -p "$RESULTS_DIR"

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() { echo -e "${BLUE}[BENCHMARK]${NC} $(date '+%H:%M:%S') $*"; }
success() { echo -e "${GREEN}[PASS]${NC} $*"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
fail() { echo -e "${RED}[FAIL]${NC} $*"; }

# ========== 测试 1: 任务吞吐量 ==========
test_throughput() {
    log "测试 1: 任务吞吐量 (100 个简单任务)"
    echo "=================================================="
    
    local start_time=$(date +%s.%N)
    local task_count=100
    local success_count=0
    
    for i in $(seq 1 $task_count); do
        if "$ROS_SCRIPT" run "bench_task_$i" "echo task_$i" >/dev/null 2>&1; then
            success_count=$((success_count + 1))
        fi
    done
    
    local end_time=$(date +%s.%N)
    local duration=$(echo "$end_time - $start_time" | bc)
    local throughput=$(echo "scale=2; $success_count / $duration" | bc)
    
    echo ""
    echo "结果:"
    echo "  任务数：$success_count/$task_count"
    echo "  总耗时：${duration}s"
    echo "  吞吐量：${throughput} 任务/秒"
    echo ""
    
    # 保存结果
    echo "{\"test\":\"throughput\",\"tasks\":$success_count,\"duration\":$duration,\"throughput\":$throughput}" > "$RESULTS_DIR/throughput.json"
    
    # 评估
    if (( $(echo "$throughput >= 50" | bc -l) )); then
        success "✅ 吞吐量达标 (≥50 任务/秒)"
        return 0
    else
        warn "⚠️  吞吐量未达标 (<50 任务/秒)"
        return 1
    fi
}

# ========== 测试 2: LLM 调用延迟 ==========
test_llm_latency() {
    log "测试 2: LLM 调用延迟 (10 次调用)"
    echo "=================================================="
    
    local latencies=()
    local call_count=10
    
    for i in $(seq 1 $call_count); do
        local start=$(date +%s.%N)
        "$ROS_SCRIPT" call planning "test_$i" >/dev/null 2>&1
        local end=$(date +%s.%N)
        local latency=$(echo "$end - $start" | bc)
        latencies+=($latency)
        echo "  调用 $i: ${latency}s"
    done
    
    # 计算统计值
    local sorted=($(printf '%s\n' "${latencies[@]}" | sort -n))
    local min=${sorted[0]}
    local max=${sorted[-1]}
    local p50=${sorted[5]}
    local p99=${sorted[9]}
    
    local sum=0
    for l in "${latencies[@]}"; do sum=$(echo "$sum + $l" | bc); done
    local avg=$(echo "scale=3; $sum / $call_count" | bc)
    
    echo ""
    echo "结果:"
    echo "  最小：${min}s"
    echo "  平均：${avg}s"
    echo "  P50: ${p50}s"
    echo "  P99: ${p99}s"
    echo "  最大：${max}s"
    echo ""
    
    # 保存结果
    cat > "$RESULTS_DIR/latency.json" << EOF
{"test":"latency","min":$min,"avg":$avg,"p50":$p50,"p99":$p99,"max":$max}
EOF
    
    # 评估
    if (( $(echo "$p99 <= 5" | bc -l) )); then
        success "✅ LLM 延迟达标 (p99 ≤5s)"
        return 0
    else
        warn "⚠️  LLM 延迟未达标 (p99 >5s)"
        return 1
    fi
}

# ========== 测试 3: 重试成功率 ==========
test_retry_success() {
    log "测试 3: 重试成功率 (模拟 50% 失败率)"
    echo "=================================================="
    
    # 创建模拟失败脚本
    local test_script="$RESULTS_DIR/flaky_task.sh"
    cat > "$test_script" << 'SCRIPT'
#!/bin/bash
# 50% 失败率的模拟任务
if [ $((RANDOM % 2)) -eq 0 ]; then
    exit 1
else
    echo "成功"
    exit 0
fi
SCRIPT
    chmod +x "$test_script"
    
    local total_attempts=50
    local success_count=0
    
    for i in $(seq 1 $total_attempts); do
        # 使用 ROS 的重试机制 (3 次重试)
        if "$ROS_SCRIPT" run "retry_test_$i" "bash $test_script" >/dev/null 2>&1; then
            success_count=$((success_count + 1))
        fi
    done
    
    local success_rate=$(echo "scale=2; $success_count * 100 / $total_attempts" | bc)
    
    echo ""
    echo "结果:"
    echo "  总任务数：$total_attempts"
    echo "  成功数：$success_count"
    echo "  成功率：${success_rate}%"
    echo ""
    
    # 保存结果
    echo "{\"test\":\"retry\",\"total\":$total_attempts,\"success\":$success_count,\"rate\":$success_rate}" > "$RESULTS_DIR/retry.json"
    
    # 评估
    if (( $(echo "$success_rate >= 90" | bc -l) )); then
        success "✅ 重试成功率达标 (≥90%)"
        return 0
    else
        warn "⚠️  重试成功率未达标 (<90%)"
        return 1
    fi
}

# ========== 生成报告 ==========
generate_report() {
    log "生成 Benchmark 报告"
    echo "=================================================="
    echo ""
    
    local report_file="$RESULTS_DIR/benchmark-$(date +%Y%m%d_%H%M%S).md"
    
    cat > "$report_file" << EOF
# ROS Benchmark 报告

**时间:** $(date)
**版本:** ROS-TaskMaster v2.1

## 测试结果

### 1. 任务吞吐量
\`\`\`
$(cat "$RESULTS_DIR/throughput.json" 2>/dev/null | python3 -m json.tool 2>/dev/null || echo "无数据")
\`\`\`

### 2. LLM 调用延迟
\`\`\`
$(cat "$RESULTS_DIR/latency.json" 2>/dev/null | python3 -m json.tool 2>/dev/null || echo "无数据")
\`\`\`

### 3. 重试成功率
\`\`\`
$(cat "$RESULTS_DIR/retry.json" 2>/dev/null | python3 -m json.tool 2>/dev/null || echo "无数据")
\`\`\`

## 总体评估

| 指标 | 目标 | 实际 | 状态 |
|------|------|------|------|
| 吞吐量 | ≥50 任务/秒 | - | - |
| LLM p99 | ≤5s | - | - |
| 重试成功率 | ≥90% | - | - |

## 建议

- 待测试完成后填写
EOF
    
    echo "报告已保存：$report_file"
    echo ""
}

# ========== 主入口 ==========
show_help() {
    cat << EOF
ROS Benchmark - 核心性能基线测试

用法: $(basename "$0") <命令>

命令:
  all           运行全部测试
  throughput    只测吞吐量
  latency       只测延迟
  retry         只测重试率
  report        生成报告
  help          显示帮助

示例:
  $(basename "$0") all
  $(basename "$0") throughput
  $(basename "$0") report
EOF
}

case "${1:-all}" in
    all)
        echo "=================================================="
        echo "ROS-TaskMaster v2.1 Benchmark"
        echo "=================================================="
        echo ""
        
        test_throughput
        echo ""
        test_llm_latency
        echo ""
        test_retry_success
        echo ""
        generate_report
        
        echo "=================================================="
        echo "✅ Benchmark 完成！"
        echo "=================================================="
        ;;
    throughput)
        test_throughput
        ;;
    latency)
        test_llm_latency
        ;;
    retry)
        test_retry_success
        ;;
    report)
        generate_report
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        show_help
        exit 1
        ;;
esac
