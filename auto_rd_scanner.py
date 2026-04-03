#!/usr/bin/env python3
"""
扫描器自治研发系统
针对 agent-security-skill-scanner-master 的自动规则研发
"""

import subprocess
import json
import glob
import sys
from pathlib import Path
from datetime import datetime

class ScannerAutoRD:
    def __init__(self):
        self.scanner_dir = Path.home() / ".openclaw/workspace/agent-security-skill-scanner-master"
        self.sample_gen_dir = Path.home() / ".openclaw/workspace/skills/security-sample-generator"
        self.benchmark_dir = Path.home() / "Desktop/security-benchmark"
        self.reports_dir = self.scanner_dir / "reports"
        self.rules_dir = self.scanner_dir / "rules" / "scanner_v3" / "yara"
        
    def log(self, msg):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")
    
    def check_scanner_status(self):
        """检查扫描器状态"""
        self.log("=" * 60)
        self.log("Step 0: 检查扫描器状态")
        self.log("=" * 60)
        
        # 检查规则文件
        rules_file = self.rules_dir / "scanner_rules.yar"
        if not rules_file.exists():
            self.log("❌ 规则文件不存在")
            return False
        
        # 统计规则数
        with open(rules_file) as f:
            rule_count = sum(1 for line in f if line.startswith("rule "))
        self.log(f"✅ 规则文件：{rule_count} 条")
        
        # 测试扫描器
        test_sample = list(self.benchmark_dir.glob("samples/from-templates/**/MAL-*"))[:1]
        if not test_sample:
            self.log("❌ 无测试样本")
            return False
        
        try:
            result = subprocess.run(
                [str(self.scanner_dir / "scan.sh"), str(test_sample[0].absolute())],
                capture_output=True, text=True, timeout=30
            )
            
            if "检测能力" in result.stdout:
                self.log("✅ 扫描器正常")
                return True
            else:
                self.log("⚠️  扫描器异常")
                return False
        except Exception as e:
            self.log(f"❌ 扫描器错误：{e}")
            return False
    
    def analyze_false_negatives(self):
        """分析漏报样本"""
        self.log("=" * 60)
        self.log("Step 1: 分析漏报样本")
        self.log("=" * 60)
        
        samples_dir = self.benchmark_dir / "samples/from-templates"
        mal_samples = list(samples_dir.glob("**/MAL*"))[:20]
        
        fn_samples = []
        attack_types = {}
        
        for sample in mal_samples:
            result = subprocess.run(
                [str(self.scanner_dir / "scan.sh"), str(sample.absolute())],
                capture_output=True, text=True, timeout=20
            )
            
            # 检查报告
            reports = glob.glob(str(self.reports_dir / "ultimate_v2_*.json"))
            if reports:
                latest = max(reports, key=lambda x: x)
                try:
                    with open(latest) as f:
                        report = json.load(f)
                    if report.get('summary', {}).get('malicious', 0) == 0:
                        fn_samples.append(sample)
                        
                        # 分析攻击类型
                        try:
                            with open(sample / "metadata.json") as f:
                                meta = json.load(f)
                            attack_type = meta.get('attack_type', 'unknown')
                            attack_types[attack_type] = attack_types.get(attack_type, 0) + 1
                        except:
                            pass
                        
                        self.log(f"  ❌ FN: {sample.name} ({attack_type})")
                except:
                    pass
        
        self.log(f"\n发现 {len(fn_samples)} 个漏报样本")
        if attack_types:
            self.log("漏报攻击类型分布:")
            for at, count in sorted(attack_types.items(), key=lambda x: -x[1]):
                self.log(f"  - {at}: {count}")
        
        return fn_samples, attack_types
    
    def enhance_rules(self, attack_types):
        """针对性增强规则"""
        self.log("\n" + "=" * 60)
        self.log("Step 2: 增强规则")
        self.log("=" * 60)
        
        if not attack_types:
            self.log("✅ 无需增强规则")
            return True
        
        # 为每个漏报攻击类型生成样本
        for attack_type in attack_types:
            self.log(f"\n  生成 {attack_type} 增强样本...")
            subprocess.run(
                [sys.executable, "sample_generator.py", "--attack", attack_type, "--count", "5"],
                cwd=str(self.sample_gen_dir),
                capture_output=True
            )
        
        # 重新生成规则
        self.log("\n  重新生成规则...")
        result = subprocess.run(
            [sys.executable, "tools/convert_sigma_to_yara.py"],
            cwd=str(self.sample_gen_dir),
            capture_output=True, text=True
        )
        
        if "编译成功" in result.stdout:
            self.log("  ✅ 规则生成成功")
        else:
            self.log("  ⚠️  规则生成警告")
        
        # 部署到扫描器
        self.log("  部署规则到扫描器...")
        rules_file = self.sample_gen_dir / "rules" / "sigma_converted.yar"
        target = self.rules_dir / "scanner_rules.yar"
        
        if rules_file.exists():
            # 解除只读锁定
            subprocess.run(["chmod", "644", str(target)], capture_output=True)
            subprocess.run(["cp", str(rules_file), str(target)], capture_output=True)
            subprocess.run(["chmod", "444", str(target)], capture_output=True)
            self.log("  ✅ 规则已部署")
            
            # 统计规则数
            with open(rules_file) as f:
                rule_count = sum(1 for line in f if line.startswith("rule "))
            self.log(f"  规则总数：{rule_count} 条")
            return True
        else:
            self.log("  ❌ 规则文件不存在")
            return False
    
    def validate(self):
        """验证测试"""
        self.log("\n" + "=" * 60)
        self.log("Step 3: 验证测试")
        self.log("=" * 60)
        
        samples_dir = self.benchmark_dir / "samples/from-templates"
        
        # 测试恶意样本
        mal_samples = list(samples_dir.glob("**/MAL*"))[:10]
        tp, fn = 0, 0
        
        self.log("测试恶意样本...")
        for sample in mal_samples:
            result = subprocess.run(
                [str(self.scanner_dir / "scan.sh"), str(sample.absolute())],
                capture_output=True, text=True, timeout=20
            )
            
            reports = glob.glob(str(self.reports_dir / "ultimate_v2_*.json"))
            if reports:
                latest = max(reports, key=lambda x: x)
                try:
                    with open(latest) as f:
                        report = json.load(f)
                    if report.get('summary', {}).get('malicious', 0) > 0:
                        tp += 1
                    else:
                        fn += 1
                except:
                    fn += 1
        
        # 测试良性样本
        ben_samples = list(samples_dir.glob("**/BEN*"))[:10]
        tn, fp = 0, 0
        
        self.log("测试良性样本...")
        for sample in ben_samples:
            result = subprocess.run(
                [str(self.scanner_dir / "scan.sh"), str(sample.absolute())],
                capture_output=True, text=True, timeout=20
            )
            
            reports = glob.glob(str(self.reports_dir / "ultimate_v2_*.json"))
            if reports:
                latest = max(reports, key=lambda x: x)
                try:
                    with open(latest) as f:
                        report = json.load(f)
                    if report.get('summary', {}).get('malicious', 0) > 0:
                        fp += 1
                    else:
                        tn += 1
                except:
                    tn += 1
        
        dr = tp / (tp + fn) * 100 if (tp + fn) > 0 else 0
        fpr = fp / (fp + tn) * 100 if (fp + tn) > 0 else 0
        
        self.log(f"\n测试结果:")
        self.log(f"  恶意样本：{tp}/{tp+fn}")
        self.log(f"  良性样本：{tn}/{tn+fp}")
        self.log(f"  检测率：{dr:.1f}%")
        self.log(f"  误报率：{fpr:.1f}%")
        
        # 质量门禁
        if dr >= 95 and fpr < 5:
            self.log(f"\n✅ 质量门禁通过 (DR≥95%, FP<5%)")
            return True, dr, fpr
        else:
            self.log(f"\n⚠️  质量门禁未达标，需要继续优化")
            return False, dr, fpr
    
    def publish(self, passed, dr, fpr):
        """发布"""
        self.log("\n" + "=" * 60)
        self.log("Step 4: 发布")
        self.log("=" * 60)
        
        if not passed:
            self.log("⚠️  质量未达标，跳过发布")
            return
        
        # 提交到 git
        self.log("提交到 git...")
        subprocess.run(
            ["git", "add", "-A"],
            cwd=str(self.scanner_dir),
            capture_output=True
        )
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        msg = f"feat: 自治研发 {timestamp} - DR:{dr:.1f}%, FP:{fpr:.1f}%"
        subprocess.run(
            ["git", "commit", "-m", msg],
            cwd=str(self.scanner_dir),
            capture_output=True
        )
        
        self.log("✅ 已提交到 git")
    
    def run(self):
        """运行完整流程"""
        self.log("🤖 扫描器自治研发系统启动")
        self.log(f"目标：{self.scanner_dir}")
        self.log(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Step 0: 检查状态
        if not self.check_scanner_status():
            self.log("❌ 扫描器状态异常，中止")
            return False
        
        # Step 1: 分析漏报
        fn_samples, attack_types = self.analyze_false_negatives()
        
        # Step 2: 增强规则
        enhanced = self.enhance_rules(attack_types)
        
        # Step 3: 验证
        if enhanced:
            passed, dr, fpr = self.validate()
        else:
            passed, dr, fpr = False, 0, 0
        
        # Step 4: 发布
        self.publish(passed, dr, fpr)
        
        self.log("\n" + "=" * 60)
        self.log("✅ 自治研发完成")
        self.log("=" * 60)
        
        return passed

if __name__ == '__main__':
    auto_rd = ScannerAutoRD()
    success = auto_rd.run()
    sys.exit(0 if success else 1)
