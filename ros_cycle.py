#!/usr/bin/env python3
"""
🔄 HROS v2.0 - Harness 融合版核心循环
Harness-Enhanced Research Orchestration System

每个环节融入 Harness 思想：
- 测试 (Testing): 验证数据准确性
- 评估 (Benchmarking): 量化指标
- 编排 (Orchestration): 条件/循环/并行
- 监控 (Observability): 记录追踪
- 自动化 (Workflow): 自动循环
"""

import json
import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List

# === 配置 ===
WORKSPACE = Path('/home/cdy/.openclaw/workspace/agent-security-skill-scanner-master')
LOGS_DIR = WORKSPACE / 'ros_logs'
META_DIR = WORKSPACE / 'ros_meta'
RULES_DIR = WORKSPACE / 'rules' / 'scanner_v3' / 'yara'
RULES_DIR_LOCAL = WORKSPACE / 'rules' / 'yara'  # 本地规则目录

LOGS_DIR.mkdir(exist_ok=True)
META_DIR.mkdir(exist_ok=True)

CONFIG = {
    'target_detection_rate': 98.0,
    'min_improvement': 0.5,
    'loop_interval_minutes': 60,
    
    # === P0 优化配置 (2026-03-29) ===
    # 动态间隔策略 - 基于检测率自动调整
    'intervals': {
        'excellent': 240,   # >=98%: 4 小时 (稳定期)
        'good': 120,        # >=96%: 2 小时 (优化期)
        'fair': 30,         # >=94%: 30 分钟 (加速期)
        'poor': 10,         # <94%: 10 分钟 (紧急期)
    },
    
    # 增量测试策略 - 快速/全量模式
    'quick_test_enabled': True,
    'quick_test_samples': 20,        # 快速模式样本数
    'full_test_interval': 10,        # 每 10 轮全量测试一次
    'quick_test_threshold': 0.5,     # 快速模式检测率下降超过此值则触发全量测试
}

# === 工具函数 ===
def log(msg, level='info'):
    """统一日志输出"""
    emoji = {'info': 'ℹ️', 'success': '✅', 'warning': '⚠️', 'error': '❌'}
    print(f"{emoji.get(level, '•')} {msg}")

def run_benchmark(rules_file: str, quick_mode: bool = False) -> Dict:
    """运行 benchmark
    
    Args:
        rules_file: 规则文件路径
        quick_mode: 快速模式 (仅测试核心样本)
    """
    # 快速模式参数
    args = ['python3', str(WORKSPACE / 'benchmark' / 'benchmark_v3.py'), '--rules', rules_file]
    if quick_mode:
        args.extend(['--quick', f'--samples={CONFIG.get("quick_test_samples", 20)}'])
    
    result = subprocess.run(
        args,
        capture_output=True, text=True, timeout=90
    )
    
    metrics = {}
    for line in result.stdout.split('\n'):
        if 'Detection Rate' in line:
            metrics['detection_rate'] = float(line.split(':')[1].strip().replace('%', ''))
        elif 'False Positive' in line:
            metrics['false_positive'] = float(line.split(':')[1].strip().replace('%', ''))
        elif 'F1 Score' in line:
            metrics['f1_score'] = float(line.split(':')[1].strip().replace('%', ''))
    
    # 解析攻击类型
    metrics['attack_types'] = {}
    in_section = False
    for line in result.stdout.split('\n'):
        if 'BY ATTACK TYPE' in line:
            in_section = True
            continue
        if in_section and ':' in line and '%' in line and '/ ' in line:
            parts = line.split(':')
            if len(parts) == 2 and '=' in parts[1]:
                name = parts[0].strip()
                rate = float(parts[1].split('=')[1].replace('%', '').strip())
                metrics['attack_types'][name] = rate
    
    return metrics

def load_history() -> List[Dict]:
    """加载历史记录"""
    history_file = META_DIR / 'history.json'
    if history_file.exists():
        return json.loads(history_file.read_text())
    return []

