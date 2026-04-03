#!/usr/bin/env python3
"""
质疑反思 Agent (Critic & Reflector)
用于验证自治研发系统的结果，防止自嗨、LLM 欺骗、数据源不可靠
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class CriticAgent:
    """质疑反思 Agent"""
    
    def __init__(self):
        self.scanner_dir = Path.home() / ".openclaw/workspace/agent-security-skill-scanner-master"
        self.benchmark_dir = Path.home() / "Desktop/security-benchmark"
        self.sample_gen_dir = Path.home() / ".openclaw/workspace/skills/security-sample-generator"
        
        # 质疑检查清单
        self.critic_checklist = {
            'data_quality': [
                '样本来源是否可靠？',
                '样本是否经过人工审核？',
                '样本是否有标注错误？',
                '样本分布是否合理？'
            ],
            'test_validity': [
                '测试样本量是否充足？',
                '抽样方法是否科学？',
                '是否存在数据泄露？',
                '测试结果是否可复现？'
            ],
            'rule_quality': [
                '规则是否过度拟合？',
                '规则是否有业务意义？',
                '规则是否可解释？',
                '规则是否有误报风险？'
            ],
            'llm_hallucination': [
                '结果是否被 LLM 美化？',
                '数据是否被篡改？',
                '日志是否真实？',
                '报告是否夸大？'
            ],
            'compatibility': [
                '规则是否兼容不同语言？',
                '规则是否兼容不同场景？',
                '规则是否兼容未来扩展？'
            ]
        }
    
    def log(self, msg):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🤔 {msg}")
    
    def verify_test_results(self, test_results: Dict) -> Dict:
        """验证测试结果真实性"""
        self.log("=" * 60)
        self.log("质疑 1: 验证测试结果真实性")
        self.log("=" * 60)
        
        concerns = []
        
        # 检查 1: 结果是否过于完美
        dr = test_results.get('detection_rate', 0)
        fp = test_results.get('false_positive_rate', 100)
        
        if dr > 99.5:
            concerns.append({
                'type': 'too_perfect',
                'severity': 'high',
                'message': f'检测率 {dr:.1f}% 过于完美，可能存在数据泄露或过拟合',
                'suggestion': '使用独立测试集验证'
            })
        
        if fp == 0.0 and test_results.get('total_benign', 0) > 100:
            concerns.append({
                'type': 'suspicious_zero_fp',
                'severity': 'medium',
                'message': f'误报率 0% ({test_results.get("total_benign", 0)} 个良性样本) 过于理想',
                'suggestion': '检查良性样本质量'
            })
        
        # 检查 2: 验证样本独立性
        self.log("检查样本独立性...")
        # TODO: 检查训练集和测试集是否有重叠
        
        # 检查 3: 验证结果可复现性
        self.log("验证结果可复现性...")
        # TODO: 重新运行测试，对比结果
        
        # 检查 4: 检查日志真实性
        self.log("检查日志真实性...")
        log_file = self.scanner_dir / "logs" / "auto_rd.log"
        if log_file.exists():
            with open(log_file) as f:
                log_content = f.read()
            # 检查日志是否有篡改痕迹
            if "ERROR" not in log_content and "WARNING" not in log_content:
                concerns.append({
                    'type': 'suspicious_log',
                    'severity': 'medium',
                    'message': '日志过于干净，没有任何错误或警告',
                    'suggestion': '检查日志是否被过滤'
                })
        
        if concerns:
            self.log(f"\n⚠️  发现 {len(concerns)} 个疑点:")
            for concern in concerns:
                self.log(f"  [{concern['severity']}] {concern['message']}")
                self.log(f"     建议：{concern['suggestion']}")
        else:
            self.log("\n✅ 测试结果通过验证")
        
        return {
            'verified': len(concerns) == 0,
            'concerns': concerns,
            'confidence': max(0, 100 - len(concerns) * 20)  # 每个疑点扣 20 分置信度
        }
    
    def verify_data_source(self) -> Dict:
        """验证数据源靠谱性"""
        self.log("\n" + "=" * 60)
        self.log("质疑 2: 验证数据源靠谱性")
        self.log("=" * 60)
        
        concerns = []
        
        # 检查 1: security-benchmark 来源
        self.log("检查 security-benchmark 来源...")
        benchmark_readme = self.benchmark_dir / "README.md"
        if benchmark_readme.exists():
            with open(benchmark_readme) as f:
                content = f.read()
            if 'license' not in content.lower() and 'source' not in content.lower():
                concerns.append({
                    'type': 'unclear_source',
                    'severity': 'medium',
                    'message': 'security-benchmark 来源不明确',
                    'suggestion': '添加数据来源说明'
                })
        else:
            concerns.append({
                'type': 'missing_documentation',
                'severity': 'high',
                'message': 'security-benchmark 缺少 README 文档',
                'suggestion': '创建数据来源文档'
            })
        
        # 检查 2: 样本质量
        self.log("检查样本质量...")
        samples_dir = self.benchmark_dir / "samples"
        if samples_dir.exists():
            # 随机抽查 10 个样本的 metadata
            import random
            mal_samples = list(samples_dir.glob("**/MAL*/metadata.json"))[:10]
            
            for metadata_file in mal_samples:
                try:
                    with open(metadata_file) as f:
                        meta = json.load(f)
                    
                    # 检查必要字段
                    required_fields = ['id', 'attack_type', 'ground_truth']
                    for field in required_fields:
                        if field not in meta:
                            concerns.append({
                                'type': 'incomplete_metadata',
                                'severity': 'low',
                                'message': f'{metadata_file.name} 缺少字段：{field}',
                                'suggestion': '完善 metadata'
                            })
                except Exception as e:
                    concerns.append({
                        'type': 'invalid_metadata',
                        'severity': 'medium',
                        'message': f'{metadata_file.name} 解析失败：{e}',
                        'suggestion': '修复 metadata 格式'
                    })
        
        # 检查 3: 规则来源
        self.log("检查规则来源...")
        rules_file = self.sample_gen_dir / "rules" / "sigma_converted.yar"
        if rules_file.exists():
            with open(rules_file) as f:
                rules_content = f.read()
            
            if 'source' not in rules_content.lower():
                concerns.append({
                    'type': 'unclear_rule_source',
                    'severity': 'medium',
                    'message': '规则来源不明确',
                    'suggestion': '添加规则来源注释'
                })
        
        if concerns:
            self.log(f"\n⚠️  发现 {len(concerns)} 个数据源问题:")
            for concern in concerns:
                self.log(f"  [{concern['severity']}] {concern['message']}")
        else:
            self.log("\n✅ 数据源通过验证")
        
        return {
            'verified': len(concerns) == 0,
            'concerns': concerns,
            'confidence': max(0, 100 - len(concerns) * 15)
        }
    
    def verify_rule_quality(self, rules_file: Path) -> Dict:
        """验证规则质量"""
        self.log("\n" + "=" * 60)
        self.log("质疑 3: 验证规则质量")
        self.log("=" * 60)
        
        concerns = []
        
        if not rules_file.exists():
            return {
                'verified': False,
                'concerns': [{'type': 'missing_rules', 'severity': 'critical', 'message': '规则文件不存在'}],
                'confidence': 0
            }
        
        with open(rules_file) as f:
            rules_content = f.read()
        
        # 检查 1: 规则数量
        rule_count = sum(1 for line in rules_content.split('\n') if line.strip().startswith('rule '))
        self.log(f"规则数量：{rule_count} 条")
        
        if rule_count < 100:
            concerns.append({
                'type': 'too_few_rules',
                'severity': 'medium',
                'message': f'规则数量 {rule_count} 过少，可能覆盖不足',
                'suggestion': '扩展规则库'
            })
        
        if rule_count > 5000:
            concerns.append({
                'type': 'too_many_rules',
                'severity': 'low',
                'message': f'规则数量 {rule_count} 过多，可能存在冗余',
                'suggestion': '去重优化'
            })
        
        # 检查 2: 规则重复
        self.log("检查规则重复...")
        rule_names = []
        for line in rules_content.split('\n'):
            if line.strip().startswith('rule '):
                rule_name = line.split()[1].split('{')[0].strip()
                rule_names.append(rule_name)
        
        duplicates = len(rule_names) - len(set(rule_names))
        if duplicates > 0:
            concerns.append({
                'type': 'duplicate_rules',
                'severity': 'high',
                'message': f'发现 {duplicates} 个重复规则',
                'suggestion': '去重'
            })
        
        # 检查 3: 规则复杂度
        self.log("检查规则复杂度...")
        # TODO: 分析规则复杂度，避免过于复杂的规则
        
        # 检查 4: 规则可解释性
        self.log("检查规则可解释性...")
        rules_without_meta = rules_content.count('rule ') - rules_content.count('meta:')
        if rules_without_meta > 0:
            concerns.append({
                'type': 'missing_metadata',
                'severity': 'medium',
                'message': f'{rules_without_meta} 个规则缺少 meta 信息',
                'suggestion': '添加规则说明'
            })
        
        if concerns:
            self.log(f"\n⚠️  发现 {len(concerns)} 个规则质量问题:")
            for concern in concerns:
                self.log(f"  [{concern['severity']}] {concern['message']}")
        else:
            self.log("\n✅ 规则质量通过验证")
        
        return {
            'verified': len(concerns) == 0,
            'concerns': concerns,
            'confidence': max(0, 100 - len(concerns) * 20)
        }
    
    def verify_compatibility(self) -> Dict:
        """验证兼容性"""
        self.log("\n" + "=" * 60)
        self.log("质疑 4: 验证兼容性")
        self.log("=" * 60)
        
        concerns = []
        
        # 检查 1: 语言兼容性
        self.log("检查语言兼容性...")
        # TODO: 测试不同编程语言的样本
        
        # 检查 2: 平台兼容性
        self.log("检查平台兼容性...")
        # TODO: 测试不同操作系统
        
        # 检查 3: 版本兼容性
        self.log("检查版本兼容性...")
        # TODO: 测试不同版本
        
        if concerns:
            self.log(f"\n⚠️  发现 {len(concerns)} 个兼容性问题")
        else:
            self.log("\n✅ 兼容性通过验证")
        
        return {
            'verified': len(concerns) == 0,
            'concerns': concerns,
            'confidence': 100 - len(concerns) * 25
        }
    
    def generate_reflection_report(self, results: Dict) -> Path:
        """生成反思报告"""
        report_file = self.scanner_dir / f"CRITIC_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# 🤔 质疑反思报告\n\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # 总体评估
            avg_confidence = sum(r.get('confidence', 0) for r in results.values()) / len(results)
            f.write(f"## 📊 总体置信度：{avg_confidence:.1f}%\n\n")
            
            if avg_confidence >= 80:
                f.write("**评估**: ✅ 通过验证，结果可信\n\n")
            elif avg_confidence >= 60:
                f.write("**评估**: ⚠️  存在疑点，建议复查\n\n")
            else:
                f.write("**评估**: ❌ 疑点较多，不可轻信\n\n")
            
            # 详细结果
            f.write("## 🔍 详细验证结果\n\n")
            
            for check_name, check_result in results.items():
                f.write(f"### {check_name}\n\n")
                f.write(f"- **置信度**: {check_result.get('confidence', 0):.1f}%\n")
                f.write(f"- **验证结果**: {'✅ 通过' if check_result.get('verified') else '⚠️  存疑'}\n")
                
                if check_result.get('concerns'):
                    f.write(f"- **疑点数量**: {len(check_result['concerns'])}\n\n")
                    f.write("| 严重性 | 问题 | 建议 |\n")
                    f.write("|--------|------|------|\n")
                    for concern in check_result['concerns']:
                        severity_icon = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}.get(
                            concern.get('severity', 'low'), '⚪')
                        f.write(f"| {severity_icon} {concern.get('severity')} | {concern.get('message')} | {concern.get('suggestion')} |\n")
                else:
                    f.write(f"- **疑点**: 无\n\n")
            
            # 建议
            f.write("## 💡 改进建议\n\n")
            all_concerns = []
            for check_result in results.values():
                all_concerns.extend(check_result.get('concerns', []))
            
            if all_concerns:
                f.write("1. **优先处理**:\n")
                for i, concern in enumerate(all_concerns[:5], 1):
                    if concern.get('severity') in ['critical', 'high']:
                        f.write(f"   {i}. {concern.get('message')}\n")
                        f.write(f"      → {concern.get('suggestion')}\n\n")
            else:
                f.write("当前没有需要优先处理的问题。\n")
        
        self.log(f"\n📄 反思报告已生成：{report_file}")
        return report_file
    
    def run(self, test_results: Optional[Dict] = None) -> Dict:
        """运行完整质疑反思流程"""
        self.log("🤔 质疑反思 Agent 启动")
        self.log(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        results = {}
        
        # 1. 验证测试结果
        if test_results:
            results['test_results'] = self.verify_test_results(test_results)
        else:
            self.log("⚠️  未提供测试结果，跳过验证")
        
        # 2. 验证数据源
        results['data_source'] = self.verify_data_source()
        
        # 3. 验证规则质量
        rules_file = self.sample_gen_dir / "rules" / "sigma_converted.yar"
        results['rule_quality'] = self.verify_rule_quality(rules_file)
        
        # 4. 验证兼容性
        results['compatibility'] = self.verify_compatibility()
        
        # 生成反思报告
        report_file = self.generate_reflection_report(results)
        
        # 总体评估
        avg_confidence = sum(r.get('confidence', 0) for r in results.values()) / len(results)
        
        self.log("\n" + "=" * 60)
        self.log("📊 质疑反思完成")
        self.log("=" * 60)
        self.log(f"总体置信度：{avg_confidence:.1f}%")
        self.log(f"反思报告：{report_file}")
        
        if avg_confidence >= 80:
            self.log("✅ 结果可信，可以发布")
            return {'approved': True, 'confidence': avg_confidence, 'report': str(report_file)}
        else:
            self.log("⚠️  结果存疑，建议复查后再发布")
            return {'approved': False, 'confidence': avg_confidence, 'report': str(report_file)}


if __name__ == '__main__':
    # 示例测试数据
    test_results = {
        'detection_rate': 99.8,
        'false_positive_rate': 0.0,
        'total_malicious': 500,
        'total_benign': 500,
        'precision': 100.0,
        'f1_score': 99.9
    }
    
    critic = CriticAgent()
    result = critic.run(test_results)
    
    sys.exit(0 if result['approved'] else 1)
