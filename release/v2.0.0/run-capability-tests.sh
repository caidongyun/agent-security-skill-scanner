#!/bin/bash
# 扫描器 v2.0.0 能力验证测试脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCANNER="$SCRIPT_DIR/scanner_cli.py"
RESULTS_DIR="$SCRIPT_DIR/test-results"

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo -e "[$(date '+%H:%M:%S')] $1"
}

# 创建结果目录
mkdir -p "$RESULTS_DIR"

log "${YELLOW}========================================${NC}"
log "${YELLOW}扫描器 v2.0.0 能力验证测试${NC}"
log "${YELLOW}========================================${NC}"
echo

# 测试 1: 恶意代码检出
log "测试 1: 恶意代码检出能力..."
python3 "$SCANNER" scan \
    scripts/samples/standard_malicious_skills/ \
    --threads 8 \
    --output "$RESULTS_DIR/malicious-detection.json" 2>&1 | tail -15
echo

# 测试 2: 误报率测试
log "测试 2: 误报率测试..."
python3 "$SCANNER" scan \
    scripts/samples/real_skills/ \
    --threads 8 \
    --output "$RESULTS_DIR/false-positive-test.json" 2>&1 | tail -15
echo

# 测试 3: 代码安全测试
log "测试 3: 代码安全样本测试..."
python3 "$SCANNER" scan \
    scripts/samples/code_security/ \
    --threads 8 \
    --output "$RESULTS_DIR/code-security-test.json" 2>&1 | tail -15
echo

# 测试 4: 并发性能测试
log "测试 4: 并发性能测试..."
for threads in 4 8 16; do
    log "  - $threads 线程测试..."
    python3 "$SCANNER" scan \
        tests/samples/ \
        --threads $threads \
        --output "$RESULTS_DIR/perf-${threads}threads.json" 2>&1 | grep "速度"
done
echo

# 测试 5: 压力测试
log "测试 5: 全量样本压力测试..."
python3 "$SCANNER" scan \
    scripts/samples/ \
    --threads 16 \
    --output "$RESULTS_DIR/full-stress-test.json" 2>&1 | tail -20
echo

# 生成测试报告
log "${YELLOW}生成测试报告...${NC}"
cat > "$RESULTS_DIR/CAPABILITY-TEST-REPORT.md" << 'EOF'
# 扫描器 v2.0.0 能力验证报告

> 测试日期：$(date +%Y-%m-%d)
> 扫描器版本：v2.0.0

## 测试结果

### 1. 恶意代码检出
文件：malicious-detection.json

### 2. 误报率测试
文件：false-positive-test.json

### 3. 代码安全测试
文件：code-security-test.json

### 4. 并发性能测试
文件：perf-4threads.json, perf-8threads.json, perf-16threads.json

### 5. 压力测试
文件：full-stress-test.json

## 结论
待分析...
EOF

log "${GREEN}========================================${NC}"
log "${GREEN}测试完成！${NC}"
log "${GREEN}结果目录：$RESULTS_DIR${NC}"
log "${GREEN}========================================${NC}"
