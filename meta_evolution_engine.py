#!/usr/bin/env python3
"""
🧬 元进化层 - 自进化系统的自我优化
Self-Reflection + Auto-Tuning + Quality Alignment
"""

import json
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

# 导入基础组件
from smart_context_manager import ContextCache, SmartContextBuilder

WORKSPACE = Path('/home/cdy/.openclaw/workspace/agent-security-skill-scanner-master')
METADATA_DIR = WORKSPACE / 'evolution_meta'
METADATA_DIR.mkdir(exist_ok=True)

# === 质量目标对齐 ===
@dataclass
class QualityTarget:
    name: str
    current: float
    target: float
    trend: List[float]  # 历史趋势
    velocity: float  # 变化速度
    eta_days: int  # 预计达成天数
    
    @classmethod
    def create(cls, name: str, current: float, target: float, history: List[float] = None):
        history = history or []
        trend = history[-7:] if len(history) > 7 else history  # 最近 7 次
        velocity = (trend[-1] - trend[0]) / len(trend) if len(trend) > 1 else 0
        
        # 计算预计达成天数
        if velocity > 0:
            remaining = target - current
            eta_days = int(remaining / velocity) if velocity > 0 else 999
        else:
            eta_days = 999  # 无法达成
        
        return cls(
            name=name,
            current=current,
            target=target,
            trend=trend,
            velocity=velocity,
            eta_days=min(eta_days, 999)
        )

# === 自我反思层 ===
class SelfReflectionLayer:
    """分析过去、识别模式、生成改进建议"""
    
    def __init__(self, meta_db: Path):
        self.meta_db = meta_db
        self.history = self._load_history()
    
    def _load_history(self) -> List[Dict]:
        history_file = self.meta_db / 'evolution_history.json'
        if history_file.exists():
            return json.loads(history_file.read_text())
        return []
    
    def analyze_last_cycle(self, before: Dict, after: Dict, tasks: List[Dict]) -> Dict:
        """分析上一轮效果"""
        improvement = after.get('detection_rate', 0) - before.get('detection_rate', 0)
        
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'before': before,
            'after': after,
            'improvement': improvement,
            'tasks': tasks,
            'success': improvement > 0,
            'significant': improvement >= 0.5,
            'regression': improvement < 0
        }
        
        # 记录历史
        self.history.append(analysis)
        self._save_history()
        
        return analysis
    
    def identify_patterns(self) -> Dict:
        """识别成功/失败模式"""
        if len(self.history) < 3:
            return {'status': 'insufficient_data', 'cycles': len(self.history)}
        
        successes = [h for h in self.history if h['success']]
        failures = [h for h in self.history if not h['success']]
        
        patterns = {
            'success_patterns': [],
            'failure_patterns': [],
            'recommendations': []
        }
        
        # 分析成功模式
        if successes:
            avg_improvement = sum(s['improvement'] for s in successes) / len(successes)
            common_tasks = self._extract_common_tasks(successes)
            patterns['success_patterns'].append({
                'avg_improvement': avg_improvement,
                'common_tasks': common_tasks[:3],
                'best_cycle': max(successes, key=lambda x: x['improvement'])
            })
        
        # 分析失败模式
        if failures:
            avg_decline = sum(f['improvement'] for f in failures) / len(failures)
            patterns['failure_patterns'].append({
                'avg_decline': avg_decline,
                'count': len(failures),
                'possible_causes': ['规则质量不足', '测试样本偏差', '优化方向错误']
            })
        
        # 生成建议
        patterns['recommendations'] = self._generate_recommendations(patterns)
        
        return patterns
    
    def _extract_common_tasks(self, cycles: List[Dict]) -> List[str]:
        """提取常见任务"""
        task_freq = {}
        for cycle in cycles:
            for task in cycle.get('tasks', []):
                task_name = task.get('file', task.get('action', 'unknown'))
                task_freq[task_name] = task_freq.get(task_name, 0) + 1
        
        return sorted(task_freq.keys(), key=lambda k: task_freq[k], reverse=True)
    
    def _generate_recommendations(self, patterns: Dict) -> List[str]:
        """生成改进建议"""
        recs = []
        
        if patterns['success_patterns']:
            sp = patterns['success_patterns'][0]
            recs.append(f"继续优化{', '.join(sp['common_tasks'])} - 历史平均提升{sp['avg_improvement']:.2f}%")
        
        if patterns['failure_patterns']:
            fp = patterns['failure_patterns'][0]
            if fp['count'] > 2:
                recs.append(f"⚠️ 连续{fp['count']}次效果不佳，建议调整策略")
        
        # 基于趋势的建议
        if len(self.history) >= 5:
            recent_5 = self.history[-5:]
            avg_recent = sum(h['improvement'] for h in recent_5) / 5
            if avg_recent < 0.2:
                recs.append("📉 最近 5 轮提升缓慢 (<0.2%)，可能需要新的优化方向")
        
        return recs
    
    def _save_history(self):
        history_file = self.meta_db / 'evolution_history.json'
        # 只保留最近 100 轮
        history_file.write_text(json.dumps(self.history[-100:], indent=2))

