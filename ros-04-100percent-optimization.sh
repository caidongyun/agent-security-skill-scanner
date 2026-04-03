#!/bin/bash
# ROS-04: 100% 准确率优化 - 全量规则 + 多级验证
# 目标：检测率 100%, 误报率 < 1%

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
log_error() { echo -e "${RED}[ERROR]${NC} $(date '+%H:%M:%S') $*"; }

echo "============================================================"
echo "🎯 ROS-04: 100% 准确率优化"
echo "============================================================"
echo ""

# ========== Step 1: 合并全量规则 ==========
log_info "Step 1: 合并全量规则..."
python3 fix_and_merge_rules.py > /tmp/merge.log 2>&1
if [ $? -ne 0 ]; then
    log_error "规则合并失败"
    cat /tmp/merge.log
    exit 1
fi
log_success "全量规则合并完成"
echo ""

# ========== Step 2: 规则分级 (使用更严格的阈值) ==========
log_info "Step 2: 规则分级 (严格阈值)..."

python3 << 'PYEOF'
import re, os, json

RULES_DIR = 'rules/scanner_v3/yara'
OUTPUT_DIR = 'rules/optimized_strict'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 更严格的 FP 阈值
FP_RATES = {
    'Agent_Curl': 0.80, 'Agent_Credential': 0.75, 'CRED_': 0.70,
    'Agent_Persistence': 0.65, 'Agent_Memory': 0.60, 'Agent_Resource': 0.55,
    'JS_': 0.65, 'PS_': 0.60, 'BASH_': 0.55,
    'Agent_Data_Exfil': 0.50, 'EXFIL_': 0.45, 'Agent_SupplyChain': 0.50,
    'Agent_Evasion': 0.40,
    'Shell_ReverseShell': 0.05, 'Shell_PrivEsc': 0.08,
    'Impact_DataDestruction': 0.02, 'Impact_Ransomware': 0.01,
    'Malicious_Hidden': 0.10, 'PrivEsc_': 0.08, 'Impact_': 0.03,
}

def estimate_fp_rate(rule_name):
    for prefix, fp_rate in sorted(FP_RATES.items(), key=lambda x: -len(x[0])):
        if rule_name.startswith(prefix):
            return fp_rate
    return 0.30

# 更严格的分级
def classify_by_fp(fp_rate):
    if fp_rate < 0.05: return 'L1'  # 仅极高置信度
    elif fp_rate < 0.20: return 'L2'  # 高置信度
    elif fp_rate < 0.50: return 'L3'  # 中置信度
    else: return 'L4'  # 低置信度 (需人工审查)

def extract_rules_yara_safe(fpath):
    content = open(fpath, 'rb').read().decode('utf-8', errors='ignore')
    rules = {}
    lines = content.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r'^rule\s+(\w+)\s*\{', line.strip())
        if m:
            rule_name = m.group(1)
            rule_lines = [line]
            bc = line.count('{') - line.count('}')
            i += 1
            while i < len(lines) and bc > 0:
                line = lines[i]
                rule_lines.append(line)
                bc += line.count('{') - line.count('}')
                i += 1
            rule_text = '\n'.join(rule_lines)
            if bc == 0:
                try:
                    import yara
                    yara.compile(source=rule_text)
                    rules[rule_name] = rule_text
                except:
                    pass
        else:
            i += 1
    return rules

def fix_unicode(text):
    def repl(m):
        return ''.join('\\x{:02x}'.format(b) for b in chr(int(m.group(1), 16)).encode('utf-8'))
    return re.sub(r'\\u([0-9a-fA-F]{4})', repl, text)

all_rules = {}
for fname in sorted(os.listdir(RULES_DIR)):
    if not fname.endswith('.yar') or 'all_rules' in fname or fname == 'all_rules_v51_dedup.yar':
        continue
    fpath = os.path.join(RULES_DIR, fname)
    rules = extract_rules_yara_safe(fpath)
    for name, text in rules.items():
        if name not in all_rules:
            all_rules[name] = fix_unicode(text)

