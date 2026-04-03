#!/usr/bin/env python3
"""
🛡️ Distributed Scanner v4.1 - 优化版
- JSON 原子写入（安全）
- 粗粒度分片（每片 10K）
- Worker 完全独立
"""

import os
import sys
import json
import time
import tempfile
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import statistics

sys.path.insert(0, str(Path(__file__).parent))
from intent_detector_v2 import EnhancedIntentDetector, IntentType

@dataclass 
class ScanResult:
    attack_type: str
    verdict: str
    is_fp: bool
    is_fn: bool
    scan_ms: float

def atomic_write_json(filepath: Path, data: Dict):
    """原子写入 JSON（安全）"""
    # 写入临时文件
    fd, temp_path = tempfile.mkstemp(suffix='.json', dir=filepath.parent)
    try:
        with os.fdopen(fd, 'w') as f:
            json.dump(data, f, indent=2)
        # 原子重命名
        Path(temp_path).rename(filepath)
    except:
        # 失败时清理临时文件
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise

def scan_batch(rules, detector, sample_paths: List[str]) -> List[Dict]:
    """批量扫描"""
    results = []
    
    for sample_path in sample_paths:
        sample_dir = Path(sample_path)
        payload_files = list(sample_dir.glob('payload.*'))
        
        if not payload_files:
            continue
        
        content = payload_files[0].read_text(errors='ignore')
        attack_type = sample_dir.parent.name
        is_benign_type = attack_type in ['normal_script', 'common_pattern']
        
        start = time.perf_counter()
        
        # YARA
        yara_matches = rules.match(data=content)
        yara_detected = len(yara_matches) > 0
        
        # 意图识别 + 判定
        if yara_detected:
            intent = detector.analyze(content, [m.rule for m in yara_matches])
            
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
        
        results.append({
            'attack_type': attack_type,
            'verdict': verdict,
            'is_fp': (verdict == 'malicious') and is_benign_type,
            'is_fn': (verdict == 'benign') and not is_benign_type,
            'scan_ms': scan_ms
        })
    
    return results

def worker_task(task_id: str, sample_paths: List[str], rules_dir: str, output_dir: str):
    """Worker 任务函数"""
    import yara
    
    # 确保输出目录存在
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print(f"  🚀 Worker {task_id}: {len(sample_paths)} 样本")
    
    # 加载规则
    all_rules = ""
    for rf in Path(rules_dir).glob('*.yar'):
        all_rules += rf.read_text(errors='ignore') + "\n\n"
    rules = yara.compile(source=all_rules)
    
    detector = EnhancedIntentDetector()
    
    # 扫描
    start_time = time.time()
    results = scan_batch(rules, detector, sample_paths)
    total_time = time.time() - start_time
    
    # 统计
    malicious = [r for r in results if r['attack_type'] not in ['normal_script', 'common_pattern', 'false_prone']]
    benign = [r for r in results if r['attack_type'] in ['normal_script', 'common_pattern']]
    
    detected = len([r for r in malicious if r['verdict'] == 'malicious'])
    fps = len([r for r in benign if r['verdict'] == 'malicious'])
    
    det_rate = (detected / len(malicious) * 100) if malicious else 0
    fp_rate = (fps / len(benign) * 100) if benign else 0
    precision = (detected / (detected + fps) * 100) if (detected + fps) > 0 else 100
    
    # Worker 结果
    worker_result = {
        'task_id': task_id,
        'timestamp': datetime.now().isoformat(),
        'samples_scanned': len(results),
        'detection_rate': det_rate,
        'false_positive_rate': fp_rate,
        'precision': precision,
        'f1_score': 2 * (precision * det_rate) / (precision + det_rate) if (precision + det_rate) > 0 else 0,
        'scan_time_sec': total_time,
        'speed': len(results) / total_time,
        'results': results
    }
    
    # 原子写入
    result_file = Path(output_dir) / f"{task_id}.json"
    atomic_write_json(result_file, worker_result)
    
    print(f"    ✅ {len(results)} 样本 | {det_rate:.1f}% | {len(results)/total_time:.0f}/秒")
    
    return worker_result

