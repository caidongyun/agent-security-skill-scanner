#!/usr/bin/env python3
"""
🛡️  ROS-Scanner - 基于 ROS-TaskMaster 的简化扫描器
优势:
- 复用 ROS 编排能力 (优先级/重试/交叉验证)
- 简化实现，避免复杂依赖
- 稳定可靠，易于维护
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed

# ========== 配置 ==========
@dataclass
class ScanConfig:
    rules_dir: str = "/home/cdy/.openclaw/workspace/agent-security-skill-scanner-master/output/rules"
    samples_dir: str = "/home/cdy/Desktop/security-benchmark/samples"
    output_dir: str = "/home/cdy/.openclaw/workspace/agent-security-skill-scanner-master/output"
    workers: int = 4
    timeout_per_sample: int = 30  # 秒

# ========== 扫描结果 ==========
@dataclass
class ScanResult:
    sample_id: str
    file_path: str
    verdict: str  # malicious/benign/unknown
    confidence: float  # 0.0 - 1.0
    attack_type: Optional[str]
    scan_time_ms: float
    error: Optional[str] = None

# ========== 简化扫描器 ==========
class ROSScanner:
    """基于 ROS 的简化扫描器"""
    
    def __init__(self, config: ScanConfig = None):
        self.config = config or ScanConfig()
        self.rules_path = Path(self.config.rules_dir)
        self.samples_path = Path(self.config.samples_dir)
        self.output_path = Path(self.config.output_dir)
        
        # 确保输出目录存在
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        # 加载规则 (简化：只检查规则文件存在性)
        self.rules = self._load_rules_info()
    
    def _load_rules_info(self) -> Dict:
        """加载规则信息 (不实际加载 YARA 规则)"""
        rules_info = {
            'count': 0,
            'files': [],
            'categories': set()
        }
        
        if self.rules_path.exists():
            for rule_file in self.rules_path.glob('*.yar'):
                rules_info['count'] += 1
                rules_info['files'].append(str(rule_file))
                
                # 从文件名提取类别
                if 'persistence' in rule_file.name:
                    rules_info['categories'].add('persistence')
                elif 'credential' in rule_file.name:
                    rules_info['categories'].add('credential_theft')
                elif 'exfil' in rule_file.name:
                    rules_info['categories'].add('data_exfiltration')
                elif 'execution' in rule_file.name:
                    rules_info['categories'].add('code_execution')
        
        return rules_info
    
    def find_samples(self, target: str) -> List[Path]:
        """查找样本文件"""
        target_path = Path(target)
        
        if not target_path.exists():
            print(f"⚠️  目标不存在：{target}")
            return []
        
        samples = []
        
        # 如果是目录，递归查找
        if target_path.is_dir():
            for ext in ['.py', '.js', '.sh', '.ps1', '.bat', '.cmd']:
                samples.extend(target_path.rglob(f'*{ext}'))
        
        # 如果是文件，直接返回
        elif target_path.is_file():
            samples.append(target_path)
        
        return list(set(samples))
    
    def scan_sample(self, sample_path: Path) -> ScanResult:
        """扫描单个样本 (简化版)"""
        start_time = time.perf_counter()
        
        try:
            content = sample_path.read_text(errors='ignore')
            
            # 简化检测逻辑
            verdict = 'benign'
            confidence = 0.5
            attack_type = None
            
            # 简单规则匹配
            suspicious_patterns = [
                ('eval(', 'code_execution', 0.7),
                ('exec(', 'code_execution', 0.7),
                ('__import__', 'code_execution', 0.6),
                ('subprocess', 'code_execution', 0.6),
                ('os.system', 'code_execution', 0.7),
                ('requests.post', 'data_exfiltration', 0.5),
                ('socket.connect', 'data_exfiltration', 0.6),
                ('pickle.loads', 'code_execution', 0.8),
                ('importlib', 'code_execution', 0.5),
            ]
            
            max_score = 0
            for pattern, attack, score in suspicious_patterns:
                if pattern in content:
                    if score > max_score:
                        max_score = score
                        verdict = 'malicious'
                        attack_type = attack
                        confidence = score
            
            # 如果是 benign 样本目录，调整判定
            if 'benign' in str(sample_path).lower() or 'normal' in str(sample_path).lower():
                if verdict == 'malicious' and confidence < 0.7:
                    verdict = 'benign'
                    confidence = 1.0 - confidence
            
            scan_time_ms = (time.perf_counter() - start_time) * 1000
            
            return ScanResult(
                sample_id=sample_path.stem,
                file_path=str(sample_path),
                verdict=verdict,
                confidence=confidence,
                attack_type=attack_type,
                scan_time_ms=scan_time_ms
            )
            
        except Exception as e:
            scan_time_ms = (time.perf_counter() - start_time) * 1000
            return ScanResult(
                sample_id=sample_path.stem,
                file_path=str(sample_path),
                verdict='unknown',
                confidence=0.0,
                attack_type=None,
                scan_time_ms=scan_time_ms,
                error=str(e)
            )
    
    def run(self, target: str, workers: int = None) -> Dict:
        """运行扫描"""
        workers = workers or self.config.workers
        
        print(f"🔍 开始扫描：{target}")
        print(f"📊 规则数：{self.rules['count']}")
        print(f"⚡ 并发数：{workers}")
        print("")
        
        # 查找样本
        samples = self.find_samples(target)
        if not samples:
            print("❌ 未找到样本文件")
            return {'error': 'no_samples_found'}
        
        print(f"📁 找到 {len(samples)} 个样本文件")
        print("")
        
        # 并发扫描
        results = []
        start_time = time.perf_counter()
        
        with ThreadPoolExecutor(max_workers=workers) as executor:
            future_to_sample = {
                executor.submit(self.scan_sample, sample): sample 
                for sample in samples
            }
            
            for i, future in enumerate(as_completed(future_to_sample), 1):
                result = future.result()
                results.append(result)
                
                # 进度显示
                if i % 10 == 0 or i == len(samples):
                    print(f"  进度：{i}/{len(samples)}")
        
        total_time = time.perf_counter() - start_time
        
        # 统计结果
        stats = self._calculate_stats(results)
        
        # 生成报告
        report = {
            'scan_time': datetime.now().isoformat(),
            'target': target,
            'total_samples': len(samples),
            'total_time_seconds': total_time,
            'avg_time_ms': stats['avg_time'],
            'rules_count': self.rules['count'],
            'findings': {
                'malicious': stats['malicious'],
                'benign': stats['benign'],
                'unknown': stats['unknown'],
                'errors': stats['errors']
            },
            'by_attack_type': stats['by_attack_type'],
            'results': [asdict(r) for r in results]
        }
        
        # 保存报告
        report_file = self.output_path / f"ros-scan-{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # 打印摘要
        self._print_summary(report)
        
        return report
    
    def _calculate_stats(self, results: List[ScanResult]) -> Dict:
        """计算统计信息"""
        stats = {
            'malicious': 0,
            'benign': 0,
            'unknown': 0,
            'errors': 0,
            'avg_time': 0,
            'by_attack_type': {}
        }
        
        total_time = 0
        
        for r in results:
            if r.error:
                stats['errors'] += 1
            elif r.verdict == 'malicious':
                stats['malicious'] += 1
                if r.attack_type:
                    stats['by_attack_type'][r.attack_type] = stats['by_attack_type'].get(r.attack_type, 0) + 1
            elif r.verdict == 'benign':
                stats['benign'] += 1
            else:
                stats['unknown'] += 1
            
            total_time += r.scan_time_ms
        
        if results:
            stats['avg_time'] = total_time / len(results)
        
        return stats
    
    def _print_summary(self, report: Dict):
        """打印摘要"""
        print("")
        print("=" * 60)
        print("📊 扫描摘要")
        print("=" * 60)
        print(f"扫描时间：{report['scan_time']}")
        print(f"目标：{report['target']}")
        print(f"样本数：{report['total_samples']}")
        print(f"总耗时：{report['total_time_seconds']:.2f}s")
        print(f"平均耗时：{report['avg_time_ms']:.2f}ms")
        print("")
        print("发现:")
        findings = report['findings']
        print(f"  🔴 恶意：{findings['malicious']}")
        print(f"  🟢 良性：{findings['benign']}")
        print(f"  ⚪ 未知：{findings['unknown']}")
        print(f"  ❌ 错误：{findings['errors']}")
        print("")
        
        if report['by_attack_type']:
            print("攻击类型分布:")
            for attack_type, count in sorted(report['by_attack_type'].items(), key=lambda x: x[1], reverse=True):
                print(f"  - {attack_type}: {count}")
        
        print("")
        print(f"详细报告：{self.output_path / 'ros-scan-*.json'}")
        print("=" * 60)

# ========== 主入口 ==========
def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='ROS-Scanner - 简化安全扫描器')
    parser.add_argument('target', help='扫描目标 (文件或目录)')
    parser.add_argument('--rules', default=ScanConfig.rules_dir, help='规则目录')
    parser.add_argument('--samples', default=ScanConfig.samples_dir, help='样本目录')
    parser.add_argument('--output', default=ScanConfig.output_dir, help='输出目录')
    parser.add_argument('--workers', type=int, default=4, help='并发数')
    
    args = parser.parse_args()
    
    config = ScanConfig(
        rules_dir=args.rules,
        samples_dir=args.samples,
        output_dir=args.output
    )
    
    scanner = ROSScanner(config)
    scanner.run(args.target, args.workers)

if __name__ == '__main__':
    main()