print('总规则数：{}'.format(len(all_rules)))

l1, l2, l3, l4 = {}, {}, {}, {}
for name, text in all_rules.items():
    fp = estimate_fp_rate(name)
    level = classify_by_fp(fp)
    if level == 'L1': l1[name] = text
    elif level == 'L2': l2[name] = text
    elif level == 'L3': l3[name] = text
    else: l4[name] = text

print('L1 (FP < 5%):   {} 条'.format(len(l1)))
print('L2 (FP 5-20%):  {} 条'.format(len(l2)))
print('L3 (FP 20-50%): {} 条'.format(len(l3)))
print('L4 (FP > 50%):  {} 条'.format(len(l4)))

# 写入
import yara
for level, rules, fname in [('L1', l1, 'l1_critical.yar'), ('L2', l2, 'l2_high.yar'),
                              ('L3', l3, 'l3_medium.yar'), ('L4', l4, 'l4_low.yar')]:
    if rules:
        out = os.path.join(OUTPUT_DIR, fname)
        content = '\n\n'.join(sorted(rules.values()))
        open(out, 'w').write(content)
        try:
            yara.compile(filepath=out)
            print('✅ {} ({} 条)'.format(fname, len(rules)))
        except Exception as e:
            print('❌ {} 失败：{}'.format(fname, e))

print('✅ 严格分级完成')
PYEOF

echo ""

# ========== Step 3: 生成多级扫描策略 ==========
log_info "Step 3: 生成多级扫描策略..."

cat > rules/optimized_strict/multi_level_scan.json << 'EOF'
{
  "strategy": "cascade",
  "levels": [
    {
      "name": "L1_Critical",
      "file": "l1_critical.yar",
      "action": "alert",
      "description": "极高置信度，直接告警"
    },
    {
      "name": "L2_High",
      "file": "l2_high.yar",
      "action": "alert_review",
      "description": "高置信度，告警 + 人工审查"
    },
    {
      "name": "L3_Medium",
      "file": "l3_medium.yar",
      "action": "review",
      "description": "中置信度，仅审查"
    },
    {
      "name": "L4_Low",
      "file": "l4_low.yar",
      "action": "log",
      "description": "低置信度，仅日志"
    }
  ],
  "optimization_goal": {
    "detection_rate": 100,
    "false_positive_rate": 1
  }
}
EOF

echo "✅ 多级扫描策略：rules/optimized_strict/multi_level_scan.json"
echo ""

# ========== Step 4: 测试 L1+L2 组合 ==========
log_info "Step 4: 测试 L1+L2 组合..."

cat rules/optimized_strict/l1_critical.yar rules/optimized_strict/l2_high.yar > /tmp/l1l2_strict.yar
cp /tmp/l1l2_strict.yar scanner-master/output/rules/scanner_master_rules.yar

python3 scanner-master/ros-scanner-v2.py samples/malicious/ --workers 4 > /tmp/ros_strict.log 2>&1

RESULT=$(python3 -c "
import json, os, glob
files = sorted(glob.glob('output/ros-scan-v2-*.json'), key=lambda f: -os.path.getmtime(f))
if files:
    d = json.load(open(files[0]))
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

echo ""
echo "📊 L1+L2 严格模式结果:"
echo "  检测率：${DR}%"
echo "  误报率：${FP}%"
echo ""

# ========== Step 5: 决策 ==========
if [ $(python3 -c "print(1 if float($DR) > 99 and float($FP) < 2 else 0)") -eq 1 ]; then
    log_success "✅ 接近 100% 准确率！DR > 99%, FP < 2%"
    echo ""
    echo "下一步：生成发布包 v3.2.0"
else
    log_info "⚠️  继续优化..."
    echo ""
    echo "当前：DR=${DR}%, FP=${FP}%"
    echo "目标：DR > 99%, FP < 2%"
fi

echo ""
echo "============================================================"
echo "✅ ROS-04 100% 准确率优化完成"
echo "============================================================"
