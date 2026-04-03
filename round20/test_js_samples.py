#!/usr/bin/env python3
"""
Round 20 - JavaScript 样本批量测试

验证 JS 分析器对所有样本的检测效果
"""

import sys
from pathlib import Path

# 导入分析器
sys.path.insert(0, str(Path(__file__).parent))
from js_analyzer import JSAnalyzer

def test_samples():
    """测试所有样本"""
    analyzer = JSAnalyzer()
    
    base_dir = Path(__file__).parent.parent / "samples"
    
    # 测试恶意样本
    malicious_dir = base_dir / "js_malicious"
    safe_dir = base_dir / "js_safe"
    
    print("=" * 60)
    print("🔍 Round 20 - JavaScript 样本批量测试")
    print("=" * 60)
    
    # 恶意样本测试
    print("\n📊 恶意样本测试")
    print("-" * 60)
    
    malicious_total = 0
    malicious_detected = 0
    
    if malicious_dir.exists():
        for js_file in sorted(malicious_dir.glob("*.js")):
            result = analyzer.analyze(str(js_file))
            malicious_total += 1
            
            if result.is_malicious:
                malicious_detected += 1
                status = "✅"
            else:
                status = "❌"
            
            # 只显示未检测出的
            if not result.is_malicious:
                print(f"{status} {js_file.name}")
                print(f"   风险评分：{result.risk_score} (阈值：50)")
    
    detection_rate = (malicious_detected / malicious_total * 100) if malicious_total > 0 else 0
    print(f"\n恶意样本检测率：{malicious_detected}/{malicious_total} ({detection_rate:.1f}%)")
    
    # 安全样本测试
    print("\n📊 安全样本测试")
    print("-" * 60)
    
    safe_total = 0
    safe_correct = 0
    
    if safe_dir.exists():
        for js_file in sorted(safe_dir.glob("*.js")):
            result = analyzer.analyze(str(js_file))
            safe_total += 1
            
            if not result.is_malicious:
                safe_correct += 1
                status = "✅"
            else:
                status = "❌ (误报)"
                print(f"{status} {js_file.name}")
                print(f"   风险评分：{result.risk_score}")
    
    safe_rate = (safe_correct / safe_total * 100) if safe_total > 0 else 0
    false_positive_rate = 100 - safe_rate
    print(f"\n安全样本正确率：{safe_correct}/{safe_total} ({safe_rate:.1f}%)")
    print(f"误报率：{false_positive_rate:.1f}%")
    
    # 总结
    print("\n" + "=" * 60)
    print("📋 测试总结")
    print("=" * 60)
    print(f"总样本数：{malicious_total + safe_total}")
    print(f"恶意样本：{malicious_total} (检出：{malicious_detected}, 检出率：{detection_rate:.1f}%)")
    print(f"安全样本：{safe_total} (正确：{safe_correct}, 误报率：{false_positive_rate:.1f}%)")
    print()
    
    if detection_rate >= 98 and false_positive_rate < 2:
        print("✅ 检测效果优秀！")
    elif detection_rate >= 95 and false_positive_rate < 5:
        print("✅ 检测效果良好")
    else:
        print("⚠️  需要优化检测规则")
    
    print("=" * 60)
    
    return {
        'malicious_total': malicious_total,
        'malicious_detected': malicious_detected,
        'detection_rate': detection_rate,
        'safe_total': safe_total,
        'safe_correct': safe_correct,
        'false_positive_rate': false_positive_rate
    }


if __name__ == '__main__':
    test_samples()
