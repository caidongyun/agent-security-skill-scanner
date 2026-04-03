#!/usr/bin/env python3
"""
🛡️ Ultimate Scanner V2 - 完全整合版
=====================================
整合所有检测能力：
1. YARA 规则 (342+ 条) - 快速初筛
2. AST 静态分析 (round16) - 混淆检测
3. JS 专用分析 (round20) - JavaScript 深度检测
4. 智能模式识别 (engine) - 行为分析
5. 意图识别 - 语义分析
6. 多级决策引擎 - 最终判定

检测流程优化:
- YARA 检出 85% → 直接判定
- 剩余 15% → AST/JS/智能/意图 分层补充
- 目标检测率：90%+
"""

import os
import sys
import json
import time
import argparse
import yara as yara_lib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict, field
from concurrent.futures import ThreadPoolExecutor, as_completed
import statistics

sys.path.insert(0, str(Path(__file__).parent))

# === 导入所有检测引擎 ===

# 1. YARA 扫描器
class YaraScanner:
    """YARA 规则扫描器"""
    def __init__(self, rules_dir: str):
        self.rules_dir = Path(rules_dir)
        self.rules, self.rule_count = self._load_rules()
    
    def _load_rules(self):
        if not self.rules_dir.exists():
            return None, 0
        
        all_rules = ""
        count = 0
        for ext in ['*.yar', '*.yaml', '*.yara']:
            for rf in self.rules_dir.glob(ext):
                try:
                    content = rf.read_text(encoding='utf-8', errors='ignore')
                    content = content.encode('ascii', 'ignore').decode('ascii')
                    if 'rule ' in content:
                        try:
                            yara_lib.compile(source=content)
                            all_rules += content + "\n\n"
                            count += content.count('\nrule ') + content.count('rule ')
                        except:
                            pass
                except:
                    pass
        
        if all_rules:
            return yara_lib.compile(source=all_rules), count
        return None, 0
    
    def scan(self, file_path: str) -> Tuple[bool, List[str]]:
        if not self.rules:
            return False, []
        try:
            matches = self.rules.match(file_path)
            return len(matches) > 0, [m.rule for m in matches]
        except:
            return False, []

# 2. AST 分析器 (round16)
class ASTAnalyzer:
    """AST 静态分析器 - round16"""
    def __init__(self):
        self.ast_scanner = None
        self.obf_detector = None
        try:
            from round16.ast_engine import ASTScanner, ObfuscationDetector
            self.ast_scanner = ASTScanner()
            self.obf_detector = ObfuscationDetector()
            print("  ✅ AST 分析：可用 (round16)")
        except Exception as e:
            print(f"  ⚠️  AST 分析：不可用 - {e}")
    
    def analyze(self, file_path: str, language: str) -> Optional[Dict]:
        if not self.ast_scanner or language not in ['python', 'javascript']:
            return None
        
        try:
            content = Path(file_path).read_text(encoding='utf-8', errors='ignore')
            result = self.ast_scanner.scan(content, language)
            
            obfuscation = False
            if self.obf_detector:
                obfuscation = self.obf_detector.detect(content, language)
            
            return {
                'ast_issues': result.get('issues', []) if isinstance(result, dict) else [],
                'obfuscation_detected': obfuscation,
                'complexity': result.get('complexity', 0) if isinstance(result, dict) else 0
            }
        except:
            return None

# 3. JS 分析器 (round20)
class JSAnalyzer:
    """JavaScript 专用分析器 - round20"""
    def __init__(self):
        self.js_analyzer = None
        try:
            from round20.js_analyzer import JSAnalyzer as JSA
            self.js_analyzer = JSA()
            print("  ✅ JS 分析：可用 (round20)")
        except Exception as e:
            print(f"  ⚠️  JS 分析：不可用 - {e}")
    
    def analyze(self, file_path: str) -> Optional[Dict]:
        if not self.js_analyzer or Path(file_path).suffix.lower() != '.js':
            return None
        
        try:
            content = Path(file_path).read_text(encoding='utf-8', errors='ignore')
            result = self.js_analyzer.analyze(content)
            
            return {
                'is_malicious': result.get('is_malicious', False) if isinstance(result, dict) else False,
                'indicators': result.get('indicators', []) if isinstance(result, dict) else [],
                'confidence': result.get('confidence', 0.0) if isinstance(result, dict) else 0.0
            }
        except:
            return None

