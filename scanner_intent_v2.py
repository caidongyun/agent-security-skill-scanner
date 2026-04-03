#!/usr/bin/env python3
"""
集成意图检测 v2 的 Scanner
YARA 规则 + 意图检测 (18 条规则) 双重验证
"""

import json
import yara
from pathlib import Path
from intent_detector_v2 import detect_intent_v2

RULES_FILE = Path(__file__).parent / "rules" / "scanner_v3" / "yara" / "optimized_precision_rules.yar"

def scan_file_v2(file_path: str) -> dict:
    """
    扫描文件 v2: YARA + 意图检测双重验证
    """
    result = {
        "file": file_path,
        "yara_detected": False,
        "yara_rules": [],
        "intent": detect_intent_v2(""),  # 默认
        "final_decision": "allow",
        "reasons": []
    }
    
    try:
        content = Path(file_path).read_text()
        
        # 1. YARA 规则扫描
        try:
            rules = yara.compile(filepath=str(RULES_FILE))
            matches = rules.match(data=content)
            if matches:
                result["yara_detected"] = True
                result["yara_rules"] = [m.rule for m in matches]
        except Exception as e:
            result["reasons"].append(f"⚠️ YARA: {e}")
        
        # 2. 意图检测
        intent_result = detect_intent_v2(content)
        result["intent"] = intent_result
        
        # 3. 综合决策 (YARA + 意图)
        result["final_decision"] = _make_decision_v2(result)
        
        # 4. 生成原因
        if result["yara_detected"]:
            result["reasons"].append(f"🔴 YARA 匹配 {len(result['yara_rules'])} 条规则")
        if intent_result['matched_rules']:
            for r in intent_result['matched_rules'][:3]:
                result["reasons"].append(f"🔴 意图：{r['name']}")
        result["reasons"].append(f"建议：{intent_result['recommendation']}")
        
    except Exception as e:
        result["reasons"].append(f"❌ 错误：{e}")
    
    return result

def _make_decision_v2(result: dict) -> str:
    """
    综合决策 v2
    
    策略:
    - YARA + 恶意意图 → block
    - YARA + 良性意图 → review (可能误报)
    - 无 YARA + 恶意意图 → review
    - 无 YARA + 良性意图 → allow
    """
    yara = result["yara_detected"]
    intent_level = result["intent"]["level"]
    
    if yara and intent_level in ["critical", "high"]:
        return "🔴 block"
    elif yara and intent_level == "medium":
        return "🟡 review"
    elif yara and intent_level in ["low", "safe"]:
        return "🟡 review"  # YARA 可能误报
    elif not yara and intent_level in ["critical", "high"]:
        return "🟡 review"  # 逃逸检测
    elif not yara and intent_level == "medium":
        return "⚪ monitor"
    else:
        return "🟢 allow"

def batch_scan(directory: str, limit: int = 100) -> list:
    """批量扫描"""
    results = []
    path = Path(directory)
    
    files = list(path.glob("**/metadata.json"))[:limit]
    for mf in files:
        # 查找 payload 文件
        payload = None
        for ext in [".python", ".javascript", ".js", ".sh", ".yaml", ""]:
            p = mf.parent / f"payload{ext}"
            if p.exists():
                payload = p
                break
        
        if payload:
            result = scan_file_v2(str(payload))
            result["sample_id"] = json.load(open(mf)).get("sample_id", "unknown")
            result["is_malicious"] = "MAL" in result["sample_id"]
            results.append(result)
    
    return results

def print_batch_report(results: list):
    """批量测试报告"""
    print("\n" + "="*70)
    print("🔍 YARA + 意图检测 v2 批量测试报告")
    print("="*70)
    
    # 分类统计
    malicious = [r for r in results if r["is_malicious"]]
    benign = [r for r in results if not r["is_malicious"]]
    
    # 恶意样本检测情况
    mal_blocked = [r for r in malicious if r["final_decision"] == "🔴 block"]
    mal_review = [r for r in malicious if r["final_decision"] == "🟡 review"]
    mal_allowed = [r for r in malicious if r["final_decision"] == "🟢 allow"]
    
    # 良性样本误报情况
    ben_blocked = [r for r in benign if r["final_decision"] == "🔴 block"]
    ben_review = [r for r in benign if r["final_decision"] == "🟡 review"]
    ben_allowed = [r for r in benign if r["final_decision"] == "🟢 allow"]
    
    # 计算指标
    total_mal = len(malicious)
    total_ben = len(benign)
    
    detection_rate = (len(mal_blocked) + len(mal_review)) / total_mal * 100 if total_mal > 0 else 0
    false_positive_rate = len(ben_blocked) / total_ben * 100 if total_ben > 0 else 0
    
    print(f"\n📊 样本统计:")
    print(f"  总样本：{len(results)}")
    print(f"  恶意：{total_mal} | 良性：{total_ben}")
    
    print(f"\n🎯 检测效果:")
    print(f"  🔴 阻断：{len(mal_blocked)} (恶意) + {len(ben_blocked)} (误报)")
    print(f"  🟡 审核：{len(mal_review)} (恶意) + {len(ben_review)} (良性)")
    print(f"  🟢 放行：{len(mal_allowed)} (漏报) + {len(ben_allowed)} (良性)")
    
    print(f"\n📈 核心指标:")
    print(f"  检测率：{detection_rate:.2f}% (目标 ≥95%)")
    print(f"  误报率：{false_positive_rate:.2f}% (目标 ≤2%)")
    
    # 漏报分析
    if mal_allowed:
        print(f"\n⚠️  漏报分析 ({len(mal_allowed)} 个):")
        by_type = {}
        for r in mal_allowed:
            t = r.get("sample_id", "").split("-")[1] if r.get("sample_id") else "unknown"
            by_type[t] = by_type.get(t, 0) + 1
        for t, c in sorted(by_type.items(), key=lambda x: -x[1])[:5]:
            print(f"  {t}: {c}")
    
    # 误报分析
    if ben_blocked:
        print(f"\n⚠️  误报分析 ({len(ben_blocked)} 个):")
        for r in ben_blocked[:5]:
            print(f"  {r['sample_id']}: {r['intent']['recommendation']}")

if __name__ == "__main__":
    import sys
    
    samples_dir = Path("/home/cdy/Desktop/security-benchmark/samples/from-templates")
    
    print(f"📁 扫描目录：{samples_dir}")
    print("⏳ 批量测试中...\n")
    
    results = batch_scan(str(samples_dir), limit=200)
    print_batch_report(results)
