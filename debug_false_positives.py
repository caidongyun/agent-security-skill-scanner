#!/usr/bin/env python3
"""调试误报"""

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
    benign_dir = SAMPLES_DIR / "benign"
    rules = load_sigma_rules()
    
    print("🔍 误报分析")
    print("=" * 60)
    print()
    
    false_positives = []
    
    for sample_file in benign_dir.glob("*.txt"):
        with open(sample_file) as f:
            content = f.read().strip()
        
        for rule in rules:
            is_match, keyword = check_sigma_match(rule, content)
            if is_match:
                false_positives.append({
                    "file": sample_file.name,
                    "content": content,
                    "rule": rule.get("title", "unknown"),
                    "keyword": keyword
                })
                print(f"⚠️  误报：{sample_file.name}")
                print(f"   规则：{rule.get('title', 'unknown')}")
                print(f"   关键词：{keyword}")
                print(f"   内容：{content[:100]}")
                print()
                break
    
    print(f"总误报数：{len(false_positives)}/{len(list(benign_dir.glob('*.txt')))}")

if __name__ == "__main__":
    main()