# 4. 智能模式识别 (engine)
class SmartPatternDetector:
    """智能模式识别器 - engine"""
    def __init__(self):
        self.scanner = None
        try:
            from engine.smart_pattern_detector import SmartScanner
            self.scanner = SmartScanner()
            print("  ✅ 智能模式：可用 (engine)")
        except Exception as e:
            print(f"  ⚠️  智能模式：不可用 - {e}")
    
    def analyze(self, file_path: str) -> Optional[Dict]:
        if not self.scanner:
            return None
        
        try:
            content = Path(file_path).read_text(encoding='utf-8', errors='ignore')[:50000]
            result = self.scanner.scan(content)
            
            return {
                'patterns_found': result.get('patterns', []) if isinstance(result, dict) else [],
                'risk_level': result.get('risk_level', 'unknown') if isinstance(result, dict) else 'unknown',
                'behaviors': result.get('behaviors', []) if isinstance(result, dict) else []
            }
        except:
            return None

# 5. 意图识别器
class IntentAnalyzer:
    """意图识别分析器"""
    def __init__(self):
        self.detector = None
        try:
            from intent_detector_v2 import EnhancedIntentDetector
            self.detector = EnhancedIntentDetector()
            print("  ✅ 意图识别：可用")
        except Exception as e:
            print(f"  ⚠️  意图识别：不可用 - {e}")
    
    def analyze(self, file_path: str, yara_matched: bool = False) -> Optional[Dict]:
        if not self.detector:
            return None
        
        try:
            content = Path(file_path).read_text(encoding='utf-8', errors='ignore')[:50000]
            yara_hints = ['yara_matched'] if yara_matched else None
            result = self.detector.analyze(content, yara_matches=yara_hints, file_path=file_path)
            
            return {
                'intent': result.intent.value if hasattr(result, 'intent') else 'unknown',
                'confidence': result.confidence if hasattr(result, 'confidence') else 0.0,
                'risk_score': result.risk_score if hasattr(result, 'risk_score') else 0.0,
                'reasons': result.reasons if hasattr(result, 'reasons') else []
            }
        except:
            return None

# 6. 智能评分器
class SmartScorer:
    """智能风险评分器"""
    
    LANG_RISK = {
        'powershell': 1.2, 'bash': 1.1, 'python': 1.0,
        'javascript': 1.0, 'vbscript': 1.3, 'batch': 1.1
    }
    
    def detect_language(self, file_path: str) -> str:
        ext = Path(file_path).suffix.lower()
        name = Path(file_path).name.lower()
        
        # 标准扩展名 + 非标准扩展名 (security-benchmark)
        lang_map = {
            '.py': 'python', '.js': 'javascript', '.sh': 'bash',
            '.ps1': 'powershell', '.bat': 'batch', '.cmd': 'batch',
            '.vbs': 'vbscript', '.lua': 'lua', '.go': 'go',
            # 非标准扩展名
            '.python': 'python', '.javascript': 'javascript',
            '.bash': 'bash', '.shell': 'bash',
            '.powershell': 'powershell', '.golang': 'go',
            # 配置文件
            '.yaml': 'yaml', '.yml': 'yaml', '.json': 'json'
        }
        
        # 检查扩展名
        if ext in lang_map:
            return lang_map[ext]
        
        # 检查 payload.* 格式
        if name.startswith('payload.'):
            payload_ext = '.' + name[8:]
            if payload_ext in lang_map:
                return lang_map[payload_ext]
        
        return 'unknown'
    
    def calculate(self, results: Dict, language: str) -> Tuple[float, str, List[str]]:
        """综合所有检测结果计算风险评分"""
        score = 0.0
        behaviors = []
        
        # YARA (0-50 分)
        if results['yara_matched']:
            base = min(30 + len(results['yara_rules']) * 3, 50)
            score += base
            critical_kws = ['credential', 'exfil', 'backdoor', 'reverse', 'ransom']
            for rule in results['yara_rules'][:5]:
                if any(kw in rule.lower() for kw in critical_kws):
                    score += 3
                    behaviors.append(f"🔴 YARA:critical:{rule}")
                else:
                    behaviors.append(f"🟡 YARA:{rule}")
        else:
            behaviors.append("⚪ YARA:none")
        
        # AST (0-15 分)
        if results.get('ast') and results['ast'].get('obfuscation_detected'):
            score += 15
            behaviors.append("🔴 AST:混淆代码检测")
        if results.get('ast') and results['ast'].get('ast_issues'):
            score += min(5, len(results['ast']['ast_issues']))
            behaviors.append(f"🟡 AST:{len(results['ast']['ast_issues'])} 个问题")
        
        # JS 分析 (0-15 分)
        if results.get('js') and results['js'].get('is_malicious'):
            score += min(15, results['js']['confidence'] * 15)
            behaviors.append(f"🔴 JS:malicious:{results['js']['confidence']:.2f}")
        
        # 智能模式 (0-10 分)
        if results.get('smart') and results['smart'].get('patterns_found'):
            score += min(10, len(results['smart']['patterns_found']) * 2)
            behaviors.append(f"🟡 Smart:{len(results['smart']['patterns_found'])} 个模式")
        
        # 意图识别 (0-10 分)
        if results.get('intent'):
            if results['intent']['intent'] == 'malicious':
                score += min(10, results['intent']['confidence'] * 10)
                behaviors.append(f"🔴 Intent:malicious")
            elif results['intent']['intent'] == 'suspicious':
                score += min(5, results['intent']['confidence'] * 5)
                behaviors.append(f"🟡 Intent:suspicious")
        
        # 语言系数
        score *= self.LANG_RISK.get(language, 1.0)
        score = max(0, min(100, score))
        
        # 风险等级
        if score >= 80: level = 'critical'
        elif score >= 60: level = 'high'
        elif score >= 40: level = 'medium'
        elif score >= 20: level = 'low'
        else: level = 'safe'
        
        return score, level, behaviors[:20]