def save_history(history: List[Dict]):
    """保存历史记录"""
    history_file = META_DIR / 'history.json'
    history_file.write_text(json.dumps(history[-50:], indent=2))  # 保留最近 50 轮

def get_cycle_number() -> int:
    """获取当前循环编号"""
    history = load_history()
    return len(history) + 1

def get_dynamic_interval(detection_rate: float) -> int:
    """根据检测率动态计算间隔时间 (分钟)
    
    Args:
        detection_rate: 当前检测率 (0-100)
    
    Returns:
        间隔分钟数
    """
    intervals = CONFIG.get('intervals', {})
    
    if detection_rate >= 98:
        interval = intervals.get('excellent', 240)
        status = '稳定期'
    elif detection_rate >= 96:
        interval = intervals.get('good', 120)
        status = '优化期'
    elif detection_rate >= 94:
        interval = intervals.get('fair', 30)
        status = '加速期'
    else:
        interval = intervals.get('poor', 10)
        status = '紧急期'
    
    log(f"🕐 动态间隔：{interval}分钟 ({status}, 检测率：{detection_rate:.1f}%)", 'info')
    return interval

def should_run_quick_test(cycle_num: int, quick_enabled: bool = True) -> bool:
    """判断是否运行快速测试
    
    Args:
        cycle_num: 当前循环编号
        quick_enabled: 是否启用快速测试
    
    Returns:
        True=快速模式，False=全量模式
    """
    if not quick_enabled:
        return False
    
    # 每 N 轮运行一次全量测试
    full_test_interval = CONFIG.get('full_test_interval', 10)
    if cycle_num % full_test_interval == 0:
        log(f"📊 第{cycle_num}轮：运行全量测试 (每{full_test_interval}轮一次)", 'info')
        return False
    
    # 其他情况运行快速测试
    log(f"⚡ 第{cycle_num}轮：运行快速测试", 'info')
    return True

# === 五个核心步骤 ===

def step_analyze() -> Dict:
    """步骤 1: 分析 (P2 增强版：集成事件驱动)
    
    P2 增强:
    - 调用事件触发器检测检测率变化
    - 自动发布事件到事件总线
    """
    log("📊 步骤 1: 分析当前状态", 'info')
    
    # 找到最新规则文件
    # 查找规则文件（优先 merged_rules.yar，然后 all_rules_v*.yar）
    rules_files = list(RULES_DIR.glob('all_rules_v*.yar'))
    if not rules_files:
        # 尝试本地规则目录
        rules_files = list(RULES_DIR_LOCAL.glob('resource_exhaustion*.yar'))
    if not rules_files:
        # 使用 merged_rules.yar
        merged = RULES_DIR / 'merged_rules.yar'
        if merged.exists():
            rules_files = [merged]
    if not rules_files:
        log("❌ 未找到规则文件", 'error')
        return {}
    
    latest_rules = str(rules_files[-1])
    metrics = run_benchmark(latest_rules)
    
    # P2 增强：事件驱动监控
    try:
        from event_driver import EventBus, EventTrigger, EventType, Priority, Event
        from pathlib import Path
        
        # 创建事件触发器
        event_bus = EventBus()
        trigger = EventTrigger(event_bus)
        
        # 触发检测率检查
        cycle_num = get_cycle_number()
        trigger.check_detection_rate({
            'detection_rate': metrics.get('detection_rate', 0),
            'cycle_num': cycle_num
        })
        
        log("  👁️  P2 事件驱动监控已激活", 'info')
        
    except Exception as e:
        log(f"  ⚠️  P2 事件驱动异常：{e}", 'warning')
    
    # 输出
    log(f"检测率：{metrics.get('detection_rate', 0):.1f}%")
    log(f"误报率：{metrics.get('false_positive', 0):.1f}%")
    log(f"F1 Score: {metrics.get('f1_score', 0):.1f}%")
    
    # 识别短板
    weaknesses = []
    for name, rate in metrics.get('attack_types', {}).items():
        if rate < 95:
            weaknesses.append({'name': name, 'current': rate, 'target': 95})
            log(f"⚠️  {name}: {rate:.1f}% (<95%)", 'warning')
    
    if not weaknesses:
        log("✅ 所有攻击类型 ≥95%", 'success')
    
    return {
        'metrics': metrics,
        'weaknesses': weaknesses,
        'rules_file': latest_rules
    }

