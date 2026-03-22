#!/usr/bin/env python3
"""
生成规则索引 - 安全版本
使用 head/grep 等工具，不读取整个文件
"""

import os
import re
import yaml
from pathlib import Path
from collections import defaultdict

# 路径配置
RULES_DIR = Path("/home/cdy/.openclaw/workspace/skills/agent-security-skill-scanner/expert_mode/rules")
OUTPUT_FILE = RULES_DIR / "RULES_INDEX.yaml"

def safe_read_head(filepath, lines=10):
    """安全读取文件头部"""
    try:
        import subprocess
        result = subprocess.run(
            ["head", f"-n{lines}", str(filepath)],
            capture_output=True, text=True, timeout=5
        )
        return result.stdout if result.returncode == 0 else ""
    except Exception as e:
        return f"# Error: {e}"

def scan_rules():
    """扫描规则目录，生成索引"""
    rules = []
    categories = {}
    
    # 遍历所有规则目录
    for category_dir in RULES_DIR.iterdir():
        if not category_dir.is_dir():
            continue
            
        category = category_dir.name
        categories[category] = 0
        
        # 递归遍历子目录
        for rule_file in category_dir.rglob("*"):
            if rule_file.is_file() and rule_file.suffix in ['.yara', '.yml', '.json']:
                # 获取元数据
                rule_info = extract_metadata(rule_file, category)
                if rule_info:
                    rules.append(rule_info)
                    categories[category] += 1
    
    return rules, categories

def extract_metadata(filepath, category):
    """从规则文件提取元数据"""
    ext = filepath.suffix
    
    try:
        if ext == '.yara':
            return extract_yara_metadata(filepath, category)
        elif ext in ['.yml', '.yaml']:
            return extract_yaml_metadata(filepath, category)
        elif ext == '.json':
            return extract_json_metadata(filepath, category)
    except Exception as e:
        print(f"Warning: {filepath.name}: {e}")
    
    return None

def extract_yara_metadata(filepath, category):
    """提取 YARA 规则元数据"""
    content = safe_read_head(filepath, 30)
    
    # 提取 rule name
    rule_match = re.search(r'rule\s+(\w+)', content)
    name = rule_match.group(1) if rule_match else filepath.stem
    
    # 提取 description
    desc_match = re.search(r'description\s*=\s*"([^"]+)"', content)
    description = desc_match.group(1) if desc_match else ""
    
    # 提取 severity
    sev_match = re.search(r'severity\s*=\s*"([^"]+)"', content)
    severity = sev_match.group(1) if sev_match else "medium"
    
    # 提取 category
    cat_match = re.search(r'category\s*=\s*"([^"]+)"', content)
    rule_category = cat_match.group(1) if cat_match else category
    
    # 提取 tags
    tags_match = re.search(r'tags\s*=\s*\[([^\]]+)\]', content)
    tags = [t.strip().strip('"') for t in tags_match.group(1).split(',')] if tags_match else []
    
    return {
        "id": name,
        "file": str(filepath.relative_to(RULES_DIR)),
        "type": "YARA",
        "category": rule_category,
        "severity": severity,
        "description": description,
        "tags": tags
    }

def extract_yaml_metadata(filepath, category):
    """提取 YAML 规则元数据"""
    content = safe_read_head(filepath, 30)
    
    # 简单提取 title
    title_match = re.search(r'title:\s*(.+)', content)
    title = title_match.group(1).strip() if title_match else filepath.stem
    
    return {
        "id": filepath.stem,
        "file": str(filepath.relative_to(RULES_DIR)),
        "type": "Sigma",
        "category": category,
        "description": title,
        "tags": [category]
    }

def extract_json_metadata(filepath, category):
    """提取 JSON 规则元数据"""
    content = safe_read_head(filepath, 30)
    
    # 尝试提取 name/description
    name_match = re.search(r'"name"\s*:\s*"([^"]+)"', content)
    desc_match = re.search(r'"description"\s*:\s*"([^"]+)"', content)
    
    return {
        "id": filepath.stem,
        "file": str(filepath.relative_to(RULES_DIR)),
        "type": "IOC" if "ioc" in category.lower() else "Runtime",
        "category": category,
        "description": desc_match.group(1) if desc_match else name_match.group(1) if name_match else "",
        "tags": [category]
    }

def main():
    print("🔍 扫描规则目录...")
    
    rules, categories = scan_rules()
    
    # 构建索引
    index = {
        "index_version": "1.0",
        "last_updated": "2026-03-18",
        "total_rules": len(rules),
        "statistics": categories,
        "rules": rules[:50]  # 限制索引大小，只存前 50 条的元数据
    }
    
    # 写入文件
    OUTPUT_FILE.write_text(yaml.dump(index, allow_unicode=True, default_flow_style=False))
    
    print(f"✅ 索引已生成: {OUTPUT_FILE}")
    print(f"   总规则数: {len(rules)}")
    print(f"   索引大小: {len(str(index))} bytes")

if __name__ == "__main__":
    main()
