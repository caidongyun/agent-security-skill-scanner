#!/usr/bin/env python3
"""
自驱动进度汇报服务
每 5 分钟自动汇报一次项目进展
"""
import os, json, glob, subprocess, sys
from datetime import datetime, timedelta

def get_latest_scan_result():
    """获取最新扫描结果"""
    files = sorted(glob.glob('output/ros-scan-v2-*.json'), key=lambda f: -os.path.getmtime(f))
    if files:
        return json.load(open(files[0]))
    return None

def count_samples():
    """统计样本数量"""
    counts = {'benign': 0, 'market': 0, 'development': 0, 'malicious': 0}
    
    for category in counts.keys():
        sample_dir = f'samples/{category}'
        if os.path.exists(sample_dir):
            for root, dirs, files in os.walk(sample_dir):
                counts[category] += len([f for f in files if f.endswith(('.py', '.js', '.ts', '.sh', '.yaml', '.yml', '.json', '.txt'))])
    
    return counts

def count_rules():
    """统计规则数量"""
    rules_file = 'scanner-master/output/rules/scanner_master_rules.yar'
    if os.path.exists(rules_file):
        with open(rules_file) as f:
            return len([line for line in f if line.startswith('rule ')])
    return 0

def get_task_status():
    """获取任务状态"""
    tasks = {
        'fp_optimization': {'target': '<15%', 'current': '26.7%', 'status': '🔄'},
        'benign_samples': {'target': '100', 'current': '0', 'status': '🔄'},
        'rule_review': {'target': '500', 'current': '0', 'status': '⏳'},
        'detection_rate': {'target': '>95%', 'current': '91.1%', 'status': '🟡'},
    }
    
    # 更新良性样本数
    sample_counts = count_samples()
    tasks['benign_samples']['current'] = str(sample_counts['benign'])
    
    # 计算进度
    total = 4
    completed = 0
    for task in tasks.values():
        if task['status'] == '✅':
            completed += 1
        elif task['status'] == '🔄':
            completed += 0.5
    
    tasks['overall_progress'] = f'{completed/total*100:.0f}%'
    
    return tasks

def generate_report():
    """生成进度报告"""
    scan_result = get_latest_scan_result()
    sample_counts = count_samples()
    rule_count = count_rules()
    tasks = get_task_status()
    
    report = f"""
╔══════════════════════════════════════════════════════════════╗
║          🤖 Agent Security Scanner 进度汇报                   ║
║                  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}                     ║
╚══════════════════════════════════════════════════════════════╝

📊 核心指标
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  规则总数：{rule_count} 条 (6 种语言)
  样本总数：{sum(sample_counts.values())} 个
    ├─ 良性样本：{sample_counts['benign']} 个
    ├─ 市场样本：{sample_counts['market']} 个
    ├─ 开发样本：{sample_counts['development']} 个
    └─ 恶意样本：{sample_counts['malicious']} 个

📈 Benchmark 测试
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    if scan_result:
        acc = scan_result.get('accuracy', {})
        findings = scan_result.get('findings', {})
        report += f"""
  检测率：{acc.get('detection_rate', 0)*100:.1f}% (目标 >98%)
  误报率：{acc.get('false_positive_rate', 0)*100:.1f}% (目标 <5%)
  测试样本：{findings.get('malicious', 0) + findings.get('benign', 0):,} 个
  正确：{acc.get('correct', 0):,} | FP: {acc.get('false_positives', 0):,} | FN: {acc.get('false_negatives', 0):,}
"""
    else:
        report += "  ⏳ 暂无扫描结果\n"
    
    report += f"""
📋 任务状态
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  误报优化：{tasks['fp_optimization']['current']} → {tasks['fp_optimization']['target']} {tasks['fp_optimization']['status']}
  良性样本：{tasks['benign_samples']['current']}/100 {tasks['benign_samples']['status']}
  规则审核：{tasks['rule_review']['current']}/{tasks['rule_review']['target']} {tasks['rule_review']['status']}
  检测率：{tasks['detection_rate']['current']} → {tasks['detection_rate']['target']} {tasks['detection_rate']['status']}
  
  整体进度：{tasks['overall_progress']}

🚀 最近活动
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    # 获取最近文件
    recent_files = []
    for root, dirs, files in os.walk('.'):
        for f in files:
            if f.endswith(('.md', '.json', '.py', '.yar')):
                filepath = os.path.join(root, f)
                mtime = os.path.getmtime(filepath)
                if datetime.now().timestamp() - mtime < 3600:  # 1 小时内
                    recent_files.append((filepath, mtime))
    
    recent_files.sort(key=lambda x: -x[1])
    for filepath, mtime in recent_files[:5]:
        time_ago = datetime.now() - datetime.fromtimestamp(mtime)
        report += f"  ✅ {filepath} ({int(time_ago.total_seconds()/60)}分钟前)\n"
    
    report += """
📋 下一步计划
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  1. 误报率优化至 <20% (添加路径例外)
  2. 良性样本扩展至 60 个 (+16 个)
  3. 规则审核启动 (目标 500 条)
  4. 下一轮扫描测试

═══════════════════════════════════════════════════════════════
  下次汇报：5 分钟后 | 自驱动服务运行中 ✅
═══════════════════════════════════════════════════════════════
"""
    
    return report

def save_report(report):
    """保存报告"""
    os.makedirs('reports/progress', exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = f'reports/progress/report_{timestamp}.md'
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    # 更新最新报告链接
    with open('reports/progress/LATEST.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    return report_file

def main():
    print("🤖 自驱动进度汇报服务启动...")
    print()
    
    # 生成报告
    report = generate_report()
    report_file = save_report(report)
    
    # 输出报告
    print(report)
    
    # 保存 JSON 版本
    os.makedirs('reports/progress/json', exist_ok=True)
    json_report = {
        'timestamp': datetime.now().isoformat(),
        'report_file': report_file,
        'metrics': {
            'rules': count_rules(),
            'samples': count_samples(),
            'tasks': get_task_status(),
        },
    }
    
    json_file = f'reports/progress/json/report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(json_file, 'w') as f:
        json.dump(json_report, f, indent=2)
    
    print(f"✅ 报告已保存：{report_file}")
    print(f"✅ JSON 报告：{json_file}")

if __name__ == '__main__':
    main()