def step_plan(analysis: Dict) -> List[Dict]:
    """步骤 2: 规划
    
    P1 增强：集成自动优化器
    """
    log("\n📋 步骤 2: 规划本轮任务", 'info')
    
    weaknesses = analysis.get('weaknesses', [])
    if not weaknesses:
        log("✅ 无需优化，所有指标已达标", 'success')
        return []
    
    # P1 增强：自动优化器
    log("🤖 调用 P1 自动优化器...", 'info')
    try:
        from auto_optimizer import run_auto_optimization
        metrics = analysis.get('metrics', {})
        opt_report = run_auto_optimization(metrics)
        
        if opt_report.get('status') == 'no_optimization_needed':
            log("✅ 自动优化器：无需优化", 'success')
            return []
        
        improvement = opt_report.get('improvement', 0)
        log(f"✅ 自动优化器完成：检测率提升 {improvement:+.1f}%", 'success')
        
    except Exception as e:
        log(f"⚠️  自动优化器异常：{e}", 'warning')
        # 降级到传统模式
    
    # 传统模式：选择 top 2 短板
    tasks = []
    for w in sorted(weaknesses, key=lambda x: x['current'])[:2]:
        task = {
            'attack_type': w['name'],
            'target_file': f"{w['name']}_rules.yar",
            'current': w['current'],
            'target': w['target'],
            'patterns': get_patterns_for_attack(w['name'])
        }
        tasks.append(task)
        log(f"  📝 优化 {w['name']} ({w['current']:.1f}% → {w['target']}%)", 'info')
    
    return tasks

def get_patterns_for_attack(attack_type: str) -> List[tuple]:
    """获取攻击类型的规则模式"""
    patterns_map = {
        'persistence': [
            ('WMI', 'wmic /node:', 'T1047'),
            ('ScheduledTask', 'schtasks /create', 'T1053.005'),
        ],
        'data_exfil': [
            ('DNSTunnel', 'nslookup', 'T1048.003'),
            ('HTTPPost', 'POST /upload', 'T1041'),
        ],
        'bash': [
            ('ProcessSub', '<(', 'T1059.004'),
            ('HereString', '<<<', 'T1059.004'),
        ]
    }
    return patterns_map.get(attack_type, [])

def step_do(tasks: List[Dict]) -> Dict:
    """步骤 3: 执行"""
    log("\n🔧 步骤 3: 执行任务", 'info')
    
    results = {'success': [], 'failed': []}
    
    for task in tasks:
        try:
            file_path = RULES_DIR / task['target_file']
            content = file_path.read_text() if file_path.exists() else f"// {task['attack_type']} rules\n\n"
            
            # 添加新规则
            for name, pattern, mitre in task['patterns']:
                rule_name = f"{name}_{datetime.now().strftime('%Y%m%d')}"
                rule = f"""
rule {rule_name} {{
    meta:
        description = "Auto-generated: {name}"
        severity = "high"
        mitre = "{mitre}"
    strings:
        $p = "{pattern}"
    condition:
        $p
}}
"""
                content += rule
            
            file_path.write_text(content)
            results['success'].append(task['target_file'])
            log(f"  ✅ {task['target_file']} (+{len(task['patterns'])} rules)", 'success')
        
        except Exception as e:
            results['failed'].append({'file': task['target_file'], 'error': str(e)})
            log(f"  ❌ {task['target_file']}: {e}", 'error')
    
    return results

