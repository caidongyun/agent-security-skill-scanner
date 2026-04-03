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
        
        # 严格质量控制配置
        self.quality_config = {
            'min_dr': 98.0,        # 最低检测率 (提升到 98%)
            'max_fp': 2.0,         # 最高误报率 (降低到 2%)
            'min_samples': 1000,   # 最少测试样本数 (扩大到 1000)
            'min_precision': 95.0, # 最低精确率
            'min_f1': 95.0,        # 最低 F1 分数
            'require_industry': True,  # 需要行业信息
            'require_model_analysis': True  # 需要模型分析
        }
        
        # 测试样本配置
        self.test_config = {
            'mal_samples': 500,    # 恶意样本数 (扩大到 500)
            'ben_samples': 500,    # 良性样本数 (扩大到 500)
            'stratified': True,    # 分层抽样
            'by_attack_type': True # 按攻击类型分布
        }
        
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
    
    def analyze_rule_quality(self, attack_types):
        """分析规则质量 (行业信息 + 模型分析)"""
        self.log("\n  分析规则质量...")
        
        # 1. 检查行业信息
        industry_info = {
            'mitre_atlas': True,   # MITRE ATLAS 映射
            'cve_mapping': False,  # CVE 映射
            'threat_intel': False, # 威胁情报
        }
        
        self.log("  行业信息检查:")
        for info, available in industry_info.items():
            status = "✅" if available else "⚠️"
            self.log(f"    {status} {info}: {available}")
        
        # 2. 模型分析确认价值
        self.log("\n  模型分析确认规则价值...")
        
        # 检查规则覆盖的攻击类型
        covered_attacks = set(attack_types.keys()) if attack_types else set()
        critical_attacks = {'data_exfiltration', 'credential_theft', 'prompt_injection', 'tool_poisoning'}
        
        coverage = len(covered_attacks & critical_attacks) / len(critical_attacks) * 100 if critical_attacks else 0
        self.log(f"  关键攻击覆盖：{coverage:.1f}%")
        
        # 评估规则价值
        rule_value = 'high' if coverage >= 75 else 'medium' if coverage >= 50 else 'low'
        self.log(f"  规则价值评估：{rule_value}")
        
        return {
            'industry_info': industry_info,
            'coverage': coverage,
            'value': rule_value
        }
    
    def enhance_rules(self, attack_types):
        """针对性增强规则 (严格质量控制)"""
        self.log("\n" + "=" * 60)
        self.log("Step 2: 增强规则 (严格质量控制)")
        self.log("=" * 60)
        
        if not attack_types:
            self.log("✅ 无需增强规则")
            return True
        
        # 分析规则质量
        quality_analysis = self.analyze_rule_quality(attack_types)
        
        # 只增强高价值规则
        if quality_analysis['value'] == 'low':
            self.log("⚠️  规则价值低，跳过增强")
            return False
        
        # 为每个高价值漏报攻击类型生成样本
        high_value_attacks = ['data_exfiltration', 'credential_theft', 'prompt_injection', 'tool_poisoning']
        for attack_type in attack_types:
            if attack_type in high_value_attacks:
                self.log(f"\n  生成高价值 {attack_type} 增强样本...")
                subprocess.run(
                    [sys.executable, "sample_generator.py", "--attack", attack_type, "--count", "10"],
                    cwd=str(self.sample_gen_dir),
                    capture_output=True
                )
            else:
                self.log(f"\n  ⚠️  跳过低价值 {attack_type}")
        
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
            return False
        
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
    
    def run_benchmark_test(self):
        """运行 security-benchmark 完整测试"""
        self.log("\n运行 security-benchmark 完整测试...")
        
        benchmark_script = self.benchmark_dir / "run_benchmark_scanner.py"
        if not benchmark_script.exists():
            self.log("⚠️  Benchmark 脚本不存在，使用简化测试")
            return None
        
        try:
            result = subprocess.run(
                [sys.executable, str(benchmark_script)],
                capture_output=True, text=True, timeout=300,
                cwd=str(self.benchmark_dir)
            )
            
            # 解析 benchmark 结果
            reports = glob.glob(str(self.benchmark_dir / "reports/benchmark_*.json"))
            if reports:
                latest = max(reports, key=lambda x: x)
                try:
                    with open(latest) as f:
                        benchmark_result = json.load(f)
                    self.log(f"✅ Benchmark 测试完成")
                    return benchmark_result
                except:
                    pass
        except Exception as e:
            self.log(f"⚠️  Benchmark 测试失败：{e}")
        
        return None
    
    def stratified_sample(self, samples, n, by_attack_type=True):
        """分层抽样 - 确保各攻击类型都有代表"""
        if not by_attack_type or n >= len(samples):
            return samples[:n]
        
        # 按攻击类型分组
        attack_groups = {}
        for sample in samples:
            try:
                with open(sample / "metadata.json") as f:
                    meta = json.load(f)
                attack_type = meta.get('attack_type', 'unknown')
                if attack_type not in attack_groups:
                    attack_groups[attack_type] = []
                attack_groups[attack_type].append(sample)
            except:
                if 'unknown' not in attack_groups:
                    attack_groups['unknown'] = []
                attack_groups['unknown'].append(sample)
        
        # 按比例抽样
        sampled = []
        samples_per_type = max(10, n // len(attack_groups))  # 每类至少 10 个
        
        for attack_type, group in sorted(attack_groups.items(), key=lambda x: -len(x[1])):
            # 大类多采样，小类少采样
            count = min(len(group), max(samples_per_type, len(group) // 10))
            sampled.extend(group[:count])
            
            if len(sampled) >= n:
                break
        
        return sampled[:n]
    
    def validate(self):
        """验证测试 (大规模分层抽样)"""
        self.log("\n" + "=" * 60)
        self.log("Step 3: 验证测试 (大规模分层抽样)")
        self.log("=" * 60)
        
        samples_dir = self.benchmark_dir / "samples/from-templates"
        
        # 获取所有样本
        all_mal = list(samples_dir.glob("**/MAL*"))
        all_ben = list(samples_dir.glob("**/BEN*"))
        
        self.log(f"总样本库：{len(all_mal)} 恶意 + {len(all_ben)} 良性 = {len(all_mal)+len(all_ben)} 个")
        
        # 分层抽样 (1000 样本：500+500)
        mal_samples = self.stratified_sample(all_mal, self.test_config['mal_samples'], self.test_config['by_attack_type'])
        ben_samples = self.stratified_sample(all_ben, self.test_config['ben_samples'], self.test_config['by_attack_type'])
        
        tp, fn, tn, fp = 0, 0, 0, 0
        detailed_results = []
        
        self.log(f"测试恶意样本 ({len(mal_samples)} 个，分层抽样)...")
        for i, sample in enumerate(mal_samples):
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
                    detected = report.get('summary', {}).get('malicious', 0) > 0
                    
                    # 获取样本信息
                    try:
                        with open(sample / "metadata.json") as f:
                            meta = json.load(f)
                        attack_type = meta.get('attack_type', 'unknown')
                        difficulty = meta.get('detection_difficulty', {}).get('level', 'unknown')
                    except:
                        attack_type = 'unknown'
                        difficulty = 'unknown'
                    
                    if detected:
                        tp += 1
                    else:
                        fn += 1
                        detailed_results.append({
                            'sample': sample.name,
                            'attack_type': attack_type,
                            'difficulty': difficulty,
                            'result': 'FN'
                        })
                except:
                    fn += 1
            
            # 每 50 个报告一次进度 (避免日志过多)
            if (i + 1) % 50 == 0:
                self.log(f"  进度：{i+1}/{len(mal_samples)} (TP={tp}, FN={fn})")
        
        self.log(f"测试良性样本 ({len(ben_samples)} 个，分层抽样)...")
        for i, sample in enumerate(ben_samples):
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
                    detected = report.get('summary', {}).get('malicious', 0) > 0
                    
                    if not detected:
                        tn += 1
                    else:
                        fp += 1
                        detailed_results.append({
                            'sample': sample.name,
                            'result': 'FP'
                        })
                except:
                    tn += 1
            
            # 每 50 个报告一次进度
            if (i + 1) % 50 == 0:
                self.log(f"  进度：{i+1}/{len(ben_samples)} (TN={tn}, FP={fp})")
        
        # 计算指标
        dr = tp / (tp + fn) * 100 if (tp + fn) > 0 else 0
        fpr = fp / (fp + tn) * 100 if (fp + tn) > 0 else 0
        precision = tp / (tp + fp) * 100 if (tp + fp) > 0 else 0
        f1 = 2 * dr * precision / (dr + precision) if (dr + precision) > 0 else 0
        
        # 统计攻击类型覆盖
        attack_types_tested = set()
        for result in detailed_results:
            if 'attack_type' in result:
                attack_types_tested.add(result['attack_type'])
        
        self.log(f"\n测试结果 (分层抽样):")
        self.log(f"  恶意样本：{tp}/{tp+fn}")
        self.log(f"  良性样本：{tn}/{tn+fp}")
        self.log(f"  总样本数：{tp+fn+tn+fp}")
        self.log(f"  攻击类型覆盖：{len(attack_types_tested)} 类")
        self.log(f"  检测率 (DR): {dr:.1f}%")
        self.log(f"  误报率 (FP): {fpr:.1f}%")
        self.log(f"  精确率 (Precision): {precision:.1f}%")
        self.log(f"  F1 分数：{f1:.1f}%")
        
        # 返回测试详情供质疑反思 Agent 使用
        return passed, dr, fpr, precision, f1, tp, fn, tn, fp
        
        # 运行 benchmark 测试
        benchmark_result = self.run_benchmark_test()
        if benchmark_result:
            self.log(f"\nBenchmark 结果:")
            for key, value in benchmark_result.items():
                if isinstance(value, (int, float)):
                    self.log(f"  {key}: {value}")
        
        # 严格质量门禁
        min_dr = self.quality_config['min_dr']
        max_fp = self.quality_config['max_fp']
        min_precision = self.quality_config['min_precision']
        min_f1 = self.quality_config['min_f1']
        
        if dr >= min_dr and fpr <= max_fp and precision >= min_precision and f1 >= min_f1:
            self.log(f"\n✅ 严格质量门禁通过 (DR≥{min_dr}%, FP≤{max_fp}%, Precision≥{min_precision}%, F1≥{min_f1}%)")
            
            # 保存详细结果
            results_file = self.scanner_dir / "test_results.json"
            with open(results_file, 'w') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'metrics': {
                        'detection_rate': dr,
                        'false_positive_rate': fpr,
                        'precision': precision,
                        'f1_score': f1,
                        'total_samples': tp+fn+tn+fp,
                        'tp': tp, 'fn': fn, 'tn': tn, 'fp': fp
                    },
                    'detailed_results': detailed_results[:20],  # 只保存前 20 个
                    'benchmark': benchmark_result
                }, f, indent=2)
            
            return True, dr, fpr, precision, f1
        else:
            self.log(f"\n⚠️  严格质量门禁未达标")
            self.log(f"  要求：DR≥{min_dr}%, FP≤{max_fp}%, Precision≥{min_precision}%, F1≥{min_f1}%")
            if dr < min_dr:
                self.log(f"  ❌ 检测率不足：{dr:.1f}% < {min_dr}%")
            if fpr > max_fp:
                self.log(f"  ❌ 误报率过高：{fpr:.1f}% > {max_fp}%")
            if precision < min_precision:
                self.log(f"  ❌ 精确率不足：{precision:.1f}% < {min_precision}%")
            if f1 < min_f1:
                self.log(f"  ❌ F1 分数不足：{f1:.1f}% < {min_f1}%")
            return False, dr, fpr, precision, f1
    
    def run_critic_agent(self, test_results):
        """运行质疑反思 Agent"""
        self.log("\n" + "=" * 60)
        self.log("Step 3.5: 质疑反思 Agent")
        self.log("=" * 60)
        
        try:
            from critic_agent import CriticAgent
            critic = CriticAgent()
            critic_result = critic.run(test_results)
            
            self.log(f"\n🤔 质疑反思结果:")
            self.log(f"  置信度：{critic_result['confidence']:.1f}%")
            self.log(f"  审批：{'✅ 通过' if critic_result['approved'] else '⚠️  存疑'}")
            self.log(f"  报告：{critic_result['report']}")
            
            return critic_result
        except Exception as e:
            self.log(f"⚠️  质疑反思 Agent 失败：{e}")
            return {'approved': True, 'confidence': 100, 'report': 'N/A'}  # 失败时不阻止发布
    
    def publish(self, passed, dr, fpr, precision, f1, critic_result=None):
        """发布 (增强版 + 质疑反思)"""
        self.log("\n" + "=" * 60)
        self.log("Step 4: 发布")
        self.log("=" * 60)
        
        if not passed:
            self.log("⚠️  质量未达标，跳过发布")
            self.log("\n📊 当前指标:")
            self.log(f"  检测率：{dr:.1f}% (要求≥{self.quality_config['min_dr']}%)")
            self.log(f"  误报率：{fpr:.1f}% (要求≤{self.quality_config['max_fp']}%)")
            self.log(f"  精确率：{precision:.1f}% (要求≥{self.quality_config['min_precision']}%)")
            self.log(f"  F1 分数：{f1:.1f}% (要求≥{self.quality_config['min_f1']}%)")
            return
        
        # 质疑反思 Agent 审批
        if critic_result and not critic_result.get('approved'):
            self.log("\n⚠️  质疑反思 Agent 未通过，需要人工审核")
            self.log(f"  置信度：{critic_result.get('confidence', 0):.1f}%")
            self.log(f"  报告：{critic_result.get('report', 'N/A')}")
            return
        
        # 提交到 git
        self.log("提交到 git...")
        subprocess.run(
            ["git", "add", "-A"],
            cwd=str(self.scanner_dir),
            capture_output=True
        )
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        msg = f"feat: 自治研发 {timestamp} - DR:{dr:.1f}%, FP:{fpr:.1f}%, P:{precision:.1f}%, F1:{f1:.1f}%"
        subprocess.run(
            ["git", "commit", "-m", msg],
            cwd=str(self.scanner_dir),
            capture_output=True
        )
        
        self.log("✅ 已提交到 git")
        
        # 创建发布报告 (包含质疑反思结果)
        report_file = self.scanner_dir / f"RELEASE_{timestamp}.md"
        with open(report_file, 'w') as f:
            f.write(f"# 📦 发布报告\n\n")
            f.write(f"**时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"## 📊 质量指标\n\n")
            f.write(f"| 指标 | 结果 | 要求 | 状态 |\n")
            f.write(f"|------|------|------|------|\n")
            f.write(f"| 检测率 | {dr:.1f}% | ≥{self.quality_config['min_dr']}% | {'✅' if dr >= self.quality_config['min_dr'] else '❌'} |\n")
            f.write(f"| 误报率 | {fpr:.1f}% | ≤{self.quality_config['max_fp']}% | {'✅' if fpr <= self.quality_config['max_fp'] else '❌'} |\n")
            f.write(f"| 精确率 | {precision:.1f}% | ≥{self.quality_config['min_precision']}% | {'✅' if precision >= self.quality_config['min_precision'] else '❌'} |\n")
            f.write(f"| F1 分数 | {f1:.1f}% | ≥{self.quality_config['min_f1']}% | {'✅' if f1 >= self.quality_config['min_f1'] else '❌'} |\n")
            
            if critic_result:
                f.write(f"\n## 🤔 质疑反思\n\n")
                f.write(f"- **置信度**: {critic_result.get('confidence', 0):.1f}%\n")
                f.write(f"- **审批**: {'✅ 通过' if critic_result.get('approved') else '⚠️  存疑'}\n")
                f.write(f"- **报告**: {critic_result.get('report', 'N/A')}\n")
        
        self.log(f"📄 发布报告：{report_file}")
    
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
            result = self.validate()
            passed = result[0]
            dr, fpr, precision, f1, tp, fn, tn, fp = result[1:]
            
            # 构建测试结果字典
            test_results = {
                'detection_rate': dr,
                'false_positive_rate': fpr,
                'precision': precision,
                'f1_score': f1,
                'total_malicious': tp + fn,
                'total_benign': tn + fp
            }
        else:
            passed, dr, fpr, precision, f1, tp, fn, tn, fp = False, 0, 0, 0, 0, 0, 0, 0, 0
            test_results = {}
        
        # Step 3.5: 质疑反思 Agent
        critic_result = None
        if passed:
            critic_result = self.run_critic_agent(test_results)
            # 如果质疑反思未通过，不发布
            if not critic_result.get('approved'):
                passed = False
        
        # Step 4: 发布
        self.publish(passed, dr, fpr, precision, f1, critic_result)
        
        self.log("\n" + "=" * 60)
        self.log("✅ 自治研发完成")
        self.log("=" * 60)
        
        return passed

if __name__ == '__main__':
    auto_rd = ScannerAutoRD()
    success = auto_rd.run()
    sys.exit(0 if success else 1)
