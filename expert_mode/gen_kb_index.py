#!/usr/bin/env python3
"""
生成知识库轻量索引 - 安全版本
使用 head 工具，不读取整个文件
"""

import subprocess
import json
import yaml
from pathlib import Path

KB_DIR = Path("/home/cdy/.openclaw/workspace/skills/agent-security-skill-scanner/expert_mode/shards/knowledge_base")
OUTPUT_FILE = Path("/home/cdy/.openclaw/workspace/skills/agent-security-skill-scanner/expert_mode/kb_index_light.yaml")

def safe_head(filepath, lines=30):
    """安全读取文件头部"""
    try:
        result = subprocess.run(
            ["head", f"-n{lines}", str(filepath)],
            capture_output=True, text=True, timeout=5
        )
        return result.stdout if result.returncode == 0 else ""
    except Exception as e:
        return f"# Error: {e}"

def parse_json_head(content, max_items=5):
    """解析 JSON 头部，提取摘要"""
    try:
        data = json.loads(content)
        
        # 处理不同的 JSON 结构
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, list) and value:
                    return {
                        "key": key,
                        "count": len(value),
                        "sample": str(value[0])[:100] if value else ""
                    }
        
        return {"error": "unknown structure"}
    except json.JSONDecodeError:
        return {"error": "parse failed"}

def scan_knowledge_base():
    """扫描知识库目录"""
    files = []
    
    for f in KB_DIR.glob("*.json"):
        # 获取文件大小
        size = f.stat().st_size
        
        # 读取头部获取摘要
        head_content = safe_head(f, 30)
        summary = parse_json_head(head_content)
        
        files.append({
            "name": f.name,
            "size_bytes": size,
            "size_mb": round(size / 1024 / 1024, 2),
            "summary": summary
        })
    
    return files

def main():
    print("🔍 扫描知识库目录...")
    
    files = scan_knowledge_base()
    
    # 构建索引
    total_size = sum(f["size_bytes"] for f in files)
    
    index = {
        "index_version": "1.0",
        "last_updated": "2026-03-18",
        "total_files": len(files),
        "total_size_mb": round(total_size / 1024 / 1024, 2),
        
        "files": files,
        
        "exclude_from_loading": [
            "kb_index.json (3.9MB - 太大)",
            "kb_index_shards.json (3.2MB - 太大)",
            "KB_SUMMARY.md (1.2MB - 太大)"
        ],
        
        "load_strategy": {
            "description": "使用 kb_index_light.yaml 获取元数据",
            "do_not_load": [
                "kb_index.json",
                "kb_index_shards.json", 
                "KB_SUMMARY.md"
            ],
            "if_needed_load": [
                "shards/knowledge_base/index.json (727 bytes - 安全)",
                "shards/knowledge_base/experiments.json (23 bytes - 安全)"
            ]
        }
    }
    
    # 写入文件
    OUTPUT_FILE.write_text(yaml.dump(index, allow_unicode=True, default_flow_style=False))
    
    print(f"✅ 索引已生成: {OUTPUT_FILE}")
    print(f"   文件数: {len(files)}")
    print(f"   总大小: {index['total_size_mb']} MB")

if __name__ == "__main__":
    main()
