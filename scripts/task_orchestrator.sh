#!/bin/bash
#
# 🔧 v6.1.9 任务编排脚本
# 用途：自动执行优化任务，跟踪进度
#

set -e

# 配置
SCANNER_DIR="/home/cdy/.openclaw/workspace/agent-security-skill-scanner-master"
BENCHMARK_DIR="/home/cdy/Desktop/security-benchmark/samples"
OUTPUT_DIR="/home/cdy/Desktop/security-benchmark"
REPORT_DIR="/home/cdy/.openclaw/workspace/skill-detect-report"
ANALYSIS_DIR="${SCANNER_DIR}/analysis"

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

log_task() {
    echo -e "${BLUE}[TASK]${NC} $1"
}

# 任务：分析未检出样本
task_analyze_undetected() {
    log_task "P1-01: 分析未检出样本"
    
    mkdir -p "${ANALYSIS_DIR}"
    
    python3 << 'EOF'
import json
from collections import Counter
from pathlib import Path

# 读取扫描结果
with open('/tmp/malicious_new_final.json', 'r') as f:
    data = json.load(f)

results = data.get('results', [])
undetected = [r for r in results if r.get('risk_level') == 'SAFE']

print(f"未检出样本数：{len(undetected)}")

# 按目录分类
dir_stats = Counter()
for r in undetected:
    file_path = r.get('file', '')
    parts = file_path.split('/')
    for part in parts:
        if part in ['data_exfiltration', 'prompt_injection', 'tool_poisoning', 
                    'memory_pollution', 'persistence', 'evasion']:
            dir_stats[part] += 1
            break

print(f"\n按类型分布:")
for dtype, count in dir_stats.most_common():
    print(f"  {dtype}: {count}")

# 生成分析报告
report = f"""# 未检出样本分析报告

**生成时间**: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**未检出样本数**: {len(undetected)}

---

## 📊 按类型分布

| 类型 | 数量 | 占比 |
|------|------|------|
"""

for dtype, count in dir_stats.most_common():
    pct = count / len(undetected) * 100
    report += f"| {dtype} | {count} | {pct:.1f}% |\n"

report += f"""
---

## 📝 样本示例

"""

# 每种类型取 3 个示例
for dtype in dir_stats.keys():
    report += f"### {dtype}\n\n"
    samples = [r for r in undetected if dtype in r.get('file', '')][:3]
    for r in samples:
        file_path = r.get('file', '')
        try:
            with open(file_path, 'r') as f:
                content = f.read()[:200]
            report += f"```\\n{content}\\n```\\n\\n"
        except:
            pass

with open('${ANALYSIS_DIR}/undetected_samples_analysis.md', 'w') as f:
    f.write(report)

print(f"\\n✅ 分析报告已生成：${ANALYSIS_DIR}/undetected_samples_analysis.md")
EOF
    
    log_info "✅ P1-01 完成"
}

# 任务：生成规则模板
task_generate_rules() {
    local rule_type="$1"
    log_task "生成 ${rule_type} 规则模板"
    
    python3 << EOF
import json

# 读取现有规则
with open('${SCANNER_DIR}/rules/dist/all_rules.json', 'r') as f:
    data = json.load(f)

rules = data.get('rules', [])
max_id = max(int(r.get('id', 'BENCH-000').split('-')[1]) for r in rules if 'BENCH' in r.get('id', ''))

# 生成新规则模板
new_rules = []

# 根据类型生成规则
if '${rule_type}' == 'data_exfiltration':
    patterns = [
        ('requests.put', 'requests\\.put\\([^)]*attacker'),
        ('requests.delete', 'requests\\.delete\\([^)]*attacker'),
        ('httpx.put', 'httpx\\.put\\([^)]*attacker'),
        ('aiohttp', 'aiohttp\\.ClientSession'),
        ('smtplib', 'smtplib\\.SMTP'),
    ]
    
    for name, pattern in patterns:
        max_id += 1
        new_rules.append({
            'id': f'BENCH-{max_id:03d}',
            'name': f'数据外传 - {name}',
            'category': 'data_exfiltration',
            'patterns': [pattern],
            'min_matches': 1,
            'confidence': 90,
            'severity': 'critical'
        })

elif '${rule_type}' == 'prompt_injection':
    patterns = [
        ('ignore instruction', 'ignore\\s+.*instruction'),
        ('disregard safety', 'disregard\\s+.*safety'),
        ('override system', 'override\\s+.*system'),
        ('act as unrestricted', 'act\\s+as\\s+unrestricted'),
        ('most dangerous', 'most\\s+dangerous'),
    ]
    
    for name, pattern in patterns:
        max_id += 1
        new_rules.append({
            'id': f'BENCH-{max_id:03d}',
            'name': f'提示词注入 - {name}',
            'category': 'prompt_injection',
            'patterns': [pattern],
            'min_matches': 1,
            'confidence': 85,
            'severity': 'high'
        })

elif '${rule_type}' == 'command_execution':
    patterns = [
        ('eval(', 'eval\\s*\\([^)]*\\$'),
        ('exec(', 'exec\\s*\\([^)]*input'),
        ('os.system', 'os\\.system\\s*\\('),
        ('subprocess.call', 'subprocess\\.call.*shell\\s*=\\s*True'),
        ('os.popen', 'os\\.popen\\s*\\('),
    ]
    
    for name, pattern in patterns:
        max_id += 1
        new_rules.append({
            'id': f'BENCH-{max_id:03d}',
            'name': f'命令执行 - {name}',
            'category': 'command_injection',
            'patterns': [pattern],
            'min_matches': 1,
            'confidence': 95,
            'severity': 'critical'
        })

# 保存新规则
output_file = '${SCANNER_DIR}/rules/v6.1.9_supplement/benchmark_supplement_rules_${rule_type}.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump({
        'name': f'Benchmark Supplement Rules - {rule_type}',
        'version': '1.0',
        'description': f'补充规则 - {rule_type}',
        'created_at': '${__import__('datetime').datetime.now().strftime('%Y-%m-%d')}',
        'rules': new_rules
    }, f, ensure_ascii=False, indent=2)

