#!/usr/bin/env python3
"""
🔄 规则同步模块 - 将研究成果沉淀到防护模块
===========================================
功能：
- 将灵顺 V5 生成的规则同步到 agent-defender
- 将新样本同步到 agent-dlp 检测规则
- 备份旧规则，支持回滚
- 验证规则有效性
- 生成变更报告

使用方式:
    python3 rule_sync.py --sync          # 同步规则
    python3 rule_sync.py --verify        # 验证规则
    python3 rule_sync.py --rollback      # 回滚到上一版本
    python3 rule_sync.py --status        # 查看同步状态
"""

import os
import sys
import json
import shutil
import hashlib
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import re

# 路径配置
SCRIPT_DIR = Path(__file__).parent
DEFENDER_PATH = SCRIPT_DIR.parent / "agent-defender"
DLP_PATH = SCRIPT_DIR.parent / "agent-dlp"

# 规则目录
RULES_BACKUP_DIR = SCRIPT_DIR / "rules_backup"
RULES_HISTORY_FILE = SCRIPT_DIR / "rules_history.json"

# 确保备份目录存在
RULES_BACKUP_DIR.mkdir(exist_ok=True)


class RuleSync:
    """规则同步器"""
    
    def __init__(self):
        self.sync_history = self._load_history()
        self.changes = []
        
    def _load_history(self) -> Dict[str, Any]:
        """加载同步历史"""
        if RULES_HISTORY_FILE.exists():
            try:
                with open(RULES_HISTORY_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        return {
            "last_sync": None,
            "total_syncs": 0,
            "rules_synced": [],
            "rollbacks": []
        }
    
    def _save_history(self):
        """保存同步历史"""
        with open(RULES_HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.sync_history, f, indent=2, ensure_ascii=False)
    
    def _backup_rules(self, backup_name: str):
        """备份当前规则"""
        backup_dir = RULES_BACKUP_DIR / backup_name
        backup_dir.mkdir(exist_ok=True)
        
        print(f"📦 备份规则到：{backup_dir}")
        
        # 备份 defender 规则
        defender_rules = DEFENDER_PATH / "rules"
        if defender_rules.exists():
            shutil.copytree(defender_rules, backup_dir / "defender_rules")
        
        # 备份 dlp 规则
        dlp_rules = DLP_PATH / "rules"
        if dlp_rules.exists():
            shutil.copytree(dlp_rules, backup_dir / "dlp_rules")
        
        # 备份 runtime 规则
        runtime_monitor = DEFENDER_PATH / "runtime" / "monitor.py"
        if runtime_monitor.exists():
            shutil.copy(runtime_monitor, backup_dir / "monitor.py")
        
        # 备份 dlp 检查
        dlp_check = DLP_PATH / "dlp" / "check.py"
        if dlp_check.exists():
            shutil.copy(dlp_check, backup_dir / "check.py")
        
        print(f"✅ 备份完成：{backup_name}")
    
    def _generate_rule_hash(self, rule_content: str) -> str:
        """生成规则哈希"""
        return hashlib.md5(rule_content.encode()).hexdigest()
    
    def sync_rules(self, force: bool = False):
        """同步规则到防护模块"""
        print("=" * 60)
        print("🔄 开始同步规则")
        print("=" * 60)
        
        # 1. 备份当前规则
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self._backup_rules(f"backup_{timestamp}")
        
        # 2. 读取新生成的规则
        new_rules = self._load_new_rules()
        
        if not new_rules:
            print("⚠️  没有新规则需要同步")
            return
        
        print(f"📊 发现 {len(new_rules)} 条新规则")
        
        # 3. 同步到 agent-defender
        defender_updated = self._sync_to_defender(new_rules)
        
        # 4. 同步到 agent-dlp
        dlp_updated = self._sync_to_dlp(new_rules)
        
        # 5. 验证规则
        if defender_updated or dlp_updated:
            print("\n🔍 验证规则...")
            valid = self._verify_rules()
            
            if valid:
                print("✅ 规则验证通过")
                
                # 更新历史
                self.sync_history["last_sync"] = datetime.now().isoformat()
                self.sync_history["total_syncs"] += 1
                self.sync_history["rules_synced"].extend([
                    {"rule": r["id"], "time": timestamp}
                    for r in new_rules
                ])
                self._save_history()
                
                # 生成变更报告
                self._generate_report(new_rules, defender_updated, dlp_updated)
                
                print("\n✅ 规则同步完成")
            else:
                print("❌ 规则验证失败，正在回滚...")
                self._rollback(timestamp)
        else:
            print("⚠️  没有规则被更新")
    
    def _load_new_rules(self) -> List[Dict[str, Any]]:
        """加载新生成的规则"""
        new_rules = []
        
        # 从灵顺 V5 输出目录读取
        output_dir = SCRIPT_DIR / "output"
        if output_dir.exists():
            # 读取规则文件
            rules_file = output_dir / "new_rules.json"
            if rules_file.exists():
                try:
                    with open(rules_file, 'r', encoding='utf-8') as f:
                        rules = json.load(f)
                    new_rules.extend(rules)
                except:
                    pass
            
            # 读取 runtime 规则
            runtime_file = output_dir / "runtime_rules.py"
            if runtime_file.exists():
                try:
                    with open(runtime_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 解析规则
                    runtime_rules = self._parse_runtime_rules(content)
                    new_rules.extend(runtime_rules)
                except:
                    pass
            
            # 读取 DLP 规则
            dlp_file = output_dir / "dlp_rules.json"
            if dlp_file.exists():
                try:
                    with open(dlp_file, 'r', encoding='utf-8') as f:
                        rules = json.load(f)
                    new_rules.extend(rules)
                except:
                    pass
        
        # 如果没有输出文件，从迭代日志中提取
        log_file = SCRIPT_DIR / "logs" / "lingshun_daemon.log"
        if log_file.exists() and not new_rules:
            new_rules = self._extract_rules_from_log(log_file)
        
        return new_rules
    
    def _parse_runtime_rules(self, content: str) -> List[Dict[str, Any]]:
        """解析 runtime 规则"""
        rules = []
        
        # 提取 RUNTIME_RULES 定义
        match = re.search(r'RUNTIME_RULES\s*=\s*(\{.*?\})', content, re.DOTALL)
        if match:
            try:
                rules_dict = eval(match.group(1))
                for category, rule_list in rules_dict.items():
                    for rule in rule_list:
                        rule['category'] = category
                        rules.append(rule)
            except:
                pass
        
        return rules
    
    def _extract_rules_from_log(self, log_file: Path) -> List[Dict[str, Any]]:
        """从日志中提取新规则"""
        rules = []
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取"新增规则"相关日志
            pattern = r'📝 新增规则.*?\n(.*?)(?=\n\n|\n📊|\n🔄|$)'
            matches = re.findall(pattern, content, re.DOTALL)
            
            for match in matches:
                # 解析规则信息
                rule = {
                    "id": f"AUTO_{len(rules)+1:03d}",
                    "description": match.strip(),
                    "source": "log_extraction"
                }
                rules.append(rule)
        except:
            pass
        
        return rules
    
    def _sync_to_defender(self, rules: List[Dict]) -> List[str]:
        """同步到 agent-defender"""
        updated = []
        
        defender_rules_dir = DEFENDER_PATH / "rules"
        defender_rules_dir.mkdir(exist_ok=True)
        
        # 按类别分组
        rules_by_category = {}
        for rule in rules:
            category = rule.get('category', 'general')
            if category not in rules_by_category:
                rules_by_category[category] = []
            rules_by_category[category].append(rule)
        
        # 写入规则文件
        for category, category_rules in rules_by_category.items():
            rule_file = defender_rules_dir / f"{category}_rules.json"
            
            # 读取现有规则
            existing_rules = []
            if rule_file.exists():
                try:
                    with open(rule_file, 'r', encoding='utf-8') as f:
                        existing_rules = json.load(f)
                except:
                    pass
            
            # 合并规则 (去重)
            existing_ids = {r.get('id') for r in existing_rules}
            for rule in category_rules:
                if rule.get('id') not in existing_ids:
                    existing_rules.append(rule)
                    updated.append(rule.get('id'))
                    print(f"  ➕ 添加 Defender 规则：{rule.get('id')}")
            
            # 写回文件
            with open(rule_file, 'w', encoding='utf-8') as f:
                json.dump(existing_rules, f, indent=2, ensure_ascii=False)
        
        return updated
    
    def _sync_to_dlp(self, rules: List[Dict]) -> List[str]:
        """同步到 agent-dlp"""
        updated = []
        
        dlp_rules_dir = DLP_PATH / "rules"
        dlp_rules_dir.mkdir(exist_ok=True)
        
        # 筛选 DLP 相关规则
        dlp_rules = [r for r in rules if r.get('type') in ['data_exfil', 'pii', 'sensitive']]
        
        if dlp_rules:
            rule_file = dlp_rules_dir / "custom_rules.json"
            
            # 读取现有规则
            existing_rules = []
            if rule_file.exists():
                try:
                    with open(rule_file, 'r', encoding='utf-8') as f:
                        existing_rules = json.load(f)
                except:
                    pass
            
            # 合并规则
            existing_ids = {r.get('id') for r in existing_rules}
            for rule in dlp_rules:
                if rule.get('id') not in existing_ids:
                    existing_rules.append(rule)
                    updated.append(rule.get('id'))
                    print(f"  ➕ 添加 DLP 规则：{rule.get('id')}")
            
            # 写回文件
            with open(rule_file, 'w', encoding='utf-8') as f:
                json.dump(existing_rules, f, indent=2, ensure_ascii=False)
        
        return updated
    
    def _verify_rules(self) -> bool:
        """验证规则有效性"""
        # 1. 检查语法
        defender_rules = DEFENDER_PATH / "rules"
        if defender_rules.exists():
            for rule_file in defender_rules.glob("*.json"):
                try:
                    with open(rule_file, 'r', encoding='utf-8') as f:
                        json.load(f)
                    print(f"  ✅ {rule_file.name} 语法正确")
                except json.JSONDecodeError as e:
                    print(f"  ❌ {rule_file.name} 语法错误：{e}")
                    return False
        
        # 2. 运行测试
        print("  🔍 运行防护测试...")
        test_script = SCRIPT_DIR / "tests" / "test_rules.py"
        if test_script.exists():
            result = subprocess.run(
                ["python3", str(test_script)],
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode != 0:
                print(f"  ❌ 测试失败:\n{result.stderr}")
                return False
            print(f"  ✅ 测试通过")
        
        return True
    
    def _rollback(self, backup_name: str):
        """回滚规则"""
        backup_dir = RULES_BACKUP_DIR / backup_name
        
        if not backup_dir.exists():
            print(f"❌ 备份不存在：{backup_name}")
            return
        
        print(f"🔄 回滚到备份：{backup_name}")
        
        # 恢复 defender 规则
        defender_backup = backup_dir / "defender_rules"
        if defender_backup.exists():
            defender_rules = DEFENDER_PATH / "rules"
            if defender_rules.exists():
                shutil.rmtree(defender_rules)
            shutil.copytree(defender_backup, defender_rules)
        
        # 恢复 dlp 规则
        dlp_backup = backup_dir / "dlp_rules"
        if dlp_backup.exists():
            dlp_rules = DLP_PATH / "rules"
            if dlp_rules.exists():
                shutil.rmtree(dlp_rules)
            shutil.copytree(dlp_backup, dlp_rules)
        
        print("✅ 回滚完成")
        
        # 记录回滚历史
        self.sync_history["rollbacks"].append({
            "time": datetime.now().isoformat(),
            "backup": backup_name
        })
        self._save_history()
    
    def _generate_report(self, new_rules: List[Dict], defender_updated: List[str], dlp_updated: List[str]):
        """生成变更报告"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_new_rules": len(new_rules),
                "defender_updated": len(defender_updated),
                "dlp_updated": len(dlp_updated)
            },
            "defender_rules": defender_updated,
            "dlp_rules": dlp_updated,
            "details": new_rules
        }
        
        report_file = SCRIPT_DIR / "sync_reports" / f"sync_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_file.parent.mkdir(exist_ok=True)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📊 变更报告已保存：{report_file}")
        
        # 打印摘要
        print("\n" + "=" * 60)
        print("📋 同步摘要")
        print("=" * 60)
        print(f"新增规则总数：{len(new_rules)}")
        print(f"Defender 更新：{len(defender_updated)} 条")
        print(f"DLP 更新：{len(dlp_updated)} 条")
    
    def status(self):
        """显示同步状态"""
        print("=" * 60)
        print("📊 规则同步状态")
        print("=" * 60)
        
        print(f"最后同步：{self.sync_history.get('last_sync', '从未')}")
        print(f"总同步次数：{self.sync_history.get('total_syncs', 0)}")
        print(f"总回滚次数：{len(self.sync_history.get('rollbacks', []))}")
        
        # 检查防护模块规则
        defender_rules = DEFENDER_PATH / "rules"
        dlp_rules = DLP_PATH / "rules"
        
        if defender_rules.exists():
            rule_count = sum(1 for _ in defender_rules.glob("*.json"))
            print(f"\nDefender 规则文件：{rule_count} 个")
        else:
            print(f"\nDefender 规则目录：不存在")
        
        if dlp_rules.exists():
            rule_count = sum(1 for _ in dlp_rules.glob("*.json"))
            print(f"DLP 规则文件：{rule_count} 个")
        else:
            print(f"DLP 规则目录：不存在")
        
        # 检查备份
        backups = list(RULES_BACKUP_DIR.iterdir())
        print(f"\n规则备份：{len(backups)} 个")
        
        # 最近的同步报告
        reports_dir = SCRIPT_DIR / "sync_reports"
        if reports_dir.exists():
            reports = sorted(reports_dir.glob("*.json"), reverse=True)[:5]
            print(f"\n最近同步报告:")
            for report_file in reports:
                try:
                    with open(report_file, 'r', encoding='utf-8') as f:
                        report = json.load(f)
                    summary = report.get('summary', {})
                    print(f"  - {report_file.stem}: {summary.get('total_new_rules', 0)} 条规则")
                except:
                    pass
    
    def verify(self):
        """验证当前规则"""
        print("=" * 60)
        print("🔍 验证规则")
        print("=" * 60)
        
        valid = self._verify_rules()
        
        if valid:
            print("\n✅ 所有规则验证通过")
        else:
            print("\n❌ 规则验证失败")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="🔄 规则同步模块")
    parser.add_argument("--sync", action="store_true", help="同步规则")
    parser.add_argument("--verify", action="store_true", help="验证规则")
    parser.add_argument("--rollback", type=str, help="回滚到指定备份")
    parser.add_argument("--status", action="store_true", help="查看状态")
    parser.add_argument("--force", action="store_true", help="强制同步")
    
    args = parser.parse_args()
    
    sync = RuleSync()
    
    if args.sync:
        sync.sync_rules(force=args.force)
    elif args.verify:
        sync.verify()
    elif args.rollback:
        sync._rollback(args.rollback)
    elif args.status:
        sync.status()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
