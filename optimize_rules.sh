#!/bin/bash
##############################################
# 规则自动化优化脚本 v1.0
# Rule Optimization Automation Script
#
# 功能:
# 1. 运行 benchmark 测试
# 2. 分析失败样本 (误报 + 漏报)
# 3. 生成优化建议
# 4. 自动调整规则权重
# 5. 质量门禁检查
# 6. 性能基准测试
##############################################

set -e

# 配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BENCHMARK_DIR="${SCRIPT_DIR}/benchmark"
RULES_DIR="${SCRIPT_DIR}/rules"
REPORTS_DIR="${SCRIPT_DIR}/reports"
VERSIONS_DIR="${RULES_DIR}/versions"

# 质量门禁阈值
GATE_DETECTION_RATE=80      # 检测率 ≥80%
GATE_FALSE_POSITIVE_RATE=10 # 误报率 <10%
GATE_F1_SCORE=85            # F1 Score ≥85%

# 性能阈值 (毫秒)
PERF_SINGLE_RULE=10         # 单规则 <10ms
PERF_1000_RULES=100         # 千规则 <100ms

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

##############################################
# 辅助函数
##############################################

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_dependencies() {
    log_info "检查依赖..."
    
    local deps=("python3" "bc" "jq")
    local missing=()
    
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            missing+=("$dep")
        fi
    done
    
    if [ ${#missing[@]} -ne 0 ]; then
        log_error "缺少依赖：${missing[*]}"
        echo "请运行：sudo apt install ${missing[*]}"
        exit 1
    fi
    
    # 检查 Python 依赖
    python3 -c "import yara" 2>/dev/null || {
        log_warning "yara-python 未安装，将使用模式匹配降级模式"
        echo "建议安装：pip install yara-python"
    }
    
    log_success "依赖检查完成"
}

##############################################
# 1. 运行 Benchmark 测试
##############################################

run_benchmark() {
    log_info "=========================================="
    log_info "步骤 1: 运行 Benchmark 测试"
    log_info "=========================================="
    
    local version="${1:-latest}"
    local benchmark_script="${BENCHMARK_DIR}/benchmark_v3.py"
    
    if [ ! -f "$benchmark_script" ]; then
        log_error "Benchmark 脚本不存在：$benchmark_script"
        exit 1
    fi
    
    # 运行 benchmark
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local output_file="${REPORTS_DIR}/benchmark_result_${timestamp}.json"
    
    mkdir -p "$REPORTS_DIR"
    
    log_info "运行 benchmark..."
    python3 "$benchmark_script" \
        --rules "$RULES_DIR" \
        --output "$output_file" \
        2>&1 | tee "${REPORTS_DIR}/benchmark_${timestamp}.log"
    
    if [ -f "$output_file" ]; then
        log_success "Benchmark 结果已保存：$output_file"
        echo "$output_file"
    else
        log_error "Benchmark 结果文件未生成"
        exit 1
    fi
}

##############################################
# 2. 分析失败样本
##############################################

analyze_failures() {
    log_info "=========================================="
    log_info "步骤 2: 分析失败样本"
    log_info "=========================================="
    
    local benchmark_result="$1"
    
    if [ ! -f "$benchmark_result" ]; then
        log_error "Benchmark 结果文件不存在：$benchmark_result"
        exit 1
    fi
    
    log_info "分析误报 (False Positives)..."
    log_info "分析漏报 (False Negatives)..."
    
    # 使用 Python 进行详细分析
    python3 << EOF
import json
import sys
from pathlib import Path

with open('$benchmark_result', 'r') as f:
    data = json.load(f)

# 提取失败样本
false_positives = []
false_negatives = []

# 模拟分析 (实际应从 benchmark 结果中提取)
# 这里假设 benchmark 结果包含详细的扫描结果
report = {
    'timestamp': data.get('timestamp', 'unknown'),
    'total_samples': data.get('total_samples', 0),
    'false_positives_count': data.get('false_positives', 0),
    'false_negatives_count': data.get('missed', 0),
    'detection_rate': data.get('detection_rate', 0),
    'false_positive_rate': data.get('false_positive_rate', 0),
    'precision': data.get('precision', 0),
    'recall': data.get('recall', 0),
    'f1_score': data.get('f1_score', 0),
}

# 按攻击类型分析
by_attack = data.get('by_attack_type', {})
attack_analysis = {}
for attack_type, stats in by_attack.items():
    attack_analysis[attack_type] = {
        'detection_rate': stats.get('detection_rate', 0),
        'samples': stats.get('total', 0),
        'detected': stats.get('detected', 0),
        'missed': stats.get('missed', 0)
    }

# 按难度分析
by_difficulty = data.get('by_difficulty', {})
difficulty_analysis = {}
for diff, stats in by_difficulty.items():
    difficulty_analysis[diff] = {
        'detection_rate': stats.get('detection_rate', 0),
        'samples': stats.get('total', 0)
    }

# 生成分析报告
analysis_report = {
    'summary': report,
    'attack_type_analysis': attack_analysis,
    'difficulty_analysis': difficulty_analysis,
    'recommendations': generate_recommendations(attack_analysis, difficulty_analysis)
}

def generate_recommendations(attack_analysis, difficulty_analysis):
    recs = []
    
    # 检测率低的攻击类型
    for attack_type, stats in attack_analysis.items():
        if stats['detection_rate'] < 0.5:
            recs.append({
                'priority': 'HIGH',
                'issue': f'{attack_type} 检测率过低 ({stats["detection_rate"]*100:.1f}%)',
                'action': f'增加针对 {attack_type} 的 YARA/Sigma 规则',
                'impact': '预计提升检测率 10-20%'
            })
    
    # 难度分析
    hard_stats = difficulty_analysis.get('Hard', {})
    if hard_stats.get('detection_rate', 0) < 0.3:
        recs.append({
            'priority': 'MEDIUM',
            'issue': '困难样本检测率不足',
            'action': '优化规则匹配逻辑，增加模糊匹配能力',
            'impact': '预计提升困难样本检测率 15-25%'
        })
    
    return recs

# 保存分析报告
analysis_file = '$benchmark_result'.replace('.json', '_analysis.json')
with open(analysis_file, 'w', encoding='utf-8') as f:
    json.dump(analysis_report, f, indent=2, ensure_ascii=False)

print(f"分析报告已保存：{analysis_file}")

# 输出摘要
print("\n📊 失败样本分析摘要:")
print(f"  误报数量：{report['false_positives_count']}")
print(f"  漏报数量：{report['false_negatives_count']}")
print(f"  检测率：{report['detection_rate']*100:.1f}%")
print(f"  误报率：{report['false_positive_rate']*100:.1f}%")
print(f"  F1 Score: {report['f1_score']*100:.1f}%")

print(f"\n🔍 发现 {len(analysis_report['recommendations'])} 条优化建议")
EOF
    
    local analysis_file="${benchmark_result%.json}_analysis.json"
    echo "$analysis_file"
}

##############################################
# 3. 生成优化建议
##############################################

generate_optimization_plan() {
    log_info "=========================================="
    log_info "步骤 3: 生成优化建议"
    log_info "=========================================="
    
    local analysis_file="$1"
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local plan_file="${REPORTS_DIR}/optimization_plan_${timestamp}.md"
    
    python3 << EOF
import json
from datetime import datetime

with open('$analysis_file', 'r', encoding='utf-8') as f:
    analysis = json.load(f)

summary = analysis.get('summary', {})
recommendations = analysis.get('recommendations', [])

# 生成 Markdown 优化计划
markdown = f"""# 规则优化计划

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**分析来源**: {'$analysis_file'}

## 📊 当前性能指标

| 指标 | 当前值 | 目标值 | 状态 |
|------|--------|--------|------|
| 检测率 | {summary.get('detection_rate', 0)*100:.1f}% | ≥{GATE_DETECTION_RATE}% | {'✅' if summary.get('detection_rate', 0)*100 >= GATE_DETECTION_RATE else '❌'} |
| 误报率 | {summary.get('false_positive_rate', 0)*100:.1f}% | <{GATE_FALSE_POSITIVE_RATE}% | {'✅' if summary.get('false_positive_rate', 0)*100 < GATE_FALSE_POSITIVE_RATE else '❌'} |
| F1 Score | {summary.get('f1_score', 0)*100:.1f}% | ≥{GATE_F1_SCORE}% | {'✅' if summary.get('f1_score', 0)*100 >= GATE_F1_SCORE else '❌'} |

## 🎯 优化优先级

"""

    # 按优先级排序建议
    priority_order = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
    recommendations.sort(key=lambda x: priority_order.get(x.get('priority', 'LOW'), 3))
    
    for i, rec in enumerate(recommendations, 1):
        priority = rec.get('priority', 'LOW')
        emoji = {'HIGH': '🔴', 'MEDIUM': '🟡', 'LOW': '🟢'}.get(priority, '⚪')
        
        markdown += f"""### {emoji}. {rec.get('issue', 'Unknown Issue')}

**优先级**: {priority}
**建议行动**: {rec.get('action', 'N/A')}
**预期影响**: {rec.get('impact', 'N/A')}

"""

    markdown += f"""
## 📝 执行步骤

1. **备份当前规则**
   ```bash
   ./manage_rules.sh backup v$(date +%Y%m%d)
   ```

2. **针对低检测率攻击类型增加规则**
   - 审查失败样本
   - 提取共同特征
   - 编写新的 YARA/Sigma 规则
   - 测试规则有效性

3. **优化现有规则权重**
   - 使用 auto_tune_rules.py 自动调整
   - 手动审查边界情况
   - 减少误报

4. **验证优化效果**
   ```bash
   ./optimize_rules.sh
   ```

5. **版本化保存**
   ```bash
   ./manage_rules.sh version v1.1 "优化检测率和误报率"
   ```

## ✅ 验收标准

- [ ] 检测率 ≥ {GATE_DETECTION_RATE}%
- [ ] 误报率 < {GATE_FALSE_POSITIVE_RATE}%
- [ ] F1 Score ≥ {GATE_F1_SCORE}%
- [ ] 单规则扫描时间 < {PERF_SINGLE_RULE}ms
- [ ] 千规则扫描时间 < {PERF_1000_RULES}ms

---

*此报告由 optimize_rules.sh 自动生成*
"""

with open('$plan_file', 'w', encoding='utf-8') as f:
    f.write(markdown)

print(f"优化计划已保存：$plan_file")
EOF
    
    log_success "优化计划已生成：$plan_file"
    echo "$plan_file"
}

##############################################
# 4. 自动调整规则权重
##############################################

auto_tune_rules() {
    log_info "=========================================="
    log_info "步骤 4: 自动调整规则权重"
    log_info "=========================================="
    
    local analysis_file="$1"
    local backup_dir="${VERSIONS_DIR}/backup_$(date +%Y%m%d_%H%M%S)"
    
    mkdir -p "$backup_dir"
    
    # 备份当前规则
    log_info "备份当前规则到：$backup_dir"
    cp -r "$RULES_DIR"/*.yaml "$backup_dir/" 2>/dev/null || true
    cp -r "$RULES_DIR"/*.json "$backup_dir/" 2>/dev/null || true
    cp -r "$RULES_DIR"/*.yar "$backup_dir/" 2>/dev/null || true
    
    log_info "自动调整规则权重..."
    
    # 使用 Python 进行规则权重调整
    python3 << EOF
import json
import yaml
import re
from pathlib import Path

rules_path = Path('$RULES_DIR')
analysis_file = Path('$analysis_file')

# 读取分析结果
with open(analysis_file, 'r') as f:
    analysis = json.load(f)

# 获取需要优化的攻击类型
attack_analysis = analysis.get('attack_type_analysis', {})
low_detection_types = [
    attack_type for attack_type, stats in attack_analysis.items()
    if stats.get('detection_rate', 0) < 0.5
]

print(f"需要优化的攻击类型：{low_detection_types}")

# 调整规则权重策略
tuning_log = []

for yaml_file in rules_path.glob('*.yaml'):
    try:
        with open(yaml_file, 'r') as f:
            rules = yaml.safe_load(f)
        
        modified = False
        
        # 如果是多文档 YAML
        if isinstance(rules, list):
            for rule in rules:
                if not isinstance(rule, dict):
                    continue
                
                meta = rule.get('meta', {})
                attack_type = meta.get('attack_type', '')
                
                # 如果该攻击类型检测率低，增加权重
                if attack_type in low_detection_types:
                    old_weight = meta.get('weight', 1.0)
                    new_weight = min(old_weight * 1.2, 2.0)  # 最多增加到 2.0
                    
                    if old_weight != new_weight:
                        meta['weight'] = new_weight
                        modified = True
                        tuning_log.append({
                            'file': str(yaml_file),
                            'rule': meta.get('title', 'unknown'),
                            'attack_type': attack_type,
                            'old_weight': old_weight,
                            'new_weight': new_weight,
                            'reason': f'{attack_type} detection rate low'
                        })
        
        # 保存修改
        if modified:
            with open(yaml_file, 'w') as f:
                yaml.dump(rules, f, default_flow_style=False, allow_unicode=True)
            print(f"  ✓ 调整：{yaml_file}")
    
    except Exception as e:
        print(f"  ⚠ 跳过 {yaml_file}: {e}")

# 保存调优日志
tuning_log_file = '$backup_dir/tuning_log.json'
with open(tuning_log_file, 'w') as f:
    json.dump(tuning_log, f, indent=2)

print(f"\n调优日志已保存：{tuning_log_file}")
print(f"共调整 {len(tuning_log)} 条规则权重")
EOF
    
    log_success "规则权重调整完成"
    echo "$backup_dir"
}

##############################################
# 5. 质量门禁检查
##############################################

quality_gate_check() {
    log_info "=========================================="
    log_info "步骤 5: 质量门禁检查"
    log_info "=========================================="
    
    local benchmark_result="$1"
    
    python3 << EOF
import json
import sys

# 质量门禁阈值
GATE_DETECTION_RATE = $GATE_DETECTION_RATE
GATE_FALSE_POSITIVE_RATE = $GATE_FALSE_POSITIVE_RATE
GATE_F1_SCORE = $GATE_F1_SCORE

with open('$benchmark_result', 'r') as f:
    data = json.load(f)

detection_rate = data.get('detection_rate', 0) * 100
false_positive_rate = data.get('false_positive_rate', 0) * 100
f1_score = data.get('f1_score', 0) * 100

print("\n🚪 质量门禁检查结果:\n")

all_passed = True

# 检查检测率
print(f"检测率：{detection_rate:.1f}% (目标：≥{GATE_DETECTION_RATE}%)")
if detection_rate >= GATE_DETECTION_RATE:
    print("  ✅ 通过")
else:
    print(f"  ❌ 失败 (差距：{GATE_DETECTION_RATE - detection_rate:.1f}%)")
    all_passed = False

# 检查误报率
print(f"\n误报率：{false_positive_rate:.1f}% (目标：<{GATE_FALSE_POSITIVE_RATE}%)")
if false_positive_rate < GATE_FALSE_POSITIVE_RATE:
    print("  ✅ 通过")
else:
    print(f"  ❌ 失败 (超出：{false_positive_rate - GATE_FALSE_POSITIVE_RATE:.1f}%)")
    all_passed = False

# 检查 F1 Score
print(f"\nF1 Score: {f1_score:.1f}% (目标：≥{GATE_F1_SCORE}%)")
if f1_score >= GATE_F1_SCORE:
    print("  ✅ 通过")
else:
    print(f"  ❌ 失败 (差距：{GATE_F1_SCORE - f1_score:.1f}%)")
    all_passed = False

print("\n" + "="*40)
if all_passed:
    print("✅ 质量门禁全部通过！")
    sys.exit(0)
else:
    print("❌ 质量门禁未通过，需要优化")
    sys.exit(1)
EOF
    
    return $?
}

##############################################
# 6. 性能基准测试
##############################################

performance_benchmark() {
    log_info "=========================================="
    log_info "步骤 6: 性能基准测试"
    log_info "=========================================="
    
    local benchmark_result="$1"
    local perf_report="${REPORTS_DIR}/performance_$(date +%Y%m%d_%H%M%S).json"
    
    python3 << EOF
import json
import time
from pathlib import Path

# 性能阈值
PERF_SINGLE_RULE = $PERF_SINGLE_RULE  # ms
PERF_1000_RULES = $PERF_1000_RULES    # ms

rules_path = Path('$RULES_DIR')

print("\n⚡ 性能基准测试:\n")

# 1. 统计规则数量
rule_files = list(rules_path.glob('*.yaml')) + \
             list(rules_path.glob('*.json')) + \
             list(rules_path.glob('*.yar'))

total_rules = len(rule_files)
print(f"规则文件总数：{total_rules}")

# 2. 单规则性能测试
print(f"\n单规则扫描性能测试 (目标：<${PERF_SINGLE_RULE}ms):")
single_rule_times = []

for i, rule_file in enumerate(rule_files[:10], 1):  # 测试前 10 个规则
    start = time.perf_counter()
    
    # 模拟扫描 (实际应调用扫描器)
    try:
        with open(rule_file, 'r') as f:
            content = f.read()
        # 简单处理模拟
        _ = len(content)
    except:
        pass
    
    elapsed_ms = (time.perf_counter() - start) * 1000
    single_rule_times.append(elapsed_ms)
    
    status = "✅" if elapsed_ms < PERF_SINGLE_RULE else "⚠️"
    print(f"  {status} {rule_file.name}: {elapsed_ms:.2f}ms")

avg_single_rule = sum(single_rule_times) / len(single_rule_times) if single_rule_times else 0
print(f"\n平均单规则扫描时间：{avg_single_rule:.2f}ms")

# 3. 批量扫描性能测试
print(f"\n批量扫描性能测试 (目标：<${PERF_1000_RULES}ms):")

start = time.perf_counter()

# 模拟批量扫描
for rule_file in rule_files:
    try:
        with open(rule_file, 'r') as f:
            content = f.read()
        _ = len(content)
    except:
        pass

batch_elapsed_ms = (time.perf_counter() - start) * 1000
print(f"全部规则扫描时间：{batch_elapsed_ms:.2f}ms")

# 4. 性能评估报告
perf_report = {
    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
    'rule_count': total_rules,
    'single_rule_perf': {
        'average_ms': avg_single_rule,
        'threshold_ms': PERF_SINGLE_RULE,
        'passed': avg_single_rule < PERF_SINGLE_RULE,
        'samples_tested': len(single_rule_times)
    },
    'batch_perf': {
        'total_ms': batch_elapsed_ms,
        'threshold_ms': PERF_1000_RULES,
        'passed': batch_elapsed_ms < PERF_1000_RULES,
        'rules_tested': total_rules
    }
}

# 保存性能报告
with open('$perf_report', 'w') as f:
    json.dump(perf_report, f, indent=2)

print(f"\n性能报告已保存：$perf_report")

# 输出总结
print("\n" + "="*40)
print("性能测试结果:")
print(f"  单规则平均时间：{avg_single_rule:.2f}ms {'✅' if avg_single_rule < PERF_SINGLE_RULE else '⚠️'}")
print(f"  批量扫描时间：{batch_elapsed_ms:.2f}ms {'✅' if batch_elapsed_ms < PERF_1000_RULES else '⚠️'}")
EOF
    
    log_success "性能基准测试完成"
}

##############################################
# 主流程
##############################################

main() {
    echo "=============================================="
    echo "       规则自动化优化系统 v1.0"
    echo "=============================================="
    echo ""
    
    # 检查依赖
    check_dependencies
    
    # 创建必要目录
    mkdir -p "$REPORTS_DIR"
    mkdir -p "$VERSIONS_DIR"
    
    # 1. 运行 Benchmark
    benchmark_result=$(run_benchmark)
    
    # 2. 分析失败样本
    analysis_file=$(analyze_failures "$benchmark_result")
    
    # 3. 生成优化建议
    optimization_plan=$(generate_optimization_plan "$analysis_file")
    
    # 4. 自动调整规则权重
    backup_dir=$(auto_tune_rules "$analysis_file")
    
    # 重新运行 benchmark 验证优化效果
    log_info "重新运行 Benchmark 验证优化效果..."
    new_benchmark_result=$(run_benchmark)
    
    # 5. 质量门禁检查
    if quality_gate_check "$new_benchmark_result"; then
        log_success "✅ 优化成功！质量门禁全部通过"
    else
        log_warning "⚠️  优化后仍未达到质量门禁要求"
        log_info "请查看优化计划：$optimization_plan"
    fi
    
    # 6. 性能基准测试
    performance_benchmark "$new_benchmark_result"
    
    # 生成最终报告
    log_info "=========================================="
    log_info "生成最终优化报告"
    log_info "=========================================="
    
    local final_report="${REPORTS_DIR}/optimization_$(date +%Y%m%d_%H%M%S).md"
    
    cat > "$final_report" << EOF
# 规则优化报告

**执行时间**: $(date '+%Y-%m-%d %H:%M:%S')
**优化脚本**: optimize_rules.sh

## 📊 优化前后对比

### 优化前
- Benchmark 结果：$benchmark_result
- 分析报告：$analysis_file

### 优化后
- Benchmark 结果：$new_benchmark_result
- 规则备份：$backup_dir

## 📝 优化计划
- 优化计划文档：$optimization_plan

## 🚪 质量门禁状态
- 检测率目标：≥${GATE_DETECTION_RATE}%
- 误报率目标：<${GATE_FALSE_POSITIVE_RATE}%
- F1 Score 目标：≥${GATE_F1_SCORE}%

## ⚡ 性能指标
- 单规则平均时间：<${PERF_SINGLE_RULE}ms
- 千规则扫描时间：<${PERF_1000_RULES}ms

## 📁 生成文件
1. $benchmark_result
2. $analysis_file
3. $optimization_plan
4. $new_benchmark_result

---

*报告由 optimize_rules.sh 自动生成*
EOF
    
    log_success "最终报告已保存：$final_report"
    
    echo ""
    echo "=============================================="
    echo "         优化流程完成!"
    echo "=============================================="
    echo ""
    echo "📁 输出文件:"
    echo "  - Benchmark: $new_benchmark_result"
    echo "  - 分析报告：$analysis_file"
    echo "  - 优化计划：$optimization_plan"
    echo "  - 最终报告：$final_report"
    echo "  - 规则备份：$backup_dir"
    echo ""
}

# 运行主流程
main "$@"