# 7. 决策引擎
class DecisionEngine:
    """多级决策引擎"""
    
    def decide(self, results: Dict, score: float) -> Tuple[bool, str, float]:
        yara = results['yara_matched']
        ast = results.get('ast', {}).get('obfuscation_detected', False)
        js = results.get('js', {}).get('is_malicious', False)
        intent = results.get('intent', {}).get('intent', 'unknown')
        
        # 规则 1: YARA 检出 → 确认恶意
        if yara:
            if score >= 50:
                return True, "✅ YARA 规则匹配 + 高风险", 0.98
            return True, "✅ YARA 规则匹配", 0.92
        
        # 规则 2: JS 检出恶意 → 高度可疑
        if js:
            return True, "⚠️ JS 分析检出恶意", 0.88
        
        # 规则 3: AST 混淆 + 高风险 → 可能恶意
        if ast and score >= 60:
            return True, "⚠️ AST 混淆 + 高风险", 0.82
        
        # 规则 4: 意图恶意 + 中等风险 → 可疑
        if intent == 'malicious' and score >= 50:
            return True, "⚠️ 意图识别恶意 + 风险支持", 0.78
        
        # 规则 5: 单纯高风险 → 可能威胁
        if score >= 70:
            return True, f"⚠️ 高风险评分 ({score:.0f})", 0.75
        
        # 规则 6: 低风险 + 良性 → 安全
        if score < 30 and intent == 'benign':
            return False, "✅ 低风险 + 良性", 0.90
        
        # 默认
        if score >= 40:
            return True, f"⚠️ 风险超过阈值 ({score:.0f})", 0.65
        return False, "✅ 未达恶意阈值", 0.80

# === 主扫描器 ===

@dataclass
class ScanResult:
    sample_path: str
    language: str
    is_malicious: bool
    decision_reason: str
    decision_confidence: float
    risk_score: float
    risk_level: str
    yara_matched: bool
    yara_rules: List[str] = field(default_factory=list)
    ast_obfuscation: bool = False
    js_malicious: bool = False
    intent_detected: Optional[str] = None
    behaviors: List[str] = field(default_factory=list)
    scan_time_ms: float = 0.0
    detection_layers: List[str] = field(default_factory=list)

