#!/usr/bin/env python3
"""
🛡️ Security Benchmark - 全量样本基准测试
使用 94,486 个真实样本测试 agent-security-skill-scanner-master 扫描器

用法:
    python3 benchmark_full_security.py --samples /path/to/samples --rules /path/to/rules
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import statistics

@dataclass
class ScanResult:
    """单个样本扫描结果"""
    sample_id: str
    attack_type: str
    file_path: str
    detected: bool
    matched_rules: List[str]
    scan_time_ms: float
    is_false_positive: bool = False
    is_false_negative: bool = False

@dataclass
class BenchmarkReport:
    """基准测试报告"""
    timestamp: str
    total_samples: int
    malicious_samples: int
    benign_samples: int
    detected_malicious: int
    false_positives: int
    false_negatives: int
    detection_rate: float
    false_positive_rate: float
    precision: float
    recall: float
    f1_score: float
    avg_scan_time_ms: float
    p50_scan_time_ms: float
    p90_scan_time_ms: float
    p99_scan_time_ms: float
    samples_per_second: float
    by_attack_type: Dict[str, Dict]
    rules_count: int
    rules_path: str
    samples_path: str

class SecurityBenchmark:
    """安全基准测试器"""
    
    def __init__(self, samples_dir: str, rules_dir: str, max_workers: int = 4):
        self.samples_dir = Path(samples_dir)
        self.rules_dir = Path(rules_dir)
        self.max_workers = max_workers
        self.compiled_rules = None
        self.rule_count = 0
        self.results: List[ScanResult] = []
        
        # 加载 YARA
        try:
            import yara
            self.yara = yara
        except ImportError:
            print("❌ yara-python 未安装：pip install yara-python")
            sys.exit(1)
    
    def load_rules(self):
        """加载 YARA 规则"""
        print("📚 加载 YARA 规则...")
        start = time.time()
        
        all_rules = ""
        for rf in self.rules_dir.glob('*.yar'):
            all_rules += rf.read_text(encoding='utf-8', errors='ignore') + "\n\n"
        
        if not all_rules:
            print("❌ 未找到 YARA 规则")
            sys.exit(1)
        
        self.compiled_rules = self.yara.compile(source=all_rules)
        self.rule_count = all_rules.count('rule ')
        
        load_time = time.time() - start
        print(f"✅ 加载 {self.rule_count} 条规则 ({load_time:.2f}s)")
        print()
    
    def scan_sample(self, sample_dir: Path, attack_type: str) -> ScanResult:
        """扫描单个样本"""
        sample_id = sample_dir.name
        
        # 查找 payload 文件
        payload_files = list(sample_dir.glob('payload.*'))
        if not payload_files:
            return None
        
        payload_file = payload_files[0]
        content = payload_file.read_text(encoding='utf-8', errors='ignore')
        
        # 扫描
        start = time.perf_counter()
        matches = self.compiled_rules.match(data=content)
        scan_time = (time.perf_counter() - start) * 1000  # ms
        
        matched_rules = [m.rule for m in matches]
        detected = len(matched_rules) > 0
        
        # 判断真假阳性/阴性
        is_benign = attack_type in ['normal_script', 'common_pattern']
        is_false_positive = detected and is_benign
        is_false_negative = not detected and not is_benign
        
        return ScanResult(
            sample_id=sample_id,
            attack_type=attack_type,
            file_path=str(payload_file),
            detected=detected,
            matched_rules=matched_rules,
            scan_time_ms=scan_time,
            is_false_positive=is_false_positive,
            is_false_negative=is_false_negative
        )
    
    def run(self, sample_limit: int = None) -> BenchmarkReport:
        """运行基准测试"""
        print("=" * 70)
        print("🛡️  Security Benchmark - 全量样本基准测试")
        print("=" * 70)
        print()
        
        # 加载规则
        self.load_rules()
        
        # 收集所有样本
        print("📂 收集样本...")
        attack_types = [
            'tool_poisoning', 'prompt_injection', 'credential_theft',
            'data_exfiltration', 'persistence', 'evasion',
            'memory_pollution', 'supply_chain_attack', 'remote_load',
            'resource_exhaustion', 'normal_script', 'common_pattern',
            'false_prone'
        ]
        
        all_samples = []
        for attack_type in attack_types:
            attack_dir = self.samples_dir / attack_type
            if not attack_dir.exists():
                continue
            
            sample_dirs = [d for d in attack_dir.iterdir() if d.is_dir()]
            if sample_limit:
                sample_dirs = sample_dirs[:sample_limit]
            
            for sample_dir in sample_dirs:
                all_samples.append((sample_dir, attack_type))
        
        print(f"✅ 收集 {len(all_samples)} 个样本")
        print()
        
        # 并行扫描
        print(f"🔍 开始扫描 (并发度：{self.max_workers})...")
        print()
        
        start_time = time.time()
        self.results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self.scan_sample, sample_dir, attack_type): (sample_dir, attack_type)
                for sample_dir, attack_type in all_samples
            }
            
            completed = 0
            for future in as_completed(futures):
                result = future.result()
                if result:
                    self.results.append(result)
                
                completed += 1
                if completed % 1000 == 0:
                    print(f"  进度：{completed}/{len(all_samples)} ({completed/len(all_samples)*100:.1f}%)")
        
        total_time = time.time() - start_time
        print()
        
        # 生成报告
        return self._generate_report(total_time)
    
    def _generate_report(self, total_time: float) -> BenchmarkReport:
        """生成测试报告"""
        # 分类统计
        malicious = [r for r in self.results if r.attack_type not in ['normal_script', 'common_pattern', 'false_prone']]
        benign = [r for r in self.results if r.attack_type in ['normal_script', 'common_pattern', 'false_prone']]
        
        detected_malicious = len([r for r in malicious if r.detected])
        false_positives = len([r for r in benign if r.detected])
        false_negatives = len([r for r in malicious if not r.detected])
        
        detection_rate = (detected_malicious / len(malicious) * 100) if malicious else 0
        false_positive_rate = (false_positives / len(benign) * 100) if benign else 0
        precision = (detected_malicious / (detected_malicious + false_positives) * 100) if (detected_malicious + false_positives) > 0 else 0
        recall = detection_rate
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        # 性能统计
        scan_times = [r.scan_time_ms for r in self.results]
        avg_time = statistics.mean(scan_times) if scan_times else 0
        sorted_times = sorted(scan_times)
        p50 = sorted_times[len(sorted_times)//2] if sorted_times else 0
        p90 = sorted_times[int(len(sorted_times)*0.9)] if sorted_times else 0
        p99 = sorted_times[int(len(sorted_times)*0.99)] if sorted_times else 0
        
        samples_per_second = len(self.results) / total_time if total_time > 0 else 0
        
        # 按攻击类型统计
        by_attack_type = {}
        for attack_type in set(r.attack_type for r in self.results):
            type_results = [r for r in self.results if r.attack_type == attack_type]
            type_detected = len([r for r in type_results if r.detected])
            type_total = len(type_results)
            type_rate = (type_detected / type_total * 100) if type_total > 0 else 0
            
            by_attack_type[attack_type] = {
                'total': type_total,
                'detected': type_detected,
                'rate': type_rate
            }
        
        report = BenchmarkReport(
            timestamp=datetime.now().isoformat(),
            total_samples=len(self.results),
            malicious_samples=len(malicious),
            benign_samples=len(benign),
            detected_malicious=detected_malicious,
            false_positives=false_positives,
            false_negatives=false_negatives,
            detection_rate=detection_rate,
            false_positive_rate=false_positive_rate,
            precision=precision,
            recall=recall,
            f1_score=f1,
            avg_scan_time_ms=avg_time,
            p50_scan_time_ms=p50,
            p90_scan_time_ms=p90,
            p99_scan_time_ms=p99,
            samples_per_second=samples_per_second,
            by_attack_type=by_attack_type,
            rules_count=self.rule_count,
            rules_path=str(self.rules_dir),
            samples_path=str(self.samples_dir)
        )
        
        return report
    
    def print_report(self, report: BenchmarkReport):
        """打印报告"""
        print("=" * 70)
        print("📊 基准测试报告")
        print("=" * 70)
        print()
        
        print(f"时间：{report.timestamp}")
        print(f"规则数：{report.rules_count}")
        print()
        
        print("总体指标:")
        print(f"  总样本数：     {report.total_samples}")
        print(f"  恶意样本：    {report.malicious_samples}")
        print(f"  良性样本：    {report.benign_samples}")
        print()
        
        print(f"  检测率：      {report.detection_rate:.1f}%")
        print(f"  误报率：      {report.false_positive_rate:.1f}%")
        print(f"  精确率：      {report.precision:.1f}%")
        print(f"  召回率：      {report.recall:.1f}%")
        print(f"  F1 Score:     {report.f1_score:.1f}")
        print()
        
        print("性能指标:")
        print(f"  平均扫描时间：{report.avg_scan_time_ms:.2f}ms")
        print(f"  P50 延迟：     {report.p50_scan_time_ms:.2f}ms")
        print(f"  P90 延迟：     {report.p90_scan_time_ms:.2f}ms")
        print(f"  P99 延迟：     {report.p99_scan_time_ms:.2f}ms")
        print(f"  扫描速度：    {report.samples_per_second:.1f} 样本/秒")
        print()
        
        print("按攻击类型:")
        sorted_types = sorted(report.by_attack_type.items(), key=lambda x: x[1]['rate'], reverse=True)
        for attack_type, stats in sorted_types:
            status = '✅' if stats['rate'] >= 90 else '⚠️' if stats['rate'] >= 70 else '🔴'
            print(f"  {status} {attack_type:25s}: {stats['rate']:6.1f}% ({stats['detected']}/{stats['total']})")
        print()
        
        # 评级
        print("评级:")
        if report.detection_rate >= 95 and report.false_positive_rate < 5:
            print("  🏆 优秀 (检测率≥95%, 误报率<5%)")
        elif report.detection_rate >= 90 and report.false_positive_rate < 10:
            print("  ✅ 良好 (检测率≥90%, 误报率<10%)")
        elif report.detection_rate >= 80:
            print("  ⚠️  可接受 (检测率≥80%)")
        else:
            print("  🔴 需要优化 (检测率<80%)")
        print()

def main():
    parser = argparse.ArgumentParser(description='Security Benchmark - 全量样本基准测试')
    parser.add_argument('--samples', default='/home/cdy/Desktop/security-benchmark/samples/from-templates',
                       help='样本目录')
    parser.add_argument('--rules', default='/home/cdy/.openclaw/workspace/agent-security-skill-scanner-master/rules/scanner_v3/yara',
                       help='YARA 规则目录')
    parser.add_argument('--limit', type=int, default=None,
                       help='每个攻击类型限制的样本数 (默认：全部)')
    parser.add_argument('--workers', type=int, default=4,
                       help='并发工作线程数 (默认：4)')
    parser.add_argument('--output', default=None,
                       help='输出报告文件 (JSON)')
    
    args = parser.parse_args()
    
    benchmark = SecurityBenchmark(args.samples, args.rules, args.workers)
    report = benchmark.run(args.limit)
    benchmark.print_report(report)
    
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(asdict(report), f, indent=2)
        print(f"💾 报告已保存：{output_path}")

if __name__ == '__main__':
    main()