# === 自动调优层 ===
class AutoTuningLayer:
    """根据反思结果自动调整参数"""
    
    def __init__(self, config: Dict, reflection: SelfReflectionLayer):
        self.config = config
        self.reflection = reflection
        self.tuning_log = []
    
    def tune(self, patterns: Dict) -> Dict:
        """根据模式自动调优"""
        changes = []
        
        # 规则 1: 连续失败 → 降低激进程度
        failures = patterns.get('failure_patterns', [])
        if failures and failures[0].get('count', 0) >= 3:
            old_mode = self.config.get('mode', 'conservative')
            if old_mode == 'aggressive':
                self.config['mode'] = 'standard'
                changes.append(f"模式调整：{old_mode} → standard (连续失败)")
            elif old_mode == 'standard':
                self.config['mode'] = 'conservative'
                changes.append(f"模式调整：{old_mode} → conservative (连续失败)")
        
        # 规则 2: 提升缓慢 → 增加周期
        recs = patterns.get('recommendations', [])
        if any('提升缓慢' in r for r in recs):
            old_cycle = self.config.get('cycle_minutes', 60)
            self.config['cycle_minutes'] = min(old_cycle * 1.5, 120)
            changes.append(f"周期调整：{old_cycle} → {self.config['cycle_minutes']} 分钟 (提升缓慢)")
        
        # 规则 3: 显著成功 → 保持或加速
        successes = patterns.get('success_patterns', [])
        if successes and successes[0].get('avg_improvement', 0) >= 0.5:
            changes.append("✅ 当前策略有效，保持不变")
        
        # 记录调优日志
        if changes:
            self.tuning_log.append({
                'timestamp': datetime.now().isoformat(),
                'changes': changes,
                'patterns': patterns
            })
        
        return {
            'config': self.config,
            'changes': changes,
            'tuned': len(changes) > 0
        }

# === 质量对齐层 ===
class QualityAlignmentLayer:
    """确保优化方向与质量目标一致"""
    
    def __init__(self, targets: Dict[str, QualityTarget]):
        self.targets = targets
        self.alignment_history = []
    
    def check_alignment(self, metrics: Dict) -> Dict:
        """检查当前状态与目标的对齐"""
        alignment = {
            'overall_score': 0,
            'metrics': {},
            'at_risk': [],
            'on_track': [],
            'achieved': []
        }
        
        scores = []
        for name, target in self.targets.items():
            current = metrics.get(name, 0)
            # 避免除零错误
            if target.target == target.current:
                progress = 100.0 if current >= target.target else 0.0
            else:
                progress = (current - target.current) / (target.target - target.current) * 100
            progress = max(0, min(100, progress))  # 0-100%
            
            status = 'achieved' if current >= target.target else \
                     'on_track' if progress > 50 else \
                     'at_risk'
            
            alignment['metrics'][name] = {
                'current': current,
                'target': target.target,
                'progress': progress,
                'status': status,
                'eta_days': target.eta_days
            }
            
            if status == 'achieved':
                alignment['achieved'].append(name)
            elif status == 'on_track':
                alignment['on_track'].append(name)
            else:
                alignment['at_risk'].append(name)
            
            scores.append(progress)
        
        alignment['overall_score'] = sum(scores) / len(scores) if scores else 0
        self.alignment_history.append(alignment)
        
        return alignment
    
    def generate_alignment_report(self) -> str:
        """生成对齐报告"""
        if not self.alignment_history:
            return "暂无对齐数据"
        
        latest = self.alignment_history[-1]
        
        report = [
            "="*60,
            "🎯 质量目标对齐报告",
            "="*60,
            f"整体对齐度：{latest['overall_score']:.1f}%",
            "",
            "✅ 已达成:",
        ]
        
        for name in latest['achieved']:
            report.append(f"  - {name}")
        
        report.append("")
        report.append("🟢 进行中:")
        for name in latest['on_track']:
            metric = latest['metrics'][name]
            report.append(f"  - {name}: {metric['current']:.1f}% → {metric['target']:.1f}% ({metric['progress']:.0f}%)")
        
        report.append("")
        report.append("🔴 有风险:")
        for name in latest['at_risk']:
            metric = latest['metrics'][name]
            report.append(f"  - {name}: {metric['current']:.1f}% → {metric['target']:.1f}% (ETA: {metric['eta_days']}天)")
        
        report.append("")
        report.append("="*60)
        
        return "\n".join(report)

