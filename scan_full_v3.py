#!/usr/bin/env python3
"""
🛡️ 终极全量扫描器 V3 - YARA + 意图识别 + 智能评分
整合三大检测能力：
1. YARA 规则匹配 (342+ 条规则)
2. 意图识别分析 (降低误报)
3. 智能风险评分 (综合评估)
"""

import os
import sys
import json
import time
import argparse
import yara as yara_lib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict, field
from concurrent.futures import ThreadPoolExecutor, as_completed
import statistics

# 导入意图识别器
sys.path.insert(0, str(Path(__file__).parent))
try:
    from intent_detector_v2 import EnhancedIntentDetector, IntentType
    INTENT_ENABLED = True
except ImportError as e:
    print(f"⚠️  意图识别器不可用：{e}")
    INTENT_ENABLED = False

@dataclass
class ScanResult:
    sample_path: str
    language: str
    is_malicious: bool
    risk_score: float  # 0-100
    risk_level: str    # critical/high/medium/low/safe
    yara_matched: bool
    yara_rules: List[str] = field(default_factory=list)
    intent_detected: Optional[str] = None
    intent_confidence: float = 0.0
    behaviors: List[str] = field(default_factory=list)
    scan_time_ms: float = 0.0

class RobustYaraScanner:
    """健壮的 YARA 扫描器"""
    
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
                            yara_lib.compile(source=content)
                            all_rules += content + "\n\n"
                        except Exception as file_err:
                            self.skipped_files.append((rf.name, str(file_err)[:80]))
                except Exception as e:
                    pass
        
        if self.skipped_files:
            print(f"⚠️  跳过 {len(self.skipped_files)} 个有问题的规则文件")
        
        if all_rules:
            self.compiled_rules = yara_lib.compile(source=all_rules)
            self.rule_count = all_rules.count('\nrule ') + all_rules.count('rule ')
            print(f"✅ YARA 规则：{self.rule_count} 条")
        else:
            raise ValueError("没有找到有效的 YARA 规则")
    
    def scan(self, file_path: str) -> Tuple[bool, List[str]]:
        """扫描单个文件"""
        try:
            matches = self.compiled_rules.match(file_path)
            is_malicious = len(matches) > 0
            matched_rules = [m.rule for m in matches]
            return is_malicious, matched_rules
        except Exception:
            return False, []

class SmartScorer:
    """智能评分器 - 综合 YARA + 意图 + 行为"""
    
    def __init__(self):
        self.intent_detector = EnhancedIntentDetector() if INTENT_ENABLED else None
    
    def detect_language(self, file_path: str) -> str:
        """检测文件语言"""
        ext = Path(file_path).suffix.lower()
        lang_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.sh': 'bash',
            '.ps1': 'powershell',
            '.bat': 'batch',
            '.cmd': 'batch',
            '.vbs': 'vbscript',
            '.lua': 'lua'
        }
        return lang_map.get(ext, 'unknown')
    
    def calculate_risk(self, yara_matched: bool, yara_rules: List[str], 
                       intent_result: Optional[dict], language: str) -> Tuple[float, str, List[str]]:
        """计算综合风险评分 (0-100)"""
        score = 0.0
        behaviors = []
        
        # YARA 规则匹配 (最高 60 分)
        if yara_matched:
            # 根据匹配规则数量和质量评分
            base_score = min(30 + len(yara_rules) * 3, 60)
            score += base_score
            
            # 关键规则加分
            critical_keywords = ['credential', 'exfil', 'backdoor', 'reverse_shell', 'ransomware']
            for rule in yara_rules:
                if any(kw in rule.lower() for kw in critical_keywords):
                    score += 5
                    behaviors.append(f"yara:critical_rule:{rule}")
                else:
                    behaviors.append(f"yara:{rule}")
        else:
            # 没有 YARA 匹配，但有其他检测
            behaviors.append("yara:none")
        
        # 意图识别 (最高 30 分)
        if intent_result:
            intent_type = intent_result.get('intent', 'unknown')
            confidence = intent_result.get('confidence', 0)
            
            if intent_type == 'malicious':
                score += min(30, confidence * 30)
                behaviors.append(f"intent:malicious:{confidence:.2f}")
            elif intent_type == 'suspicious':
                score += min(15, confidence * 15)
                behaviors.append(f"intent:suspicious:{confidence:.2f}")
            elif intent_type == 'benign':
                # 良性意图降低风险
                score = max(0, score - 20)
                behaviors.append(f"intent:benign:{confidence:.2f}")
        
        # 语言风险系数
        lang_risk = {
            'powershell': 1.2,
            'bash': 1.1,
            'python': 1.0,
            'javascript': 1.0,
            'vbscript': 1.3,
            'batch': 1.1
        }
        score *= lang_risk.get(language, 1.0)
        
        # 限制 0-100
        score = max(0, min(100, score))
        
        # 确定风险等级
        if score >= 80:
            risk_level = 'critical'
        elif score >= 60:
            risk_level = 'high'
        elif score >= 40:
            risk_level = 'medium'
        elif score >= 20:
            risk_level = 'low'
        else:
            risk_level = 'safe'
        
        return score, risk_level, behaviors
    
    def analyze_intent(self, file_path: str, language: str, yara_matched: bool = False) -> Optional[dict]:
        """分析文件意图"""
        if not self.intent_detector:
            return None
        
        try:
            content = Path(file_path).read_text(encoding='utf-8', errors='ignore')
            if len(content) > 50000:  # 限制文件大小
                content = content[:50000]
            
            result = self.intent_detector.analyze(content, file_path=file_path)
            
            # 提取结果
            intent = result.intent.value if hasattr(result, 'intent') else 'unknown'
            confidence = result.confidence if hasattr(result, 'confidence') else 0.0
            risk_score = result.risk_score if hasattr(result, 'risk_score') else 0.0
            
            # 如果有 YARA 匹配，重新分析
            if yara_matched:
                result2 = self.intent_detector.analyze(content, yara_matches=['yara_matched'], file_path=file_path)
                intent = result2.intent.value
                confidence = result2.confidence
                risk_score = result2.risk_score
            
            return {
                'intent': intent,
                'confidence': confidence,
                'risk_score': risk_score,
                'indicators': result.reasons if hasattr(result, 'reasons') else []
            }
        except Exception as e:
            return None

