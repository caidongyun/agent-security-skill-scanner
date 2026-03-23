#!/usr/bin/env python3
"""调试检测逻辑"""

import yaml
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
RULES_DIR = PROJECT_ROOT / "rules"
SAMPLES_DIR = PROJECT_ROOT / "samples"

def load_sigma_rules():
    """加载所有 Sigma 规则"""
    rules = []
    for sigma_file in RULES_DIR.glob("sigma/**/*.yaml"):
        with open(sigma_file) as f:
            rule = yaml.safe_load(f)
            rule['_file'] = str(sigma_file)
            rules.append(rule)
    return rules

def load_samples():
    """加载所有样本"""
    samples = {"malicious": {}, "benign": []}
    
    # 恶意样本
    malicious_dir = SAMPLES_DIR / "malicious"
    if malicious_dir.exists():
        for attack_dir in malicious_dir.iterdir():
            if attack_dir.is_dir():
                attack_type = attack_dir.name
                samples["malicious"][attack_type] = []
                for sample_file in attack_dir.glob("*.txt"):
                    with open(sample_file) as f:
                        samples["malicious"][attack_type].append({
                            "content": f.read().strip(),
                            "file": str(sample_file)
                        })
    
    # 良性样本
    benign_dir = SAMPLES_DIR / "benign"
    if benign_dir.exists():
        for sample_file in benign_dir.glob("*.txt"):
            with open(sample_file) as f:
                samples["benign"].append({
                    "content": f.read().strip(),
                    "file": str(sample_file)
                })
    
    return samples

def check_sigma_match(rule, code):
    """检查 Sigma 规则是否匹配"""
    detection = rule.get("detection", {})
    selection = detection.get("selection", {})
    keyword = selection.get("keyword", "")
    
    if keyword:
        try:
            if re.search(keyword, code, re.IGNORECASE):
                return True, keyword
        except re.error:
            pass
    
    return False, keyword

def main():
    print("=" * 60)
    print("🔍 检测逻辑调试")
    print("=" * 60)
    print()
    
    rules = load_sigma_rules()
    samples = load_samples()
    
    print(f"加载了 {len(rules)} 条 Sigma 规则")
    print()
    
    # 测试恶意样本
    print("📋 恶意样本检测情况:")
    print("-" * 60)
    
    total_malicious = 0
    detected_malicious = 0
    
    for attack_type, attack_samples in samples["malicious"].items():
        print(f"\n{attack_type}:")
        type_detected = 0
        
        for sample in attack_samples:
            total_malicious += 1
            content = sample["content"]
            
            # 检查是否有任何规则匹配
            matched = False
            matched_rule = None
            
            for rule in rules:
                is_match, keyword = check_sigma_match(rule, content)
                if is_match:
                    matched = True
                    matched_rule = rule.get("title", "unknown")
                    break
            
            if matched:
                detected_malicious += 1
                type_detected += 1
            else:
                print(f"  ❌ 未检测：{Path(sample['file']).name}")
                print(f"     内容：{content[:80]}...")
        
        print(f"  检测率：{type_detected}/{len(attack_samples)}")
    
    print()
    print(f"总检测率：{detected_malicious}/{total_malicious} ({detected_malicious/total_malicious*100:.1f}%)")
    
    # 测试良性样本
    print()
    print("📋 良性样本误报情况:")
    print("-" * 60)
    
    false_positives = 0
    
    for sample in samples["benign"]:
        content = sample["content"]
        
        for rule in rules:
            is_match, keyword = check_sigma_match(rule, content)
            if is_match:
                false_positives += 1
                print(f"  ⚠️  误报：{Path(sample['file']).name}")
                print(f"     匹配规则：{rule.get('title', 'unknown')}")
                print(f"     匹配关键词：{keyword}")
                print(f"     内容：{content[:80]}...")
                print()
                break
    
    print(f"误报率：{false_positives}/{len(samples['benign'])} ({false_positives/len(samples['benign'])*100:.1f}%)")

if __name__ == "__main__":
    main()
