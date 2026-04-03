#!/usr/bin/env python3
"""
🧬 自进化系统核心引擎 v2
- 集成智能上下文管理
- 大文件缓冲层
- LLM 上下文精准优化
"""

import json
import subprocess
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# 导入智能上下文管理
from smart_context_manager import ContextCache, SmartContextBuilder

# === 配置 ===
WORKSPACE = Path('/home/cdy/.openclaw/workspace/agent-security-skill-scanner-master')
CONFIG = {
    'mode': 'conservative',  # conservative | standard | aggressive
    'cycle_minutes': 60,  # 保守模式 60 分钟
    'target_detection_rate': 98.0,
    'target_fp_rate': 0.0,
    'min_improvement': 0.5,
    'max_context_tokens': 4000,
    'cache_size_mb': 50,
}

# === 知识库 ===
class KnowledgeBase:
    def __init__(self):
        self.path = WORKSPACE / 'evolution_knowledge.json'
        self.data = self.load()
    
    def load(self) -> Dict:
        if self.path.exists():
            return json.loads(self.path.read_text())
        return {
            'successful_patterns': [],
            'failed_attempts': [],
            'optimized_rules': [],
            'weaknesses_history': [],
            'evolution_log': []
        }
    
    def save(self):
        self.path.write_text(json.dumps(self.data, indent=2, ensure_ascii=False))
    
    def add_experience(self, exp_type: str, data: Dict):
        if exp_type not in self.data:
            self.data[exp_type] = []
        self.data[exp_type].append({
            'timestamp': datetime.now().isoformat(),
            **data
        })
        self.save()

# === 1. 感知层 ===
class PerceptionLayer:
    def __init__(self):
        self.benchmark_script = WORKSPACE / 'benchmark' / 'benchmark_v3.py'
    
    def collect_metrics(self, rules_file: str) -> Dict:
        """收集性能指标"""
        result = subprocess.run(
            ['python3', str(self.benchmark_script), '--rules', rules_file],
            capture_output=True, text=True, timeout=90
        )
        
        metrics = {'raw_output': result.stdout}
        
        # 解析关键指标
        for line in result.stdout.split('\n'):
            if 'Detection Rate' in line:
                metrics['detection_rate'] = self._parse_percent(line)
            elif 'False Positive' in line:
                metrics['false_positive'] = self._parse_percent(line)
            elif 'F1 Score' in line:
                metrics['f1_score'] = self._parse_percent(line)
        
        # 解析攻击类型
        metrics['attack_types'] = {}
        in_attack_section = False
        for line in result.stdout.split('\n'):
            if 'BY ATTACK TYPE' in line:
                in_attack_section = True
                continue
            if in_attack_section and ':' in line and '%' in line:
                parts = line.split(':')
                if len(parts) == 2 and '/' in parts[1]:
                    name = parts[0].strip()
                    rate = self._parse_percent(parts[1])
                    metrics['attack_types'][name] = rate
        
        return metrics
    
    def _parse_percent(self, text: str) -> float:
        try:
            return float(text.replace('%', '').replace(':', '').strip())
        except:
            return 0.0
    
    def detect_anomalies(self, metrics: Dict) -> List[str]:
        """检测异常"""
        anomalies = []
        
        if metrics.get('detection_rate', 0) < CONFIG['target_detection_rate']:
            anomalies.append(f"检测率 {metrics['detection_rate']:.1f}% < 目标{CONFIG['target_detection_rate']}%")
        
        if metrics.get('false_positive', 0) > CONFIG['target_fp_rate']:
            anomalies.append(f"误报率 {metrics['false_positive']:.1f}% > 目标{CONFIG['target_fp_rate']}%")
        
        for attack, rate in metrics.get('attack_types', {}).items():
            if rate < 90:
                anomalies.append(f"{attack}: {rate:.1f}% < 90%")
        
        return anomalies

