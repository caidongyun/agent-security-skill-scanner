#!/usr/bin/env python3
"""
扫描器集成 - Integration Scanner v2.0

功能:
- 扫描生成的样本
- 使用 YARA 规则检测
- 计算检测率/误报率
- 生成扫描报告
"""

import json
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class ScanResult:
    """扫描结果"""
    file_path: str
    detected: bool
    matched_rules: List[str] = field(default_factory=list)
    scan_time_ms: float = 0.0
    error: str = ""


@dataclass
class ScanReport:
    """扫描报告"""
    timestamp: str
    total_samples: int
    detected_samples: int
    missed_samples: int
    detection_rate: float
    false_positive_rate: float
    results: List[ScanResult] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            'timestamp': self.timestamp,
            'total_samples': self.total_samples,
            'detected_samples': self.detected_samples,
            'missed_samples': self.missed_samples,
            'detection_rate': self.detection_rate,
            'false_positive_rate': self.false_positive_rate,
            'results': [
                {
                    'file': r.file_path,
                    'detected': r.detected,
                    'rules': r.matched_rules,
                    'time_ms': r.scan_time_ms,
                    'error': r.error
                }
                for r in self.results
            ]
        }


class IntegrationScanner:
    """集成扫描器"""
    
    def __init__(self, yara_rules_path: str, samples_path: str):
        self.yara_rules_path = Path(yara_rules_path)
        self.samples_path = Path(samples_path)
        self.results = []
    
    def scan_with_yara(self, sample_path: Path, rules_path: Path) -> ScanResult:
        """使用 YARA 扫描单个样本"""
        import time
        start_time = time.time()
        
        try:
            # 尝试使用 yara-python
            try:
                import yara
                
                # 编译规则
                if rules_path.is_file():
                    rules = yara.compile(str(rules_path))
                else:
                    # 合并所有规则
                    all_rules = ""
                    for rule_file in rules_path.glob('*.yar'):
                        all_rules += rule_file.read_text() + "\n\n"
                    rules = yara.compile(source=all_rules)
                
                # 扫描
                matches = rules.match(str(sample_path))
                
                scan_time = (time.time() - start_time) * 1000
                
                matched_rules = [m.rule for m in matches]
                
                return ScanResult(
                    file_path=str(sample_path),
                    detected=len(matches) > 0,
                    matched_rules=matched_rules,
                    scan_time_ms=scan_time
                )
                
            except ImportError:
                # yara-python 未安装，尝试命令行 yara
                return self._scan_with_yara_cli(sample_path, rules_path, start_time)
                
        except Exception as e:
            return ScanResult(
                file_path=str(sample_path),
                detected=False,
                error=str(e)
            )
    
    def _scan_with_yara_cli(self, sample_path: Path, rules_path: Path, start_time: float) -> ScanResult:
        """使用命令行 YARA 扫描"""
        try:
            result = subprocess.run(
                ['yara', str(rules_path), str(sample_path)],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            scan_time = (time.time() - start_time) * 1000
            
            if result.returncode == 0:
                matched_rules = []
                for line in result.stdout.strip().split('\n'):
                    if line:
                        rule_name = line.split()[0]
                        matched_rules.append(rule_name)
                
                return ScanResult(
                    file_path=str(sample_path),
                    detected=len(matched_rules) > 0,
                    matched_rules=matched_rules,
                    scan_time_ms=scan_time
                )
            else:
                return ScanResult(
                    file_path=str(sample_path),
                    detected=False,
                    scan_time_ms=scan_time,
                    error=result.stderr
                )
                
        except FileNotFoundError:
            # YARA 未安装，回退到简单模式匹配
            return self._scan_with_regex(sample_path, start_time)
        except Exception as e:
            return ScanResult(
                file_path=str(sample_path),
                detected=False,
                error=str(e)
            )
    
    def _scan_with_regex(self, sample_path: Path, start_time: float) -> ScanResult:
        """使用正则表达式扫描 (回退方案)"""
        import re
        
        try:
            content = sample_path.read_text(encoding='utf-8')
            
            # 简单模式匹配
            patterns = {
                'Malicious_Import': r'import\s+(subprocess|socket|base64)',
                'Dangerous_Function': r'(eval|exec|system|popen)\s*\(',
                'SSH_Access': r'\.ssh',
                'Credential_Theft': r'(credential|password|secret)',
                'Data_Exfil': r'(exfil|steal|collect).*(data|info)',
            }
            
            matched_rules = []
            for rule_name, pattern in patterns.items():
                if re.search(pattern, content, re.IGNORECASE):
                    matched_rules.append(rule_name)
            
            scan_time = (time.time() - start_time) * 1000
            
            return ScanResult(
                file_path=str(sample_path),
                detected=len(matched_rules) > 0,
                matched_rules=matched_rules,
                scan_time_ms=scan_time
            )
            
        except Exception as e:
            return ScanResult(
                file_path=str(sample_path),
                detected=False,
                error=str(e)
            )
    
    def scan_samples(self) -> List[ScanResult]:
        """扫描所有样本"""
        results = []
        
        # 扫描恶意样本
        for sample_file in self.samples_path.glob('*.py'):
            result = self.scan_with_yara(sample_file, self.yara_rules_path)
            results.append(result)
        
        self.results = results
        return results
    
    def calculate_metrics(self, results: List[ScanResult]) -> Dict:
        """计算检测指标"""
        total = len(results)
        detected = sum(1 for r in results if r.detected)
        missed = total - detected
        
        detection_rate = (detected / max(total, 1)) * 100
        
        # 误报率需要白样本，这里先设为 0
        false_positive_rate = 0.0
        
        return {
            'total': total,
            'detected': detected,
            'missed': missed,
            'detection_rate': detection_rate,
            'false_positive_rate': false_positive_rate,
        }
    
    def generate_report(self, output_path: Path) -> ScanReport:
        """生成扫描报告"""
        if not self.results:
            self.scan_samples()
        
        metrics = self.calculate_metrics(self.results)
        
        report = ScanReport(
            timestamp=datetime.now().isoformat(),
            total_samples=metrics['total'],
            detected_samples=metrics['detected'],
            missed_samples=metrics['missed'],
            detection_rate=metrics['detection_rate'],
            false_positive_rate=metrics['false_positive_rate'],
            results=self.results
        )
        
        # 保存报告
        self._save_report(report, output_path)
        
        return report
    
    def _save_report(self, report: ScanReport, output_path: Path) -> None:
        """保存报告"""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # JSON 格式
        json_path = output_path.with_suffix('.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(report.to_dict(), f, indent=2, ensure_ascii=False)
        
        # Markdown 格式
        md_path = output_path.with_suffix('.md')
        md_content = self._report_to_markdown(report)
        md_path.write_text(md_content, encoding='utf-8')
    
    def _report_to_markdown(self, report: ScanReport) -> str:
        """转换为 Markdown"""
        lines = [
            "# 扫描检测报告",
            "",
            f"**生成时间**: {report.timestamp}",
            "",
            "## 📊 汇总",
            "",
            f"- 总样本数：{report.total_samples}",
            f"- 检出数：{report.detected_samples}",
            f"- 漏检数：{report.missed_samples}",
            f"- **检测率**: {report.detection_rate:.1f}%",
            f"- 误报率：{report.false_positive_rate:.1f}%",
            "",
            "## 🎯 质量评估",
            "",
        ]
        
        # 质量评估
        if report.detection_rate >= 95:
            lines.append("✅ **优秀**: 检测率 ≥95%")
        elif report.detection_rate >= 90:
            lines.append("✅ **良好**: 检测率 ≥90%")
        elif report.detection_rate >= 80:
            lines.append("⚠️ **合格**: 检测率 ≥80%")
        else:
            lines.append("❌ **需改进**: 检测率 <80%")
        
        lines.extend([
            "",
            "## 🔍 详细结果",
            "",
            "| 文件 | 状态 | 匹配规则 | 耗时 (ms) |",
            "|------|------|----------|-----------|",
        ])
        
        # 按检出/漏检分组
        detected_results = [r for r in report.results if r.detected]
        missed_results = [r for r in report.results if not r.detected]
        
        # 显示前 10 个检出的
        for r in detected_results[:10]:
            filename = Path(r.file_path).name
            rules = ', '.join(r.matched_rules[:3])
            if len(r.matched_rules) > 3:
                rules += f" (+{len(r.matched_rules)-3})"
            status = '✅'
            lines.append(f"| {filename} | {status} | {rules} | {r.scan_time_ms:.1f} |")
        
        if len(detected_results) > 10:
            lines.append(f"| ... | | 还有 {len(detected_results)-10} 个检出 | |")
        
        # 显示所有漏检的
        if missed_results:
            lines.append("")
            lines.append("### ❌ 漏检样本")
            lines.append("")
            for r in missed_results:
                filename = Path(r.file_path).name
                error = r.error[:50] if r.error else "未知原因"
                lines.append(f"| {filename} | ❌ | - | {r.scan_time_ms:.1f} |")
                if r.error:
                    lines.append(f"| | | `{error}` | |")
        
        lines.extend([
            "",
            "## 💡 建议",
            "",
        ])
        
        if report.detection_rate < 90:
            lines.append("1. 增加 YARA 规则覆盖范围")
            lines.append("2. 优化现有规则的模式匹配")
            lines.append("3. 分析漏检样本特征，添加针对性规则")
        elif report.detection_rate < 95:
            lines.append("1. 分析漏检样本，补充规则")
            lines.append("2. 考虑增加规则字符串数量")
        else:
            lines.append("✅ 检测率优秀，保持现有规则质量")
        
        lines.append("")
        return '\n'.join(lines)


def main():
    """CLI 入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='集成扫描器')
    parser.add_argument('--rules', '-r', default='output/rules/python_all.yar',
                       help='YARA 规则文件/目录')
    parser.add_argument('--samples', '-s', default='output/samples/python',
                       help='样本目录')
    parser.add_argument('--output', '-o', default='reports/scan_results',
                       help='输出报告路径')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='详细输出')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("集成扫描器 v2.0")
    print("=" * 60)
    print()
    
    rules_path = Path(args.rules)
    samples_path = Path(args.samples)
    
    print(f"📂 规则路径：{rules_path}")
    print(f"📂 样本路径：{samples_path}")
    print()
    
    # 检查路径
    if not samples_path.exists():
        print(f"❌ 样本目录不存在：{samples_path}")
        return 1
    
    if not rules_path.exists():
        print(f"❌ 规则文件/目录不存在：{rules_path}")
        return 1
    
    # 创建扫描器
    scanner = IntegrationScanner(str(rules_path), str(samples_path))
    
    # 扫描
    print("🔍 开始扫描...")
    print()
    
    results = scanner.scan_samples()
    
    # 进度显示
    detected = sum(1 for r in results if r.detected)
    total = len(results)
    print(f"  已扫描：{total}/{total}")
    print(f"  检出：{detected}")
    print(f"  漏检：{total - detected}")
    print()
    
    # 生成报告
    output_path = Path(args.output)
    print(f"📝 生成报告：{output_path}")
    report = scanner.generate_report(output_path)
    
    # 输出摘要
    print()
    print("=" * 60)
    print("扫描完成!")
    print("=" * 60)
    print()
    print(f"📊 检测率：{report.detection_rate:.1f}%")
    print(f"✅ 检出：{report.detected_samples}/{report.total_samples}")
    print(f"❌ 漏检：{report.missed_samples}")
    print()
    
    # 质量评估
    if report.detection_rate >= 95:
        print("🎯 质量评估：✅ 优秀 (≥95%)")
    elif report.detection_rate >= 90:
        print("🎯 质量评估：✅ 良好 (≥90%)")
    elif report.detection_rate >= 80:
        print("🎯 质量评估：⚠️ 合格 (≥80%)")
    else:
        print("🎯 质量评估：❌ 需改进 (<80%)")
    
    print()
    print(f"💾 报告已保存:")
    print(f"   JSON: {output_path.with_suffix('.json')}")
    print(f"   Markdown: {output_path.with_suffix('.md')}")
    print()
    
    # 返回码
    if report.detection_rate >= 80:
        return 0
    else:
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(main())