class UltimateScannerV2:
    """终极智能扫描器 V2 - 完全整合版"""
    
    def __init__(self, rules_dir: str, enable_ast: bool = True, 
                 enable_js: bool = True, enable_smart: bool = True,
                 enable_intent: bool = True):
        print("🔧 初始化检测引擎...")
        
        # 1. YARA (始终启用)
        self.yara = YaraScanner(rules_dir)
        print(f"  ✅ YARA 规则：{self.yara.rule_count} 条")
        
        # 2. AST (可选)
        self.ast = ASTAnalyzer() if enable_ast else None
        
        # 3. JS 分析 (可选)
        self.js = JSAnalyzer() if enable_js else None
        
        # 4. 智能模式 (可选)
        self.smart = SmartPatternDetector() if enable_smart else None
        
        # 5. 意图识别 (可选)
        self.intent = IntentAnalyzer() if enable_intent else None
        
        # 6. 评分器 + 决策
        self.scorer = SmartScorer()
        self.decider = DecisionEngine()
    
    def scan_file(self, file_path: str) -> ScanResult:
        """分层扫描单个文件"""
        start = time.perf_counter()
        
        language = self.scorer.detect_language(file_path)
        detection_layers = []
        results = {'yara_matched': False, 'yara_rules': []}
        
        # 层 1: YARA (100% 样本)
        yara_matched, yara_rules = self.yara.scan(file_path)
        results['yara_matched'] = yara_matched
        results['yara_rules'] = yara_rules
        if yara_matched:
            detection_layers.append('yara')
        
        # 层 2: AST (仅 YARA 未检出)
        if not yara_matched and self.ast:
            ast_result = self.ast.analyze(file_path, language)
            results['ast'] = ast_result
            if ast_result and ast_result.get('obfuscation_detected'):
                detection_layers.append('ast')
        
        # 层 3: JS 分析 (仅 YARA 未检出的 JS 文件)
        if not yara_matched and self.js and language == 'javascript':
            js_result = self.js.analyze(file_path)
            results['js'] = js_result
            if js_result and js_result.get('is_malicious'):
                detection_layers.append('js')
        
        # 层 4: 智能模式 (仅 YARA 未检出)
        if not yara_matched and self.smart:
            smart_result = self.smart.analyze(file_path)
            results['smart'] = smart_result
            if smart_result and smart_result.get('patterns_found'):
                detection_layers.append('smart')
        
        # 层 5: 意图识别 (最后补充)
        if not yara_matched and self.intent:
            intent_result = self.intent.analyze(file_path, yara_matched)
            results['intent'] = intent_result
            if intent_result and intent_result.get('intent') in ['malicious', 'suspicious']:
                detection_layers.append('intent')
        
        # 层 6: 智能评分 (确保所有键都存在)
        risk_score, risk_level, behaviors = self.scorer.calculate(results, language)
        
        # 层 7: 最终决策
        is_malicious, reason, confidence = self.decider.decide(results, risk_score)
        
        duration = (time.perf_counter() - start) * 1000
        
        return ScanResult(
            sample_path=str(file_path),
            language=language,
            is_malicious=is_malicious,
            decision_reason=reason,
            decision_confidence=confidence,
            risk_score=round(risk_score, 2),
            risk_level=risk_level,
            yara_matched=yara_matched,
            yara_rules=yara_rules,
            ast_obfuscation=results.get('ast', {}).get('obfuscation_detected', False),
            js_malicious=results.get('js', {}).get('is_malicious', False),
            intent_detected=results.get('intent', {}).get('intent') if results.get('intent') else None,
            behaviors=behaviors,
            scan_time_ms=round(duration, 3),
            detection_layers=detection_layers
        )
    
    def scan_directory(self, samples_dir: str, workers: int = 4) -> Tuple[List[ScanResult], float]:
        samples_path = Path(samples_dir)
        
        # 标准扩展名 + security-benchmark 特有扩展名
        extensions = {
            '.py', '.js', '.sh', '.ps1', '.bat', '.cmd', '.vbs', '.lua', '.go',
            '.python', '.javascript', '.bash', '.shell', '.powershell', '.golang'
        }
        
        sample_files = []
        for ext in extensions:
            sample_files.extend(samples_path.rglob(f"*{ext}"))
        
        # 也查找 payload.* 格式
        for name_pattern in ['payload.*', '*.payload']:
            sample_files.extend(samples_path.rglob(name_pattern))
        
        sample_files = list(set(sample_files))
        
        print(f"\n📂 发现 {len(sample_files)} 个样本文件")
        print(f"⚡ 启动 {workers} 线程并发扫描...")
        
        start_time = time.perf_counter()
        results = []
        
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {executor.submit(self.scan_file, str(f)): f for f in sample_files}
            
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
    total = len(results)
    malicious = sum(1 for r in results if r.is_malicious)
    detection_rate = malicious / total if total > 0 else 0
    
    by_language = {}
    by_risk_level = {}
    by_layers = {}
    
    for r in results:
        if r.language not in by_language:
            by_language[r.language] = {'total': 0, 'malicious': 0}
        by_language[r.language]['total'] += 1
        if r.is_malicious:
            by_language[r.language]['malicious'] += 1
        
        by_risk_level[r.risk_level] = by_risk_level.get(r.risk_level, 0) + 1
        layers = '-'.join(sorted(r.detection_layers)) if r.detection_layers else 'none'
        by_layers[layers] = by_layers.get(layers, 0) + 1
    
    top_threats = sorted(
        [r for r in results if r.is_malicious],
        key=lambda x: x.risk_score,
        reverse=True
    )[:10]
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total": total,
            "malicious": malicious,
            "detection_rate": f"{detection_rate * 100:.1f}%"
        },
        "performance": {
            "scan_time_seconds": round(total_time, 3),
            "avg_time_ms": round(statistics.mean([r.scan_time_ms for r in results]), 3) if results else 0
        },
        "by_language": by_language,
        "by_risk_level": by_risk_level,
        "by_detection_layers": by_layers,
        "top_threats": [asdict(t) for t in top_threats]
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 70)
    print("📊 扫描结果 - Ultimate Scanner V2")
    print("=" * 70)
    print(f"✅ 扫描样本：{total} 个")
    print(f"🔴 恶意样本：{malicious} ({detection_rate * 100:.1f}%)")
    print(f"⚡ 扫描耗时：{total_time:.3f} 秒")
    print(f"⚡ 平均耗时：{report['performance']['avg_time_ms']:.3f} ms/样本")
    
    print("\n📈 按语言:")
    for lang, stats in sorted(by_language.items(), key=lambda x: x[1]['total'], reverse=True):
        rate = stats['malicious'] / stats['total'] * 100 if stats['total'] > 0 else 0
        print(f"   {lang}: {stats['malicious']}/{stats['total']} ({rate:.1f}%)")
    
    print("\n🎯 按风险等级:")
    for level in ['critical', 'high', 'medium', 'low', 'safe']:
        count = by_risk_level.get(level, 0)
        if count > 0:
            emoji = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢', 'safe': '⚪'}[level]
            print(f"   {emoji} {level}: {count}")
    
    print("\n🔬 检测层组合 (Top 5):")
    for layers, count in sorted(by_layers.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"   {layers}: {count}")
    
    if top_threats:
        print("\n🔥 Top 5 高危样本:")
        for t in top_threats[:5]:
            print(f"   [{t.risk_level}] {t.risk_score:.0f}分 - {Path(t.sample_path).name}")
            print(f"      原因：{t.decision_reason}")
    
    print(f"\n💾 报告已保存：{output_file}")
    
    print("\n" + "=" * 70)
    if detection_rate >= 0.95:
        print("✅ 检测能力：优秀 (≥95%) 🏆")
    elif detection_rate >= 0.90:
        print("✅ 检测能力：良好 (≥90%) ✨")
    elif detection_rate >= 0.80:
        print("⚠️  检测能力：一般 (≥80%)")
    else:
        print("❌ 检测能力：不足 (<80%)")
    print("=" * 70)