# === 元进化引擎 ===
class MetaEvolutionEngine:
    """自进化系统的自我优化引擎"""
    
    def __init__(self):
        self.config = {
            'mode': 'conservative',
            'cycle_minutes': 60,
            'target_detection_rate': 98.0,
            'target_fp_rate': 0.0,
            'min_improvement': 0.5,
        }
        
        self.reflection = SelfReflectionLayer(METADATA_DIR)
        self.tuning = AutoTuningLayer(self.config, self.reflection)
        
        # 质量目标
        self.targets = {
            'detection_rate': QualityTarget.create('检测率', 95.8, 98.0, [95.0, 95.2, 95.5, 95.8]),
            'fp_rate': QualityTarget.create('误报率', 0.0, 0.0, [0.0, 0.0, 0.0, 0.0]),
            'f1_score': QualityTarget.create('F1 Score', 97.8, 99.0, [97.0, 97.3, 97.5, 97.8]),
        }
        
        self.alignment = QualityAlignmentLayer(self.targets)
    
    def run_meta_cycle(self, before: Dict, after: Dict, tasks: List[Dict]):
        """运行元进化周期"""
        print("\n" + "="*60)
        print("🧬 元进化周期 - 自我反思与调优")
        print("="*60)
        
        # 1. 自我反思
        print("\n🤔 1. 自我反思")
        analysis = self.reflection.analyze_last_cycle(before, after, tasks)
        
        if analysis['significant']:
            print(f"  ✅ 显著成功 (+{analysis['improvement']:.1f}%)")
        elif analysis['success']:
            print(f"  ⚠️  略有提升 (+{analysis['improvement']:.1f}%)")
        elif analysis['regression']:
            print(f"  🔴 需要调整 ({analysis['improvement']:.1f}%)")
        else:
            print(f"  ➖ 持平 ({analysis['improvement']:.1f}%)")
        
        # 2. 识别模式
        print("\n🔍 2. 模式识别")
        patterns = self.reflection.identify_patterns()
        
        if 'status' in patterns and patterns['status'] == 'insufficient_data':
            print(f"  📊 数据不足 (仅{patterns['cycles']}轮)")
        else:
            if patterns['success_patterns']:
                sp = patterns['success_patterns'][0]
                print(f"  ✅ 成功模式：平均提升 {sp['avg_improvement']:.2f}%")
            if patterns['failure_patterns']:
                fp = patterns['failure_patterns'][0]
                print(f"  ⚠️  失败模式：{fp['count']}次，平均下降 {fp['avg_decline']:.2f}%")
        
        # 3. 自动调优
        print("\n🔧 3. 自动调优")
        tuning_result = self.tuning.tune(patterns)
        
        if tuning_result['tuned']:
            print("  调整:")
            for change in tuning_result['changes']:
                print(f"    - {change}")
        else:
            print("  ✅ 当前策略有效，无需调整")
        
        # 4. 质量对齐检查
        print("\n🎯 4. 质量对齐")
        alignment = self.alignment.check_alignment(after)
        
        print(f"  整体对齐度：{alignment['overall_score']:.1f}%")
        if alignment['achieved']:
            print(f"  ✅ 已达成：{', '.join(alignment['achieved'])}")
        if alignment['at_risk']:
            print(f"  🔴 有风险：{', '.join(alignment['at_risk'])}")
        
        # 5. 生成建议
        print("\n💡 5. 改进建议")
        if 'recommendations' in patterns:
            recommendations = self.reflection._generate_recommendations(patterns)
            for rec in recommendations:
                print(f"  - {rec}")
        else:
            print("  📊 数据积累中，暂无建议")
        
        print("\n" + "="*60)
        
        return {
            'analysis': analysis,
            'patterns': patterns,
            'tuning': tuning_result,
            'alignment': alignment,
            'config': self.config
        }

# === 使用示例 ===
if __name__ == '__main__':
    # 模拟一轮优化结果
    before = {
        'detection_rate': 95.3,
        'false_positive': 0.0,
        'f1_score': 97.3
    }
    
    after = {
        'detection_rate': 95.8,
        'false_positive': 0.0,
        'f1_score': 97.8
    }
    
    tasks = [
        {'action': 'add_rules', 'file': 'persistence_rules.yar'},
        {'action': 'add_rules', 'file': 'data_exfil_rules.yar'}
    ]
    
    # 运行元进化
    engine = MetaEvolutionEngine()
    result = engine.run_meta_cycle(before, after, tasks)
    
    # 生成对齐报告
    print("\n" + engine.alignment.generate_alignment_report())
    
    # 保存配置
    config_file = METADATA_DIR / 'config.json'
    config_file.write_text(json.dumps(result['config'], indent=2))
    print(f"\n💾 配置已保存：{config_file}")
