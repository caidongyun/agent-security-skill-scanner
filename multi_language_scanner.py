#!/usr/bin/env python3
"""
Scanner V3 - 多语言统一检测器 (Round 23)

整合 Python/JavaScript/Shell/PowerShell 检测器
提供统一的扫描接口和批量处理能力
"""

import sys
import json
import time
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# 导入各语言检测器
sys.path.insert(0, str(Path(__file__).parent))

try:
    from round16.ast_engine import ASTScanner, ObfuscationDetector
except ImportError:
    ASTScanner = None
    ObfuscationDetector = None

try:
    from round20.js_analyzer import JSAnalyzer
except ImportError:
    JSAnalyzer = None

@dataclass
class ScanResult:
    """单个文件扫描结果"""
    file_path: str
    language: str
    is_malicious: bool
    risk_score: float
    risk_level: str
    behaviors: List[str] = field(default_factory=list)
    mitre_techniques: List[str] = field(default_factory=list)
    details: str = ""
    scan_time_ms: float = 0.0

@dataclass
class BatchScanReport:
    """批量扫描报告"""
    total_files: int
    malicious_files: int
    safe_files: int
    detection_rate: float
    scan_time_seconds: float
    by_language: Dict[str, Dict]
    by_risk_level: Dict[str, int]
    top_threats: List[Dict]
    timestamp: str

class MultiLanguageScanner:
    """多语言统一扫描器"""
    
    def __init__(self):
        # 初始化各语言检测器
        self.python_detector = ASTScanner() if ASTScanner else None
        self.js_analyzer = JSAnalyzer() if JSAnalyzer else None
        self.shell_analyzer = None  # ShellAnalyzer() - not available
        self.ps_analyzer = None  # PowerShellAnalyzer() - not available
        
        # 文件扩展名映射
        self.lang_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'javascript',
            '.tsx': 'javascript',
            '.sh': 'shell',
            '.bash': 'shell',
            '.zsh': 'shell',
            '.ps1': 'powershell',
            '.psm1': 'powershell',
            '.psd1': 'powershell',
        }
        
        # 统计信息
        self.stats = {
            'python': {'total': 0, 'malicious': 0},
            'javascript': {'total': 0, 'malicious': 0},
            'shell': {'total': 0, 'malicious': 0},
            'powershell': {'total': 0, 'malicious': 0},
            'unknown': {'total': 0, 'malicious': 0},
        }
    
    def detect_language(self, file_path: str) -> str:
        """检测文件语言"""
        path = Path(file_path)
        ext = path.suffix.lower()
        return self.lang_map.get(ext, 'unknown')
    
    def scan_file(self, file_path: str) -> ScanResult:
        """扫描单个文件"""
        start_time = time.time()
        
        path = Path(file_path)
        if not path.exists():
            return ScanResult(
                file_path=str(file_path),
                language='unknown',
                is_malicious=False,
                risk_score=0,
                risk_level='error',
                details='File not found'
            )
        
        # 检测语言
        language = self.detect_language(str(path))
        
        if language == 'unknown':
            return ScanResult(
                file_path=str(file_path),
                language='unknown',
                is_malicious=False,
                risk_score=0,
                risk_level='safe',
                details='Unsupported language'
            )
        
        # 读取文件
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                code = f.read()
        except Exception as e:
            return ScanResult(
                file_path=str(file_path),
                language=language,
                is_malicious=False,
                risk_score=0,
                risk_level='error',
                details=f'Read error: {str(e)}'
            )
        
        # 调用对应语言的检测器
        if language == 'python':
            result = self.python_detector.analyze_code(code, str(path))
            scan_result = ScanResult(
                file_path=str(file_path),
                language=language,
                is_malicious=result.is_malicious,
                risk_score=result.risk_score,
                risk_level=result.risk_level.value,
                behaviors=result.behaviors,
                mitre_techniques=result.mitre_techniques,
                details=result.details
            )
        
        elif language == 'javascript':
            result = self.js_analyzer.analyze_code(code, str(path))
            scan_result = ScanResult(
                file_path=str(file_path),
                language=language,
                is_malicious=result.is_malicious,
                risk_score=result.risk_score,
                risk_level=result.risk_level.value,
                behaviors=result.behaviors,
                mitre_techniques=result.mitre_techniques,
                details=result.details
            )
        
        elif language == 'shell':
            result = self.shell_analyzer.analyze(str(path))
            scan_result = ScanResult(
                file_path=str(file_path),
                language=language,
                is_malicious=result.is_malicious,
                risk_score=result.risk_score,
                risk_level=result.risk_level.value,
                behaviors=result.behaviors,
                mitre_techniques=result.mitre_techniques,
                details=result.details
            )
        
        elif language == 'powershell':
            result = self.ps_analyzer.analyze(str(path))
            scan_result = ScanResult(
                file_path=str(file_path),
                language=language,
                is_malicious=result.is_malicious,
                risk_score=result.risk_score,
                risk_level=result.risk_level.value,
                behaviors=result.behaviors,
                mitre_techniques=result.mitre_techniques,
                details=result.details
            )
        
        else:
            scan_result = ScanResult(
                file_path=str(file_path),
                language='unknown',
                is_malicious=False,
                risk_score=0,
                risk_level='safe',
                details='Unsupported language'
            )
        
        # 记录扫描时间
        scan_time_ms = (time.time() - start_time) * 1000
        scan_result.scan_time_ms = round(scan_time_ms, 2)
        
        # 更新统计
        self.stats[language]['total'] += 1
        if scan_result.is_malicious:
            self.stats[language]['malicious'] += 1
        
        return scan_result
    
    def scan_directory(self, dir_path: str, recursive: bool = True, 
                      max_workers: int = 4) -> List[ScanResult]:
        """批量扫描目录"""
        path = Path(dir_path)
        
        if not path.exists():
            print(f"❌ 目录不存在：{dir_path}")
            return []
        
        # 收集所有文件
        files_to_scan = []
        if recursive:
            for ext in self.lang_map.keys():
                files_to_scan.extend(path.glob(f"**/*{ext}"))
        else:
            for ext in self.lang_map.keys():
                files_to_scan.extend(path.glob(f"*{ext}"))
        
        print(f"📁 发现 {len(files_to_scan)} 个文件待扫描")
        
        # 并发扫描
        results = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_file = {executor.submit(self.scan_file, str(f)): f for f in files_to_scan}
            
            for future in as_completed(future_to_file):
                result = future.result()
                results.append(result)
        
        return results
    
    def generate_report(self, results: List[ScanResult], scan_time: float) -> BatchScanReport:
        """生成扫描报告"""
        total = len(results)
        malicious = sum(1 for r in results if r.is_malicious)
        safe = total - malicious
        
        # 按语言统计
        by_language = {}
        for lang in ['python', 'javascript', 'shell', 'powershell', 'unknown']:
            lang_results = [r for r in results if r.language == lang]
            lang_malicious = sum(1 for r in lang_results if r.is_malicious)
            if lang_results:
                by_language[lang] = {
                    'total': len(lang_results),
                    'malicious': lang_malicious,
                    'safe': len(lang_results) - lang_malicious,
                    'detection_rate': round(lang_malicious / len(lang_results) * 100, 1) if lang_results else 0
                }
        
        # 按风险等级统计
        by_risk_level = {}
        for r in results:
            level = r.risk_level
            by_risk_level[level] = by_risk_level.get(level, 0) + 1
        
        # 前 10 大威胁
        malicious_results = [r for r in results if r.is_malicious]
        malicious_results.sort(key=lambda x: x.risk_score, reverse=True)
        top_threats = [asdict(r) for r in malicious_results[:10]]
        
        return BatchScanReport(
            total_files=total,
            malicious_files=malicious,
            safe_files=safe,
            detection_rate=round(malicious / total * 100, 1) if total > 0 else 0,
            scan_time_seconds=round(scan_time, 2),
            by_language=by_language,
            by_risk_level=by_risk_level,
            top_threats=top_threats,
            timestamp=datetime.now().isoformat()
        )
    
    def print_report(self, report: BatchScanReport):
        """打印扫描报告"""
        print("\n" + "=" * 70)
        print("📊 Scanner V3 - 多语言批量扫描报告")
        print("=" * 70)
        
        print(f"\n⏱️  扫描时间：{report.scan_time_seconds} 秒")
        print(f"📁 总文件数：{report.total_files}")
        print(f"🔴 恶意文件：{report.malicious_files}")
        print(f"🟢 安全文件：{report.safe_files}")
        print(f"📈 检测率：{report.detection_rate}%")
        
        print(f"\n📊 按语言统计:")
        for lang, stats in sorted(report.by_language.items()):
            if stats['total'] > 0:
                print(f"   {lang}: {stats['malicious']}/{stats['total']} ({stats['detection_rate']}%)")
        
        print(f"\n⚠️  风险等级分布:")
        for level, count in sorted(report.by_risk_level.items()):
            emoji = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🔵', 'safe': '🟢'}.get(level, '⚪')
            print(f"   {emoji} {level}: {count}")
        
        if report.top_threats:
            print(f"\n🚨 Top 10 威胁:")
            for i, threat in enumerate(report.top_threats, 1):
                print(f"   {i}. {Path(threat['file_path']).name}")
                print(f"      语言：{threat['language']}, 风险：{threat['risk_score']}, 等级：{threat['risk_level']}")
        
        print("\n" + "=" * 70)


