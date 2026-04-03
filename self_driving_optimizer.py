#!/usr/bin/env python3
"""
🚀 产品自驱动优化系统
自动分析 → 自动规划 → 自动执行 → 自动验证
"""

import subprocess
import json
from pathlib import Path
from datetime import datetime

WORKSPACE = Path('/home/cdy/.openclaw/workspace/agent-security-skill-scanner-master')
BENCHMARK = WORKSPACE / 'benchmark' / 'benchmark_v3.py'
RULES_DIR = WORKSPACE / 'rules' / 'scanner_v3' / 'yara'
LOG_DIR = WORKSPACE / 'logs'
LOG_FILE = LOG_DIR / f'evolution_{datetime.now().strftime("%Y%m%d_%H%M")}.log'

LOG_DIR.mkdir(parents=True, exist_ok=True)

def log(msg):
    print(msg)
    with open(LOG_FILE, 'a') as f:
        f.write(msg + '\n')

def run_benchmark(rules_file):
    """运行 benchmark 测试"""
    result = subprocess.run(
        ['python3', str(BENCHMARK), '--rules', str(rules_file)],
        capture_output=True, text=True, timeout=90
    )
    
    # 解析结果
    lines = result.stdout.split('\n')
    metrics = {}
    
    for line in lines:
        if 'Detection Rate' in line:
            metrics['detection_rate'] = float(line.split(':')[1].strip().replace('%', ''))
        elif 'False Positive' in line:
            metrics['false_positive'] = float(line.split(':')[1].strip().replace('%', ''))
        elif 'F1 Score' in line:
            metrics['f1_score'] = float(line.split(':')[1].strip().replace('%', ''))
    
    # 解析攻击类型
    attack_types = {}
    for line in lines:
        if ':' in line and '/ ' in line and '%' in line:
            parts = line.split(':')
            if len(parts) == 2:
                name = parts[0].strip()
                rate_part = parts[1].strip()
                if '=' in rate_part:
                    rate = float(rate_part.split('=')[1].replace('%', '').strip())
                    attack_types[name] = rate
    
    metrics['attack_types'] = attack_types
    return metrics

def analyze_weaknesses(metrics):
    """分析短板"""
    weaknesses = []
    
    # 检测率目标
    if metrics.get('detection_rate', 0) < 98:
        weaknesses.append({
            'type': 'overall',
            'name': '整体检测率',
            'current': metrics.get('detection_rate', 0),
            'target': 98,
            'priority': 'high'
        })
    
    # 攻击类型短板
    for attack, rate in metrics.get('attack_types', {}).items():
        if rate < 95:
            priority = 'high' if rate < 80 else 'medium'
            weaknesses.append({
                'type': 'attack_type',
                'name': attack,
                'current': rate,
                'target': 95,
                'priority': priority
            })
    
    return weaknesses

def generate_optimization_task(weakness):
    """生成优化任务"""
    name = weakness['name']
    
    if name == 'persistence':
        return {
            'action': 'add_rules',
            'target_file': 'persistence_rules.yar',
            'patterns': [
                ('WMI 持久化', 'wmic /node:', 'T1047'),
                ('计划任务', 'schtasks /create', 'T1053.005'),
                ('启动文件夹', 'Startup', 'T1547.001'),
            ]
        }
    elif name == 'data_exfil':
        return {
            'action': 'add_rules',
            'target_file': 'data_exfil_rules.yar',
            'patterns': [
                ('DNS 隧道', 'nslookup', 'T1048.003'),
                ('ICMP 隧道', 'ping -t', 'T1048.003'),
                ('HTTPS 隐蔽', 'POST /upload', 'T1041'),
            ]
        }
    elif name == 'bash':
        return {
            'action': 'add_rules',
            'target_file': 'bash_rules.yar',
            'patterns': [
                ('进程替换', '<(', 'T1059.004'),
                ('Here-string', '<<<', 'T1059.004'),
                ('数组混淆', 'declare -a', 'T1027'),
            ]
        }
    else:
        return None

