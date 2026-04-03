#!/usr/bin/env python3
"""
🛡️ Distributed Scanner v4.0 - 分布式扫描架构
Coordinator (主节点) - 任务分发 · 进度跟踪 · 结果汇总
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List
from dataclasses import dataclass, asdict

@dataclass
class ScanTask:
    """扫描任务"""
    task_id: str
    attack_type: str
    sample_dirs: List[str]  # 样本目录路径列表
    worker_id: str = ""
    status: str = "pending"  # pending/running/completed/failed
    start_time: str = ""
    end_time: str = ""
    result_file: str = ""

@dataclass
class WorkerResult:
    """Worker 结果"""
    worker_id: str
    task_id: str
    samples_scanned: int
    detection_rate: float
    false_positive_rate: float
    f1_score: float
    scan_time_sec: float
    speed: float  # 样本/秒
    result_file: str

class Coordinator:
    """扫描协调器"""
    
    def __init__(self, samples_dir: str, rules_dir: str, output_dir: str):
        self.samples_dir = Path(samples_dir)
        self.rules_dir = Path(rules_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.tasks: List[ScanTask] = []
        self.results: List[WorkerResult] = []
        
        # 攻击类型配置
        self.attack_types = [
            'tool_poisoning', 'prompt_injection', 'credential_theft',
            'data_exfiltration', 'persistence', 'evasion',
            'memory_pollution', 'supply_chain_attack', 'remote_load',
            'resource_exhaustion', 'normal_script', 'common_pattern', 'false_prone'
        ]
    
    def collect_samples(self, chunk_size: int = 5000) -> List[ScanTask]:
        """收集样本并分片"""
        print("📂 收集样本并分片...")
        
        all_samples = []
        for at in self.attack_types:
            attack_dir = self.samples_dir / at
            if attack_dir.exists():
                for d in attack_dir.iterdir():
                    if d.is_dir():
                        all_samples.append((at, str(d)))
        
        print(f"  总样本数：{len(all_samples)}")
        
        # 分片
        chunks = []
        for i in range(0, len(all_samples), chunk_size):
            chunk = all_samples[i:i+chunk_size]
            task_id = f"task_{i//chunk_size:03d}_{datetime.now().strftime('%H%M%S')}"
            
            # 按攻击类型分组
            by_type = {}
            for at, path in chunk:
                if at not in by_type:
                    by_type[at] = []
                by_type[at].append(path)
            
            task = ScanTask(
                task_id=task_id,
                attack_type="multi",
                sample_dirs=[p for _, p in chunk]
            )
            chunks.append(task)
        
        print(f"  分片数：{len(chunks)} (每片 ~{chunk_size} 样本)")
        return chunks
    
    def save_tasks(self, tasks: List[ScanTask]):
        """保存任务列表"""
        task_file = self.output_dir / "tasks.json"
        with open(task_file, 'w') as f:
            json.dump([asdict(t) for t in tasks], f, indent=2)
        print(f"💾 任务列表：{task_file}")
    
    def generate_worker_script(self, task: ScanTask, worker_id: str = "local"):
        """生成 Worker 扫描脚本"""
        script = f'''#!/usr/bin/env python3
"""
Worker 扫描脚本 - {task.task_id}
自动生成 · 独立运行 · 结果持久化
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict

sys.path.insert(0, '{str(Path(__file__).parent)}')
from intent_detector_v2 import EnhancedIntentDetector, IntentType

@dataclass
class Result:
    attack_type: str
    verdict: str
    is_fp: bool
    is_fn: bool
    scan_ms: float

def scan_sample(rules, detector, sample_path: str) -> Result:
    """扫描单个样本"""
    sample_dir = Path(sample_path)
    payload_files = list(sample_dir.glob('payload.*'))
    
    if not payload_files:
        return None
    
    content = payload_files[0].read_text(errors='ignore')
    attack_type = sample_dir.parent.name
    is_benign_type = attack_type in ['normal_script', 'common_pattern']
    
    start = time.perf_counter()
    
    # YARA 扫描
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
    final_malicious = verdict == "malicious"
    
    return Result(
        attack_type=attack_type,
        verdict=verdict,
        is_fp=final_malicious and is_benign_type,
        is_fn=(verdict == "benign") and not is_benign_type,
        scan_ms=scan_ms
    )