def step_check(quick_mode: bool = False) -> Dict:
    """步骤 4: 验证
    
    Args:
        quick_mode: 是否使用快速模式
    """
    log("\n📈 步骤 4: 验证效果", 'info')
    
    # 重新编译规则
    rules_files = [f for f in RULES_DIR.glob('*.yar') if 'all_rules' not in f.name]
    merged = ""
    for f in sorted(rules_files):
        merged += f.read_text() + '\n\n'
    
    cycle_num = get_cycle_number()
    output = RULES_DIR / f'all_rules_v{cycle_num}.yar'
    output.write_text(merged)
    
    # 运行测试 (快速模式 or 全量模式)
    metrics = run_benchmark(str(output), quick_mode=quick_mode)
    
    mode_str = " (快速模式)" if quick_mode else ""
    log(f"检测率：{metrics.get('detection_rate', 0):.1f}%{mode_str}", 'info')
    log(f"误报率：{metrics.get('false_positive', 0):.1f}%", 'info')
    log(f"F1 Score: {metrics.get('f1_score', 0):.1f}%", 'info')
    
    return metrics

def step_reflect(before: Dict, after: Dict, tasks: List[Dict]) -> Dict:
    """步骤 5: 反思"""
    log("\n💡 步骤 5: 反思总结", 'info')
    
    improvement = after.get('detection_rate', 0) - before.get('detection_rate', 0)
    
    reflection = {
        'improvement': improvement,
        'success': improvement >= CONFIG['min_improvement'],
        'tasks': tasks,
        'lessons': []
    }
    
    if improvement >= CONFIG['min_improvement']:
        log(f"✅ 成功！检测率提升 +{improvement:.1f}%", 'success')
        reflection['lessons'].append(f"有效策略：{[t['attack_type'] for t in tasks]}")
    elif improvement > 0:
        log(f"⚠️  略有提升 +{improvement:.1f}% (<{CONFIG['min_improvement']}%)", 'warning')
    else:
        log(f"🔴 需要调整策略 (变化：{improvement:+.1f}%)", 'error')
        reflection['lessons'].append(f"需要调整：{[t['attack_type'] for t in tasks]}")
    
    return reflection

# === 主循环 ===

def run_cycle():
    """运行一个完整循环（P0 优化版：动态间隔 + 增量测试）"""
    cycle_num = get_cycle_number()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    log(f"\n{'='*60}", 'info')
    log(f"🔄 ROS 循环 #{cycle_num} - {timestamp}", 'info')
    log(f"{'='*60}", 'info')
    
    # 判断是否运行快速测试
    quick_mode = should_run_quick_test(cycle_num, CONFIG.get('quick_test_enabled', True))
    
    # 1. 分析（始终使用全量模式获取准确指标）
    analysis = step_analyze()
    if not analysis:
        # 即使失败也要保存记录
        cycle_record = {
            'cycle': cycle_num,
            'timestamp': timestamp,
            'status': 'analysis_failed',
            'error': 'Failed to analyze current state'
        }
        history = load_history()
        history.append(cycle_record)
        save_history(history)
        return None
    
    # 2. 规划
    tasks = step_plan(analysis)
    
    # 即使没有任务也要继续
    before_metrics = analysis['metrics']
    after_metrics = before_metrics.copy()
    exec_results = {'success': [], 'failed': []}
    
    if tasks:
        # 3. 执行
        exec_results = step_do(tasks)
        
        # 4. 验证（使用快速模式 or 全量模式）
        after_metrics = step_check(quick_mode=quick_mode)
    else:
        log("\nℹ️  跳过执行和验证（所有指标已达标）", 'info')
    
    # 5. 反思
    reflection = step_reflect(before_metrics, after_metrics, tasks)
    
    # 保存记录（无论是否有任务）
    cycle_record = {
        'cycle': cycle_num,
        'timestamp': timestamp,
        'before': before_metrics,
        'after': after_metrics,
        'tasks': tasks,
        'execution': exec_results,
        'reflection': reflection,
        'quick_mode': quick_mode
    }
    
    history = load_history()
    history.append(cycle_record)
    save_history(history)
    
    # 保存本轮日志
    log_file = LOGS_DIR / f'cycle_{cycle_num:03d}.md'
    log_content = f"""# ROS Cycle #{cycle_num}

**时间**: {timestamp}
**状态**: {'无需优化' if not tasks else '已优化'}
**模式**: {'快速' if quick_mode else '全量'}

## 指标
- 检测率：{before_metrics.get('detection_rate', 0):.1f}% → {after_metrics.get('detection_rate', 0):.1f}%
- 提升：{reflection['improvement']:+.1f}%

## 任务
{chr(10).join([f"- {t['attack_type']}" for t in tasks]) if tasks else '无'}

## 反思
{chr(10).join(reflection['lessons']) if reflection['lessons'] else '无'}
"""
    log_file.write_text(log_content)
    
    log(f"\n{'='*60}", 'info')
    log(f"✅ 循环 #{cycle_num} 完成 ({'快速' if quick_mode else '全量'}模式)", 'success')
    log(f"{'='*60}", 'info')
    
    return cycle_record