def main():
    """主函数 - 测试多语言扫描器"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Scanner V3 - 多语言统一检测器')
    parser.add_argument('path', help='扫描路径 (文件或目录)')
    parser.add_argument('-r', '--recursive', action='store_true', help='递归扫描子目录')
    parser.add_argument('-w', '--workers', type=int, default=4, help='并发工作线程数')
    parser.add_argument('-o', '--output', help='输出报告文件 (JSON)')
    
    args = parser.parse_args()
    
    scanner = MultiLanguageScanner()
    
    print("=" * 70)
    print("🔍 Scanner V3 - 多语言统一检测器")
    print("=" * 70)
    print(f"\n📁 扫描路径：{args.path}")
    print(f"🔄 递归：{args.recursive}")
    print(f"👷 并发数：{args.workers}")
    
    start_time = time.time()
    
    path = Path(args.path)
    if path.is_file():
        # 单文件扫描
        result = scanner.scan_file(str(path))
        print(f"\n📄 文件：{path.name}")
        print(f"   语言：{result.language}")
        print(f"   恶意：{'✅ 是' if result.is_malicious else '❌ 否'}")
        print(f"   风险评分：{result.risk_score}")
        print(f"   风险等级：{result.risk_level}")
        print(f"   扫描时间：{result.scan_time_ms}ms")
        if result.behaviors:
            print(f"   行为：{', '.join(result.behaviors[:3])}")
    else:
        # 目录扫描
        results = scanner.scan_directory(str(path), recursive=args.recursive, max_workers=args.workers)
        scan_time = time.time() - start_time
        report = scanner.generate_report(results, scan_time)
        scanner.print_report(report)
        
        # 保存报告
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(asdict(report), f, indent=2, ensure_ascii=False)
            print(f"\n💾 报告已保存：{args.output}")
    
    print("\n✅ 扫描完成!")


if __name__ == '__main__':
    main()