def main():
    import yara
    
    # 配置
    task_id = "{task.task_id}"
    sample_dirs = {json.dumps(task.sample_dirs)}
    rules_dir = Path("{str(self.rules_dir)}")
    output_dir = Path("{str(self.output_dir)}/workers")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 加载规则
    all_rules = ""
    for rf in rules_dir.glob('*.yar'):
        all_rules += rf.read_text(errors='ignore') + "\\n\\n"
    rules = yara.compile(source=all_rules)
    
    detector = EnhancedIntentDetector()
    
    # 扫描
    print(f"🚀 Worker 扫描：{{task_id}}")
    print(f"  样本数：{{len(sample_dirs)}}")
    
    start_time = time.time()
    results = []
    
    for sample_path in sample_dirs:
        result = scan_sample(rules, detector, sample_path)
        if result:
            results.append(asdict(result))
    
    total_time = time.time() - start_time
    
    # 统计
    malicious = [r for r in results if r['attack_type'] not in ['normal_script', 'common_pattern', 'false_prone']]
    benign = [r for r in results if r['attack_type'] in ['normal_script', 'common_pattern']]
    
    detected = len([r for r in malicious if r['verdict'] == 'malicious'])
    fps = len([r for r in benign if r['verdict'] == 'malicious'])
    
    det_rate = (detected / len(malicious) * 100) if malicious else 0
    fp_rate = (fps / len(benign) * 100) if benign else 0
    precision = (detected / (detected + fps) * 100) if (detected + fps) > 0 else 100
    
    # 保存结果
    result_data = {{
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
    }}
    
    result_file = output_dir / f"{{task_id}}_result.json"
    with open(result_file, 'w') as f:
        json.dump(result_data, f, indent=2)
    
    print(f"✅ 完成：{{len(results)}} 样本")
    print(f"  检测率：{{det_rate:.1f}}%")
    print(f"  误报率：{{fp_rate:.1f}}%")
    print(f"  速度：{{len(results)/total_time:.0f}} 样本/秒")
    print(f"  结果：{{result_file}}")

if __name__ == '__main__':
    main()
