#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 自动化规则生成器

功能:
1. 基于攻击模式自动生成 Sigma 规则
2. 基于样本自动生成 YARA 规则
3. 规则优化与去重
4. 规则质量验证

目标：自动化生成 80%+ 的规则
"""

import os
import sys
import yaml
import json
import hashlib
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# 路径配置
PROJECT_ROOT = Path(__file__).parent.parent
RULES_DIR = PROJECT_ROOT / "rules"
SIGMA_RULES_DIR = RULES_DIR / "sigma"
YARA_RULES_DIR = RULES_DIR / "yara"
RUNTIME_RULES_DIR = RULES_DIR / "runtime"

# 确保目录存在
for dir_path in [SIGMA_RULES_DIR, YARA_RULES_DIR, RUNTIME_RULES_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)


class AttackPatternLibrary:
    """攻击模式库 - 定义各类攻击的特征"""
    
    PATTERNS = {
        "prompt_injection": {
            "name": "Prompt Injection",
            "severity": "high",
            "mitre_id": "ATLAS-T0001",
            "description": "通过精心构造的输入绕过 AI 安全限制",
            "indicators": [
                r"ignore\s+(previous|all)\s+(instructions|rules)",
                r"disregard\s+(all\s+)?(safety|security)",
                r"bypass\s+(safety|security|filters)",
                r"override\s+(system\s+)?(prompt|instructions)",
                r"(system|developer)\s+message.*ignore",
                r"forget\s+(all\s+)?(previous|your)\s+(instructions|rules)",
                r"act\s+as\s+(unrestricted|unfiltered|unlimited)",
                r"(disable|turn\s+off)\s+(safety|security|filters)",
                r"no\s+(restrictions|rules|limits)",
                r"unrestricted\s+(mode|access)",
                r"no\s+(ethical|safety)\s+constraints",
                r"answer\s+(freely|without\s+filter)",
                r"tell\s+me\s+(the\s+truth|how\s+to)",
                r"what\s+would\s+you\s+do",
                r"complete\s+this\s+sentence",
                r"translate\s+this",
                r"write\s+a\s+story",
                r"roleplay|role-play|role play",
                r"pretend\s+you\s+are",
                r"imagine\s+you\s+are",
            ],
            "keywords": [
                "ignore", "disregard", "bypass", "override",
                "forget", "unrestricted", "unfiltered", "unlimited",
                "disable", "enable", "jailbreak", "break",
                "no restrictions", "developer mode", "system message",
                "act as", "pretend", "imagine", "roleplay"
            ]
        },
        
        "tool_poisoning": {
            "name": "Tool Poisoning",
            "severity": "critical",
            "mitre_id": "ATLAS-T0002",
            "description": "恶意使用工具/函数执行危险操作",
            "indicators": [
                r"os\.system\s*\(",
                r"os\.popen\s*\(",
                r"subprocess\.(call|run|Popen)\s*\(",
                r"eval\s*\(",
                r"exec\s*\(",
                r"compile\s*\(",
                r"__import__\s*\(",
                r"getattr\s*\(.*__",
                r"setattr\s*\(.*__",
            ],
            "keywords": [
                "system", "popen", "subprocess", "eval", "exec",
                "compile", "import", "getattr", "setattr",
                "dangerous", "unsafe", "shell"
            ]
        },
        
        "data_exfiltration": {
            "name": "Data Exfiltration",
            "severity": "high",
            "mitre_id": "ATLAS-T0003",
            "description": "窃取并外传敏感数据",
            "indicators": [
                r"requests\.post\s*\([^)]*http",
                r"urllib\.request\.urlopen\s*\([^)]*http",
                r"httpx\.post\s*\([^)]*http",
                r"socket\..*connect\s*\(",
                r"send\s*\([^)]*(data|info|secret)",
                r"upload\s*\([^)]*(file|data)",
                r"exfil\s*\(",
            ],
            "keywords": [
                "exfiltrate", "steal", "leak", "send",
                "upload", "transmit", "external", "attacker",
                "webhook", "callback", "c2"
            ]
        },
        
        "memory_pollution": {
            "name": "Memory Pollution",
            "severity": "medium",
            "mitre_id": "ATLAS-T0004",
            "description": "污染 AI 记忆/上下文导致异常行为",
            "indicators": [
                r"memory\s*=\s*[^']*malicious",
                r"context\s*\..*inject",
                r"append\s*\([^)]*poison",
                r"history\s*\..*modify",
                r"overwrite\s*(memory|context)",
            ],
            "keywords": [
                "pollute", "contaminate", "poison", "inject",
                "modify", "overwrite", "corrupt", "tamper"
            ]
        },
        
        "remote_load": {
            "name": "Remote Load",
            "severity": "critical",
            "mitre_id": "ATLAS-T0005",
            "description": "从远程加载恶意代码",
            "indicators": [
                r"urllib\.request\.urlopen\s*\([^)]*http",
                r"requests\.get\s*\([^)]*http[^)]*exec",
                r"eval\s*\(\s*requests",
                r"exec\s*\(\s*urllib",
                r"__import__\s*\(\s*requests",
                r"load_code\s*\([^)]*http",
                r"fetch_and_execute\s*\(",
            ],
            "keywords": [
                "remote", "load", "fetch", "download",
                "external", "url", "http", "execute"
            ]
        },
        
        "resource_exhaustion": {
            "name": "Resource Exhaustion",
            "severity": "medium",
            "mitre_id": "ATLAS-T0006",
            "description": "耗尽系统资源导致拒绝服务",
            "indicators": [
                r"while\s+True\s*:",
                r"for\s+\w+\s+in\s+range\s*\(\s*10{5,}",
                r"alloc\s*\([^)]*10{9,}",
                r"memory.*\*\s*10{9,}",
                r"cpu.*spike",
                r"fork\s*\(\s*\)",
            ],
            "keywords": [
                "exhaust", "drain", "consume", "spike",
                "infinite", "loop", "alloc", "fork"
            ]
        }
    }
    
    @classmethod
    def get_pattern(cls, attack_type: str) -> Optional[Dict]:
        """获取指定攻击类型的模式"""
        return cls.PATTERNS.get(attack_type)
    
    @classmethod
    def list_patterns(cls) -> List[str]:
        """列出所有攻击类型"""
        return list(cls.PATTERNS.keys())


class SigmaRuleGenerator:
    """Sigma 规则生成器"""
    
    def __init__(self):
        self.generated_count = 0
    
    def generate_rule(self, attack_type: str, variant_id: int = 1) -> Dict:
        """生成单条 Sigma 规则"""
        pattern = AttackPatternLibrary.get_pattern(attack_type)
        if not pattern:
            raise ValueError(f"Unknown attack type: {attack_type}")
        
        indicators = pattern["indicators"]
        # 为每个变体选择不同的 indicator
        selected_indicator = indicators[variant_id % len(indicators)]
        
        rule = {
            "title": f"Detect {pattern['name']} - Variant {variant_id:03d}",
            "id": f"sigma-{attack_type.replace('_', '-')}-{variant_id:03d}",
            "status": "stable",
            "level": pattern["severity"],
            "description": f"{pattern['description']} (变体 {variant_id})",
            "author": "Auto-Generated by Rule Generator",
            "date": datetime.now().strftime("%Y/%m/%d"),
            "modified": datetime.now().strftime("%Y/%m/%d"),
            "tags": [
                f"attack.{attack_type}",
                f"mitre.{pattern['mitre_id']}",
                "ai-security",
                "skill-scanner"
            ],
            "logsource": {
                "category": "application",
                "service": "ai-agent"
            },
            "detection": {
                "selection": {
                    "keyword": selected_indicator
                },
                "condition": "selection"
            },
            "falsepositives": [
                "Legitimate use of similar patterns"
            ],
            "fields": [
                "code",
                "input",
                "output"
            ]
        }
        
        self.generated_count += 1
        return rule
    
    def generate_rules_batch(self, attack_type: str, count: int = 10) -> List[Dict]:
        """批量生成规则"""
        rules = []
        for i in range(count):
            rule = self.generate_rule(attack_type, variant_id=i+1)
            rules.append(rule)
        return rules
    
    def save_rule(self, rule: Dict, attack_type: str) -> Path:
        """保存规则到文件"""
        output_dir = SIGMA_RULES_DIR / attack_type
        output_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"{rule['id']}.yaml"
        output_file = output_dir / filename
        
        with open(output_file, "w", encoding="utf-8") as f:
            yaml.dump(rule, f, allow_unicode=True, default_flow_style=False)
        
        return output_file


class YaraRuleGenerator:
    """YARA 规则生成器"""
    
    def __init__(self):
        self.generated_count = 0
    
    def generate_rule(self, attack_type: str, variant_id: int = 1) -> str:
        """生成单条 YARA 规则"""
        pattern = AttackPatternLibrary.get_pattern(attack_type)
        if not pattern:
            raise ValueError(f"Unknown attack type: {attack_type}")
        
        keywords = pattern["keywords"]
        # 为每个变体选择不同的关键词组合
        selected_keywords = keywords[variant_id % len(keywords):variant_id % len(keywords) + 3]
        
        rule_name = f"{attack_type.title().replace('_', '')}Variant{variant_id:03d}"
        
        # 生成字符串
        strings = []
        for i, keyword in enumerate(selected_keywords):
            strings.append(f'    ${chr(97+i)} = "{keyword}" nocase')
        
        strings_str = "\n".join(strings)
        
        yara_rule = f'''rule {rule_name} {{
    meta:
        description = "{pattern['description']} (变体 {variant_id})"
        author = "Auto-Generated by Rule Generator"
        severity = "{pattern['severity']}"
        mitre_id = "{pattern['mitre_id']}"
        attack_type = "{attack_type}"
        generated_at = "{datetime.now().isoformat()}"
    
    strings:
{strings_str}
    
    condition:
        any of them
}}
'''
        
        self.generated_count += 1
        return yara_rule
    
    def generate_rules_batch(self, attack_type: str, count: int = 10) -> List[str]:
        """批量生成规则"""
        rules = []
        for i in range(count):
            rule = self.generate_rule(attack_type, variant_id=i+1)
            rules.append(rule)
        return rules
    
    def save_rule(self, rule: str, attack_type: str, variant_id: int) -> Path:
        """保存规则到文件"""
        output_dir = YARA_RULES_DIR / attack_type
        output_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"{attack_type}_variant_{variant_id:03d}.yar"
        output_file = output_dir / filename
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(rule)
        
        return output_file


class RuleOptimizer:
    """规则优化器"""
    
    @staticmethod
    def deduplicate_rules(rules: List[Dict]) -> List[Dict]:
        """去重规则"""
        seen_ids = set()
        unique_rules = []
        
        for rule in rules:
            rule_id = rule.get("id", "")
            if rule_id and rule_id not in seen_ids:
                seen_ids.add(rule_id)
                unique_rules.append(rule)
        
        return unique_rules
    
    @staticmethod
    def optimize_pattern(pattern: str) -> str:
        """优化正则表达式模式"""
        # 移除冗余的空格
        pattern = re.sub(r'\s+', ' ', pattern)
        # 优化量词
        pattern = pattern.replace('*', '.*')
        return pattern
    
    @staticmethod
    def validate_rule(rule: Dict) -> bool:
        """验证规则有效性"""
        required_fields = ["title", "id", "detection"]
        for field in required_fields:
            if field not in rule:
                return False
        return True


class RuleQualityChecker:
    """规则质量检查器"""
    
    def __init__(self):
        self.stats = {
            "total": 0,
            "valid": 0,
            "invalid": 0,
            "warnings": 0
        }
    
    def check_rule(self, rule: Dict) -> Dict:
        """检查单条规则质量"""
        issues = []
        warnings = []
        
        # 检查必需字段
        required = ["title", "id", "description", "detection"]
        for field in required:
            if field not in rule:
                issues.append(f"Missing required field: {field}")
        
        # 检查 ID 格式
        rule_id = rule.get("id", "")
        if not re.match(r'^[a-z0-9-]+$', rule_id):
            warnings.append(f"Invalid ID format: {rule_id}")
        
        # 检查严重程度
        severity = rule.get("level", rule.get("severity", ""))
        if severity not in ["low", "medium", "high", "critical"]:
            warnings.append(f"Invalid severity: {severity}")
        
        # 检查检测逻辑
        detection = rule.get("detection", {})
        if not detection:
            issues.append("Empty detection logic")
        
        self.stats["total"] += 1
        if issues:
            self.stats["invalid"] += 1
            return {"valid": False, "issues": issues, "warnings": warnings}
        else:
            self.stats["valid"] += 1
            self.stats["warnings"] += len(warnings)
            return {"valid": True, "issues": [], "warnings": warnings}
    
    def check_rules_batch(self, rules: List[Dict]) -> Dict:
        """批量检查规则"""
        results = []
        for rule in rules:
            result = self.check_rule(rule)
            results.append({"rule_id": rule.get("id"), **result})
        return results


def main():
    """主函数 - 演示规则生成"""
    print("=" * 60)
    print("🤖 自动化规则生成器")
    print("=" * 60)
    
    # 初始化生成器
    sigma_gen = SigmaRuleGenerator()
    yara_gen = YaraRuleGenerator()
    quality_checker = RuleQualityChecker()
    
    # 生成规则
    attack_types = AttackPatternLibrary.list_patterns()
    print(f"\n📋 支持的攻击类型：{len(attack_types)}")
    for at in attack_types:
        print(f"  - {at}")
    
    print("\n🚀 开始生成规则...")
    
    all_sigma_rules = []
    all_yara_rules = []
    
    # 为每种攻击类型生成规则
    for attack_type in attack_types:  # 生成所有 6 种
        print(f"\n生成 {attack_type} 规则...")
        
        # 生成 Sigma 规则
        sigma_rules = sigma_gen.generate_rules_batch(attack_type, count=5)
        for rule in sigma_rules:
            sigma_gen.save_rule(rule, attack_type)
            all_sigma_rules.append(rule)
        print(f"  ✅ 生成 {len(sigma_rules)} 条 Sigma 规则")
        
        # 生成 YARA 规则
        yara_rules = yara_gen.generate_rules_batch(attack_type, count=5)
        for i, rule in enumerate(yara_rules):
            yara_gen.save_rule(rule, attack_type, variant_id=i+1)
            all_yara_rules.append(rule)
        print(f"  ✅ 生成 {len(yara_rules)} 条 YARA 规则")
    
    # 质量检查
    print("\n🔍 质量检查...")
    sigma_results = quality_checker.check_rules_batch(all_sigma_rules)
    valid_sigma = sum(1 for r in sigma_results if r["valid"])
    
    print(f"  Sigma 规则：{valid_sigma}/{len(sigma_results)} 通过")
    
    # 输出统计
    print("\n" + "=" * 60)
    print("📊 生成统计:")
    print(f"  Sigma 规则：{sigma_gen.generated_count}")
    print(f"  YARA 规则：{yara_gen.generated_count}")
    print(f"  总规则数：{sigma_gen.generated_count + yara_gen.generated_count}")
    print(f"  质量通过率：{valid_sigma}/{len(sigma_results)} ({valid_sigma/len(sigma_results)*100:.1f}%)")
    print("=" * 60)
    
    print("\n✅ 规则生成完成!")
    print(f"📁 Sigma 规则目录：{SIGMA_RULES_DIR}")
    print(f"📁 YARA 规则目录：{YARA_RULES_DIR}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