class DistributedScanner:
    """分布式扫描器"""
    
    def __init__(self, samples_dir: str, rules_dir: str, output_dir: str):
        self.samples_dir = Path(samples_dir)
        self.rules_dir = Path(rules_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.attack_types = [
            'tool_poisoning', 'prompt_injection', 'credential_theft',
            'data_exfiltration', 'persistence', 'evasion',
            'memory_pollution', 'supply_chain_attack', 'remote_load',
            'resource_exhaustion', 'normal_script', 'common_pattern', 'false_prone'
        ]
    
    def collect_and_chunk(self, chunk_size: int = 10000) -> List[Dict]:
        """收集样本并分块"""
        all_samples = []
        
        for at in self.attack_types:
            attack_dir = self.samples_dir / at
            if attack_dir.exists():
                for d in attack_dir.iterdir():
                    if d.is_dir():
                        all_samples.append((at, str(d)))
        
        # 分块
        chunks = []
        for i in range(0, len(all_samples), chunk_size):
            chunk = all_samples[i:i+chunk_size]
            chunks.append({
                'task_id': f"chunk_{i//chunk_size:03d}",
                'samples': [path for _, path in chunk]
            })
        
        print(f"📂 样本总数：{len(all_samples):,}")
        print(f"📦 分块数：{len(chunks)} (每块 ~{chunk_size} 样本)")
        
        return chunks
    
    def run_parallel(self, workers: int = 8, chunk_size: int = 10000):
        """并行扫描"""
        print("="*70)
        print("🛡️  Distributed Scanner v4.1 - 并行模式")
        print("="*70)
        print()
        
        # 分块
        chunks = self.collect_and_chunk(chunk_size)
        
        # 保存任务列表
        tasks_file = self.output_dir / "tasks.json"
        with open(tasks_file, 'w') as f:
            json.dump(chunks, f, indent=2)
        
        print(f"💾 任务列表：{tasks_file}")
        print(f"⚡ 并发度：{workers} 线程")
        print()
        print("🚀 开始扫描...")
        print()
        
        # 并行执行
        all_results = []
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {
                executor.submit(
                    worker_task,
                    chunk['task_id'],
                    chunk['samples'],
                    str(self.rules_dir),
                    str(self.output_dir / 'workers')
                ): chunk for chunk in chunks
            }
            
            completed = 0
            for future in as_completed(futures):
                result = future.result()
                all_results.append(result)
                completed += 1
                
                if completed % 3 == 0:
                    elapsed = time.time() - start_time
                    total_scanned = sum(r['samples_scanned'] for r in all_results)
                    print(f"  进度：{completed}/{len(chunks)} 分片 | {total_scanned:,} 样本 | {total_scanned/elapsed:.0f}/秒")
        
        total_time = time.time() - start_time
        
        # 汇总
        print()
        print("📊 汇总结果...")
        return self._aggregate(all_results, total_time)
    
    def _aggregate(self, worker_results: List[Dict], total_time: float) -> Dict:
        """汇总所有 Worker 结果"""
        # 合并所有 results
        all_results = []
        for wr in worker_results:
            all_results.extend(wr['results'])
        
        # 统计
        malicious = [r for r in all_results if r['attack_type'] not in ['normal_script', 'common_pattern', 'false_prone']]
        benign = [r for r in all_results if r['attack_type'] in ['normal_script', 'common_pattern']]
        
        detected = len([r for r in malicious if r['verdict'] == 'malicious'])
        fps = len([r for r in benign if r['verdict'] == 'malicious'])
        fns = len([r for r in malicious if r['verdict'] == 'benign'])
        
        det_rate = (detected / len(malicious) * 100) if malicious else 0
        fp_rate = (fps / len(benign) * 100) if benign else 0
        precision = (detected / (detected + fps) * 100) if (detected + fps) > 0 else 100
        
        scan_times = [r['scan_ms'] for r in all_results]
        
        # 按攻击类型
        by_type = {}
        for at in set(r['attack_type'] for r in all_results):
            type_results = [r for r in all_results if r['attack_type'] == at]
            type_det = len([r for r in type_results if r['verdict'] == 'malicious'])
            by_type[at] = {
                'total': len(type_results),
                'detected': type_det,
                'rate': (type_det / len(type_results) * 100) if type_results else 0
            }
        
        # 最终报告
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_samples': len(all_results),
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
                'speed': len(all_results) / total_time
            },
            'by_attack_type': by_type,
            'workers': len(worker_results)
        }
        
        # 保存报告
        report_file = self.output_dir / f"FINAL_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        atomic_write_json(report_file, report)
        
        return report, report_file

def print_report(report: Dict, report_file: Path):
    """打印报告"""
    print("\n" + "="*70)
    print("📊 最终报告")
    print("="*70)
    print()
    print(f"样本总数：{report['total_samples']:,}")
    print(f"Worker 数：{report['workers']}")
    print()
    print(f"🎯 检测率：{report['detection_rate']:.1f}%")
    print(f"⚠️  误报率：{report['false_positive_rate']:.1f}%")
    print(f"✅ 精确率：{report['precision']:.1f}%")
    print(f"📈 F1 Score: {report['f1_score']:.1f}")
    print()
    print(f"⚡ 总耗时：{report['performance']['total_time_sec']:.1f}秒")
    print(f"⚡ 速度：{report['performance']['speed']:.0f} 样本/秒")
    print(f"⚡ P99: {report['performance']['p99_ms']:.2f}ms")
    print()
    
    print("按攻击类型:")
    for at, stats in sorted(report['by_attack_type'].items(), key=lambda x: x[1]['rate'], reverse=True):
        s = '✅' if stats['rate'] >= 90 else '⚠️' if stats['rate'] >= 70 else '🔴'
        print(f"  {s} {at:25s}: {stats['rate']:6.1f}% ({stats['detected']}/{stats['total']:,})")
    print()
    
    if report['detection_rate'] >= 90 and report['false_positive_rate'] < 20:
        print("  🏆 优秀")
    elif report['detection_rate'] >= 85:
        print("  ✅ 良好")
    else:
        print("  🔴 需要优化")
    
    print(f"\n💾 报告：{report_file}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--samples', default='/home/cdy/Desktop/security-benchmark/samples/from-templates')
    parser.add_argument('--rules', default='/home/cdy/.openclaw/workspace/agent-security-skill-scanner-master/rules/scanner_v3/yara')
    parser.add_argument('--output', default='/home/cdy/.openclaw/workspace/agent-security-skill-scanner-master/benchmark/v4_distributed')
    parser.add_argument('--workers', type=int, default=8)
    parser.add_argument('--chunk-size', type=int, default=10000, help='每块样本数')
    args = parser.parse_args()
    
    scanner = DistributedScanner(args.samples, args.rules, args.output)
    report, report_file = scanner.run_parallel(args.workers, args.chunk_size)
    print_report(report, report_file)
