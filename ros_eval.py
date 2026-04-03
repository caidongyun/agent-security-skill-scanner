#!/usr/bin/env python3
"""
📈 HROS 评估基准
Performance Metrics / Version Comparison / Leaderboard / Report Export
"""

import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

# === 配置 ===
WORKSPACE = Path('/home/cdy/.openclaw/workspace/agent-security-skill-scanner-master')
BENCHMARK = WORKSPACE / 'benchmark' / 'benchmark_v3.py'
RULES_DIR = WORKSPACE / 'rules' / 'scanner_v3' / 'yara'
META_DIR = WORKSPACE / 'ros_meta'

META_DIR.mkdir(exist_ok=True)

@dataclass
class BenchmarkMetrics:
    version: str
    timestamp: str
    detection_rate: float
    false_positive: float
    precision: float
    recall: float
    f1_score: float
    scan_speed: Optional[float] = None
    rules_count: int = 0

# === 评估器 ===

class RosEvaluator:
    """HROS 评估基准"""
    
    def __init__(self):
        self.metrics_history: List[BenchmarkMetrics] = []
        self.load_history()
    
    def load_history(self):
        """加载历史数据"""
        history_file = META_DIR / 'eval_history.json'
        if history_file.exists():
            data = json.loads(history_file.read_text())
            self.metrics_history = [BenchmarkMetrics(**m) for m in data]
    
    def save_history(self):
        """保存历史数据"""
        history_file = META_DIR / 'eval_history.json'
        data = [asdict(m) for m in self.metrics_history]
        history_file.write_text(json.dumps(data, indent=2))
    
    def run_benchmark(self, rules_file: Optional[str] = None) -> BenchmarkMetrics:
        """运行基准测试"""
        print("📊 运行基准测试...")
        
        # 找到规则文件
        if not rules_file:
            rule_files = sorted(RULES_DIR.glob('all_rules_v*.yar'))
            if not rule_files:
                raise Exception("未找到规则文件")
            rules_file = str(rule_files[-1])
        
        # 运行 benchmark
        result = subprocess.run(
            ['python3', str(BENCHMARK), '--rules', rules_file],
            capture_output=True, text=True, timeout=90
        )
        
        # 解析结果
        metrics = self._parse_benchmark_output(result.stdout, rules_file)
        
        # 保存历史
        self.metrics_history.append(metrics)
        self.save_history()
        
        return metrics
    
    def _parse_benchmark_output(self, output: str, rules_file: str) -> BenchmarkMetrics:
        """解析 benchmark 输出"""
        import re
        
        def extract_metric(pattern: str) -> float:
            match = re.search(pattern, output)
            if match:
                return float(match.group(1).replace('%', ''))
            return 0.0
        
        # 提取规则数量
        rules_count = 0
        rules_match = re.search(r'YARA Rules Loaded:\s*(\d+)', output)
        if rules_match:
            rules_count = int(rules_match.group(1))
        
        # 提取版本
        version = Path(rules_file).stem.replace('all_rules_', '')
        
        return BenchmarkMetrics(
            version=version,
            timestamp=datetime.now().isoformat(),
            detection_rate=extract_metric(r'Detection Rate:\s*([\d.]+)%'),
            false_positive=extract_metric(r'False Positive:\s*([\d.]+)%'),
            precision=extract_metric(r'Precision:\s*([\d.]+)%'),
            recall=extract_metric(r'Recall:\s*([\d.]+)%'),
            f1_score=extract_metric(r'F1 Score:\s*([\d.]+)'),
            scan_speed=None,  # 待实现
            rules_count=rules_count
        )
    
    def compare_versions(self, v1: str, v2: str) -> Dict:
        """对比两个版本"""
        print(f"\n📊 版本对比：{v1} vs {v2}")
        
        m1 = next((m for m in self.metrics_history if m.version == v1), None)
        m2 = next((m for m in self.metrics_history if m.version == v2), None)
        
        if not m1 or not m2:
            return {'error': '版本未找到'}
        
        comparison = {
            'v1': asdict(m1),
            'v2': asdict(m2),
            'changes': {
                'detection_rate': m2.detection_rate - m1.detection_rate,
                'false_positive': m2.false_positive - m1.false_positive,
                'f1_score': m2.f1_score - m1.f1_score,
                'rules_count': m2.rules_count - m1.rules_count
            }
        }
        
        print(f"  检测率：{m1.detection_rate:.1f}% → {m2.detection_rate:.1f}% ({comparison['changes']['detection_rate']:+.1f}%)")
        print(f"  误报率：{m1.false_positive:.1f}% → {m2.false_positive:.1f}% ({comparison['changes']['false_positive']:+.1f}%)")
        print(f"  F1 Score: {m1.f1_score:.1f} → {m2.f1_score:.1f} ({comparison['changes']['f1_score']:+.1f})")
        print(f"  规则数：{m1.rules_count} → {m2.rules_count} ({comparison['changes']['rules_count']:+d})")
        
        return comparison
    
    def generate_leaderboard(self) -> str:
        """生成排行榜"""
        print("\n🏆 生成排行榜...")
        
        if not self.metrics_history:
            return "暂无数据"
        
        # 按检测率排序
        sorted_metrics = sorted(self.metrics_history, key=lambda m: m.f1_score, reverse=True)
        
        lines = [
            "="*70,
            "🏆 HROS 评估基准排行榜",
            "="*70,
            "",
            f"{'排名':<4} {'版本':<15} {'检测率':<10} {'误报率':<10} {'F1':<8} {'规则数':<8}",
            "-"*70
        ]
        
        for i, m in enumerate(sorted_metrics[:10], 1):
            lines.append(
                f"{i:<4} {m.version:<15} {m.detection_rate:>6.1f}%   "
                f"{m.false_positive:>6.1f}%   {m.f1_score:>6.1f}   {m.rules_count:<8}"
            )
        
        lines.append("="*70)
        
        return "\n".join(lines)
    
    def export_report(self, format: str = 'markdown') -> str:
        """导出报告"""
        print("\n📄 导出评估报告...")
        
        if not self.metrics_history:
            return "暂无数据"
        
        latest = self.metrics_history[-1]
        
        if format == 'markdown':
            report = self._export_markdown(latest)
        elif format == 'json':
            report = json.dumps(asdict(latest), indent=2)
        else:
            report = str(asdict(latest))
        
        return report
    
    def _export_markdown(self, metrics: BenchmarkMetrics) -> str:
        """导出 Markdown 格式报告"""
        return f"""# HROS 评估基准报告

**版本**: {metrics.version}  
**时间**: {metrics.timestamp}

## 核心指标

| 指标 | 数值 |
|------|------|
| 检测率 | {metrics.detection_rate:.1f}% |
| 误报率 | {metrics.false_positive:.1f}% |
| 精确率 | {metrics.precision:.1f}% |
| 召回率 | {metrics.recall:.1f}% |
| F1 Score | {metrics.f1_score:.1f} |
| 规则数量 | {metrics.rules_count} |

## 历史趋势

共 {len(self.metrics_history)} 轮测试

"""

# === 主函数 ===
if __name__ == '__main__':
    evaluator = RosEvaluator()
    
    # 运行基准测试
    metrics = evaluator.run_benchmark()
    print(f"\n✅ 基准测试完成")
    print(f"   检测率：{metrics.detection_rate:.1f}%")
    print(f"   F1 Score: {metrics.f1_score:.1f}")
    
    # 生成排行榜
    print(evaluator.generate_leaderboard())
    
    # 导出报告
    report = evaluator.export_report()
    report_file = META_DIR / 'eval_report.md'
    report_file.write_text(report)
    print(f"\n💾 报告已保存：{report_file}")