def scan_sample(yara_scanner: RobustYaraScanner, scorer: SmartScorer, 
                sample_path: str) -> ScanResult:
    """扫描单个样本"""
    start = time.perf_counter()
    
    # 检测语言
    language = scorer.detect_language(sample_path)
    
    # YARA 扫描
    yara_matched, yara_rules = yara_scanner.scan(sample_path)
    
    # 意图分析 (传递 YARA 匹配信息)
    intent_result = scorer.analyze_intent(sample_path, language, yara_matched)
    
    # 综合评分
    risk_score, risk_level, behaviors = scorer.calculate_risk(
        yara_matched, yara_rules, intent_result, language
    )
    
    # 判断是否恶意
    is_malicious = risk_score >= 40 or yara_matched
    
    duration = (time.perf_counter() - start) * 1000
    
    return ScanResult(
        sample_path=sample_path,
        language=language,
        is_malicious=is_malicious,
        risk_score=round(risk_score, 2),
        risk_level=risk_level,
        yara_matched=yara_matched,
        yara_rules=yara_rules,
        intent_detected=intent_result['intent'] if intent_result else None,
        intent_confidence=intent_result['confidence'] if intent_result else 0.0,
        behaviors=behaviors[:10],  # 限制行为数量
        scan_time_ms=round(duration, 3)
    )

