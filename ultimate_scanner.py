#!/usr/bin/env python3
"""
🛡️ Ultimate Scanner - 终极智能扫描器
=====================================
用户只需一条命令，自动执行最优扫描策略！

检测流程:
1. YARA 规则扫描 (342+ 条规则) - 快速初筛
2. 意图识别分析 - 降低误报
3. AST 静态分析 (可选) - 检测混淆代码
4. 智能风险评分 - 综合评估
5. 多级决策引擎 - 最终判定

特点:
- 自动选择最优检测路径
- 多层检测互为补充
- 输出清晰可信的报告
- 检测率目标：95%+
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

# === 导入所有检测引擎 ===
sys.path.insert(0, str(Path(__file__).parent))

# 1. YARA 扫描器
class YaraScanner:
    """YARA 规则扫描器"""
    def __init__(self, rules_dir: str):
        self.rules_dir = Path(rules_dir)
        self.rules, self.rule_count = self._load_rules()
    
    def _load_rules(self):
        """加载规则"""
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
        """扫描文件"""
        if not self.rules:
            return False, []
        try:
            matches = self.rules.match(file_path)
            return len(matches) > 0, [m.rule for m in matches]
        except:
            return False, []

# 2. 意图识别器
class IntentAnalyzer:
    """意图识别分析器"""
    def __init__(self):
        self.detector = None
        try:
            from intent_detector_v2 import EnhancedIntentDetector
            self.detector = EnhancedIntentDetector()
        except:
            pass
    
    def analyze(self, file_path: str, yara_matched: bool = False) -> Optional[Dict]:
        """分析意图"""
        if not self.detector:
            return None
        
        try:
            content = Path(file_path).read_text(encoding='utf-8', errors='ignore')[:50000]
            
            # 如果有 YARA 匹配，传入提示信息
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

# 3. AST 分析器 (可选)
class ASTAnalyzer:
    """AST 静态分析器"""
    def __init__(self):
        self.scanner = None
        try:
            from round16.ast_engine import ASTScanner
            self.scanner = ASTScanner()
        except:
            pass
    
    def analyze(self, file_path: str, language: str) -> Optional[Dict]:
        """AST 分析"""
        if not self.scanner or language not in ['python', 'javascript']:
            return None
        
        try:
            content = Path(file_path).read_text(encoding='utf-8', errors='ignore')
            result = self.scanner.scan(content, language)
            return {
                'obfuscation_detected': result.get('obfuscation', False) if isinstance(result, dict) else False,
                'ast_issues': result.get('issues', []) if isinstance(result, dict) else []
            }
        except:
            return None

# 4. 智能评分器
class SmartScorer:
    """智能风险评分器"""
    
    LANG_RISK = {
        'powershell': 1.2,
        'bash': 1.1,
        'python': 1.0,
        'javascript': 1.0,
        'vbscript': 1.3,
        'batch': 1.1
    }
    
    def detect_language(self, file_path: str) -> str:
        ext = Path(file_path).suffix.lower()
        return {
            '.py': 'python', '.js': 'javascript', '.sh': 'bash',
            '.ps1': 'powershell', '.bat': 'batch', '.cmd': 'batch',
            '.vbs': 'vbscript', '.lua': 'lua'
        }.get(ext, 'unknown')
    
    def calculate(self, yara: Dict, intent: Optional[Dict], 
                  ast: Optional[Dict], language: str) -> Tuple[float, str, List[str]]:
        """计算综合风险评分"""
        score = 0.0
        behaviors = []
        
        # YARA (0-60 分)
        if yara['matched']:
            base = min(30 + len(yara['rules']) * 3, 60)
            score += base
            critical_kws = ['credential', 'exfil', 'backdoor', 'reverse', 'ransom']
            for rule in yara['rules']:
                if any(kw in rule.lower() for kw in critical_kws):
                    score += 5
                    behaviors.append(f"🔴 YARA:critical:{rule}")
                else:
                    behaviors.append(f"🟡 YARA:{rule}")
        else:
            behaviors.append("⚪ YARA:none")
        
        # 意图 (0-30 分)
        if intent:
            if intent['intent'] == 'malicious':
                score += min(30, intent['confidence'] * 30)
                behaviors.append(f"🔴 Intent:malicious:{intent['confidence']:.2f}")
            elif intent['intent'] == 'suspicious':
                score += min(15, intent['confidence'] * 15)
                behaviors.append(f"🟡 Intent:suspicious:{intent['confidence']:.2f}")
            elif intent['intent'] == 'benign':
                score = max(0, score - 20)
                behaviors.append(f"⚪ Intent:benign:{intent['confidence']:.2f}")
        
        # AST (0-10 分)
        if ast and ast.get('obfuscation_detected'):
            score += 10
            behaviors.append("🔴 AST:obfuscation_detected")
        
        # 语言系数
        score *= self.LANG_RISK.get(language, 1.0)
        score = max(0, min(100, score))
        
        # 风险等级
        if score >= 80: level = 'critical'
        elif score >= 60: level = 'high'
        elif score >= 40: level = 'medium'
        elif score >= 20: level = 'low'
        else: level = 'safe'
        
        return score, level, behaviors[:15]

# 5. 决策引擎
class DecisionEngine:
    """多级决策引擎"""
    
    def decide(self, result: Dict) -> Tuple[bool, str, float]:
        """
        最终决策
        Returns: (is_malicious, reason, confidence)
        """
        score = result['risk_score']
        yara_matched = result['yara_matched']
        intent = result.get('intent_detected')
        
        # 规则 1: 仅 YARA 匹配 → 确认恶意 (最高优先级)
        if yara_matched:
            if score >= 60:
                return True, "YARA 规则匹配 + 高风险评分", 0.98
            elif score >= 40:
                return True, "YARA 规则匹配 + 中等风险", 0.95
            else:
                return True, "YARA 规则匹配", 0.90
        
        # 规则 2: 高风险评分 (无 YARA) → 很可能恶意
        if score >= 70:
            return True, "高风险评分", 0.85
        
        # 规则 3: 中等风险 + 恶意意图 → 可疑
        if score >= 50 and intent == 'malicious':
            return True, "中等风险 + 恶意意图", 0.75
        
        # 规则 4: 中低风险 + 恶意意图 → 需要审查
        if score >= 30 and intent == 'malicious':
            return True, "低风险 + 恶意意图 (需审查)", 0.60
        
        # 规则 5: 低风险 + 良性意图 → 安全
        if score < 30 and intent == 'benign':
            return False, "低风险 + 良性意图", 0.90
        
        # 默认：根据分数判断
        if score >= 40:
            return True, f"风险评分超过阈值 ({score:.1f})", 0.65
        
        return False, "未检测到明显威胁", 0.80

# === 主扫描器 ===

@dataclass
class ScanResult:
    sample_path: str
    language: str
    file_size: int
    is_malicious: bool
    decision_reason: str
    decision_confidence: float
    risk_score: float
    risk_level: str
    yara_matched: bool
    yara_rules: List[str] = field(default_factory=list)
    intent_detected: Optional[str] = None
    intent_confidence: float = 0.0
    ast_obfuscation: bool = False
    behaviors: List[str] = field(default_factory=list)
    scan_time_ms: float = 0.0
    detection_layers: List[str] = field(default_factory=list)

class UltimateScanner:
    """终极智能扫描器"""
    
    def __init__(self, rules_dir: str, enable_ast: bool = True):
        print("🔧 初始化检测引擎...")
        self.yara = YaraScanner(rules_dir)
        self.intent = IntentAnalyzer()
        self.ast = ASTAnalyzer() if enable_ast else None
        self.scorer = SmartScorer()
        self.decider = DecisionEngine()
        
        print(f"  ✅ YARA 规则：{self.yara.rule_count} 条")
        print(f"  {'✅' if self.intent.detector else '⚠️'}  意图识别：{'可用' if self.intent.detector else '不可用'}")
        print(f"  {'✅' if self.ast else '⚠️'}  AST 分析：{'可用' if self.ast else '不可用 (可选)'}")
    
    def scan_file(self, file_path: str) -> ScanResult:
        """扫描单个文件 - 分层检测 (优化版)"""
        start = time.perf_counter()
        
        # 基础信息
        language = self.scorer.detect_language(file_path)
        file_size = Path(file_path).stat().st_size
        detection_layers = []
        
        # ========== 层 1: YARA 规则扫描 (快速初筛) ==========
        yara_matched, yara_rules = self.yara.scan(file_path)
        if yara_matched:
            detection_layers.append('yara')
        
        # ========== 层 2: AST 分析 (仅当 YARA 未检出) ==========
        # AST 是静态结构分析，比意图识别更快、更客观
        ast_result = None
        if not yara_matched:
            ast_result = self.ast.analyze(file_path, language) if self.ast else None
            if ast_result and ast_result.get('obfuscation_detected'):
                detection_layers.append('ast')
        
        # ========== 层 3: 意图识别 (仅当 YARA+AST 都未检出) ==========
        # 作为最后一道防线，捕获未知威胁
        intent_result = None
        if not yara_matched and (not ast_result or not ast_result.get('obfuscation_detected')):
            intent_result = self.intent.analyze(file_path, yara_matched)
            if intent_result and intent_result.get('intent') in ['malicious', 'suspicious']:
                detection_layers.append('intent')
        
        # ========== 层 4: 智能评分 (综合所有检测结果) ==========
        risk_score, risk_level, behaviors = self.scorer.calculate(
            {'matched': yara_matched, 'rules': yara_rules},
            intent_result,
            ast_result,
            language
        )
        
        # ========== 层 5: 最终决策 ==========
        is_malicious, reason, confidence = self.decider.decide({
            'risk_score': risk_score,
            'yara_matched': yara_matched,
            'intent_detected': intent_result['intent'] if intent_result else None,
            'ast_obfuscation': ast_result.get('obfuscation_detected', False) if ast_result else False,
            'detection_layers': detection_layers
        })
        
        duration = (time.perf_counter() - start) * 1000
        
        return ScanResult(
            sample_path=str(file_path),
            language=language,
            file_size=file_size,
            is_malicious=is_malicious,
            decision_reason=reason,
            decision_confidence=confidence,
            risk_score=round(risk_score, 2),
            risk_level=risk_level,
            yara_matched=yara_matched,
            yara_rules=yara_rules,
            intent_detected=intent_result['intent'] if intent_result else None,
            intent_confidence=intent_result['confidence'] if intent_result else 0.0,
            ast_obfuscation=ast_result.get('obfuscation_detected', False) if ast_result else False,
            behaviors=behaviors,
            scan_time_ms=round(duration, 3),
            detection_layers=detection_layers
        )
    
    def scan_directory(self, samples_dir: str, workers: int = 4) -> Tuple[List[ScanResult], float]:
        """扫描目录"""
        samples_path = Path(samples_dir)
        extensions = {'.py', '.js', '.sh', '.ps1', '.bat', '.cmd', '.vbs', '.lua'}
        
        sample_files = []
        for ext in extensions:
            sample_files.extend(samples_path.rglob(f"*{ext}"))
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
    """生成报告"""
    total = len(results)
    malicious = sum(1 for r in results if r.is_malicious)
    benign = total - malicious
    detection_rate = malicious / total if total > 0 else 0
    
    # 统计
    by_language = {}
    by_risk_level = {}
    by_intent = {}
    by_layers = {}
    
    for r in results:
        # 按语言
        if r.language not in by_language:
            by_language[r.language] = {'total': 0, 'malicious': 0}
        by_language[r.language]['total'] += 1
        if r.is_malicious:
            by_language[r.language]['malicious'] += 1
        
        # 按风险等级
        by_risk_level[r.risk_level] = by_risk_level.get(r.risk_level, 0) + 1
        
        # 按意图
        intent = r.intent_detected or 'unknown'
        by_intent[intent] = by_intent.get(intent, 0) + 1
        
        # 按检测层
        layers = '-'.join(sorted(r.detection_layers))
        by_layers[layers] = by_layers.get(layers, 0) + 1
    
    # Top 威胁
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
            "benign": benign,
            "detection_rate": f"{detection_rate * 100:.1f}%"
        },
        "performance": {
            "scan_time_seconds": round(total_time, 3),
            "avg_time_ms": round(statistics.mean([r.scan_time_ms for r in results]), 3) if results else 0,
            "throughput": round(total / total_time, 1) if total_time > 0 else 0
        },
        "by_language": by_language,
        "by_risk_level": by_risk_level,
        "by_intent": by_intent,
        "by_detection_layers": by_layers,
        "top_threats": [asdict(t) for t in top_threats]
    }
    
    # 保存
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    # 显示
    print("\n" + "=" * 70)
    print("📊 扫描结果 - Ultimate Scanner")
    print("=" * 70)
    print(f"✅ 扫描样本：{total} 个")
    print(f"🔴 恶意样本：{malicious} ({detection_rate * 100:.1f}%)")
    print(f"🟢 安全样本：{benign} ({(1 - detection_rate) * 100:.1f}%)")
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
    
    print("\n🧠 按意图类型:")
    for intent, count in sorted(by_intent.items(), key=lambda x: x[1], reverse=True)[:5]:
        emoji = {'malicious': '🔴', 'suspicious': '🟡', 'benign': '⚪', 'unknown': '⚪'}[intent]
        print(f"   {emoji} {intent}: {count}")
    
    print("\n🔬 检测层组合 (Top 5):")
    for layers, count in sorted(by_layers.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"   {layers}: {count}")
    
    if top_threats:
        print("\n🔥 Top 5 高危样本:")
        for t in top_threats[:5]:
            print(f"   [{t.risk_level}] {t.risk_score:.0f}分 - {Path(t.sample_path).name}")
            print(f"      原因：{t.decision_reason}")
    
    print(f"\n💾 报告已保存：{output_file}")
    
    # 评估
    print("\n" + "=" * 70)
    if detection_rate >= 0.95:
        print("✅ 检测能力：优秀 (≥95%) 🏆")
    elif detection_rate >= 0.90:
        print("✅ 检测能力：良好 (≥90) ✨")
    elif detection_rate >= 0.80:
        print("⚠️  检测能力：一般 (≥80%)")
    else:
        print("❌ 检测能力：不足 (<80%) - 建议优化规则")
    print("=" * 70)

def main():
    parser = argparse.ArgumentParser(
        description='🛡️ Ultimate Scanner - 终极智能扫描器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 扫描默认样本库
  python3 ultimate_scanner.py
  
  # 扫描指定目录
  python3 ultimate_scanner.py /path/to/scan
  
  # 禁用 AST 分析 (更快)
  python3 ultimate_scanner.py --no-ast
  
  # 增加并发数
  python3 ultimate_scanner.py --workers 8
        """
    )
    parser.add_argument('--samples', default='samples', help='样本目录 (默认：samples)')
    parser.add_argument('--rules', default='rules/scanner_v3/yara', help='规则目录')
    parser.add_argument('--output', default=None, help='输出报告文件')
    parser.add_argument('--workers', type=int, default=4, help='并发数 (默认：4)')
    parser.add_argument('--no-ast', action='store_true', help='禁用 AST 分析')
    parser.add_argument('--verbose', action='store_true', help='详细输出')
    
    args = parser.parse_args()
    
    script_dir = Path(__file__).parent
    samples_dir = script_dir / args.samples if not Path(args.samples).is_absolute() else Path(args.samples)
    rules_dir = script_dir / args.rules if not Path(args.rules).is_absolute() else Path(args.rules)
    output_file = args.output or f"reports/ultimate_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    print("=" * 70)
    print("🛡️  Ultimate Scanner - 终极智能扫描器")
    print("   YARA + 意图识别 + AST + 智能评分 + 多级决策")
    print("=" * 70)
    print(f"📂 样本目录：{samples_dir}")
    print(f"📚 规则目录：{rules_dir}")
    print(f"💾 输出文件：{output_file}")
    print(f"⚡ 并发数：{args.workers}")
    print(f"🔬 AST 分析：{'禁用' if args.no_ast else '启用'}")
    print()
    
    # 创建扫描器
    scanner = UltimateScanner(str(rules_dir), enable_ast=not args.no_ast)
    
    # 扫描
    results, total_time = scanner.scan_directory(str(samples_dir), args.workers)
    
    # 生成报告
    generate_report(results, total_time, output_file)

if __name__ == '__main__':
    main()
