#!/usr/bin/env python3
"""
🛡️ 终极全量扫描器 V2 - 使用 benchmark_v3.py 的规则加载策略
单独编译每个规则文件，跳过有问题的文件
"""

import os
import sys
import json
import time
import argparse
import yara
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict, field
from concurrent.futures import ThreadPoolExecutor, as_completed
import statistics

@dataclass
class ScanResult:
    sample_path: str
    is_malicious: bool
    matched_rules: List[str] = field(default_factory=list)
    scan_time_ms: float = 0.0

class RobustYaraScanner:
    """健壮的 YARA 扫描器 - 单独编译每个规则文件"""
    
    def __init__(self, rules_dir: str):
        self.rules_path = Path(rules_dir)
        self.compiled_rules = None
        self.rule_count = 0
        self.skipped_files = []
        self._load_rules()
    
    def _load_rules(self):
        """加载并编译规则"""
        if not self.rules_path.exists():
            raise FileNotFoundError(f"规则目录不存在：{self.rules_path}")
        
        all_rules = ""
        
        for ext in ['*.yaml', '*.yar', '*.yara']:
            for rf in self.rules_path.glob(ext):
                try:
                    content = rf.read_text(encoding='utf-8', errors='ignore')
                    content = content.encode('ascii', 'ignore').decode('ascii')
                    
                    if 'rule ' in content:
                        try:
                            # 单独编译每个文件
                            yara.compile(source=content)
                            all_rules += content + "\n\n"
                        except Exception as file_err:
                            self.skipped_files.append((rf.name, str(file_err)[:80]))
                except Exception as e:
                    print(f"⚠️  跳过文件 {rf.name}: {e}")
        
        # 报告跳过的文件
        if self.skipped_files:
            print(f"⚠️  跳过 {len(self.skipped_files)} 个有问题的规则文件:")
            for fname, err in self.skipped_files[:5]:
                print(f"    - {fname}: {err}")
        
        if all_rules:
            self.compiled_rules = yara.compile(source=all_rules)
            self.rule_count = all_rules.count('\nrule ') + all_rules.count('rule ')
            print(f"✅ 编译完成：{self.rule_count} 条 YARA 规则")
        else:
            raise ValueError("没有找到有效的 YARA 规则")
    
    def scan(self, file_path: str) -> Tuple[bool, List[str], float]:
        """扫描单个文件"""
        start = time.perf_counter()
        try:
            matches = self.compiled_rules.match(file_path)
            is_malicious = len(matches) > 0
            matched_rules = [m.rule for m in matches]
        except Exception as e:
            is_malicious = False
            matched_rules = []
        
        duration = (time.perf_counter() - start) * 1000
        return is_malicious, matched_rules, duration

def scan_sample(scanner: RobustYaraScanner, sample_path: str) -> ScanResult:
    """扫描单个样本"""
    is_malicious, matched_rules, duration = scanner.scan(sample_path)
    return ScanResult(
        sample_path=sample_path,
        is_malicious=is_malicious,
        matched_rules=matched_rules,
        scan_time_ms=duration
    )

def scan_directory(scanner: RobustYaraScanner, samples_dir: str, workers: int = 8) -> Tuple[List[ScanResult], float]:
    """并发扫描目录"""
    samples_path = Path(samples_dir)
    if not samples_path.exists():
        raise FileNotFoundError(f"样本目录不存在：{samples_path}")
    
    # 收集所有样本文件
    extensions = {'.py', '.js', '.sh', '.ps1', '.bat', '.cmd', '.vbs', '.lua'}
    sample_files = []
    for ext in extensions:
        sample_files.extend(samples_path.rglob(f"*{ext}"))
    
    # 去重
    sample_files = list(set(sample_files))
    
    print(f"📂 找到 {len(sample_files)} 个样本文件")
    print(f"⚡ 启动 {workers} 线程并发扫描...")
    
    start_time = time.perf_counter()
    results = []
    
    # 由于 yara.Rules 对象不能跨线程共享，我们创建每个线程的扫描器
    def scan_worker(file_path: str) -> ScanResult:
        # 每个线程重新加载规则（有点慢但安全）
        thread_scanner = RobustYaraScanner(str(scanner.rules_path))
        return scan_sample(thread_scanner, file_path)
    
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(scan_worker, str(f)): f for f in sample_files}
        
        for i, future in enumerate(as_completed(futures)):
            try:
                result = future.result()
                results.append(result)
                
                if (i + 1) % 50 == 0:
                    print(f"  已扫描 {i+1}/{len(sample_files)} ...")
            except Exception as e:
                print(f"⚠️  扫描错误：{e}")
    
    total_time = time.perf_counter() - start_time
    return results, total_time

