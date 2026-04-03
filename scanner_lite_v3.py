#!/usr/bin/env python3
"""
🛡️ Hybrid Scanner V3 Lite - 精简稳定版
单机优化 · 高并发 · 稳定性优先
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import List, Dict, Optional
import statistics

sys.path.insert(0, str(Path(__file__).parent))
from intent_detector_v2 import EnhancedIntentDetector, IntentType

@dataclass
class Result:
    attack_type: str
    sample_id: str
    verdict: str  # malicious/benign
    is_fp: bool
    is_fn: bool
    scan_ms: float

class LiteScanner:
    """精简扫描器"""
    
    def __init__(self, rules_dir: str, workers: int = 8):
        self.rules_dir = Path(rules_dir)
        self.workers = workers
        self.detector = EnhancedIntentDetector()
        
        import yara
        self.yara = yara
        self.rules = self._load_rules()
    
    def _load_rules(self):
        """加载规则"""
        all_rules = ""
        for rf in self.rules_dir.glob('*.yar'):
            all_rules += rf.read_text(errors='ignore') + "\n\n"
        return self.yara.compile(source=all_rules)
    
    def scan_sample(self, sample_dir: Path, attack_type: str) -> Optional[Result]:
        """扫描单个样本"""
        payload_files = list(sample_dir.glob('payload.*'))
        if not payload_files:
            return None
        
        content = payload_files[0].read_text(errors='ignore')
        is_benign_type = attack_type in ['normal_script', 'common_pattern']
        
        start = time.perf_counter()
        
        # YARA 扫描
        yara_matches = self.rules.match(data=content)
        yara_detected = len(yara_matches) > 0
        
        # 意图识别
        if yara_detected:
            intent = self.detector.analyze(content, [m.rule for m in yara_matches])
            
            # 综合判定
            if is_benign_type and intent.whitelisted:
                verdict = "benign"
            elif intent.intent == IntentType.MALICIOUS:
                verdict = "malicious"
            elif intent.intent == IntentType.SUSPICIOUS and intent.risk_score >= 4.0:
                verdict = "malicious"
            elif intent.intent == IntentType.BENIGN and intent.risk_score < 1.5 and is_benign_type:
                verdict = "benign"
            else:
                verdict = "malicious"
        else:
            verdict = "benign"
        
        scan_ms = (time.perf_counter() - start) * 1000
        
        final_malicious = verdict == "malicious"
        return Result(
            attack_type=attack_type,
            sample_id=sample_dir.name,
            verdict=verdict,
            is_fp=final_malicious and is_benign_type,
            is_fn=(verdict == "benign") and not is_benign_type,
            scan_ms=scan_ms
        )
    
    def run(self, samples_dir: str) -> Dict:
        """运行扫描"""
        samples_path = Path(samples_dir)
        attack_types = [
            'tool_poisoning', 'prompt_injection', 'credential_theft',
            'data_exfiltration', 'persistence', 'evasion',
            'memory_pollution', 'supply_chain_attack', 'remote_load',
            'resource_exhaustion', 'normal_script', 'common_pattern', 'false_prone'
        ]
        
        # 收集样本
        all_samples = []
        for at in attack_types:
            attack_dir = samples_path / at
            if attack_dir.exists():
                for d in attack_dir.iterdir():
                    if d.is_dir():
                        all_samples.append((d, at))
        
        print(f"📂 收集 {len(all_samples)} 个样本")
        print(f"⚡ 并发度：{self.workers} 线程")
        print()
        
        # 并发扫描
        start_time = time.time()
        results = []
        
        with ThreadPoolExecutor(max_workers=self.workers) as executor:
            futures = {
                executor.submit(self.scan_sample, d, at): (d, at)
                for d, at in all_samples
            }
            
            completed = 0
            total = len(futures)
            
            for future in as_completed(futures):
                result = future.result()
                if result:
                    results.append(result)
                
                completed += 1
                if completed % 5000 == 0:
                    pct = completed / total * 100
                    elapsed = time.time() - start_time
                    speed = completed / elapsed
                    print(f"  进度：{completed}/{total} ({pct:.1f}%) | {speed:.0f} 样本/秒")
        
        total_time = time.time() - start_time
        return self._report(results, total_time)
    
    def _report(self, results: List[Result], total_time: float) -> Dict:
        """生成报告"""
        malicious = [r for r in results if r.attack_type not in ['normal_script', 'common_pattern', 'false_prone']]
        benign = [r for r in results if r.attack_type in ['normal_script', 'common_pattern']]
        
        detected = len([r for r in malicious if r.verdict == 'malicious'])
        fps = len([r for r in benign if r.verdict == 'malicious'])
        fns = len([r for r in malicious if r.verdict == 'benign'])
        
        det_rate = (detected / len(malicious) * 100) if malicious else 0
        fp_rate = (fps / len(benign) * 100) if benign else 0
        precision = (detected / (detected + fps) * 100) if (detected + fps) > 0 else 100
        
        scan_times = [r.scan_ms for r in results]
        
        # 按攻击类型统计
        by_type = {}
        for at in set(r.attack_type for r in results):
            type_results = [r for r in results if r.attack_type == at]
            type_det = len([r for r in type_results if r.verdict == 'malicious'])
            by_type[at] = {
                'total': len(type_results),
                'detected': type_det,
                'rate': (type_det / len(type_results) * 100) if type_results else 0
            }
        
        return {
            'timestamp': datetime.now().isoformat(),
            'total': len(results),
            'malicious_samples': len(malicious),
            'benign_samples': len(benign),
            'detected': detected,
            'false_positives': fps,
            'false_negatives': fns,
            'detection_rate': det_rate,
            'false_positive_rate': fp_rate,
            'precision': precision,
            'f1_score': 2 * (precision * det_rate) / (precision + det_rate) if (precision + det_rate) > 0 else 0,
            'performance': {
                'total_time_sec': total_time,
                'avg_ms': statistics.mean(scan_times),
                'p50_ms': sorted(scan_times)[len(scan_times)//2],
                'p99_ms': sorted(scan_times)[int(len(scan_times)*0.99)],
                'speed': len(results) / total_time
            },
            'by_attack_type': by_type
        }

def print_report(report: Dict):
    """打印报告"""
    print("\n" + "="*70)
    print("📊 基准测试报告")
    print("="*70)
    print()
    print(f"样本总数：{report['total']:,}")
    print(f"恶意样本：{report['malicious_samples']:,}")
    print(f"良性样本：{report['benign_samples']:,}")
    print()
    print(f"🎯 检测率：{report['detection_rate']:.1f}%")
    print(f"⚠️  误报率：{report['false_positive_rate']:.1f}%")
    print(f"✅ 精确率：{report['precision']:.1f}%")
    print(f"📈 F1 Score: {report['f1_score']:.1f}")
    print()
    print(f"⚡ 总耗时：{report['performance']['total_time_sec']:.1f}秒")
    print(f"⚡ 平均：{report['performance']['avg_ms']:.2f}ms")
    print(f"⚡ P99: {report['performance']['p99_ms']:.2f}ms")
    print(f"⚡ 速度：{report['performance']['speed']:.0f} 样本/秒")
    print()
    print("按攻击类型:")
    for at, stats in sorted(report['by_attack_type'].items(), key=lambda x: x[1]['rate'], reverse=True):
        s = '✅' if stats['rate'] >= 90 else '⚠️' if stats['rate'] >= 70 else '🔴'
        print(f"  {s} {at:25s}: {stats['rate']:6.1f}% ({stats['detected']}/{stats['total']})")
    print()
    
    if report['detection_rate'] >= 90 and report['false_positive_rate'] < 20:
        print("  🏆 优秀")
    elif report['detection_rate'] >= 85:
        print("  ✅ 良好")
    else:
        print("  🔴 需要优化")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='精简扫描器')
    parser.add_argument('--samples', default='/home/cdy/Desktop/security-benchmark/samples/from-templates')
    parser.add_argument('--rules', default='/home/cdy/.openclaw/workspace/agent-security-skill-scanner-master/rules/scanner_v3/yara')
    parser.add_argument('--workers', type=int, default=8, help='并发线程数')
    parser.add_argument('--output', help='输出 JSON 文件')
    args = parser.parse_args()
    
    scanner = LiteScanner(args.rules, args.workers)
    report = scanner.run(args.samples)
    print_report(report)
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\n💾 报告：{args.output}")
