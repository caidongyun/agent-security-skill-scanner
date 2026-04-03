#!/bin/bash
# ROS-02: 精细调优 - 针对高 FP 规则优化
# 目标：降低特定规则的误报率

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $(date '+%H:%M:%S') $*"; }
log_success() { echo -e "${GREEN}[OK]${NC} $(date '+%H:%M:%S') $*"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $(date '+%H:%M:%S') $*"; }

echo "============================================================"
echo "🔧 ROS-02: 精细调优"
echo "============================================================"
echo ""

# ========== Step 1: 分析高 FP 规则 ==========
log_info "Step 1: 分析高 FP 规则..."

python3 << 'EOF'
import json, os, glob

files = sorted([f for f in os.listdir('output') if f.startswith('ros-scan-v2-') and f.endswith('.json')], 
               key=lambda f: -os.path.getmtime('output/'+f))
if not files:
    print("无扫描结果，先运行 ros-01-rule-optimization.sh")
    exit(1)

d = json.load(open('output/'+files[0]))
by_type = d.get('by_attack_type', {})
total = sum(by_type.values())

print("📊 高 FP 规则分析:")
print("")
for i, (attack, count) in enumerate(sorted(by_type.items(), key=lambda x: -x[1])[:10], 1):
    pct = count / total * 100
    print("{:2d}. {:40s} {:6,} ({:5.1f}%)".format(i, attack, count, pct))

# 生成优化配置
config = {
    'high_fp_rules': [attack for attack, _ in sorted(by_type.items(), key=lambda x: -x[1])[:5]],
    'fp_threshold': 0.05,
    'dr_threshold': 0.98,
}
json.dump(config, open('config/optimization_config.json', 'w'), indent=2)
print("")
print("✅ 生成优化配置：config/optimization_config.json")
EOF

if [ ! -f config/optimization_config.json ]; then
    mkdir -p config
fi

echo ""

# ========== Step 2: 调整 FP 阈值 ==========
log_info "Step 2: 调整规则分级阈值..."

python3 << 'EOF'
import json

config = json.load(open('config/optimization_config.json'))
high_fp = config.get('high_fp_rules', [])

print("高 FP 规则列表:")
for rule in high_fp:
    print("  - {}".format(rule))

# 生成优化后的 FP_RATES
fp_rates = {}
for rule in high_fp:
    fp_rates[rule] = 0.70  # 提高 FP 估计，强制移至 L3

print("")
print("调整后的 FP_RATES:")
for rule, rate in fp_rates.items():
    print("  '{}': {:.2f}".format(rule, rate))

# 保存到临时文件供 optimize_rules_v5.py 使用
json.dump(fp_rates, open('/tmp/custom_fp_rates.json', 'w'), indent=2)
print("")
print("✅ 生成自定义 FP 配置：/tmp/custom_fp_rates.json")
EOF

echo ""

# ========== Step 3: 运行优化 ==========
log_info "Step 3: 运行优化脚本..."

python3 << 'EOF'
import re, os, json

# 加载自定义 FP 率
custom_fp = json.load(open('/tmp/custom_fp_rates.json'))

RULES_DIR = 'rules/scanner_v3/yara'
OUTPUT_DIR = 'rules/optimized'

FP_RATES = {
    'Agent_Curl': 0.60, 'Agent_Credential': 0.55, 'CRED_': 0.50,
    'Agent_Persistence': 0.45, 'Agent_Memory': 0.40, 'Agent_Resource': 0.35,
    'JS_': 0.45, 'PS_': 0.40, 'BASH_': 0.35,
    'Agent_Data_Exfil': 0.30, 'EXFIL_': 0.25, 'Agent_SupplyChain': 0.30,
    'Agent_Evasion': 0.20,
    'Shell_ReverseShell': 0.05, 'Shell_PrivEsc': 0.08,
    'Impact_DataDestruction': 0.03, 'Impact_Ransomware': 0.02,
    'Malicious_Hidden': 0.10, 'PrivEsc_': 0.08, 'Impact_': 0.05,
}
# 合并自定义 FP 率
FP_RATES.update(custom_fp)

def estimate_fp_rate(rule_name):
    for prefix, fp_rate in sorted(FP_RATES.items(), key=lambda x: -len(x[0])):
        if rule_name.startswith(prefix):
            return fp_rate
    return 0.25

def classify_by_fp(fp_rate):
    if fp_rate < 0.10: return 'L1'
    elif fp_rate < 0.30: return 'L2'
    else: return 'L3'

def extract_rules_from_file(fpath):
    content = open(fpath, 'rb').read().decode('utf-8', errors='ignore')
    rules = {}
    pattern = re.compile(r'^(rule\s+\w+)\s*\{(.*?)^\}', re.MULTILINE | re.DOTALL)
    for m in pattern.finditer(content):
        rule_name = m.group(1).split()[1]
        rule_text = m.group(1) + ' {' + m.group(2) + '\n}'
        rules[rule_name] = rule_text
    return rules

def fix_unicode_escapes(text):
    def replacer(m):
        cp = int(m.group(1), 16)
        char = chr(cp)
        return ''.join('\\x{:02x}'.format(b) for b in char.encode('utf-8'))
    return re.sub(r'\\u([0-9a-fA-F]{4})', replacer, text)

def add_confidence_metadata(rule_name, rule_text, level, fp_estimate):
    if 'meta:' not in rule_text:
        m = re.match(r'^(rule\s+\w+\s*\{)', rule_text)
        if m:
            prefix = m.group(1)
            rest = rule_text[len(prefix):]
            meta = '\n    meta:\n        confidence_level = "{}"\n        estimated_fp_rate = {:.2f}\n'.format(level, fp_estimate)
            return prefix + meta + rest
    return rule_text

os.makedirs(OUTPUT_DIR, exist_ok=True)

all_rules = {}
for fname in sorted(os.listdir(RULES_DIR)):
    if not fname.endswith('.yar') or 'all_rules' in fname or fname == 'all_rules_v51_dedup.yar':
        continue
    fpath = os.path.join(RULES_DIR, fname)
    rules = extract_rules_from_file(fpath)
    for name, text in rules.items():
        if name not in all_rules:
            all_rules[name] = fix_unicode_escapes(text)

print("总规则数：{}".format(len(all_rules)))

l1_rules, l2_rules, l3_rules = {}, {}, {}
for name, text in all_rules.items():
    fp_rate = estimate_fp_rate(name)
    level = classify_by_fp(fp_rate)
    optimized = add_confidence_metadata(name, text, level, fp_rate)
    
    if level == 'L1': l1_rules[name] = optimized
    elif level == 'L2': l2_rules[name] = optimized
    else: l3_rules[name] = optimized

print("L1 (FP < 10%): {} 条".format(len(l1_rules)))
print("L2 (FP 10-30%): {} 条".format(len(l2_rules)))
print("L3 (FP > 30%): {} 条".format(len(l3_rules)))

# 写入并验证
for level, rules, fname in [('L1', l1_rules, 'l1_high_confidence.yar'),
                              ('L2', l2_rules, 'l2_medium_confidence.yar'),
                              ('L3', l3_rules, 'l3_low_confidence.yar')]:
    if rules:
        out_path = os.path.join(OUTPUT_DIR, fname)
        content = '\n\n'.join(sorted(rules.values()))
        open(out_path, 'w', encoding='utf-8').write(content)
        
        try:
            import yara
            yara.compile(filepath=out_path)
            print("✅ {} ({} 条)".format(fname, len(rules)))
        except Exception as e:
            print("❌ {} 验证失败：{}".format(fname, e))

print("")
print("✅ 规则优化完成!")
EOF

echo ""

# ========== Step 4: 重新测试 ==========
log_info "Step 4: 重新测试..."

cp rules/optimized/l1_high_confidence.yar scanner-master/output/rules/scanner_master_rules.yar
python3 scanner-master/ros-scanner-v2.py samples/malicious/ --workers 4 > /tmp/ros_scan_tuned.log 2>&1

RESULT=$(python3 -c "
import json, os, glob
files = sorted(glob.glob('output/ros-scan-v2-*.json'), key=lambda f: -os.path.getmtime('output/'+f))
if files:
    d = json.load(open('output/'+files[0]))
    acc = d.get('accuracy', {})
    print('{:.1f},{:.1f},{:,},{:,}'.format(
        acc.get('detection_rate', 0) * 100,
        acc.get('false_positive_rate', 0) * 100,
        acc.get('false_positives', 0),
        acc.get('false_negatives', 0)
    ))
")

DR=$(echo $RESULT | cut -d',' -f1)
FP=$(echo $RESULT | cut -d',' -f2)
FP_NUM=$(echo $RESULT | cut -d',' -f3)
FN_NUM=$(echo $RESULT | cut -d',' -f4)

echo ""
echo "📊 调优结果:"
echo "  检测率：${DR}%"
echo "  误报率：${FP}%"
echo "  FP:     ${FP_NUM}"
echo "  FN:     ${FN_NUM}"
echo ""

# ========== Step 5: 决策 ==========
log_info "Step 5: 评估是否达标..."

FP_OK=$(python3 -c "print(1 if float($FP) < 5.0 else 0)")
DR_OK=$(python3 -c "print(1 if float($DR) > 98.0 else 0)")

if [ "$FP_OK" == "1" ] && [ "$DR_OK" == "1" ]; then
    log_success "✅ 达标！进入发布流程"
    echo ""
    echo "下一步：运行 ros-01-rule-optimization.sh 生成发布包"
else
    log_warn "⚠️  仍未达标"
    echo ""
    echo "建议操作:"
    echo "  1. 进一步调整 FP_RATES 阈值"
    echo "  2. 为高 FP 规则添加例外条件"
    echo "  3. 考虑使用 L1+L2 组合规则"
    echo ""
    echo "下一步：手动调整 config/optimization_config.json 后重新运行"
fi

echo ""
echo "============================================================"
echo "✅ ROS-02 精细调优完成"
echo "============================================================"
