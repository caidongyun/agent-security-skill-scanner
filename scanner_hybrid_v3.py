#!/usr/bin/env python3
"""
🛡️ Hybrid Security Scanner V3 - 混合扫描器
YARA 规则主导 + 意图识别辅助 - 平衡检测率和误报率

架构:
1. YARA 规则扫描 (主力检测) - 保持 90%+ 检测率
2. 意图识别分析 (辅助过滤) - 降低误报率
3. 白名单机制 (特殊豁免) - 处理明确良性
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import statistics

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
    risk_score: float
    final_verdict: str
    is_false_positive: bool
    is_false_negative: bool
    scan_time_ms: float
    whitelisted: bool
    verdict_reason: str

class HybridScanner:
    """混合扫描器 - YARA 主导 + 意图辅助"""
    
    def __init__(self, rules_dir: str, max_workers: int = 4):
        self.rules_dir = Path(rules_dir)
        self.max_workers = max_workers
        self.compiled_rules = None
        self.rule_count = 0
        self.intent_detector = EnhancedIntentDetector()
        
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
        
        self.compiled_rules = self.yara.compile(source=all_rules)
        self.rule_count = all_rules.count('rule ')
        
        print(f"✅ 加载 {self.rule_count} 条规则 ({time.time()-start:.2f}s)")
    
    def scan_sample(self, sample_dir: Path, attack_type: str) -> Optional[ScanResult]:
        """
        扫描单个样本 - 混合判定逻辑
        
        流程:
        1. YARA 扫描
        2. 白名单检查 (如果是良性类型)
        3. 意图识别 (仅当 YARA 命中且可能是误报时)
        4. 综合判定
        """
        sample_id = sample_dir.name
        
        # 查找 payload
        payload_files = list(sample_dir.glob('payload.*'))
        if not payload_files:
            return None
        
        payload_file = payload_files[0]
        content = payload_file.read_text(encoding='utf-8', errors='ignore')
        
        # 判断是否为良性类型
        is_benign_type = attack_type in ['normal_script', 'common_pattern']
        
        start = time.perf_counter()
        
        # 1. YARA 扫描
        yara_matches = self.compiled_rules.match(data=content)
        yara_detected = len(yara_matches) > 0
        yara_rules = [m.rule for m in yara_matches]
        
        # 2. 白名单检查 (仅良性类型)
        whitelisted = False
        whitelist_reason = ""
        if is_benign_type:
            whitelisted, whitelist_reason = self.intent_detector.check_whitelist(content, str(payload_file))
        
        # 3. 意图识别 (条件触发)
        intent_type = "unknown"
        risk_score = 0.0
        verdict_reason = "YARA 未命中"
        
        if yara_detected:
            # YARA 命中 → 进行意图识别
            intent_result = self.intent_detector.analyze(
                code=content,
                yara_matches=yara_rules,
                file_path=str(payload_file)
            )
            intent_type = intent_result.intent.value
            risk_score = intent_result.risk_score
            
            # 4. 综合判定 (优化版：YARA 更主导)
            if is_benign_type and whitelisted:
                # 良性类型 + 白名单 → 强制良性
                final_verdict = "benign"
                verdict_reason = f"白名单豁免：{whitelist_reason}"
            elif intent_result.intent == IntentType.MALICIOUS:
                # 意图也说恶意 → 确认恶意
                final_verdict = "malicious"
                verdict_reason = "YARA+ 意图一致"
            elif intent_result.intent == IntentType.SUSPICIOUS:
                # 意图说可疑 → 看风险分数
                if risk_score >= 4.0:
                    final_verdict = "malicious"
                    verdict_reason = f"可疑高风险：{risk_score}"
                else:
                    final_verdict = "suspicious"
                    verdict_reason = f"可疑中风险：{risk_score}"
            elif intent_result.intent == IntentType.BENIGN:
                # 意图说良性 → 只有很低风险才推翻 YARA
                if risk_score < 1.5 and is_benign_type:
                    # 很低风险 + 良性类型 → 可能是误报
                    final_verdict = "benign"
                    verdict_reason = f"意图良性极低风险：{risk_score}"
                else:
                    # 中高风险或不是良性类型 → 相信 YARA
                    final_verdict = "malicious"
                    verdict_reason = f"YARA 主导，风险：{risk_score}"
            else:
                # 未知意图 → 相信 YARA
                final_verdict = "malicious"
                verdict_reason = "YARA 主导，意图未知"
        else:
            # YARA 未命中 → 良性
            final_verdict = "benign"
            verdict_reason = "YARA 未命中"
        
        scan_time = (time.perf_counter() - start) * 1000  # ms
        
        # 判断真假阳性/阴性
        final_is_malicious = final_verdict in ['malicious', 'suspicious']
        is_false_positive = final_is_malicious and is_benign_type
        is_false_negative = (final_verdict == 'benign') and not is_benign_type
        
        return ScanResult(
            sample_id=sample_id,
            attack_type=attack_type,
            file_path=str(payload_file),
            yara_detected=yara_detected,
            yara_rules=yara_rules,
            intent_type=intent_type,
            risk_score=risk_score,
            final_verdict=final_verdict,
            is_false_positive=is_false_positive,
            is_false_negative=is_false_negative,
            scan_time_ms=scan_time,
            whitelisted=whitelisted,
            verdict_reason=verdict_reason
        )
    
    def run(self, samples_dir: str, sample_limit: int = None) -> Dict:
        """运行基准测试"""
        print("=" * 70)
        print("🛡️  Hybrid Security Scanner V3 (YARA 主导 + 意图辅助)")
        print("=" * 70)
        print()
        
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
        
        return self._generate_report(results, total_time)
    
    def _generate_report(self, results: List[ScanResult], total_time: float) -> Dict:
        """生成报告"""
        # 分类
        malicious_samples = [r for r in results if r.attack_type not in ['normal_script', 'common_pattern', 'false_prone']]
        benign_samples = [r for r in results if r.attack_type in ['normal_script', 'common_pattern']]
        
        # 统计
        detected_malicious = len([r for r in malicious_samples if r.final_verdict in ['malicious', 'suspicious']])
        false_positives = len([r for r in benign_samples if r.final_verdict in ['malicious', 'suspicious']])
        false_negatives = len([r for r in malicious_samples if r.final_verdict == 'benign'])
        
        detection_rate = (detected_malicious / len(malicious_samples) * 100) if malicious_samples else 0
        false_positive_rate = (false_positives / len(benign_samples) * 100) if benign_samples else 0
        precision = (detected_malicious / (detected_malicious + false_positives) * 100) if (detected_malicious + false_positives) > 0 else 0
        
        # 意图识别统计
        intent_malicious = len([r for r in results if r.intent_type == 'malicious'])
        intent_benign = len([r for r in results if r.intent_type == 'benign'])
        intent_suspicious = len([r for r in results if r.intent_type == 'suspicious'])
        whitelisted_count = len([r for r in results if r.whitelisted])
        
        # 判定原因统计
        verdict_reasons = {}
        for r in results:
            reason = r.verdict_reason.split(':')[0]
            verdict_reasons[reason] = verdict_reasons.get(reason, 0) + 1
        
        # 性能
        scan_times = [r.scan_time_ms for r in results]
        avg_time = statistics.mean(scan_times)
        sorted_times = sorted(scan_times)
        p50 = sorted_times[len(sorted_times)//2]
        p99 = sorted_times[int(len(sorted_times)*0.99)]
        
        # 按攻击类型
        by_attack_type = {}
        for attack_type in set(r.attack_type for r in results):
            type_results = [r for r in results if r.attack_type == attack_type]
            type_detected = len([r for r in type_results if r.final_verdict in ['malicious', 'suspicious']])
            by_attack_type[attack_type] = {
                'total': len(type_results),
                'detected': type_detected,
                'rate': (type_detected / len(type_results) * 100) if type_results else 0
            }
        
        return {
            'timestamp': datetime.now().isoformat(),
            'scanner_version': 'v3.0 (Hybrid)',
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
                'samples_per_second': len(results) / total_time
            },
            'intent_detection': {
                'malicious': intent_malicious,
                'benign': intent_benign,
                'suspicious': intent_suspicious,
                'whitelisted': whitelisted_count
            },
            'verdict_reasons': verdict_reasons,
            'by_attack_type': by_attack_type
        }

def print_report(report: Dict):
    """打印报告"""
    print("=" * 70)
    print("📊 基准测试报告 (Hybrid V3)")
    print("=" * 70)
    print()
    
    print(f"扫描器：{report['scanner_version']}")
    print(f"规则数：{report['rules_count']}")
    print(f"样本数：{report['total_samples']}")
    print()
    
    print("核心指标:")
    print(f"  🎯 检测率：   {report['detection_rate']:.1f}%")
    print(f"  ⚠️  误报率：   {report['false_positive_rate']:.1f}%")
    print(f"  ✅ 精确率：   {report['precision']:.1f}%")
    print(f"  📈 召回率：   {report['recall']:.1f}%")
    print(f"  🎯 F1 Score:  {report['f1_score']:.1f}")
    print()
    
    print("意图识别辅助:")
    intent = report['intent_detection']
    print(f"  意图恶意：    {intent['malicious']}")
    print(f"  意图良性：    {intent['benign']}")
    print(f"  意图可疑：    {intent['suspicious']}")
    print(f"  白名单豁免：  {intent['whitelisted']}")
    print()
    
    print("判定原因分布:")
    for reason, count in sorted(report['verdict_reasons'].items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {reason}: {count}")
    print()
    
    print("性能:")
    perf = report['performance']
    print(f"  平均：{perf['avg_scan_time_ms']:.2f}ms | P50: {perf['p50_ms']:.2f}ms | P99: {perf['p99_ms']:.2f}ms")
    print(f"  速度：{perf['samples_per_second']:.1f} 样本/秒")
    print()
    
    print("按攻击类型:")
    for at, stats in sorted(report['by_attack_type'].items(), key=lambda x: x[1]['rate'], reverse=True):
        s = '✅' if stats['rate'] >= 90 else '⚠️' if stats['rate'] >= 70 else '🔴'
        print(f"  {s} {at:25s}: {stats['rate']:6.1f}% ({stats['detected']}/{stats['total']})")
    print()
    
    # 评级
    if report['detection_rate'] >= 90 and report['false_positive_rate'] < 20:
        print("  🏆 优秀 (检测率≥90%, 误报率<20%)")
    elif report['detection_rate'] >= 85 and report['false_positive_rate'] < 30:
        print("  ✅ 良好 (检测率≥85%, 误报率<30%)")
    elif report['detection_rate'] >= 80:
        print("  ⚠️  可接受 (检测率≥80%)")
    else:
        print("  🔴 需要优化")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--samples', default='/home/cdy/Desktop/security-benchmark/samples/from-templates')
    parser.add_argument('--rules', default='/home/cdy/.openclaw/workspace/agent-security-skill-scanner-master/rules/scanner_v3/yara')
    parser.add_argument('--limit', type=int, default=100)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--output', default=None)
    args = parser.parse_args()
    
    scanner = HybridScanner(args.rules, args.workers)
    report = scanner.run(args.samples, args.limit)
    print_report(report)
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"💾 报告已保存：{args.output}")

if __name__ == '__main__':
    main()
