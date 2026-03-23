"""
Rule Agent - 规则管理代理

负责规则加载、匹配、生成和优化
"""

import asyncio
from typing import Dict, List, Optional, Any
from pathlib import Path
import yaml

from agents.base_agent import BaseAgent, Task, Result, AgentStatus


class RuleAgent(BaseAgent):
    """规则 Agent - 规则管理"""
    
    def __init__(self, rules_path: str = "./rules/"):
        super().__init__(
            name="RuleAgent",
            description="规则管理 - 加载/匹配/生成/优化",
            capabilities=["rules", "match", "generate", "optimize"]
        )
        self.rules_path = Path(rules_path)
        self.rules = []
        self._load_rules()
    
    def _load_rules(self):
        """加载规则"""
        if not self.rules_path.exists():
            print(f"⚠️ 规则目录不存在：{self.rules_path}")
            return
        
        # 加载 YAML 规则
        for rule_file in self.rules_path.glob("*.yaml"):
            try:
                with open(rule_file, 'r', encoding='utf-8') as f:
                    rules = yaml.safe_load(f)
                    if isinstance(rules, list):
                        self.rules.extend(rules)
                    elif isinstance(rules, dict):
                        self.rules.append(rules)
            except Exception as e:
                print(f"⚠️ 加载规则失败 {rule_file}: {e}")
        
        # 加载 YARA 规则
        import re
        for rule_file in self.rules_path.rglob("*.yar"):
            try:
                with open(rule_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    rule_names = re.findall(r'rule\s+(\w+)', content)
                    for name in rule_names:
                        self.rules.append({
                            'name': name,
                            'type': 'yara',
                            'file': str(rule_file),
                            'content': content[:500]
                        })
            except Exception as e:
                print(f"⚠️ 加载YARA规则失败 {rule_file}: {e}")
        
        print(f"✅ 已加载 {len(self.rules)} 条规则")
    
    async def execute(self, task: Task) -> Result:
        """执行规则任务"""
        try:
            if task.type == "match":
                return await self._match_rules(task)
            elif task.type == "generate":
                return await self._generate_rule(task)
            elif task.type == "optimize":
                return await self._optimize_rules(task)
            elif task.type == "validate":
                return await self._validate_rule(task)
            elif task.type == "search":
                return await self._search_rules(task)
            else:
                return Result(
                    task_id=task.id,
                    agent_id=self.agent_id,
                    success=False,
                    error=f"未知任务类型：{task.type}"
                )
        except Exception as e:
            return Result(
                task_id=task.id,
                agent_id=self.agent_id,
                success=False,
                error=str(e)
            )
    
    async def _match_rules(self, task: Task) -> Result:
        """规则匹配"""
        target = task.parameters.get("target")
        code = task.parameters.get("code")
        tier = task.parameters.get("tier", "all")
        
        if not code and not target:
            return Result(task_id=task.id, agent_id=self.agent_id, success=False, error="缺少代码或目标文件")
        
        # 读取代码
        if not code and target:
            file_path = Path(target)
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    code = f.read()
            else:
                return Result(task_id=task.id, agent_id=self.agent_id, success=False, error=f"文件不存在：{target}")
        
        # 过滤规则
        rules_to_match = self.rules
        if tier != "all":
            rules_to_match = [r for r in self.rules if r.get('tier') == tier]
        
        # 匹配规则
        matches = []
        for rule in rules_to_match:
            match_result = self._match_single_rule(code, rule)
            if match_result['matched']:
                matches.append({
                    'rule_id': rule.get('id'),
                    'rule_name': rule.get('name'),
                    'tier': rule.get('tier'),
                    'severity': rule.get('severity'),
                    'description': rule.get('description'),
                    'match_details': match_result['details']
                })
        
        return Result(task_id=task.id, agent_id=self.agent_id, success=True,
            data={
                'total_rules': len(rules_to_match),
                'matched_rules': len(matches),
                'matches': matches
            }
        )
    
    def _match_single_rule(self, code: str, rule: Dict) -> Dict:
        """匹配单条规则"""
        import re
        
        rule_type = rule.get('type', 'regex')
        pattern = rule.get('pattern')
        
        # YARA 规则特殊处理
        if rule_type == 'yara':
            content = rule.get('content', '')
            # 提取 YARA 规则中的字符串
            yara_strings = re.findall(r'\$[\w]+ = "([^"]+)"', content)
            if yara_strings:
                found = [s for s in yara_strings if s.lower() in code.lower()]
                return {
                    'matched': len(found) > 0,
                    'details': {
                        'count': len(found),
                        'keywords': found
                    }
                }
            return {'matched': False}
        
        if not pattern:
            return {'matched': False}
        
        try:
            if rule_type == 'regex':
                flags = re.MULTILINE
                if rule.get('case_insensitive', False):
                    flags |= re.IGNORECASE
                
                matches = re.findall(pattern, code, flags)
                return {
                    'matched': len(matches) > 0,
                    'details': {
                        'count': len(matches),
                        'samples': matches[:5]  # 最多返回 5 个样本
                    }
                }
            elif rule_type == 'keyword':
                keywords = pattern if isinstance(pattern, list) else [pattern]
                found = [kw for kw in keywords if kw in code]
                return {
                    'matched': len(found) > 0,
                    'details': {
                        'count': len(found),
                        'keywords': found
                    }
                }
            else:
                return {'matched': False, 'error': f'未知规则类型：{rule_type}'}
        except Exception as e:
            return {'matched': False, 'error': str(e)}
    
    async def _generate_rule(self, task: Task) -> Result:
        """生成规则"""
        samples = task.parameters.get("samples", [])
        attack_type = task.parameters.get("attack_type")
        tier = task.parameters.get("tier", "L1")
        
        if not samples:
            return Result(task_id=task.id, agent_id=self.agent_id, success=False, error="缺少样本")
        
        # 从样本中提取共同特征
        common_patterns = self._extract_common_patterns(samples)
        
        # 生成规则
        generated_rules = []
        for pattern_info in common_patterns:
            rule = {
                'id': f"gen_{attack_type}_{len(generated_rules) + 1:03d}",
                'name': f"Generated {attack_type} Rule",
                'type': 'regex',
                'pattern': pattern_info['pattern'],
                'attack_type': attack_type,
                'tier': tier,
                'severity': 'medium',
                'description': f"Auto-generated rule for {attack_type}",
                'confidence': pattern_info['confidence'],
                'created_at': asyncio.get_event_loop().time()
            }
            generated_rules.append(rule)
        
        return Result(task_id=task.id, agent_id=self.agent_id, success=True,
            data={
                'generated_count': len(generated_rules),
                'rules': generated_rules
            }
        )
    
    def _extract_common_patterns(self, samples: List[str]) -> List[Dict]:
        """从样本中提取共同模式"""
        import re
        
        # 简化的模式提取
        patterns = []
        
        # 提取共同关键词
        all_words = []
        for sample in samples:
            words = re.findall(r'\b\w+\b', sample.lower())
            all_words.extend(words)
        
        # 统计词频
        from collections import Counter
        word_counts = Counter(all_words)
        
        # 选择高频词作为模式
        common_words = [word for word, count in word_counts.most_common(20) 
                       if count > len(samples) * 0.5]
        
        if common_words:
            pattern = '|'.join(re.escape(word) for word in common_words[:10])
            patterns.append({
                'pattern': pattern,
                'confidence': 0.8
            })
        
        return patterns
    
    async def _optimize_rules(self, task: Task) -> Result:
        """优化规则"""
        # 去重
        unique_rules = []
        seen_ids = set()
        
        for rule in self.rules:
            rule_id = rule.get('id')
            if rule_id and rule_id not in seen_ids:
                unique_rules.append(rule)
                seen_ids.add(rule_id)
        
        # 按层级分组
        tier_groups = {}
        for rule in unique_rules:
            tier = rule.get('tier', 'L1')
            if tier not in tier_groups:
                tier_groups[tier] = []
            tier_groups[tier].append(rule)
        
        return Result(task_id=task.id, agent_id=self.agent_id, success=True,
            data={
                'original_count': len(self.rules),
                'optimized_count': len(unique_rules),
                'removed_duplicates': len(self.rules) - len(unique_rules),
                'by_tier': {tier: len(rules) for tier, rules in tier_groups.items()}
            }
        )
    
    async def _validate_rule(self, task: Task) -> Result:
        """验证规则"""
        rule = task.parameters.get("rule")
        
        if not rule:
            return Result(task_id=task.id, agent_id=self.agent_id, success=False, error="缺少规则")
        
        errors = []
        warnings = []
        
        # 检查必需字段
        required_fields = ['id', 'name', 'type', 'pattern']
        for field in required_fields:
            if field not in rule:
                errors.append(f"缺少必需字段：{field}")
        
        # 检查规则类型
        valid_types = ['regex', 'keyword', 'ast', 'behavior']
        if rule.get('type') not in valid_types:
            errors.append(f"无效的规则类型：{rule.get('type')}")
        
        # 检查模式有效性
        if rule.get('type') == 'regex':
            try:
                import re
                re.compile(rule.get('pattern'))
            except Exception as e:
                errors.append(f"正则表达式无效：{e}")
        
        # 检查严重程度
        valid_severities = ['low', 'medium', 'high', 'critical']
        if rule.get('severity') not in valid_severities:
            warnings.append(f"建议的严重程度：{valid_severities}")
        
        return Result(task_id=task.id, agent_id=self.agent_id, success=len(errors) == 0,
            data={
                'valid': len(errors) == 0,
                'errors': errors,
                'warnings': warnings
            }
        )
    
    async def _search_rules(self, task: Task) -> Result:
        """搜索规则"""
        query = task.parameters.get("query")
        attack_type = task.parameters.get("attack_type")
        tier = task.parameters.get("tier")
        
        results = self.rules
        
        if query:
            results = [r for r in results if 
                      query.lower() in r.get('name', '').lower() or
                      query.lower() in r.get('description', '').lower()]
        
        if attack_type:
            results = [r for r in results if r.get('attack_type') == attack_type]
        
        if tier:
            results = [r for r in results if r.get('tier') == tier]
        
        return Result(task_id=task.id, agent_id=self.agent_id, success=True,
            data={
                'count': len(results),
                'rules': results
            }
        )
    
    def get_status(self) -> Dict:
        """获取状态"""
        # 按层级统计
        tier_stats = {}
        for rule in self.rules:
            tier = rule.get('tier', 'unknown')
            tier_stats[tier] = tier_stats.get(tier, 0) + 1
        
        # 按攻击类型统计
        attack_stats = {}
        for rule in self.rules:
            attack = rule.get('attack_type', 'unknown')
            attack_stats[attack] = attack_stats.get(attack, 0) + 1
        
        return {
            'name': self.name,
            'status': self._status.value,
            'capabilities': self.capabilities,
            'tasks_completed': self._tasks_completed,
            'total_rules': len(self.rules),
            'by_tier': tier_stats,
            'by_attack_type': attack_stats
        }