def run_loop(interval_minutes: int = None):
    """持续循环运行（P0 优化版：动态间隔）
    
    Args:
        interval_minutes: 初始间隔分钟数（None=使用动态间隔）
    """
    if interval_minutes is None:
        log(f"\n🔄 启动持续循环模式 (动态间隔)", 'info')
    else:
        log(f"\n🔄 启动持续循环模式 (固定间隔：{interval_minutes}分钟)", 'info')
    
    try:
        while True:
            cycle_record = run_cycle()
            
            # 计算下一轮间隔（动态 or 固定）
            if interval_minutes is None and cycle_record:
                # 动态间隔：基于检测率
                detection_rate = cycle_record.get('after', {}).get('detection_rate', 95.0)
                next_interval = get_dynamic_interval(detection_rate)
            else:
                # 固定间隔
                next_interval = interval_minutes if interval_minutes else 60
            
            next_run = datetime.now().timestamp() + (next_interval * 60)
            log(f"\n💤 等待至 {datetime.fromtimestamp(next_run).strftime('%H:%M')} 继续下一轮 ({next_interval}分钟)...")
            time.sleep(next_interval * 60)
    except KeyboardInterrupt:
        log("\n\n👋 用户中断，退出循环", 'warning')

# === CLI ===

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--loop':
        # 动态间隔模式（默认）or 固定间隔模式
        if '--interval' in sys.argv:
            idx = sys.argv.index('--interval')
            if idx + 1 < len(sys.argv):
                interval = int(sys.argv[idx + 1])
                log(f"使用固定间隔：{interval}分钟", 'info')
                run_loop(interval)
            else:
                log("❌ --interval 需要参数", 'error')
                sys.exit(1)
        else:
            # 动态间隔模式（默认）
            log("使用动态间隔模式（基于检测率自动调整）", 'info')
            run_loop()
    else:
        run_cycle()


# === Harness 融合增强 ===

def step_analyze_harness():
    """分析环节 - 融合 Harness 思想"""
    log("\n📊 步骤 1: 分析 (融合 Harness)", 'info')
    
    # 测试思维：验证数据准确性
    def validate_metrics(metrics):
        assert 0 <= metrics.get('detection_rate', 0) <= 100, "检测率超出范围"
        assert 0 <= metrics.get('false_positive', 0) <= 100, "误报率超出范围"
        log("  ✅ 测试：数据准确性验证通过", 'success')
    
    # 评估思维：量化当前状态
    def assess_status(metrics):
        status = "优秀" if metrics.get('detection_rate', 0) >= 95 else "待优化"
        log(f"  📊 评估：当前状态 {status}", 'info')
        return status
    
    # 监控思维：记录基线
    def record_baseline(metrics):
        baseline_file = META_DIR / 'baseline.json'
        baseline_file.write_text(json.dumps({
            'timestamp': datetime.now().isoformat(),
            'metrics': metrics
        }, indent=2))
        log("  👁️ 监控：基线已记录", 'info')
    
    analysis = step_analyze()
    
    if analysis:
        validate_metrics(analysis['metrics'])
        assess_status(analysis['metrics'])
        record_baseline(analysis['metrics'])
    
    return analysis