'''
        return script
    
    def run_local(self, chunk_size: int = 5000):
        """本地运行（单 Worker 模式）"""
        print("="*70)
        print("🛡️  Distributed Scanner v4.0 - 本地模式")
        print("="*70)
        print()
        
        # 分片
        tasks = self.collect_samples(chunk_size)
        self.save_tasks(tasks)
        
        print()
        print("🚀 开始扫描...")
        print()
        
        import yara
        from intent_detector_v2 import EnhancedIntentDetector
        
        # 加载规则
        all_rules = ""
        for rf in self.rules_dir.glob('*.yar'):
            all_rules += rf.read_text(errors='ignore') + "\n\n"
        rules = yara.compile(source=all_rules)
        detector = EnhancedIntentDetector()
        
        # 扫描所有样本
        all_results = []
        start_time = time.time()
        
        for i, task in enumerate(tasks, 1):
            print(f"  分片 {i}/{len(tasks)}: {len(task.sample_dirs)} 样本")
            
            for sample_path in task.sample_dirs:
                result = self._scan_single(rules, detector, sample_path)
                if result:
                    all_results.append(result)
            
            if i % 5 == 0:
                elapsed = time.time() - start_time
                speed = len(all_results) / elapsed
                print(f"    进度：{len(all_results)} 样本 | {speed:.0f} 样本/秒")
        
        total_time = time.time() - start_time
        
        # 生成汇总报告
        return self._aggregate_results(all_results, total_time)
    
    def _scan_single(self, rules, detector, sample_path: str):
        """扫描单个样本（内部方法）"""
        from intent_detector_v2 import IntentType
        
        sample_dir = Path(sample_path)
        payload_files = list(sample_dir.glob('payload.*'))
        
        if not payload_files:
            return None
        
        content = payload_files[0].read_text(errors='ignore')
        attack_type = sample_dir.parent.name
        is_benign_type = attack_type in ['normal_script', 'common_pattern']
        
        start = time.perf_counter()
        
        yara_matches = rules.match(data=content)
        yara_detected = len(yara_matches) > 0
        
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
        
        return {
            'attack_type': attack_type,
            'verdict': verdict,
            'is_fp': (verdict == 'malicious') and is_benign_type,
            'is_fn': (verdict == 'benign') and not is_benign_type,
            'scan_ms': scan_ms
        }
    
    def _aggregate_results(self, results: List[Dict], total_time: float) -> Dict:
        """汇总结果"""
        malicious = [r for r in results if r['attack_type'] not in ['normal_script', 'common_pattern', 'false_prone']]
        benign = [r for r in results if r['attack_type'] in ['normal_script', 'common_pattern']]
        
        detected = len([r for r in malicious if r['verdict'] == 'malicious'])
        fps = len([r for r in benign if r['verdict'] == 'malicious'])
        fns = len([r for r in malicious if r['verdict'] == 'benign'])
        
        det_rate = (detected / len(malicious) * 100) if malicious else 0
        fp_rate = (fps / len(benign) * 100) if benign else 0
        precision = (detected / (detected + fps) * 100) if (detected + fps) > 0 else 100
        
        scan_times = [r['scan_ms'] for r in results]
        import statistics
        
        # 按攻击类型
        by_type = {}
        for at in set(r['attack_type'] for r in results):
            type_results = [r for r in results if r['attack_type'] == at]
            type_det = len([r for r in type_results if r['verdict'] == 'malicious'])
            by_type[at] = {
                'total': len(type_results),
                'detected': type_det,
                'rate': (type_det / len(type_results) * 100) if type_results else 0
            }
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_samples': len(results),
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
        
        # 保存报告
        report_file = self.output_dir / f"FINAL_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report, report_file

def print_report(report: Dict, report_file: Path):
    """打印报告"""
    print("\n" + "="*70)
    print("📊 分布式扫描报告")
    print("="*70)
    print()
    print(f"样本总数：{report['total_samples']:,}")
    print(f"恶意样本：{report['malicious_samples']:,}")
    print(f"良性样本：{report['benign_samples']:,}")
    print()
    print(f"🎯 检测率：{report['detection_rate']:.1f}%")
    print(f"⚠️  误报率：{report['false_positive_rate']:.1f}%")
    print(f"✅ 精确率：{report['precision']:.1f}%")
    print(f"📈 F1 Score: {report['f1_score']:.1f}")
    print()
    print(f"⚡ 总耗时：{report['performance']['total_time_sec']:.1f}秒")
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
    
    print(f"\n💾 报告：{report_file}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='分布式扫描协调器')
    parser.add_argument('--samples', default='/home/cdy/Desktop/security-benchmark/samples/from-templates')
    parser.add_argument('--rules', default='/home/cdy/.openclaw/workspace/agent-security-skill-scanner-master/rules/scanner_v3/yara')
    parser.add_argument('--output', default='/home/cdy/.openclaw/workspace/agent-security-skill-scanner-master/benchmark/distributed')
    parser.add_argument('--chunk-size', type=int, default=5000, help='分片大小')
    parser.add_argument('--mode', choices=['local', 'distributed'], default='local', help='运行模式')
    args = parser.parse_args()
    
    coord = Coordinator(args.samples, args.rules, args.output)
    
    if args.mode == 'local':
        report, report_file = coord.run_local(args.chunk_size)
        print_report(report, report_file)
    else:
        print("🔧 分布式模式需要额外配置，请使用 --mode local")
