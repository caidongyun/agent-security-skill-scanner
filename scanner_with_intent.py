#!/usr/bin/env python3
"""
集成意图检测的 Scanner - 降低误报率
结合 YARA 规则匹配 + 意图行为分析
"""

import json
import yara
from pathlib import Path
from intent_detector import detect_intent, IntentType

RULES_FILE = Path(__file__).parent / "rules" / "scanner_v3" / "yara" / "optimized_precision_rules.yar"

def scan_file(file_path: str) -> dict:
    """
    扫描文件：YARA 规则 + 意图检测
    
    返回:
        {
            "file": str,
            "yara_detected": bool,
            "yara_rules": list,
            "intent": str,
            "intent_confidence": float,
            "risk_score": float,
            "final_decision": str,  # block/allow/review
            "reasons": list
        }
    """
    result = {
        "file": file_path,
        "yara_detected": False,
        "yara_rules": [],
        "intent": "unknown",
        "intent_confidence": 0.0,
        "risk_score": 0.0,
        "final_decision": "allow",
        "reasons": []
    }
    
    # 1. YARA 规则扫描
    try:
        rules = yara.compile(filepath=str(RULES_FILE))
        content = Path(file_path).read_text()
        matches = rules.match(data=content)
        
        if matches:
            result["yara_detected"] = True
            result["yara_rules"] = [m.rule for m in matches]
            result["reasons"].append(f"🔴 YARA 匹配 {len(matches)} 条规则")
    except Exception as e:
        result["reasons"].append(f"⚠️ YARA 规则加载失败：{e}")
    
    # 2. 意图检测
    try:
        content = Path(file_path).read_text()
        intent_result = detect_intent(content, result["yara_rules"])
        
        result["intent"] = intent_result["intent"]
        result["intent_confidence"] = intent_result["confidence"]
        result["risk_score"] = intent_result["risk_score"]
        result["reasons"].extend(intent_result["reasons"])
        result["reasons"].append(f"建议：{intent_result['recommendation']}")
    except Exception as e:
        result["reasons"].append(f"⚠️ 意图检测失败：{e}")
    
    # 3. 综合决策
    result["final_decision"] = _make_decision(result)
    
    return result

def _make_decision(result: dict) -> str:
    """
    综合决策逻辑
    
    YARA + 意图组合策略:
    - YARA 匹配 + 恶意意图 → block
    - YARA 匹配 + 良性意图 → review (可能是误报)
    - YARA 匹配 + 未知意图 → review
    - 无 YARA + 恶意意图 → review
    - 无 YARA + 良性意图 → allow
    """
    yara = result["yara_detected"]
    intent = result["intent"]
    
    if yara and intent == "malicious":
        return "🔴 block"  # 高置信度恶意
    elif yara and intent == "benign":
        return "🟡 review"  # YARA 误报
    elif yara and intent == "suspicious":
        return "🟡 review"  # 需要人工审核
    elif yara and intent == "unknown":
        return "🟡 review"  # 需要进一步分析
    elif not yara and intent == "malicious":
        return "🟡 review"  # 逃逸检测
    elif not yara and intent == "benign":
        return "🟢 allow"  # 正常代码
    else:
        return "🟢 allow"  # 默认放行


def scan_directory(dir_path: str, recursive: bool = False) -> list:
    """扫描目录"""
    results = []
    path = Path(dir_path)
    
    files = list(path.rglob("*")) if recursive else list(path.glob("*"))
    
    for f in files:
        if f.is_file() and f.suffix in [".py", ".js", ".sh", ".yaml", ".yml"]:
            result = scan_file(str(f))
            results.append(result)
    
    return results


def print_report(results: list):
    """打印报告"""
    print("\n" + "="*70)
    print("🔍 Scanner + 意图检测 报告")
    print("="*70)
    
    block_count = sum(1 for r in results if r["final_decision"] == "🔴 block")
    review_count = sum(1 for r in results if r["final_decision"] == "🟡 review")
    allow_count = sum(1 for r in results if r["final_decision"] == "🟢 allow")
    
    print(f"\n📊 统计:")
    print(f"  总文件数：{len(results)}")
    print(f"  🔴 阻断：{block_count}")
    print(f"  🟡 审核：{review_count}")
    print(f"  🟢 放行：{allow_count}")
    
    print(f"\n📈 误报率优化:")
    yara_only_fp = sum(1 for r in results if r["yara_detected"] and r["intent"] == "benign")
    print(f"  YARA 单独检测误报：{yara_only_fp} 个 (通过意图检测纠正)")
    
    print("\n" + "-"*70)
    print("📋 详细结果:")
    print("-"*70)
    
    for r in results:
        print(f"\n文件：{r['file']}")
        print(f"  决策：{r['final_decision']}")
        print(f"  YARA: {'✅ 匹配' if r['yara_detected'] else '❌ 无'} ({len(r['yara_rules'])} 条)")
        print(f"  意图：{r['intent']} (置信度：{r['intent_confidence']:.2f})")
        print(f"  风险：{r['risk_score']:.1f}/10")
        if r['reasons']:
            print(f"  原因:")
            for reason in r['reasons'][:5]:
                print(f"    - {reason}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("用法：python3 scanner_with_intent.py <扫描路径> [递归]")
        print("示例：python3 scanner_with_intent.py /path/to/scan")
        sys.exit(1)
    
    scan_path = sys.argv[1]
    recursive = sys.argv[2].lower() == "true" if len(sys.argv) > 2 else False
    
    if Path(scan_path).is_file():
        results = [scan_file(scan_path)]
    else:
        results = scan_directory(scan_path, recursive)
    
    print_report(results)