def execute_task(task):
    """执行优化任务"""
    if task['action'] != 'add_rules':
        return False
    
    target_file = RULES_DIR / task['target_file']
    
    # 读取现有内容
    if target_file.exists():
        content = target_file.read_text()
    else:
        content = "// Auto-generated rules\n\n"
    
    # 添加新规则
    new_rules = []
    for pattern_name, pattern, mitre in task['patterns']:
        rule_name = pattern_name.upper().replace(' ', '_')
        rule = f"""
rule {rule_name} {{
    meta:
        description = "Auto-generated: {pattern_name}"
        severity = "high"
        mitre = "{mitre}"
    strings:
        $p = "{pattern}"
    condition:
        $p
}}
"""
        new_rules.append(rule)
        content += rule
        log(f"  ✅ 添加规则：{rule_name}")
    
    # 保存
    target_file.write_text(content)
    return True

def rebuild_and_test():
    """重新编译并测试"""
    log("\n🔧 重新编译规则...")
    
    files = [
        'scanner_v3_yar', 'privilege_escalation_rules.yar', 'impact_rules.yar',
        'enhanced_shell_rules_optimized.yar', 'enhanced_js_rules.yar',
        'powershell_rules.yar', 'credential_theft_rules.yar', 'persistence_rules.yar',
        'bash_rules.yar', 'supply_chain_rules.yar'
    ]
    
    merged = ""
    total = 0
    
    for f in files:
        fpath = RULES_DIR / f
        if fpath.exists():
            content = fpath.read_text()
            merged += content + '\n\n'
            total += content.count('rule ')
    
    output = RULES_DIR / 'all_rules_v7.yar'
    output.write_text(merged)
    log(f"✅ 编译完成：all_rules_v7.yar ({total} rules)")
    
    log("\n📊 运行测试...")
    metrics = run_benchmark(output)
    
    log("\n" + "="*60)
    log("📈 优化结果")
    log("="*60)
    log(f"检测率：{metrics.get('detection_rate', 0):.1f}%")
    log(f"误报率：{metrics.get('false_positive', 0):.1f}%")
    log(f"F1 Score: {metrics.get('f1_score', 0):.1f}")
    
    if 'attack_types' in metrics:
        log("\n攻击类型检测率:")
        for attack, rate in sorted(metrics['attack_types'].items(), key=lambda x: x[1]):
            status = '✅' if rate >= 95 else '⚠️' if rate >= 80 else '🔴'
            log(f"  {status} {attack}: {rate:.1f}%")
    
    return metrics

def main():
    log("\n" + "="*60)
    log(f"🚀 产品自驱动优化 - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    log("="*60)
    
    # 1. 运行基准测试
    log("\n📊 步骤 1: 基准测试")
    current_rules = RULES_DIR / 'all_rules_v6.yar'
    if not current_rules.exists():
        current_rules = RULES_DIR / 'all_rules_v5.yar'
    
    metrics = run_benchmark(current_rules)
    log(f"当前检测率：{metrics.get('detection_rate', 0):.1f}%")
    
    # 2. 分析短板
    log("\n🔍 步骤 2: 分析短板")
    weaknesses = analyze_weaknesses(metrics)
    
    if not weaknesses:
        log("✅ 所有指标已达标，无需优化")
        return
    
    for w in weaknesses:
        log(f"  ⚠️ {w['name']}: {w['current']:.1f}% (目标：{w['target']}%)")
    
    # 3. 生成优化任务
    log("\n📋 步骤 3: 生成优化任务")
    for w in weaknesses[:3]:  # 优先处理前 3 个短板
        if w['type'] == 'attack_type':
            task = generate_optimization_task(w)
            if task:
                log(f"\n🔧 执行任务：优化 {w['name']}")
                execute_task(task)
    
    # 4. 重新测试
    log("\n✅ 步骤 4: 验证优化")
    new_metrics = rebuild_and_test()
    
    # 5. 对比结果
    log("\n" + "="*60)
    log("📊 优化对比")
    log("="*60)
    old_rate = metrics.get('detection_rate', 0)
    new_rate = new_metrics.get('detection_rate', 0)
    improvement = new_rate - old_rate
    
    if improvement > 0:
        log(f"✅ 检测率提升：{old_rate:.1f}% → {new_rate:.1f}% (+{improvement:.1f}%)")
    elif improvement == 0:
        log(f"⚠️  检测率持平：{new_rate:.1f}%")
    else:
        log(f"🔴 检测率下降：{old_rate:.1f}% → {new_rate:.1f}% ({improvement:.1f}%)")
    
    log("\n" + "="*60)
    log("✅ 本轮优化完成")
    log("="*60)

if __name__ == '__main__':
    main()
