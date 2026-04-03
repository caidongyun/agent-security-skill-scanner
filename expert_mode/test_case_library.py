#!/usr/bin/env python3
"""
📚 测试用例库 - 记录和复用测试代码
=====================================
功能:
1. 记录测试用例代码
2. 版本控制
3. 复用已通过的测试
4. 只对新增/修改的规则生成测试

使用方式:
    python3 test_case_library.py --save TO-RUNTIME-001    # 保存测试用例
    python3 test_case_library.py --load TO-RUNTIME-001  # 加载测试用例
    python3 test_case_library.py --check COVERAGE       # 检查覆盖率
    python3 test_case_library.py --generate              # 生成缺失的测试
"""

import os
import sys
import json
import hashlib
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional


# 测试用例库目录
LIBRARY_DIR = Path(__file__).parent / "test_case_library"
CASES_DIR = LIBRARY_DIR / "cases"
METADATA_FILE = LIBRARY_DIR / "metadata.json"

LIBRARY_DIR.mkdir(exist_ok=True)
CASES_DIR.mkdir(exist_ok=True)


class TestCaseLibrary:
    """测试用例库"""
    
    def __init__(self):
        self.metadata = self.load_metadata()
    
    def load_metadata(self) -> Dict:
        """加载元数据"""
        if METADATA_FILE.exists():
            with open(METADATA_FILE, 'r') as f:
                return json.load(f)
        return {
            "version": "1.0",
            "rules": {},
            "total_cases": 0,
            "created_at": datetime.now().isoformat()
        }
    
    def save_metadata(self):
        """保存元数据"""
        with open(METADATA_FILE, 'w') as f:
            json.dump(self.metadata, f, indent=2)
    
    def compute_rule_hash(self, rule: Dict) -> str:
        """计算规则哈希"""
        content = json.dumps(rule, sort_keys=True)
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def save_test_case(self, rule_id: str, rule: Dict, test_code: str) -> bool:
        """保存测试用例"""
        # 计算规则哈希
        rule_hash = self.compute_rule_hash(rule)
        
        # 存储测试代码
        case_file = CASES_DIR / f"{rule_id}.py"
        with open(case_file, 'w') as f:
            f.write(test_code)
        
        # 更新元数据
        self.metadata["rules"][rule_id] = {
            "hash": rule_hash,
            "saved_at": datetime.now().isoformat(),
            "test_file": str(case_file),
            "test_count": test_code.count("def test_")
        }
        
        self.metadata["total_cases"] = sum(
            r.get("test_count", 0) 
            for r in self.metadata["rules"].values()
        )
        
        self.save_metadata()
        
        print(f"✅ 已保存测试用例: {rule_id} ({self.metadata['rules'][rule_id]['test_count']} 个测试)")
        return True
    
    def load_test_case(self, rule_id: str) -> Optional[str]:
        """加载测试用例"""
        case_file = CASES_DIR / f"{rule_id}.py"
        if case_file.exists():
            return case_file.read_text()
        return None
    
    def is_up_to_date(self, rule_id: str, rule: Dict) -> bool:
        """检查测试用例是否最新"""
        if rule_id not in self.metadata["rules"]:
            return False
        
        saved_hash = self.metadata["rules"][rule_id]["hash"]
        current_hash = self.compute_rule_hash(rule)
        
        return saved_hash == current_hash
    
    def generate_test_code(self, rule_id: str, rule: Dict) -> str:
        """生成测试代码"""
        patterns = rule.get("patterns", [])
        category = rule.get("category", "unknown")
        severity = rule.get("severity", "medium")
        
        # 生成测试代码
        test_code = f'''"""
{rule_id} 单元测试
===================
规则: {rule.get('name', 'N/A')}
类型: {category}
严重程度: {severity}

自动生成
"""

import pytest
import re


class Test{rule_id.replace("-", "_")}:
    """测试 {rule_id}"""
'''
        
        # 正向测试用例
        for i, pattern in enumerate(patterns[:3]):
            safe_pattern = pattern.replace("\\", "\\\\")
            test_code += f'''
    def test_positive_{i+1}(self):
        """正向测试 {i+1}"""
        rule = {json.dumps(rule, indent=4, ensure_ascii=False)}
        
        # 测试模式: {pattern}
        for test_input in {json.dumps([p.replace("\\\\", "\\") for p in patterns[:2]], indent=8)}:
            # 这里应该调用检测器
            pass
'''
        
        # 负向测试用例
        test_code += '''
    def test_negative(self):
        """负向测试"""
        # 不应该触发的情况
        pass
'''
        
        return test_code
    
    def sync_with_rules(self) -> Dict:
        """同步规则和测试用例"""
        rules_dir = Path(__file__).parent / "rules"
        
        stats = {
            "total_rules": 0,
            "up_to_date": 0,
            "needs_update": 0,
            "missing": 0,
            "generated": 0
        }
        
        # 遍历所有规则
        for rule_file in rules_dir.rglob("*.json"):
            try:
                with open(rule_file) as f:
                    rule = json.load(f)
                
                rule_id = rule.get("id", "")
                if not rule_id:
                    continue
                
                stats["total_rules"] += 1
                
                # 检查是否有测试用例
                test_code = self.load_test_case(rule_id)
                
                if test_code is None:
                    # 生成新的测试用例
                    stats["missing"] += 1
                    test_code = self.generate_test_code(rule_id, rule)
                    self.save_test_case(rule_id, rule, test_code)
                    stats["generated"] += 1
                    
                elif not self.is_up_to_date(rule_id, rule):
                    # 规则已更新，重新生成
                    stats["needs_update"] += 1
                    test_code = self.generate_test_code(rule_id, rule)
                    self.save_test_case(rule_id, rule, test_code)
                else:
                    stats["up_to_date"] += 1
                    
            except Exception as e:
                print(f"⚠️  处理失败 {rule_file}: {e}")
        
        return stats
    
    def check_coverage(self) -> Dict:
        """检查测试覆盖率"""
        rules_dir = Path(__file__).parent / "rules"
        
        total_rules = 0
        covered_rules = 0
        
        for rule_file in rules_dir.rglob("*.json"):
            total_rules += 1
            rule_id = json.load(open(rule_file)).get("id", "")
            
            if rule_id and self.load_test_case(rule_id):
                covered_rules += 1
        
        coverage = (covered_rules / total_rules * 100) if total_rules > 0 else 0
        
        return {
            "total_rules": total_rules,
            "covered_rules": covered_rules,
            "coverage_percent": coverage
        }
    
    def status(self):
        """显示状态"""
        coverage = self.check_coverage()
        
        print(f"\n{'='*60}")
        print(f"📚 测试用例库状态")
        print(f"{'='*60}")
        print(f"规则总数: {coverage['total_rules']}")
        print(f"已覆盖: {coverage['covered_rules']}")
        print(f"覆盖率: {coverage['coverage_percent']:.1f}%")
        print(f"测试用例数: {self.metadata['total_cases']}")
        print(f"库目录: {CASES_DIR}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="📚 测试用例库")
    parser.add_argument("--save", type=str, help="保存测试用例")
    parser.add_argument("--load", type=str, help="加载测试用例")
    parser.add_argument("--check", action="store_true", help="检查覆盖率")
    parser.add_argument("--sync", action="store_true", help="同步规则和测试")
    parser.add_argument("--status", action="store_true", help="显示状态")
    
    args = parser.parse_args()
    
    library = TestCaseLibrary()
    
    if args.status:
        library.status()
    
    elif args.check:
        coverage = library.check_coverage()
        print(f"\n📊 覆盖率: {coverage['coverage_percent']:.1f}%")
        print(f"   已覆盖: {coverage['covered_rules']}/{coverage['total_rules']}")
    
    elif args.sync:
        print("🔄 同步中...")
        stats = library.sync_with_rules()
        print(f"\n📊 同步结果:")
        print(f"   总规则: {stats['total_rules']}")
        print(f"   最新: {stats['up_to_date']}")
        print(f"   需要更新: {stats['needs_update']}")
        print(f"   已生成: {stats['generated']}")
    
    elif args.save:
        # 保存指定的测试用例
        rules_dir = Path(__file__).parent / "rules"
        
        # 查找规则文件
        for rule_file in rules_dir.rglob(f"{args.save}.json"):
            with open(rule_file) as f:
                rule = json.load(f)
            
            test_code = library.generate_test_code(args.save, rule)
            library.save_test_case(args.save, rule, test_code)
            break
        else:
            print(f"❌ 规则 {args.save} 不存在")
    
    elif args.load:
        test_code = library.load_test_case(args.load)
        if test_code:
            print(test_code)
        else:
            print(f"❌ 测试用例 {args.load} 不存在")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