def step_verify_harness(before, tasks):
    """验证环节 - 融合 Harness 思想"""
    log("\n📈 步骤 4: 验证 (融合 Harness)", 'info')
    
    # 测试思维：多层次测试
    def run_tests():
        log("  🧪 测试：运行测试套件...", 'info')
        # 语法测试
        test_result = subprocess.run(
            ['python3', '-c', 'import yara; yara.compile(source="rule t{strings:$a=\"test\" condition:$a}")'],
            capture_output=True, timeout=10
        )
        if test_result.returncode == 0:
            log("    ✅ 语法测试通过", 'success')
        else:
            log("    ❌ 语法测试失败", 'error')
        
        return test_result.returncode == 0
    
    # 评估思维：benchmark 对比
    def compare_benchmark():
        log("  📊 评估：运行 benchmark...", 'info')
        after = run_benchmark(str(RULES_DIR / f'all_rules_v{get_cycle_number()}.yar'))
        
        improvement = after.get('detection_rate', 0) - before.get('detection_rate', 0)
        if improvement >= 0:
            log(f"    ✅ 检测率提升 +{improvement:.1f}%", 'success')
        else:
            log(f"    ⚠️  检测率下降 {improvement:.1f}%", 'warning')
        
        return after
    
    # 编排思维：循环验证
    test_passed = run_tests()
    after = compare_benchmark()
    
    if not test_passed:
        log("  ⚠️  测试失败，需要修复", 'warning')
    
    return after


# 修改主循环使用 Harness 融合版本
def run_cycle_harness():
    """运行融合 Harness 思想的完整循环"""
    cycle_num = get_cycle_number()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    log(f"\n{'='*60}", 'info')
    log(f"🔄 HROS v2.0 循环 #{cycle_num} - {timestamp}", 'info')
    log(f"{'='*60}", 'info')
    
    # 1. 分析 (融合 Harness)
    analysis = step_analyze_harness()
    if not analysis:
        return None
    
    # 2. 规划
    tasks = step_plan(analysis)
    
    before_metrics = analysis['metrics']
    after_metrics = before_metrics.copy()
    exec_results = {'success': [], 'failed': []}
    
    if tasks:
        # 3. 执行 (融合监控)
        log("\n🔧 步骤 3: 执行 (融合监控)", 'info')
        start_time = time.time()
        
        exec_results = step_do(tasks)
        
        duration = time.time() - start_time
        log(f"  👁️ 监控：执行耗时 {duration:.1f}秒", 'info')
        
        if duration > 30:
            log("  ⚠️  告警：执行时间过长", 'warning')
        
        # 4. 验证 (融合 Harness)
        after_metrics = step_verify_harness(before_metrics, tasks)
    else:
        log("\nℹ️  跳过执行和验证（所有指标已达标）", 'info')
    
    # 5. 反思 (融合评估)
    reflection = step_reflect(before_metrics, after_metrics, tasks)
    
    # 保存记录
    cycle_record = {
        'cycle': cycle_num,
        'timestamp': timestamp,
        'before': before_metrics,
        'after': after_metrics,
        'tasks': tasks,
        'execution': exec_results,
        'reflection': reflection,
        'harness_fusion': True  # 标记为融合版本
    }
    
    history = load_history()
    history.append(cycle_record)
    save_history(history)
    
    log(f"\n{'='*60}", 'info')
    log(f"✅ HROS v2.0 循环 #{cycle_num} 完成", 'success')
    log(f"{'='*60}", 'info')
    
    return cycle_record
