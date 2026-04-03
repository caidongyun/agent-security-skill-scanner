#!/bin/bash
# ROS-01: 规则优化循环 - 持续降低误报率
# 目标：FP < 5%, 检测率 > 98%

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $(date '+%H:%M:%S') $*"; }
log_success() { echo -e "${GREEN}[OK]${NC} $(date '+%H:%M:%S') $*"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $(date '+%H:%M:%S') $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $(date '+%H:%M:%S') $*"; }

echo "============================================================"
echo "🔄 ROS-01: 规则优化循环"
echo "============================================================"
echo ""

# ========== Step 1: 生成规则 ==========
log_info "Step 1: 生成/合并规则..."
python3 fix_and_merge_rules.py
if [ $? -ne 0 ]; then
    log_error "规则合并失败"
    exit 1
fi
log_success "规则合并完成"
echo ""

# ========== Step 2: 规则分级 ==========
log_info "Step 2: 规则分级..."
python3 optimize_rules_v4.py
if [ $? -ne 0 ]; then
    log_error "规则分级失败"
    exit 1
fi
log_success "规则分级完成"
echo ""

# ========== Step 3: L1 规则测试 ==========
log_info "Step 3: L1 规则扫描测试..."
cp rules/optimized/l1_high_confidence.yar scanner-master/output/rules/scanner_master_rules.yar
python3 scanner-master/ros-scanner-v2.py samples/malicious/ --workers 4 > /tmp/ros_scan_l1.log 2>&1
if [ $? -ne 0 ]; then
    log_error "L1 扫描失败"
    cat /tmp/ros_scan_l1.log
    exit 1
fi
log_success "L1 扫描完成"

# 提取结果
L1_RESULT=$(python3 -c "
import json, os, glob
files = sorted(glob.glob('output/ros-scan-v2-*.json'), key=lambda f: -os.path.getmtime('output/'+f))
if files:
    d = json.load(open('output/'+files[0]))
    acc = d.get('accuracy', {})
    print('{:.1f},{:.1f}'.format(
        acc.get('detection_rate', 0) * 100,
        acc.get('false_positive_rate', 0) * 100
    ))
")
L1_DR=$(echo $L1_RESULT | cut -d',' -f1)
L1_FP=$(echo $L1_RESULT | cut -d',' -f2)
echo "L1 结果：检测率 ${L1_DR}%, 误报率 ${L1_FP}%"
echo ""

# ========== Step 4: 评估阈值 ==========
log_info "Step 4: 评估优化效果..."

# 检查是否达标
FP_OK=$(python3 -c "print(1 if float($L1_FP) < 5.0 else 0)")
DR_OK=$(python3 -c "print(1 if float($L1_DR) > 98.0 else 0)")

if [ "$FP_OK" == "1" ] && [ "$DR_OK" == "1" ]; then
    log_success "✅ 优化达标！FP < 5%, DR > 98%"
    
    # 生成发布包
    log_info "生成发布包..."
    python3 release/prepare_release.py --version 3.1.0 --output release/v3.1.0
    log_success "发布包生成完成"
    
    # 生成报告
    log_info "生成优化报告..."
    python3 << 'EOF'
import json, os, datetime

files = sorted([f for f in os.listdir('output') if f.startswith('ros-scan-v2-') and f.endswith('.json')], 
               key=lambda f: -os.path.getmtime('output/'+f))
d = json.load(open('output/'+files[0]))
acc = d.get('accuracy', {})
findings = d.get('findings', {})

report = """# ROS-01 优化报告

**日期**: {}
**状态**: ✅ 达标

## 核心指标
- 检测率: {:.1f}% (> 98% ✅)
- 误报率: {:.1f}% (< 5% ✅)
- FP 数量: {:,}
- FN 数量: {:,}

## 规则统计
- L1 规则：{} 条
- L2 规则：{} 条
- L3 规则：{} 条

## 发布版本
- 版本：v3.1.0
- 位置：release/v3.1.0/
""".format(
    datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
    acc.get('detection_rate', 0) * 100,
    acc.get('false_positive_rate', 0) * 100,
    acc.get('false_positives', 0),
    acc.get('false_negatives', 0),
    len(open('rules/optimized/l1_high_confidence.yar').read().split('rule ')) - 1,
    len(open('rules/optimized/l2_medium_confidence.yar').read().split('rule ')) - 1 if os.path.exists('rules/optimized/l2_medium_confidence.yar') else 0,
    len(open('rules/optimized/l3_low_confidence.yar').read().split('rule ')) - 1
)

open('reports/ROS01_OPTIMIZATION_REPORT.md', 'w').write(report)
print('报告生成：reports/ROS01_OPTIMIZATION_REPORT.md')
EOF
    log_success "报告生成完成"
    
    echo ""
    echo "============================================================"
    echo "✅ ROS-01 优化完成 - 达标!"
    echo "============================================================"
    exit 0
else
    log_warn "⚠️  未达标，需要进一步优化"
    echo "  当前：FP=${L1_FP}% (目标 <5%), DR=${L1_DR}% (目标 >98%)"
    echo ""
fi

# ========== Step 5: 生成优化建议 ==========
log_info "Step 5: 生成优化建议..."

python3 << 'EOF'
import json, os, glob

files = sorted([f for f in os.listdir('output') if f.startswith('ros-scan-v2-') and f.endswith('.json')], 
               key=lambda f: -os.path.getmtime('output/'+f))
d = json.load(open('output/'+files[0]))
by_type = d.get('by_attack_type', {})

print("📋 优化建议:")
print("")
print("1. 高频误报规则 (建议移至 L3):")
for attack, count in sorted(by_type.items(), key=lambda x: -x[1])[:5]:
    print("   - {}: {:,} 次".format(attack, count))

print("")
print("2. 建议操作:")
print("   - 调整 FP_RATES 阈值，将高 FP 规则移至 L3")
print("   - 为高频误报规则添加例外条件")
print("   - 运行 ros-02-fine-tune.sh 进行精细调优")
EOF

echo ""
echo "============================================================"
echo "⚠️  ROS-01 优化完成 - 未达标，进入下一轮"
echo "============================================================"
echo ""
echo "下一步：运行 ros-02-fine-tune.sh 进行精细调优"
echo ""

exit 0
