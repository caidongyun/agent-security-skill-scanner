#!/usr/bin/env python3
"""
🛡️ Security Scanner with Intent Detection V2
集成增强意图识别的安全扫描器 - 大幅降低误报率

功能:
1. YARA 规则扫描
2. 意图识别分析
3. 白名单过滤
4. 综合判定
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import statistics

# 导入意图识别器
sys.path.insert(0, str(Path(__file__).parent))
from intent_detector_v2 import EnhancedIntentDetector, IntentType

@dataclass
class ScanResult:
    """扫描结果"""
    sample_id: str
    attack_type: str
    file_path: str
    yara_detected: bool
    yara_rules: List[str]
    intent_type: str
    intent_confidence: float
    risk_score: float
    final_verdict: str  # malicious, benign, suspicious
    is_false_positive: bool
    is_false_negative: bool
    scan_time_ms: float
    whitelisted: bool = False

class IntentAwareScanner:
    """集成意图识别的扫描器"""
    
    def __init__(self, rules_dir: str, max_workers: int = 4):
        self.rules_dir = Path(rules_dir)
        self.max_workers = max_workers
        self.compiled_rules = None
        self.rule_count = 0
        self.intent_detector = EnhancedIntentDetector()
        
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
    
    def scan_sample(self, sample_dir: Path, attack_type: str) -> Optional[ScanResult]:
        """扫描单个样本 (YARA + 意图识别)"""
        sample_id = sample_dir.name
        
        # 查找 payload 文件
        payload_files = list(sample_dir.glob('payload.*'))
        if not payload_files:
            return None
        
        payload_file = payload_files[0]
        content = payload_file.read_text(encoding='utf-8', errors='ignore')
        
        # 1. YARA 扫描
        start = time.perf_counter()
        yara_matches = self.compiled_rules.match(data=content)
        yara_detected = len(yara_matches) > 0
        yara_rules = [m.rule for m in yara_matches]
        
        # 2. 意图识别
        intent_result = self.intent_detector.analyze(
            code=content,
            yara_matches=yara_rules,
            file_path=str(payload_file)
        )
        
        scan_time = (time.perf_counter() - start) * 1000  # ms
        
        # 3. 综合判定 (优化版：更平衡)
        # 规则：
        # 1. YARA 说恶意 + 意图说恶意 → 恶意
        # 2. YARA 说恶意 + 意图说良性 → 看风险分数
        # 3. YARA 说良性 → 良性
        
        if yara_detected and intent_result.intent == IntentType.MALICIOUS:
            # 一致：恶意
            final_verdict = "malicious"
        elif yara_detected and intent_result.intent == IntentType.SUSPICIOUS:
            # 可疑也当作恶意
            final_verdict = "malicious"
        elif yara_detected and intent_result.intent == IntentType.BENIGN:
            # YARA 说恶意但意图说良性 → 看风险分数
            if intent_result.risk_score < 2.0:
                # 很低风险 → 相信意图识别，判定良性
                final_verdict = "benign"
            elif intent_result.risk_score < 5.0:
                # 中等风险 → 可疑 (需要人工审查)
                final_verdict = "suspicious"
            else:
                # 高风险 → 即使意图说良性，也判定为恶意 (YARA 可能更准确)
                final_verdict = "malicious"
        else:
            # YARA 没有检测到 → 良性
            final_verdict = "benign"
        
        # 4. 判断真假阳性/阴性
        is_benign_type = attack_type in ['normal_script', 'common_pattern']
        is_false_positive = (final_verdict == "malicious" or final_verdict == "suspicious") and is_benign_type
        is_false_negative = final_verdict == "benign" and not is_benign_type
        
        return ScanResult(
            sample_id=sample_id,
            attack_type=attack_type,
            file_path=str(payload_file),
            yara_detected=yara_detected,
            yara_rules=yara_rules,
            intent_type=intent_result.intent.value,
            intent_confidence=intent_result.confidence,
            risk_score=intent_result.risk_score,
            final_verdict=final_verdict,
            is_false_positive=is_false_positive,
            is_false_negative=is_false_negative,
            scan_time_ms=scan_time,
            whitelisted=intent_result.whitelisted
        )
    
    def run(self, samples_dir: str, sample_limit: int = None) -> Dict:
        """运行基准测试"""
        print("=" * 70)
        print("🛡️  Intent-Aware Security Scanner V2")
        print("=" * 70)
        print()
        
        # 加载规则
        self.load_rules()
        print()
        
        # 收集样本
        samples_dir = Path(samples_dir)
        attack_types = [
            'tool_poisoning', 'prompt_injection', 'credential_theft',
            'data_exfiltration', 'persistence', 'evasion',
            'memory_pollution', 'supply_chain_attack', 'remote_load',
            'resource_exhaustion', 'normal_script', 'common_pattern',
            'false_prone'
        ]
        
        print("📂 收集样本...")
        all_samples = []
        for attack_type in attack_types:
            attack_dir = samples_dir / attack_type
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
        results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self.scan_sample, sample_dir, attack_type): (sample_dir, attack_type)
                for sample_dir, attack_type in all_samples
            }
            
            completed = 0
            for future in as_completed(futures):
                result = future.result()
                if result:
                    results.append(result)
                
                completed += 1
                if completed % 500 == 0:
                    print(f"  进度：{completed}/{len(all_samples)} ({completed/len(all_samples)*100:.1f}%)")
        
        total_time = time.time() - start_time
        print()
        
        # 生成报告
        return self._generate_report(results, total_time)
    
    def _generate_report(self, results: List[ScanResult], total_time: float) -> Dict:
        """生成测试报告"""
        # 分类统计
        malicious_samples = [r for r in results if r.attack_type not in ['normal_script', 'common_pattern', 'false_prone']]
        benign_samples = [r for r in results if r.attack_type in ['normal_script', 'common_pattern']]
        
        # 最终判定为恶意的数量
        detected_malicious = len([r for r in malicious_samples if r.final_verdict == 'malicious' or r.final_verdict == 'suspicious'])
        false_positives = len([r for r in benign_samples if r.final_verdict == 'malicious' or r.final_verdict == 'suspicious'])
        false_negatives = len([r for r in malicious_samples if r.final_verdict == 'benign'])
        
        detection_rate = (detected_malicious / len(malicious_samples) * 100) if malicious_samples else 0
        false_positive_rate = (false_positives / len(benign_samples) * 100) if benign_samples else 0
        precision = (detected_malicious / (detected_malicious + false_positives) * 100) if (detected_malicious + false_positives) > 0 else 0
        
        # 意图识别效果
        whitelisted_count = len([r for r in results if r.whitelisted])
        intent_malicious = len([r for r in results if r.intent_type == 'malicious'])
        intent_benign = len([r for r in results if r.intent_type == 'benign'])
        intent_suspicious = len([r for r in results if r.intent_type == 'suspicious'])
        
        # 性能统计
        scan_times = [r.scan_time_ms for r in results]
        avg_time = statistics.mean(scan_times) if scan_times else 0
        sorted_times = sorted(scan_times)
        p50 = sorted_times[len(sorted_times)//2] if sorted_times else 0
        p99 = sorted_times[int(len(sorted_times)*0.99)] if sorted_times else 0
        
        samples_per_second = len(results) / total_time if total_time > 0 else 0
        
        # 按攻击类型统计
        by_attack_type = {}
        for attack_type in set(r.attack_type for r in results):
            type_results = [r for r in results if r.attack_type == attack_type]
            type_detected = len([r for r in type_results if r.final_verdict == 'malicious' or r.final_verdict == 'suspicious'])
            type_total = len(type_results)
            type_rate = (type_detected / type_total * 100) if type_total > 0 else 0
            
            by_attack_type[attack_type] = {
                'total': type_total,
                'detected': type_detected,
                'rate': type_rate
            }
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'scanner_version': 'v2.0 (Intent-Aware)',
            'rules_count': self.rule_count,
            'total_samples': len(results),
            'malicious_samples': len(malicious_samples),
            'benign_samples': len(benign_samples),
            'detected_malicious': detected_malicious,
            'false_positives': false_positives,
            'false_negatives': false_negatives,
            'detection_rate': detection_rate,
            'false_positive_rate': false_positive_rate,
            'precision': precision,
            'recall': detection_rate,
            'f1_score': 2 * (precision * detection_rate) / (precision + detection_rate) if (precision + detection_rate) > 0 else 0,
            'performance': {
                'avg_scan_time_ms': avg_time,
                'p50_ms': p50,
                'p99_ms': p99,
                'samples_per_second': samples_per_second
            },
            'intent_detection': {
                'whitelisted': whitelisted_count,
                'intent_malicious': intent_malicious,
                'intent_benign': intent_benign,
                'intent_suspicious': intent_suspicious
            },
            'by_attack_type': by_attack_type
        }
        
        return report

def print_report(report: Dict):
    """打印报告"""
    print("=" * 70)
    print("📊 基准测试报告 (Intent-Aware V2)")
    print("=" * 70)
    print()
    
    print(f"时间：{report['timestamp']}")
    print(f"扫描器版本：{report['scanner_version']}")
    print(f"规则数：{report['rules_count']}")
    print()
    
    print("总体指标:")
    print(f"  总样本数：     {report['total_samples']}")
    print(f"  恶意样本：    {report['malicious_samples']}")
    print(f"  良性样本：    {report['benign_samples']}")
    print()
    
    print(f"  🎯 检测率：   {report['detection_rate']:.1f}%")
    print(f"  ⚠️  误报率：   {report['false_positive_rate']:.1f}%")
    print(f"  ✅ 精确率：   {report['precision']:.1f}%")
    print(f"  📈 召回率：   {report['recall']:.1f}%")
    print(f"  🎯 F1 Score:  {report['f1_score']:.1f}")
    print()
    
    print("意图识别效果:")
    intent = report['intent_detection']
    print(f"  白名单豁免：  {intent['whitelisted']}")
    print(f"  意图恶意：    {intent['intent_malicious']}")
    print(f"  意图良性：    {intent['intent_benign']}")
    print(f"  意图可疑：    {intent['intent_suspicious']}")
    print()
    
    print("性能指标:")
    perf = report['performance']
    print(f"  平均扫描时间：{perf['avg_scan_time_ms']:.2f}ms")
    print(f"  P50 延迟：     {perf['p50_ms']:.2f}ms")
    print(f"  P99 延迟：     {perf['p99_ms']:.2f}ms")
    print(f"  扫描速度：    {perf['samples_per_second']:.1f} 样本/秒")
    print()
    
    print("按攻击类型:")
    sorted_types = sorted(report['by_attack_type'].items(), key=lambda x: x[1]['rate'], reverse=True)
    for attack_type, stats in sorted_types:
        status = '✅' if stats['rate'] >= 90 else '⚠️' if stats['rate'] >= 70 else '🔴'
        print(f"  {status} {attack_type:25s}: {stats['rate']:6.1f}% ({stats['detected']}/{stats['total']})")
    print()
    
    # 评级
    print("评级:")
    if report['detection_rate'] >= 95 and report['false_positive_rate'] < 10:
        print("  🏆 优秀 (检测率≥95%, 误报率<10%)")
    elif report['detection_rate'] >= 90 and report['false_positive_rate'] < 20:
        print("  ✅ 良好 (检测率≥90%, 误报率<20%)")
    elif report['detection_rate'] >= 80:
        print("  ⚠️  可接受 (检测率≥80%)")
    else:
        print("  🔴 需要优化 (检测率<80%)")
    print()

def main():
    parser = argparse.ArgumentParser(description='Intent-Aware Security Scanner V2')
    parser.add_argument('--samples', default='/home/cdy/Desktop/security-benchmark/samples/from-templates',
                       help='样本目录')
    parser.add_argument('--rules', default='/home/cdy/.openclaw/workspace/agent-security-skill-scanner-master/rules/scanner_v3/yara',
                       help='YARA 规则目录')
    parser.add_argument('--limit', type=int, default=100,
                       help='每个攻击类型限制的样本数 (默认：100)')
    parser.add_argument('--workers', type=int, default=4,
                       help='并发工作线程数 (默认：4)')
    parser.add_argument('--output', default=None,
                       help='输出报告文件 (JSON)')
    
    args = parser.parse_args()
    
    scanner = IntentAwareScanner(args.rules, args.workers)
    report = scanner.run(args.samples, args.limit)
    print_report(report)
    
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"💾 报告已保存：{output_path}")

if __name__ == '__main__':
    main()