# === 2. 决策层 ===
class DecisionLayer:
    def __init__(self, kb: KnowledgeBase):
        self.kb = kb
    
    def analyze(self, metrics: Dict, anomalies: List[str]) -> Dict:
        """分析现状"""
        analysis = {
            'strengths': [],
            'weaknesses': [],
            'opportunities': [],
            'priorities': []
        }
        
        # 识别优势
        for attack, rate in metrics.get('attack_types', {}).items():
            if rate >= 95:
                analysis['strengths'].append(f"{attack}: {rate:.1f}%")
            elif rate < 90:
                analysis['weaknesses'].append({
                    'name': attack,
                    'current': rate,
                    'gap': 95 - rate,
                    'priority': 'high' if rate < 80 else 'medium'
                })
        
        # 排序优先级
        analysis['weaknesses'].sort(key=lambda x: x['gap'], reverse=True)
        analysis['priorities'] = [w['name'] for w in analysis['weaknesses'][:3]]
        
        return analysis
    
    def plan(self, analysis: Dict) -> List[Dict]:
        """生成优化计划"""
        tasks = []
        
        for weakness in analysis['weaknesses'][:3]:
            task = self._generate_task(weakness['name'])
            if task:
                tasks.append(task)
        
        return tasks
    
    def _generate_task(self, attack_type: str) -> Optional[Dict]:
        """生成优化任务"""
        task_map = {
            'persistence': {
                'action': 'add_rules',
                'file': 'persistence_rules.yar',
                'patterns': [
                    ('WMI', 'wmic', 'T1047'),
                    ('ScheduledTask', 'schtasks', 'T1053.005'),
                ]
            },
            'data_exfil': {
                'action': 'add_rules',
                'file': 'data_exfil_rules.yar',
                'patterns': [
                    ('DNSTunnel', 'nslookup', 'T1048.003'),
                    ('HTTPPost', 'POST /upload', 'T1041'),
                ]
            },
            'bash': {
                'action': 'add_rules',
                'file': 'bash_rules.yar',
                'patterns': [
                    ('ProcessSub', '<(', 'T1059.004'),
                    ('HereString', '<<<', 'T1059.004'),
                ]
            }
        }
        
        return task_map.get(attack_type)

# === 3. 执行层 ===
class ExecutionLayer:
    def __init__(self, kb: KnowledgeBase):
        self.kb = kb
        self.rules_dir = WORKSPACE / 'rules' / 'scanner_v3' / 'yara'
    
    def execute(self, tasks: List[Dict]) -> Dict:
        """执行任务"""
        results = {'success': [], 'failed': []}
        
        for task in tasks:
            try:
                if task['action'] == 'add_rules':
                    self._add_rules(task)
                    results['success'].append(task['file'])
            except Exception as e:
                results['failed'].append({'file': task['file'], 'error': str(e)})
        
        return results
    
    def _add_rules(self, task: Dict):
        """添加规则"""
        file_path = self.rules_dir / task['file']
        content = file_path.read_text() if file_path.exists() else ""
        
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
    
    def rebuild_and_test(self) -> Dict:
        """重新编译并测试"""
        # 编译所有规则
        files = [f for f in self.rules_dir.glob('*.yar') if 'all_rules' not in f.name]
        merged = ""
        
        for f in sorted(files):
            merged += f.read_text() + '\n\n'
        
        output = self.rules_dir / 'all_rules_v7.yar'
        output.write_text(merged)
        
        # 运行测试
        result = subprocess.run(
            ['python3', str(WORKSPACE / 'benchmark' / 'benchmark_v3.py'), '--rules', str(output)],
            capture_output=True, text=True, timeout=90
        )
        
        return {'output': output.name, 'test_result': result.stdout}

# === 4. 学习层 ===
class LearningLayer:
    def __init__(self, kb: KnowledgeBase):
        self.kb = kb
    
    def learn(self, before: Dict, after: Dict, tasks: List[Dict], results: Dict):
        """从本轮学习"""
        improvement = after.get('detection_rate', 0) - before.get('detection_rate', 0)
        
        self.kb.add_experience('evolution_log', {
            'before': before,
            'after': after,
            'improvement': improvement,
            'tasks': tasks,
            'results': results
        })
        
        if improvement > 0:
            self.kb.add_experience('successful_patterns', {
                'tasks': tasks,
                'improvement': improvement
            })
        elif improvement < 0:
            self.kb.add_experience('failed_attempts', {
                'tasks': tasks,
                'decline': -improvement
            })