def main():
    parser = argparse.ArgumentParser(description='🛡️ Ultimate Scanner V2 - 完全整合版')
    parser.add_argument('--samples', default='samples', help='样本目录')
    parser.add_argument('--rules', default='rules/scanner_v3/yara', help='规则目录')
    parser.add_argument('--output', default=None, help='输出文件')
    parser.add_argument('--workers', type=int, default=4, help='并发数')
    parser.add_argument('--no-ast', action='store_true', help='禁用 AST')
    parser.add_argument('--no-js', action='store_true', help='禁用 JS 分析')
    parser.add_argument('--no-smart', action='store_true', help='禁用智能模式')
    parser.add_argument('--no-intent', action='store_true', help='禁用意图识别')
    parser.add_argument('--full', action='store_true', help='启用所有检测 (默认)')
    
    args = parser.parse_args()
    
    script_dir = Path(__file__).parent
    samples_dir = script_dir / args.samples if not Path(args.samples).is_absolute() else Path(args.samples)
    rules_dir = script_dir / args.rules if not Path(args.rules).is_absolute() else Path(args.rules)
    output_file = args.output or f"reports/ultimate_v2_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    print("=" * 70)
    print("🛡️  Ultimate Scanner V2 - 完全整合版")
    print("   YARA + AST + JS + 智能模式 + 意图识别 + 决策引擎")
    print("=" * 70)
    print(f"📂 样本目录：{samples_dir}")
    print(f"📚 规则目录：{rules_dir}")
    print()
    
    # 创建扫描器 (默认启用所有)
    scanner = UltimateScannerV2(
        str(rules_dir),
        enable_ast=not args.no_ast,
        enable_js=not args.no_js,
        enable_smart=not args.no_smart,
        enable_intent=not args.no_intent
    )
    
    results, total_time = scanner.scan_directory(str(samples_dir), args.workers)
    generate_report(results, total_time, output_file)

if __name__ == '__main__':
    main()
