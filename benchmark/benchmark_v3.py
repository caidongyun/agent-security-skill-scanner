#!/usr/bin/env python3
"""
Benchmark Suite v3 - 使用完整 YARA 规则检测
Round 22 - P0 紧急修复
生成时间：2026-03-28
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Tuple
from datetime import datetime

# 尝试导入 yara-python
try:
    import yara
    YARA_AVAILABLE = True
except ImportError:
    YARA_AVAILABLE = False
    print("⚠️  Warning: yara-python not installed, falling back to pattern matching")
    print("   Install: pip install yara-python")


@dataclass
class ScanResult:
    file_path: str
    category: str  # malicious / benign
    attack_type: str
    language: str
    difficulty: str
    detected: bool
    matched_rules: List[str] = field(default_factory=list)
    scan_time_ms: float = 0.0


@dataclass
class BenchmarkReport:
    timestamp: str
    total_samples: int
    malicious_samples: int
    benign_samples: int
    detected_malicious: int
    false_positives: int
    detection_rate: float
    false_positive_rate: float
    precision: float
    recall: float
    f1_score: float
    by_attack_type: Dict[str, Dict]
    by_difficulty: Dict[str, Dict]
    by_language: Dict[str, Dict]
    yara_rules_used: int = 0
    
    def to_dict(self) -> Dict:
        return {
            'timestamp': self.timestamp,
            'total_samples': self.total_samples,
            'malicious_samples': self.malicious_samples,
            'benign_samples': self.benign_samples,
            'detected_malicious': self.detected_malicious,
            'false_positives': self.false_positives,
            'detection_rate': self.detection_rate,
            'false_positive_rate': self.false_positive_rate,
            'precision': self.precision,
            'recall': self.recall,
            'f1_score': self.f1_score,
            'by_attack_type': self.by_attack_type,
            'by_difficulty': self.by_difficulty,
            'by_language': self.by_language,
            'yara_rules_used': self.yara_rules_used,
        }


class YaraScanner:
    """YARA 规则扫描器"""
    
    def __init__(self, rules_path: str):
        self.rules_path = Path(rules_path)
        self.compiled_rules = None
        self.rule_count = 0
        
        if YARA_AVAILABLE:
            self._compile_rules()
    
    def _compile_rules(self):
        """编译 YARA 规则"""
        if not self.rules_path.exists():
            print(f"⚠️  Rules file not found: {self.rules_path}")
            return
        
        try:
            # 如果是目录，合并所有 .yaml 和 .yar 文件
            if self.rules_path.is_dir():
                all_rules = ""
                skipped_files = []
                for ext in ['*.yaml', '*.yar', '*.yara']:
                    for rf in self.rules_path.glob(ext):
                        try:
                            # 读取文件，转换为 ASCII，忽略非 ASCII 字符
                            content = rf.read_text(encoding='utf-8', errors='ignore')
                            # 移除非 ASCII 字符（YARA 不支持）
                            content = content.encode('ascii', 'ignore').decode('ascii')
                            # 只提取 YARA 规则部分 (rule ... { ... })
                            if 'rule ' in content:
                                # 尝试单独编译这个文件，检查是否有问题
                                try:
                                    yara.compile(source=content)
                                    all_rules += content + "\n\n"
                                except Exception as file_err:
                                    skipped_files.append((rf.name, str(file_err)))
                        except Exception as e:
                            print(f"  Warning: Could not read {rf}: {e}")
                
                # 报告跳过的文件
                if skipped_files:
                    print(f"⚠️  Skipped {len(skipped_files)} problematic rule file(s):")
                    for fname, err in skipped_files[:5]:  # 只显示前 5 个
                        print(f"    - {fname}: {err[:80]}")
                
                if all_rules:
                    self.compiled_rules = yara.compile(source=all_rules)
                    # 统计规则数
                    self.rule_count = all_rules.count('\nrule ') + all_rules.count('rule ')
                    print(f"✓ Compiled {self.rule_count} YARA rules from directory")
                else:
                    print("⚠️  No YARA rules found in directory")
            
            # 如果是文件
            elif self.rules_path.is_file():
                content = self.rules_path.read_text(encoding='utf-8', errors='ignore')
                content = content.encode('ascii', 'ignore').decode('ascii')
                self.compiled_rules = yara.compile(source=content)
                self.rule_count = content.count('\nrule ') + content.count('rule ')
                print(f"✓ Compiled {self.rule_count} YARA rules from file")
        
        except Exception as e:
            print(f"✗ Error compiling rules: {e}")
            self.compiled_rules = None
    
    def scan(self, file_path: Path) -> Tuple[bool, List[str], float]:
        """扫描单个文件"""
        start_time = time.time()
        
        if not YARA_AVAILABLE or not self.compiled_rules:
            # Fallback to pattern matching
            return self._scan_fallback(file_path)
        
        try:
            matches = self.compiled_rules.match(str(file_path))
            scan_time = (time.time() - start_time) * 1000
            
            matched_rules = [m.rule for m in matches]
            is_malicious = len(matches) > 0
            
            return is_malicious, matched_rules, scan_time
        
        except Exception as e:
            return False, [f"error:{str(e)}"], (time.time() - start_time) * 1000
    
    def _scan_fallback(self, file_path: Path) -> Tuple[bool, List[str], float]:
        """Fallback 模式：简单的字符串匹配"""
        start_time = time.time()
        
        patterns = {
            'critical': ['eval(', 'exec(', 'pickle.loads', 'os.system', 'subprocess'],
            'high': ['requests.post', 'socket.socket', 'base64.b64', 'curl ', 'wget '],
            'medium': ['chmod', 'crontab', 'nc ', 'netcat'],
        }
        
        content = file_path.read_text().lower()
        matched = []
        score = 0
        
        for level, pats in patterns.items():
            for p in pats:
                if p.lower() in content:
                    matched.append(f"{level}:{p}")
                    if level == 'critical': score += 0.3
                    elif level == 'high': score += 0.2
                    else: score += 0.1
        
        scan_time = (time.time() - start_time) * 1000
        return score >= 0.3, matched, scan_time


class BenchmarkRunner:
    """Benchmark 运行器"""
    
    def __init__(self, samples_dir: str, rules_dir: str):
        self.samples_dir = Path(samples_dir)
        self.scanner = YaraScanner(rules_dir)
    
    def load_samples(self) -> List[Dict]:
        """加载测试样本"""
        samples = []
        
        for category in ['malicious', 'benign']:
            cat_dir = self.samples_dir / category
            if not cat_dir.exists():
                continue
            
            for lang_dir in cat_dir.iterdir():
                if not lang_dir.is_dir():
                    continue
                
                for meta_file in lang_dir.glob('*.json'):
                    try:
                        meta = json.loads(meta_file.read_text())
                        samples.append({
                            'path': meta_file.with_suffix('.py' if meta.get('language') == 'python' else 
                                                          '.js' if meta.get('language') == 'javascript' else
                                                          '.sh' if meta.get('language') == 'bash' else
                                                          '.ps1'),
                            'category': category,
                            'language': meta.get('language', 'unknown'),
                            'attack_type': meta.get('attack_type'),
                            'difficulty': meta.get('difficulty', 'unknown'),
                        })
                    except Exception as e:
                        pass
        
        return samples
    
    def run(self) -> BenchmarkReport:
        """运行完整 benchmark"""
        samples = self.load_samples()
        results = []
        
        print(f"\nScanning {len(samples)} samples...")
        
        for sample in samples:
            path = Path(sample['path'])
            if not path.exists():
                continue
            
            detected, matched_rules, scan_time = self.scanner.scan(path)
            
            results.append(ScanResult(
                file_path=str(path),
                category=sample['category'],
                attack_type=sample['attack_type'],
                language=sample['language'],
                difficulty=sample['difficulty'],
                detected=detected,
                matched_rules=matched_rules,
                scan_time_ms=scan_time,
            ))
        
        # 统计
        malicious = [r for r in results if r.category == 'malicious']
        benign = [r for r in results if r.category == 'benign']
        
        detected_mal = len([r for r in malicious if r.detected])
        fp = len([r for r in benign if r.detected])
        
        mal_total = len(malicious) if malicious else 1
        ben_total = len(benign) if benign else 1
        
        det_rate = detected_mal / mal_total
        fp_rate = fp / ben_total
        precision = detected_mal / (detected_mal + fp) if (detected_mal + fp) > 0 else 0
        recall = det_rate
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        
        # 按攻击类型统计
        by_attack_type = {}
        attack_types = set(r.attack_type for r in malicious if r.attack_type)
        for at in attack_types:
            at_samples = [r for r in malicious if r.attack_type == at]
            detected = len([r for r in at_samples if r.detected])
            total = len(at_samples)
            by_attack_type[at] = {
                'total': total,
                'detected': detected,
                'rate': round(detected / total if total > 0 else 0, 3)
            }
        
        # 按难度统计
        by_difficulty = {}
        for diff in ['easy', 'medium', 'hard']:
            diff_samples = [r for r in malicious if r.difficulty == diff]
            if diff_samples:
                detected = len([r for r in diff_samples if r.detected])
                total = len(diff_samples)
                by_difficulty[diff] = {
                    'total': total,
                    'detected': detected,
                    'rate': round(detected / total, 3)
                }
        
        # 按语言统计
        by_language = {}
        languages = set(r.language for r in results)
        for lang in languages:
            lang_samples = [r for r in results if r.language == lang]
            mal = [r for r in lang_samples if r.category == 'malicious']
            ben = [r for r in lang_samples if r.category == 'benign']
            mal_det = len([r for r in mal if r.detected])
            ben_fp = len([r for r in ben if r.detected])
            by_language[lang] = {
                'malicious': {'total': len(mal), 'detected': mal_det},
                'benign': {'total': len(ben), 'false_positives': ben_fp}
            }
        
        return BenchmarkReport(
            timestamp=datetime.now().isoformat(),
            total_samples=len(results),
            malicious_samples=len(malicious),
            benign_samples=len(benign),
            detected_malicious=detected_mal,
            false_positives=fp,
            detection_rate=round(det_rate, 3),
            false_positive_rate=round(fp_rate, 3),
            precision=round(precision, 3),
            recall=round(recall, 3),
            f1_score=round(f1, 3),
            by_attack_type=by_attack_type,
            by_difficulty=by_difficulty,
            by_language=by_language,
            yara_rules_used=self.scanner.rule_count,
        )


def main():
    parser = argparse.ArgumentParser(description='Benchmark Suite v3 - 使用 YARA 规则')
    parser.add_argument('--samples', default='benchmark_samples', help='样本目录')
    parser.add_argument('--rules', default='rules/scanner_v3/yara/', help='YARA 规则目录')
    parser.add_argument('--output', default='benchmark_result_v3.json', help='输出文件')
    args = parser.parse_args()
    
    print("="*70)
    print("📊 BENCHMARK SUITE v3 - YARA Rules")
    print("="*70)
    print(f"Samples directory: {args.samples}")
    print(f"Rules directory: {args.rules}")
    print(f"YARA available: {YARA_AVAILABLE}")
    
    runner = BenchmarkRunner(args.samples, args.rules)
    report = runner.run()
    
    # 打印报告
    print("\n" + "="*70)
    print("📊 BENCHMARK RESULTS v3")
    print("="*70)
    print(f"\nYARA Rules Loaded: {report.yara_rules_used}")
    print(f"\n📈 OVERALL METRICS")
    print(f"  Total Samples:     {report.total_samples}")
    print(f"  Malicious:         {report.malicious_samples}")
    print(f"  Benign:            {report.benign_samples}")
    print(f"\n  Detection Rate:    {report.detection_rate:.1%}")
    print(f"  False Positive:    {report.false_positive_rate:.1%}")
    print(f"  Precision:         {report.precision:.1%}")
    print(f"  Recall:            {report.recall:.1%}")
    print(f"  F1 Score:          {report.f1_score:.1%}")
    
    print(f"\n📈 BY DIFFICULTY")
    for diff, data in sorted(report.by_difficulty.items()):
        print(f"  {diff:8s}: {data['detected']:3d}/{data['total']:3d} = {data['rate']:5.1%}")
    
    print(f"\n📈 BY ATTACK TYPE")
    for at, data in sorted(report.by_attack_type.items(), key=lambda x: x[1]['rate'], reverse=True):
        print(f"  {at:25s}: {data['detected']:2d}/{data['total']:2d} = {data['rate']:5.1%}")
    
    print(f"\n📈 BY LANGUAGE")
    for lang, data in sorted(report.by_language.items()):
        mal_rate = data['malicious']['detected'] / data['malicious']['total'] if data['malicious']['total'] > 0 else 0
        fp_rate = data['benign']['false_positives'] / data['benign']['total'] if data['benign']['total'] > 0 else 0
        print(f"  {lang:12s}: Mal {data['malicious']['detected']:2d}/{data['malicious']['total']:2d} ({mal_rate:5.1%}) | Ben FP {data['benign']['false_positives']:2d}/{data['benign']['total']:2d} ({fp_rate:5.1%})")
    
    # 保存结果
    output_path = Path(args.output)
    output_path.write_text(json.dumps(report.to_dict(), indent=2))
    print(f"\n✅ Results saved to {output_path}")
    print("="*70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
