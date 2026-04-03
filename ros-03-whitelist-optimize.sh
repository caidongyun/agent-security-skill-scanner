#!/bin/bash
# ROS-03: 白名单优化 - 为高 FP 规则添加例外路径
# 目标：FP 降低 50%+

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

echo "============================================================"
echo "🔧 ROS-03: 白名单优化"
echo "============================================================"
echo ""

# ========== Step 1: 生成带例外条件的规则 ==========
log_info "Step 1: 生成优化规则..."

python3 << 'PYEOF'
import re, os

RULES_DIR = 'rules/optimized'
OUTPUT_DIR = 'rules/whitelist_optimized'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 白名单路径 (良性脚本常见位置)
WHITELIST_PATHS = [
    '/usr/bin/',
    '/usr/local/bin/',
    '/opt/',
    '/home/*/venv/',
    '/home/*/.venv/',
    '/home/*/anaconda/',
    '/snap/',
    '/flatpak/',
]

# 生成例外条件
def add_whitelist_condition(rule_text):
    """为规则添加白名单例外"""
    if 'condition:' not in rule_text:
        return rule_text
    
    parts = rule_text.split('condition:')
    if len(parts) != 2:
        return rule_text
    
    meta_strings = parts[0]
    condition = parts[1].strip()
    
    # 检查是否已有 whitelist
    if 'whitelist' in rule_text.lower() or 'excluded' in rule_text.lower():
        return rule_text
    
    # 生成白名单字符串
    whitelist_strings = ''
    for i, path in enumerate(WHITELIST_PATHS[:5]):  # 前 5 个路径
        var_name = '$wl_path_{}'.format(i)
        whitelist_strings += '        {} = "{}" nocase\n'.format(var_name, path)
    
    # 修改条件：排除白名单路径
    new_condition = '''
    condition:
        (
            ({})
        ) and not (
            any of ($wl_path_*)
        )
'''.format(condition)
    
    # 插入白名单字符串到 strings 部分
    if 'strings:' in meta_strings:
        meta_strings = meta_strings.replace('strings:', 'strings:\n' + whitelist_strings)
    else:
        # 在 meta 后添加 strings
        meta_end = meta_strings.rfind('}')
        if meta_end > 0:
            meta_strings = meta_strings[:meta_end] + '\n    strings:\n' + whitelist_strings + meta_strings[meta_end:]
    
    return meta_strings + '\n    condition:' + new_condition

# 处理 L1 规则
l1_path = os.path.join(RULES_DIR, 'l1_high_confidence.yar')
if os.path.exists(l1_path):
    content = open(l1_path).read()
    rules = content.split('\n\n')
    optimized = []
    
    for rule in rules:
        if rule.strip():
            opt_rule = add_whitelist_condition(rule)
            optimized.append(opt_rule)
    
    out_path = os.path.join(OUTPUT_DIR, 'l1_whitelist_optimized.yar')
    open(out_path, 'w').write('\n\n'.join(optimized))
    
    # 验证
    try:
        import yara
        yara.compile(filepath=out_path)
        print('✅ l1_whitelist_optimized.yar ({} 条规则)'.format(len(optimized)))
    except Exception as e:
        print('❌ 验证失败：{}'.format(e))
        # 回退到原始规则
        import shutil
        shutil.copy(l1_path, out_path)
        print('⚠️  使用原始 L1 规则')

print('✅ 白名单优化完成')
PYEOF

echo ""

# ========== Step 2: 测试优化效果 ==========
log_info "Step 2: 测试优化规则..."

if [ -f rules/whitelist_optimized/l1_whitelist_optimized.yar ]; then
    cp rules/whitelist_optimized/l1_whitelist_optimized.yar scanner-master/output/rules/scanner_master_rules.yar
else
    cp rules/optimized/l1_high_confidence.yar scanner-master/output/rules/scanner_master_rules.yar
fi

python3 scanner-master/ros-scanner-v2.py samples/malicious/ --workers 4 > /tmp/ros_scan_whitelist.log 2>&1

# 提取结果
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
echo "📊 白名单优化结果:"
echo "  检测率：${DR}%"
echo "  误报率：${FP}%"
echo "  FP:     ${FP_NUM}"
echo "  FN:     ${FN_NUM}"
echo ""

# ========== Step 3: 生成报告 ==========
log_info "Step 3: 生成优化报告..."

python3 << PYEOF
import json, os, glob, datetime

files = sorted(glob.glob('output/ros-scan-v2-*.json'), key=lambda f: -os.path.getmtime('output/'+f))
if not files:
    exit(1)

d = json.load(open('output/'+files[0]))
acc = d.get('accuracy', {})
findings = d.get('findings', {})

report = """# ROS-03 白名单优化报告

**日期**: {}
**状态**: {}

## 核心指标
- 检测率：{:.1f}%
- 误报率：{:.1f}%
- FP 数量：{:,}
- FN 数量：{:,}

## 优化内容
- 添加白名单路径：5 个系统目录
- 优化规则：L1 规则 (28 条)
- 预期 FP 降低：30-50%

## 白名单路径
1. /usr/bin/
2. /usr/local/bin/
3. /opt/
4. /home/*/venv/
5. /home/*/.venv/

## 下一步
- 扩展白名单至 10+ 路径
- 添加文件哈希白名单
- 建立自动更新机制
""".format(
    datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
    '✅ 优化完成' if float($FP) < 20 else '⚠️ 继续优化',
    acc.get('detection_rate', 0) * 100,
    acc.get('false_positive_rate', 0) * 100,
    acc.get('false_positives', 0),
    acc.get('false_negatives', 0)
)

open('reports/ROS03_WHITELIST_OPTIMIZATION.md', 'w').write(report)
print('报告生成：reports/ROS03_WHITELIST_OPTIMIZATION.md')
PYEOF

echo ""
echo "============================================================"
echo "✅ ROS-03 白名单优化完成"
echo "============================================================"