def scan_directory(yara_scanner: RobustYaraScanner, scorer: SmartScorer,
                   samples_dir: str, workers: int = 4) -> Tuple[List[ScanResult], float]:
    """并发扫描目录"""
    samples_path = Path(samples_dir)
    if not samples_path.exists():
        raise FileNotFoundError(f"样本目录不存在：{samples_path}")
    
    # 收集所有样本文件
    extensions = {'.py', '.js', '.sh', '.ps1', '.bat', '.cmd', '.vbs', '.lua'}
    sample_files = []
    for ext in extensions:
        sample_files.extend(samples_path.rglob(f"*{ext}"))
    
    sample_files = list(set(sample_files))
    
    print(f"📂 找到 {len(sample_files)} 个样本文件")
    print(f"⚡ 启动 {workers} 线程并发扫描...")
    
    start_time = time.perf_counter()
    results = []
    
    # 每个线程独立加载扫描器
    def scan_worker(file_path: str) -> ScanResult:
        thread_scanner = RobustYaraScanner(str(yara_scanner.rules_path))
        return scan_sample(thread_scanner, scorer, file_path)
    
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
    
    # 按语言统计
    by_language = {}
    for r in results:
        lang = r.language
        if lang not in by_language:
            by_language[lang] = {'total': 0, 'malicious': 0, 'avg_risk': 0}
        by_language[lang]['total'] += 1
        if r.is_malicious:
            by_language[lang]['malicious'] += 1
        by_language[lang]['avg_risk'] += r.risk_score
    
    for lang in by_language:
        if by_language[lang]['total'] > 0:
            by_language[lang]['avg_risk'] /= by_language[lang]['total']
    
    # 按风险等级统计
    by_risk_level = {}
    for r in results:
        level = r.risk_level
        by_risk_level[level] = by_risk_level.get(level, 0) + 1
    
    # 统计意图类型
    by_intent = {}
    for r in results:
        intent = r.intent_detected or 'unknown'
        by_intent[intent] = by_intent.get(intent, 0) + 1
    
    # Top 威胁
    top_threats = sorted(
        [r for r in results if r.is_malicious],
        key=lambda x: x.risk_score,
        reverse=True
    )[:10]
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "total_samples": total,
        "malicious_count": malicious,
        "benign_count": benign,
        "detection_rate": detection_rate,
        "detection_rate_percent": f"{detection_rate * 100:.1f}%",
        "scan_time_seconds": round(total_time, 3),
        "avg_time_ms": avg_time,
        "throughput_samples_per_sec": round(total / total_time, 1) if total_time > 0 else 0,
        "by_language": by_language,
        "by_risk_level": by_risk_level,
        "by_intent": by_intent,
        "top_threats": [asdict(t) for t in top_threats],
        "features": {
            "yara_enabled": True,
            "intent_enabled": INTENT_ENABLED,
            "smart_scoring": True
        }
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
    
    print("\n📈 按语言:")
    for lang, stats in sorted(by_language.items(), key=lambda x: x[1]['total'], reverse=True):
        rate = stats['malicious'] / stats['total'] * 100 if stats['total'] > 0 else 0
        print(f"   {lang}: {stats['malicious']}/{stats['total']} ({rate:.1f}%) 平均风险：{stats['avg_risk']:.1f}")
    
    print("\n🎯 按风险等级:")
    for level in ['critical', 'high', 'medium', 'low', 'safe']:
        count = by_risk_level.get(level, 0)
        if count > 0:
            print(f"   {level}: {count}")
    
    if by_intent:
        print("\n🧠 按意图类型:")
        for intent, count in sorted(by_intent.items(), key=lambda x: x[1], reverse=True):
            print(f"   {intent}: {count}")
    
    if top_threats:
        print("\n🔥 Top 5 高危样本:")
        for t in top_threats[:5]:
            print(f"   [{t.risk_level}] {t.risk_score:.0f}分 - {Path(t.sample_path).name}")
    
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
    parser = argparse.ArgumentParser(description='🛡️ 终极全量扫描器 V3 - YARA+ 意图 + 评分')
    parser.add_argument('--samples', default='samples', help='样本目录')
    parser.add_argument('--rules', default='rules/scanner_v3/yara', help='规则目录')
    parser.add_argument('--output', default=None, help='输出报告文件')
    parser.add_argument('--workers', type=int, default=4, help='并发数')
    parser.add_argument('--no-intent', action='store_true', help='禁用意图识别')
    
    args = parser.parse_args()
    
    script_dir = Path(__file__).parent
    samples_dir = script_dir / args.samples if not Path(args.samples).is_absolute() else Path(args.samples)
    rules_dir = script_dir / args.rules if not Path(args.rules).is_absolute() else Path(args.rules)
    
    output_file = args.output or f"reports/ultimate_scan_v3_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    print("=" * 70)
    print("🛡️  终极全量扫描器 V3 - YARA + 意图识别 + 智能评分")
    print("=" * 70)
    print(f"📂 样本目录：{samples_dir}")
    print(f"📚 规则目录：{rules_dir}")
    print(f"💾 输出文件：{output_file}")
    print(f"🧠 意图识别：{'✅ 启用' if INTENT_ENABLED and not args.no_intent else '❌ 禁用'}")
    print(f"⚡ 并发数：{args.workers}")
    print()
    
    # 加载 YARA 扫描器
    yara_scanner = RobustYaraScanner(str(rules_dir))
    
    # 创建评分器
    scorer = SmartScorer()
    if args.no_intent:
        scorer.intent_detector = None
    
    # 扫描
    results, total_time = scan_directory(yara_scanner, scorer, str(samples_dir), args.workers)
    
    # 生成报告
    generate_report(results, total_time, output_file)

if __name__ == '__main__':
    main()