# === 主循环 ===
class SelfEvolvingEngine:
    def __init__(self):
        self.kb = KnowledgeBase()
        self.perception = PerceptionLayer()
        self.decision = DecisionLayer(self.kb)
        self.execution = ExecutionLayer(self.kb)
        self.learning = LearningLayer(self.kb)
    
    def run_cycle(self):
        """运行一个进化周期"""
        print(f"\n{'='*60}")
        print(f"🧬 自进化周期 - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print(f"{'='*60}")
        
        # 1. 感知
        print("\n📊 1. 感知层 - 收集指标")
        current_rules = str(self.execution.rules_dir / 'all_rules_v7.yar')
        if not Path(current_rules).exists():
            current_rules = str(self.execution.rules_dir / 'all_rules_v6.yar')
        
        metrics = self.perception.collect_metrics(current_rules)
        print(f"   检测率：{metrics.get('detection_rate', 0):.1f}%")
        print(f"   误报率：{metrics.get('false_positive', 0):.1f}%")
        
        anomalies = self.perception.detect_anomalies(metrics)
        if anomalies:
            print(f"   异常：{len(anomalies)} 个")
            for a in anomalies[:3]:
                print(f"     - {a}")
        
        # 2. 决策
        print("\n🧠 2. 决策层 - 分析规划")
        analysis = self.decision.analyze(metrics, anomalies)
        print(f"   优势：{len(analysis['strengths'])} 个")
        print(f"   短板：{len(analysis['weaknesses'])} 个")
        
        tasks = self.decision.plan(analysis)
        print(f"   任务：{len(tasks)} 个")
        
        if not tasks:
            print("   ✅ 无需优化，所有指标已达标")
            return
        
        # 3. 执行
        print("\n🔧 3. 执行层 - 执行任务")
        results = self.execution.execute(tasks)
        print(f"   成功：{len(results['success'])} 个")
        print(f"   失败：{len(results['failed'])} 个")
        
        # 4. 测试
        print("\n📈 4. 验证层 - 测试新版本")
        test_result = self.execution.rebuild_and_test()
        new_metrics = self.perception.collect_metrics(str(self.execution.rules_dir / test_result['output']))
        print(f"   新检测率：{new_metrics.get('detection_rate', 0):.1f}%")
        
        # 5. 学习
        print("\n📚 5. 学习层 - 记录经验")
        self.learning.learn(metrics, new_metrics, tasks, results)
        improvement = new_metrics.get('detection_rate', 0) - metrics.get('detection_rate', 0)
        print(f"   提升：{improvement:+.1f}%")
        
        # 6. 总结
        print(f"\n{'='*60}")
        if improvement > CONFIG['min_improvement']:
            print(f"✅ 优化成功！检测率提升 {improvement:.1f}%")
        elif improvement > 0:
            print(f"⚠️  略有提升 (+{improvement:.1f}%)")
        else:
            print(f"🔴 需要调整策略 (变化：{improvement:.1f}%)")
        print(f"{'='*60}")

# === 启动 ===
if __name__ == '__main__':
    engine = SelfEvolvingEngine()
    
    # 单次运行
    engine.run_cycle()
    
    # 持续运行（取消注释启用）
    # print(f"\n🔄 启动持续进化模式 (周期：{CONFIG['cycle_minutes']}分钟)")
    # while True:
    #     try:
    #         engine.run_cycle()
    #         print(f"\n💤 等待 {CONFIG['cycle_minutes']} 分钟后继续...")
    #         time.sleep(CONFIG['cycle_minutes'] * 60)
    #     except KeyboardInterrupt:
    #         print("\n\n👋 用户中断，退出")
    #         break
    #     except Exception as e:
    #         print(f"\n❌ 错误：{e}")
    #         time.sleep(60)
