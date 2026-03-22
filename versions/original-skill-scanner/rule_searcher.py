#!/usr/bin/env python3
"""
规则检索系统 - 索引 + grep
不依赖向量数据库，直接搜索结构化文本
"""

import subprocess
import yaml
import json
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass

# 路径配置
RULES_DIR = Path("/home/cdy/.openclaw/workspace/skills/agent-security-skill-scanner/expert_mode/rules")
RULES_INDEX = RULES_DIR / "RULES_INDEX.yaml"

@dataclass
class SearchResult:
    """搜索结果"""
    rule_id: str
    file: str
    category: str
    description: str
    tags: List[str]
    matched_lines: str  # grep 匹配的行
    
    def to_context(self) -> str:
        """转换为上下文格式"""
        return f"""
## {self.rule_id} ({self.category})

**描述**: {self.description}
**标签**: {', '.join(self.tags)}
**文件**: {self.file}

**匹配内容**:
{self.matched_lines[:500]}
"""


class RuleSearcher:
    """规则搜索引擎"""
    
    def __init__(self):
        self.index = self._load_index()
    
    def _load_index(self) -> Dict:
        """加载索引"""
        if not RULES_INDEX.exists():
            return {"rules": [], "statistics": {}}
        
        with open(RULES_INDEX, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def search(self, keywords: List[str], max_results: int = 3) -> List[SearchResult]:
        """
        搜索规则
        
        Args:
            keywords: 搜索关键词
            max_results: 最大返回结果数
            
        Returns:
            匹配的规则列表
        """
        results = []
        keywords_lower = [k.lower() for k in keywords]
        
        for rule in self.index.get("rules", []):
            # 匹配标签
            rule_tags = [t.lower() for t in rule.get("tags", [])]
            rule_desc = rule.get("description", "").lower()
            rule_id = rule.get("id", "").lower()
            
            # 计算匹配分数
            score = 0
            for kw in keywords_lower:
                if kw in rule_tags:
                    score += 3
                if kw in rule_desc:
                    score += 2
                if kw in rule_id:
                    score += 1
            
            if score > 0:
                # 用 grep 获取匹配行
                matched_lines = self._grep_matched_lines(
                    rule.get("file", ""),
                    keywords
                )
                
                results.append(SearchResult(
                    rule_id=rule.get("id", ""),
                    file=rule.get("file", ""),
                    category=rule.get("category", ""),
                    description=rule.get("description", ""),
                    tags=rule.get("tags", []),
                    matched_lines=matched_lines
                ))
        
        # 按分数排序，返回 Top N
        results.sort(key=lambda x: len(x.matched_lines), reverse=True)
        return results[:max_results]
    
    def _grep_matched_lines(self, filepath: str, keywords: List[str], max_bytes: int = 500) -> str:
        """用 grep 获取匹配的行"""
        if not filepath:
            return ""
        
        full_path = RULES_DIR / filepath
        if not full_path.exists():
            return f"[文件不存在: {filepath}]"
        
        try:
            # 构造 grep 命令
            pattern = "|".join(keywords)
            result = subprocess.run(
                ["grep", "-i", "-n", pattern, str(full_path)],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                # 限制返回的行数和长度
                limited_lines = lines[:10]
                content = '\n'.join(limited_lines)
                
                # 限制总字节数
                if len(content) > max_bytes:
                    content = content[:max_bytes] + "..."
                
                return content
            else:
                return "[无匹配]"
                
        except subprocess.TimeoutExpired:
            return "[搜索超时]"
        except Exception as e:
            return f"[搜索错误: {e}]"
    
    def search_by_category(self, category: str) -> List[Dict]:
        """按类别搜索"""
        return [
            rule for rule in self.index.get("rules", [])
            if category.lower() in rule.get("category", "").lower()
        ]
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        return self.index.get("statistics", {})
    
    def get_total_rules(self) -> int:
        """获取总规则数"""
        return self.index.get("total_rules", 0)


def search_rules(query: str, max_results: int = 3) -> str:
    """
    搜索规则 - 主入口
    
    Args:
        query: 搜索查询 (可以是多个关键词)
        max_results: 最大返回结果数
        
    Returns:
        格式化的搜索结果字符串
    """
    # 解析关键词
    keywords = [k.strip() for k in query.replace(",", " ").split() if k.strip()]
    
    if not keywords:
        return "请提供搜索关键词"
    
    # 搜索
    searcher = RuleSearcher()
    results = searcher.search(keywords, max_results)
    
    if not results:
        return f"未找到与 {', '.join(keywords)} 相关的规则"
    
    # 格式化结果
    context_parts = [
        f"# 搜索结果: {query}\n",
        f"找到 {len(results)} 条相关规则 (显示前 {max_results} 条)\n",
        "---"
    ]
    
    for result in results:
        context_parts.append(result.to_context())
    
    return '\n'.join(context_parts)


# CLI 入口
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python3 rule_searcher.py <搜索关键词>")
        print("示例: python3 rule_searcher.py APT29 YARA")
        sys.exit(1)
    
    query = " ".join(sys.argv[1:])
    result = search_rules(query)
    print(result)
