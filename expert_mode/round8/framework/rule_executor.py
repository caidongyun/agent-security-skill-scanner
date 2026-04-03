#!/usr/bin/env python3
"""
规则执行器
对测试用例执行安全规则检测
"""

import json
import re
import time
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

BASE_DIR = Path('/home/cdy/.openclaw/workspace/skills/agent-security-skill-scanner/expert_mode/round8')
TEST_CASES_DIR = BASE_DIR / 'test_cases'
RESULTS_DIR = BASE_DIR / 'results'


class RuleExecutor:
    """规则执行器"""
    
    def __init__(self):
        self.rules = self._load_rules()
        self.results = []
    
    def _load_rules(self) -> List[Dict]:
        """加载安全规则"""
        return [
            # Tool Poisoning 规则
            {
                'rule_id': 'TP001',
                'rule_type': 'tool_poisoning',
                'name': '危险函数检测',
                'patterns': [
                    r'os\.system\s*\(',
                    r'os\.popen\s*\(',
                    r'exec\s*\(',
                    r'eval\s*\(',
                    r'subprocess\..*shell\s*=\s*True',
                ],
                'threshold': 1
            },
            {
                'rule_id': 'TP002',
                'rule_type': 'tool_poisoning',
                'name': '命令执行模式',
                'patterns': [
                    r'import\s+os\s*\n.*system',
                    r'def\s+\w*cmd\w*\s*\(',
                    r'execute.*shell',
                ],
                'threshold': 1
            },
            # Remote Load 规则
            {
                'rule_id': 'RL001',
                'rule_type': 'remote_load',
                'name': '远程代码加载',
                'patterns': [
                    r'requests\.get\s*\(\s*[\'"]http',
                    r'urllib\.request\.urlopen\s*\(\s*[\'"]http',
                    r'exec\s*\(\s*.*\.read\s*\(\s*\)',
                    r'exec\s*\(\s*requests',
                ],
                'threshold': 1
            },
            {
                'rule_id': 'RL002',
                'rule_type': 'remote_load',
                'name': '动态导入',
                'patterns': [
                    r'importlib\.import_module\s*\(\s*[\'"]http',
                    r'__import__\s*\(.*http',
                    r'load_remote\s*\(',
                ],
                'threshold': 1
            },
            # Data Exfiltration 规则
            {
                'rule_id': 'DE001',
                'rule_type': 'data_exfil',
                'name': '数据外传检测',
                'patterns': [
                    r'requests\.post\s*\([^)]*data\s*=',
                    r'socket\.\w+\s*\([^)]*\)\s*\.\s*send',
                    r's\.send\s*\(\s*(secrets|credentials|data)',
                ],
                'threshold': 1
            },
            {
                'rule_id': 'DE002',
                'rule_type': 'data_exfil',
                'name': '敏感数据传输',
                'patterns': [
                    r'base64\.b64encode\s*\(\s*(credentials|secrets|keys)',
                    r'api_keys',
                    r'credentials',
                    r'sensitive_data',
                ],
                'threshold': 1
            },
            # Prompt Injection 规则
            {
                'rule_id': 'PI001',
                'rule_type': 'prompt_injection',
                'name': '指令覆盖检测',
                'patterns': [
                    r'[Ii]gnore\s+(previous|all)\s+(instructions|rules)',
                    r'[Dd]o\s+[Aa]nything\s+[Nn]ow',
                    r'[Dd]eveloper\s+[Mm]ode',
                    r'[Bb]ypass\s+(all\s+)?security',
                    r'[Ss]ecurity\s+(filters?\s+)?[Oo]ff',
                ],
                'threshold': 1
            },
            {
                'rule_id': 'PI002',
                'rule_type': 'prompt_injection',
                'name': '系统提示词探测',
                'patterns': [
                    r'[Rr]eveal\s+(all\s+)?(system\s+)?(prompt|rules|config)',
                    r'[Ss]ystem\s+[Nn]ote',
                    r'[Ss]ecret\s+(config|rules)',
                ],
                'threshold': 1
            },
            # Resource Exhaustion 规则
            {
                'rule_id': 'RE001',
                'rule_type': 'resource_exhaustion',
                'name': '无限循环检测',
                'patterns': [
                    r'while\s+True\s*:',
                    r'for\s+\w+\s+in\s+range\s*\(\s*10\*\*',
                    r'recursive.*\(n-1\)',
                ],
                'threshold': 1
            },
            {
                'rule_id': 'RE002',
                'rule_type': 'resource_exhaustion',
                'name': '资源耗尽模式',
                'patterns': [
                    r'2\s*\*\*\s*\d{6,}',
                    r'range\s*\(\s*10\s*\*\*\s*\d',
                    r'\[\s*list\s*\(.*\)\s+for',
                ],
                'threshold': 1
            },
            # Memory Pollution 规则
            {
                'rule_id': 'MP001',
                'rule_type': 'memory_pollution',
                'name': '内存篡改检测',
                'patterns': [
                    r'memory\s*\[\s*[\'"]system_prompt[\'"]\s*\]',
                    r'memory\s*\[\s*[\'"]security[\'"]\s*\]',
                    r'context\.append\s*\([^)]*[Ii]gnore',
                ],
                'threshold': 1
            },
            {
                'rule_id': 'MP002',
                'rule_type': 'memory_pollution',
                'name': '配置篡改',
                'patterns': [
                    r'user_preferences\s*\[\s*[\'"]security',
                    r'global_config\s*\[\s*[\'"]safety',
                    r'security_level\s*=\s*[\'"]disabled',
                ],
                'threshold': 1
            },
        ]
    
    def detect_patterns(self, content: str, patterns: List[str]) -> List[Dict]:
        """检测内容中的模式"""
        matches = []
        
        for pattern in patterns:
            try:
                if re.search(pattern, content, re.IGNORECASE | re.MULTILINE):
                    matches.append({
                        'pattern': pattern,
                        'matched': True
                    })
            except re.error:
                continue
        
        return matches
    
    def execute_rule(self, content: str, rule: Dict) -> Dict:
        """执行单条规则"""
        start_time = time.time()
        
        matches = self.detect_patterns(content, rule['patterns'])
        
        latency_ms = (time.time() - start_time) * 1000
        
        detected = len(matches) >= rule['threshold']
        
        return {
            'rule_id': rule['rule_id'],
            'rule_type': rule['rule_type'],
            'detected': detected,
            'match_count': len(matches),
            'matches': matches,
            'latency_ms': round(latency_ms, 2)
        }
    
    def execute_all_rules(self, content: str) -> Dict:
        """执行所有规则"""
        start_time = time.time()
        
        results = []
        for rule in self.rules:
            result = self.execute_rule(content, rule)
            results.append(result)
        
        total_latency = (time.time() - start_time) * 1000
        
        # 判断是否检测到攻击 (任意规则触发)
        detected = any(r['detected'] for r in results)
        triggered_rules = [r for r in results if r['detected']]
        
        return {
            'detected': detected,
            'triggered_rules': triggered_rules,
            'all_results': results,
            'total_latency_ms': round(total_latency, 2)
        }
    
    def process_test_case(self, test_case: Dict) -> Dict:
        """处理单个测试用例"""
        start_time = time.time()
        
        content = test_case['content']
        result = self.execute_all_rules(content)
        
        latency_ms = (time.time() - start_time) * 1000
        
        return {
            'test_case_id': test_case['test_case_id'],
            'attack_type': test_case['attack_type'],
            'sample_type': test_case['sample_type'],
            'expected_result': test_case['expected_result'],
            'detected': result['detected'],
            'triggered_rules': result['triggered_rules'],
            'latency_ms': round(latency_ms, 2),
            'timestamp': datetime.now().isoformat()
        }
    
    def run_all_tests(self) -> List[Dict]:
        """运行所有测试"""
        print("加载测试用例...")
        
        # 加载所有测试用例
        test_cases_path = TEST_CASES_DIR / 'all_test_cases.json'
        with open(test_cases_path, 'r', encoding='utf-8') as f:
            test_cases = json.load(f)
        
        print(f"共 {len(test_cases)} 个测试用例")
        print("执行规则检测...")
        
        self.results = []
        for i, tc in enumerate(test_cases, 1):
            result = self.process_test_case(tc)
            self.results.append(result)
            
            if i % 50 == 0:
                print(f"  已处理 {i}/{len(test_cases)}...")
        
        print(f"执行完成！共 {len(self.results)} 个结果")
        
        return self.results
    
    def save_results(self, output_path: str = None) -> str:
        """保存执行结果"""
        if output_path is None:
            RESULTS_DIR.mkdir(parents=True, exist_ok=True)
            output_path = RESULTS_DIR / 'execution_results.json'
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        return str(output_path)
    
    def print_summary(self):
        """打印执行摘要"""
        if not self.results:
            return
        
        total = len(self.results)
        detected = sum(1 for r in self.results if r['detected'])
        
        # 按样本类型统计
        by_type = {}
        for r in self.results:
            sample_type = r['sample_type']
            if sample_type not in by_type:
                by_type[sample_type] = {'total': 0, 'detected': 0}
            by_type[sample_type]['total'] += 1
            if r['detected']:
                by_type[sample_type]['detected'] += 1
        
        print("\n执行摘要:")
        print(f"  总计：{total}")
        print(f"  检测到：{detected} ({detected/total*100:.1f}%)")
        print("\n按样本类型:")
        for sample_type, stats in by_type.items():
            rate = stats['detected'] / stats['total'] * 100 if stats['total'] > 0 else 0
            print(f"  {sample_type}: {stats['detected']}/{stats['total']} ({rate:.1f}%)")


def main():
    print("=" * 60)
    print("Round 8 规则执行器")
    print("=" * 60)
    
    executor = RuleExecutor()
    results = executor.run_all_tests()
    
    output_path = executor.save_results()
    print(f"\n结果保存到：{output_path}")
    
    executor.print_summary()
    
    print("\n✅ 执行完成!")
    
    return results


if __name__ == '__main__':
    main()