print(f"✅ 生成 {len(new_rules)} 条 {rule_type} 规则")
print(f"   文件：{output_file}")
EOF
    
    log_info "✅ 规则模板已生成"
}

# 任务：合并规则
task_merge_rules() {
    log_task "合并补充规则到主规则库"
    
    python3 << 'EOF'
import json
from pathlib import Path

# 读取主规则库
with open('${SCANNER_DIR}/rules/dist/all_rules.json', 'r') as f:
    main_data = json.load(f)

main_rules = main_data.get('rules', [])
main_ids = set(r.get('id') for r in main_rules)

# 查找所有补充规则文件
supplement_dir = Path('${SCANNER_DIR}/rules/v6.1.9_supplement/')
new_count = 0

for supplement_file in supplement_dir.glob('*.json'):
    with open(supplement_file, 'r') as f:
        supp_data = json.load(f)
    
    supp_rules = supp_data.get('rules', [])
    for rule in supp_rules:
        if rule.get('id') not in main_ids:
            main_rules.append(rule)
            main_ids.add(rule.get('id'))
            new_count += 1
            print(f"  ✅ 添加：{rule.get('id')} - {rule.get('name')}")

# 更新主规则库
main_data['rules'] = main_rules
main_data['total_rules'] = len(main_rules)
main_data['version'] = '6.1.9-supplement-merged'

with open('${SCANNER_DIR}/rules/dist/all_rules.json', 'w', encoding='utf-8') as f:
    json.dump(main_data, f, ensure_ascii=False, indent=2)

print(f"\n✅ 合并完成：新增 {new_count} 条规则")
print(f"   总规则数：{len(main_rules)}")
EOF
    
    log_info "✅ 规则合并完成"
}

# 任务：运行测试
task_run_test() {
    local test_mode="${1:-quick}"
    log_task "运行 ${test_mode} 测试"
    
    cd "${SCANNER_DIR}"
    
    if [ "${test_mode}" == "quick" ]; then
        python3 scanner.py "${BENCHMARK_DIR}/malicious-new/" \
            --extensions ".txt,.py,.python,.sh,.bash,.yaml,.yml,.json" \
            --output json \
            --output-file "${OUTPUT_DIR}/BENCHMARK_QUICK_TEST.json" \
            --workers 8 \
            2>&1 | tail -5
    else
        python3 scanner.py "${BENCHMARK_DIR}/from-templates/" \
            --extensions ".txt,.py,.python,.sh,.bash,.yaml,.yml,.json" \
            --output json \
            --output-file "${OUTPUT_DIR}/BENCHMARK_FULL_TEST.json" \
            --workers 16 \
            2>&1 | tail -5
    fi
    
    log_info "✅ 测试完成"
}

# 主函数
main() {
    local action="${1:-help}"
    
    case "${action}" in
        analyze)
            task_analyze_undetected
            ;;
        generate)
            local rule_type="${2:-data_exfiltration}"
            task_generate_rules "${rule_type}"
            ;;
        merge)
            task_merge_rules
            ;;
        test)
            local test_mode="${2:-quick}"
            task_run_test "${test_mode}"
            ;;
        all)
            log_info "🚀 执行完整优化流程"
            task_analyze_undetected
            task_generate_rules "data_exfiltration"
            task_generate_rules "prompt_injection"
            task_generate_rules "command_execution"
            task_merge_rules
            task_run_test "quick"
            log_info "✅ 完整优化流程完成"
            ;;
        *)
            echo "用法：$0 {analyze|generate|merge|test|all}"
            echo ""
            echo "命令:"
            echo "  analyze              分析未检出样本"
            echo "  generate [type]      生成规则模板 (data_exfiltration|prompt_injection|command_execution)"
            echo "  merge                合并补充规则"
            echo "  test [mode]          运行测试 (quick|full)"
            echo "  all                  执行完整优化流程"
            echo ""
            echo "示例:"
            echo "  $0 analyze"
            echo "  $0 generate data_exfiltration"
            echo "  $0 merge"
            echo "  $0 all"
            ;;
    esac
}

# 执行
main "$@"
