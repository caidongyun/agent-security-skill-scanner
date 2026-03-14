#!/usr/bin/env python3
"""
规则迭代器 - 自动检测规则更新、验证、测试
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass
from datetime import datetime


@dataclass
class RuleStats:
    """规则统计"""
    rule_id: str
    category: str
    severity: str
    pattern_count: int
    whitelist_count: int
    test_coverage: float = 0.0
    false_positive_rate: float = 0.0


class RuleIterator:
    """规则迭代器"""

    def __init__(self, rules_dir: str):
        self.rules_dir = Path(rules_dir)
        self.rules_file = self.rules_dir / "detection_rules.json"
        self.stats_file = self.rules_dir / "rule-stats.json"
        self.changelog_file = self.rules_dir / "CHANGELOG.md"
        
        self.rules = {}
        self.stats = {}
        self._load_rules()

    def _load_rules(self):
        """加载规则"""
        if self.rules_file.exists():
            with open(self.rules_file, "r") as f:
                self.rules = json.load(f)
        else:
            print(f"❌ 规则文件不存在: {self.rules_file}")
            sys.exit(1)

    def _save_rules(self):
        """保存规则"""
        with open(self.rules_file, "w") as f:
            json.dump(self.rules, f, indent=2, ensure_ascii=False)
        print(f"✅ 规则已保存: {self.rules_file}")

    def validate_rules(self) -> Tuple[bool, List[str]]:
        """验证规则完整性"""
        errors = []
        
        # 检查必需字段
        required_fields = ["version", "updated", "total_rules", "categories"]
        for field in required_fields:
            if field not in self.rules:
                errors.append(f"缺少必需字段: {field}")

        # 统计规则数
        total = 0
        for cat in self.rules.get("categories", []):
            total += len(cat.get("rules", []))
        
        if total != self.rules.get("total_rules", 0):
            errors.append(f"规则总数不匹配: 声明 {self.rules.get('total_rules')}, 实际 {total}")
            self.rules["total_rules"] = total

        # 验证每个规则
        for cat in self.rules.get("categories", []):
            for rule in cat.get("rules", []):
                if "id" not in rule:
                    errors.append(f"规则缺少ID")
                if "name" not in rule:
                    errors.append(f"规则 {rule.get('id')} 缺少名称")
                if "patterns" not in rule or not rule["patterns"]:
                    errors.append(f"规则 {rule.get('id')} 缺少检测模式")
                
                # 验证正则表达式
                for pattern in rule.get("patterns", []):
                    try:
                        re.compile(pattern)
                    except re.error as e:
                        errors.append(f"规则 {rule.get('id')} 正则错误: {e}")

        # 验证白名单
        for cat in self.rules.get("categories", []):
            for rule in cat.get("rules", []):
                for wl in rule.get("whitelist", []):
                    try:
                        re.compile(wl)
                    except re.error as e:
                        errors.append(f"规则 {rule.get('id')} 白名单正则错误: {e}")

        return (len(errors) == 0, errors)

    def test_rule(self, rule_id: str, test_samples: Dict[str, bool]) -> Dict:
        """测试单个规则"""
        # 找到规则
        rule = None
        category = None
        for cat in self.rules.get("categories", []):
            for r in cat.get("rules", []):
                if r["id"] == rule_id:
                    rule = r
                    category = cat
                    break

        if not rule:
            return {"error": f"规则不存在: {rule_id}"}

        # 测试每个样本
        results = {
            "rule_id": rule_id,
            "category": category["name"],
            "severity": rule.get("severity", "MEDIUM"),
            "tests": []
        }

        for sample, expected_malicious in test_samples.items():
            matched = False
            for pattern in rule.get("patterns", []):
                if re.search(pattern, sample, re.IGNORECASE):
                    matched = True
                    break

            # 检查白名单
            whitelisted = False
            for pattern in rule.get("whitelist", []):
                if re.search(pattern, sample, re.IGNORECASE):
                    whitelisted = True
                    break

            detected = matched and not whitelisted
            correct = detected == expected_malicious

            results["tests"].append({
                "sample": sample[:50] + "...",
                "expected": "恶意" if expected_malicious else "正常",
                "detected": "恶意" if detected else "正常",
                "correct": correct
            })

        # 计算准确率
        correct_count = sum(1 for t in results["tests"] if t["correct"])
        results["accuracy"] = correct_count / len(results["tests"]) * 100 if results["tests"] else 0

        return results

    def add_rule(self, category_id: str, new_rule: Dict) -> bool:
        """添加新规则"""
        # 找到分类
        for cat in self.rules.get("categories", []):
            if cat["id"] == category_id:
                # 检查ID唯一性
                for r in cat.get("rules", []):
                    if r["id"] == new_rule["id"]:
                        print(f"❌ 规则ID已存在: {new_rule['id']}")
                        return False
                
                cat["rules"].append(new_rule)
                self.rules["total_rules"] += 1
                self.rules["updated"] = datetime.now().strftime("%Y-%m-%d")
                self._save_rules()
                
                # 记录变更
                self._log_change("ADD", new_rule["id"], new_rule.get("name", ""))
                
                print(f"✅ 添加规则: {new_rule['id']}")
                return True

        print(f"❌ 分类不存在: {category_id}")
        return False

    def update_rule(self, rule_id: str, updates: Dict) -> bool:
        """更新规则"""
        for cat in self.rules.get("categories", []):
            for r in cat.get("rules", []):
                if r["id"] == rule_id:
                    r.update(updates)
                    self.rules["updated"] = datetime.now().strftime("%Y-%m-%d")
                    self._save_rules()
                    
                    # 记录变更
                    self._log_change("UPDATE", rule_id, updates.get("name", ""))
                    
                    print(f"✅ 更新规则: {rule_id}")
                    return True

        print(f"❌ 规则不存在: {rule_id}")
        return False

    def remove_rule(self, rule_id: str) -> bool:
        """删除规则"""
        for cat in self.rules.get("categories", []):
            for i, r in enumerate(cat.get("rules", [])):
                if r["id"] == rule_id:
                    cat["rules"].pop(i)
                    self.rules["total_rules"] -= 1
                    self.rules["updated"] = datetime.now().strftime("%Y-%m-%d")
                    self._save_rules()
                    
                    # 记录变更
                    self._log_change("REMOVE", rule_id, "")
                    
                    print(f"✅ 删除规则: {rule_id}")
                    return True

        print(f"❌ 规则不存在: {rule_id}")
        return False

    def _log_change(self, action: str, rule_id: str, description: str):
        """记录变更"""
        entry = f"- {datetime.now().strftime('%Y-%m-%d %H:%M')} [{action}] {rule_id}: {description}\n"
        
        if not self.changelog_file.exists():
            with open(self.changelog_file, "w") as f:
                f.write("# 规则变更日志\n\n")
        
        with open(self.changelog_file, "r") as f:
            content = f.read()
        
        # 插入到变更日志开头
        lines = content.split("\n")
        insert_idx = 2  # 跳过标题
        lines.insert(insert_idx, entry.strip())
        
        with open(self.changelog_file, "w") as f:
            f.write("\n".join(lines))

    def generate_stats(self) -> Dict:
        """生成统计报告"""
        stats = {
            "version": self.rules.get("version"),
            "updated": self.rules.get("updated"),
            "total_rules": self.rules.get("total_rules"),
            "categories": {},
            "severity_distribution": {},
            "top_rules": []
        }

        # 按分类统计
        for cat in self.rules.get("categories", []):
            cat_id = cat["id"]
            cat_name = cat["name"]
            rule_count = len(cat.get("rules", []))
            weight = cat.get("weight", 10)
            
            stats["categories"][cat_id] = {
                "name": cat_name,
                "rule_count": rule_count,
                "weight": weight,
                "score": rule_count * weight
            }

        # 按严重程度统计
        severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for cat in self.rules.get("categories", []):
            for rule in cat.get("rules", []):
                sev = rule.get("severity", "MEDIUM")
                severity_counts[sev] = severity_counts.get(sev, 0) + 1
        
        stats["severity_distribution"] = severity_counts

        # 保存统计
        with open(self.stats_file, "w") as f:
            json.dump(stats, f, indent=2)

        return stats

    def print_summary(self):
        """打印摘要"""
        print("\n" + "=" * 60)
        print("📊 规则统计摘要")
        print("=" * 60)
        print(f"版本: {self.rules.get('version')}")
        print(f"更新时间: {self.rules.get('updated')}")
        print(f"总规则数: {self.rules.get('total_rules')}")
        
        print("\n📁 按分类:")
        for cat in self.rules.get("categories", []):
            print(f"  • {cat['name']}: {len(cat.get('rules', []))} 条规则")
        
        print("\n⚠️ 按严重程度:")
        stats = self.generate_stats()
        for sev, count in stats["severity_distribution"].items():
            emoji = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢"}.get(sev, "⚪")
            print(f"  {emoji} {sev}: {count}")
        
        print("\n" + "=" * 60)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="规则迭代器")
    parser.add_argument("--rules-dir", "-r", default=".", help="规则目录")
    parser.add_argument("--validate", "-v", action="store_true", help="验证规则")
    parser.add_argument("--stats", "-s", action="store_true", help="显示统计")
    parser.add_argument("--add", "-a", help="添加规则 (JSON)")
    parser.add_argument("--update", "-u", help="更新规则")
    parser.add_argument("--remove", "-d", help="删除规则")
    parser.add_argument("--test", "-t", help="测试规则ID")
    
    args = parser.parse_args()
    
    iterator = RuleIterator(args.rules_dir)
    
    if args.validate:
        valid, errors = iterator.validate_rules()
        if valid:
            print("✅ 规则验证通过")
        else:
            print("❌ 规则验证失败:")
            for e in errors:
                print(f"  - {e}")
            sys.exit(1)
    
    if args.stats:
        iterator.print_summary()
    
    if args.test:
        # 测试示例
        test_samples = {
            "eval('1+1')": False,  # 安全
            "eval(user_input)": True,  # 危险
            "exec('rm -rf /')": True,  # 危险
            "exec('1+1')": False,  # 安全
        }
        results = iterator.test_rule(args.test, test_samples)
        print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