def generate_report(results: List[ScanResult], total_time: float, output_file: str):
    """生成扫描报告"""
    total = len(results)
    malicious = sum(1 for r in results if r.is_malicious)
    benign = total - malicious
    
    detection_rate = malicious / total if total > 0 else 0
    avg_time = statistics.mean([r.scan_time_ms for r in results]) if results else 0
    
    # 统计规则匹配次数
    rule_counts = {}
    for r in results:
        for rule in r.matched_rules:
            rule_counts[rule] = rule_counts.get(rule, 0) + 1
    
    # 排序
    top_rules = sorted(rule_counts.items(), key=lambda x: x[1], reverse=True)[:20]
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "total_samples": total,
        "malicious_count": malicious,
        "benign_count": benign,
        "detection_rate": detection_rate,
        "detection_rate_percent": f"{detection_rate * 100:.1f}%",
        "scan_time_seconds": round(total_time, 3),
        "avg_time_ms": round(avg_time, 3),
        "throughput_samples_per_sec": round(total / total_time, 1) if total_time > 0 else 0,
        "top_matched_rules": dict(top_rules),
    }
    
    # 保存 JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    # 显示摘要
    print("\n" + "=" * 70)
    print("📊 扫描结果")
    print("=" * 70)
    print(f"✅ 扫描样本：{total} 个")
    print(f"🔴 恶意样本：{malicious} ({detection_rate * 100:.1f}%)")
    print(f"🟢 安全样本：{benign} ({(1 - detection_rate) * 100:.1f}%)")
    print(f"⚡ 扫描耗时：{total_time:.3f} 秒")
    print(f"⚡ 平均耗时：{avg_time:.3f} ms/样本")
    print(f"⚡ 吞吐量：{total / total_time:.1f} 样本/秒")
    
    if top_rules:
        print("\n📋 Top 10 规则匹配:")
        for rule, count in top_rules[:10]:
            print(f"   {rule}: {count} 次")
    
    print(f"\n💾 报告已保存：{output_file}")
    
    # 评估
    print("\n" + "=" * 70)
    if detection_rate >= 0.95:
        print("✅ 检测能力：优秀 (≥95%)")
    elif detection_rate >= 0.90:
        print("✅ 检测能力：良好 (≥90%)")
    elif detection_rate >= 0.80:
        print("⚠️  检测能力：一般 (≥80%)")
    else:
        print("❌ 检测能力：不足 (<80%) - 需要优化规则")
    print("=" * 70)

def main():
    parser = argparse.ArgumentParser(description='🛡️ 终极全量扫描器 V2')
    parser.add_argument('--samples', default='samples', help='样本目录')
    parser.add_argument('--rules', default='rules/scanner_v3/yara', help='规则目录')
    parser.add_argument('--output', default=None, help='输出报告文件')
    parser.add_argument('--workers', type=int, default=4, help='并发数')
    
    args = parser.parse_args()
    
    script_dir = Path(__file__).parent
    samples_dir = script_dir / args.samples if not Path(args.samples).is_absolute() else Path(args.samples)
    rules_dir = script_dir / args.rules if not Path(args.rules).is_absolute() else Path(args.rules)
    
    output_file = args.output or f"reports/ultimate_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    print("=" * 70)
    print("🛡️  终极全量扫描器 V2 - 最高检测能力")
    print("=" * 70)
    print(f"📂 样本目录：{samples_dir}")
    print(f"📚 规则目录：{rules_dir}")
    print(f"💾 输出文件：{output_file}")
    print()
    
    # 加载规则
    scanner = RobustYaraScanner(str(rules_dir))
    
    # 扫描
    results, total_time = scan_directory(scanner, str(samples_dir), args.workers)
    
    # 生成报告
    generate_report(results, total_time, output_file)

if __name__ == '__main__':
    main()
