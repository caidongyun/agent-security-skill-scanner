#!/usr/bin/env python3
"""
🎯 Training & Improvement Agent - 训练提升 Agent
================================================
功能:
1. 使用 benchmark 样本进行扫描测试
2. 自动发现问题并优化代码
3. 记录问题到知识库 (用于未来参考)
4. 生成改进建议 (样本生成、规则设计)

工作流程:
扫描测试 → 发现问题 → 分析原因 → 优化代码 → 记录知识库 → 生成建议
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import statistics

SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

@dataclass
class IssueRecord:
    """问题记录"""
    id: str
    timestamp: str
    issue_type: str  # detection_failure, false_positive, performance, rule_issue
    severity: str    # critical, high, medium, low
    description: str
    sample_path: str
    sample_language: str
    attack_type: Optional[str]
    root_cause: Optional[str]
    suggested_fix: Optional[str]
    status: str      # open, investigating, fixed, wont_fix
    related_files: List[str]

@dataclass
class TrainingSession:
    """训练会话记录"""
    session_id: str
    start_time: str
    end_time: str
    total_samples: int
    scanned_samples: int
    detection_rate: float
    issues_found: int
    issues_fixed: int
    optimizations_made: List[str]
    knowledge_base_updated: bool

class TrainingAgent:
    """训练提升 Agent"""
    
    def __init__(self, project_dir: str, benchmark_dir: str, 
                 rules_dir: str, samples_dir: str):
        self.project_dir = Path(project_dir)
        self.benchmark_dir = Path(benchmark_dir)
        self.rules_dir = Path(rules_dir)
        self.samples_dir = Path(samples_dir)
        
        # 输出目录
        self.issues_dir = self.project_dir / 'training' / 'issues'
        self.kb_dir = self.project_dir / 'training' / 'knowledge-base'
        self.reports_dir = self.project_dir / 'training' / 'reports'
        
        for dir_path in [self.issues_dir, self.kb_dir, self.reports_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        self.issues: List[IssueRecord] = []
        self.session: Optional[TrainingSession] = None
        
    def run_benchmark_scan(self, scanner_name: str = 'ultimate_v2') -> Dict:
        """运行基准扫描测试"""
        print("\n" + "=" * 70)
        print("🎯 训练提升 Agent - 基准扫描测试")
        print("=" * 70)
        print(f"扫描器：{scanner_name}")
        print(f"样本目录：{self.samples_dir}")
        print()
        
        # 调用扫描器
        scanner_path = self.project_dir / f"{scanner_name}.py"
        if not scanner_path.exists():
            # 尝试备用名称
            alt_scanner_path = self.project_dir / f"ultimate_scanner_{scanner_name}.py"
            if alt_scanner_path.exists():
                scanner_path = alt_scanner_path
            else:
                print(f"❌ 扫描器不存在：{scanner_path}")
                return {}
        
        cmd = [
            'python3', str(scanner_path),
            '--samples', str(self.samples_dir),
            '--rules', str(self.rules_dir),
            '--workers', '8',
            '--output', str(self.reports_dir / f'benchmark_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            # 解析输出
            output = result.stdout + result.stderr
            print(output)
            
            # 提取关键指标
            metrics = self._parse_scan_output(output)
            return metrics
            
        except subprocess.TimeoutExpired:
            print("❌ 扫描超时 (5 分钟)")
            return {'error': 'timeout'}
        except Exception as e:
            print(f"❌ 扫描失败：{e}")
            return {'error': str(e)}
    
    def _parse_scan_output(self, output: str) -> Dict:
        """解析扫描输出"""
        metrics = {}
        
        # 提取检测率
        if '检测率：' in output:
            for line in output.split('\n'):
                if '检测率：' in line and '%' in line:
                    try:
                        rate = float(line.split('：')[1].split('%')[0].strip())
                        metrics['detection_rate'] = rate
                    except:
                        pass
        
        # 提取样本数
        if '扫描样本：' in output:
            for line in output.split('\n'):
                if '扫描样本：' in line:
                    try:
                        count = int(line.split('：')[1].strip())
                        metrics['total_samples'] = count
                    except:
                        pass
        
        # 提取恶意样本数
        if '恶意样本：' in output:
            for line in output.split('\n'):
                if '恶意样本：' in line and '/' in line:
                    try:
                        parts = line.split('：')[1].strip().split('/')
                        malicious = int(parts[0])
                        metrics['malicious_detected'] = malicious
                    except:
                        pass
        
        return metrics
    
    def analyze_failures(self, scan_results: Dict) -> List[IssueRecord]:
        """分析扫描失败案例"""
        print("\n" + "=" * 70)
        print("🔍 分析扫描失败案例")
        print("=" * 70)
        
        issues = []
        detection_rate = scan_results.get('detection_rate', 0)
        
        # 如果检测率低于目标 (95%)
        if detection_rate < 95:
            print(f"⚠️  检测率 {detection_rate}% < 95% (目标)")
            
            issue = IssueRecord(
                id=f"DET-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                timestamp=datetime.now().isoformat(),
                issue_type='detection_failure',
                severity='high' if detection_rate < 80 else 'medium',
                description=f'检测率 {detection_rate}% 低于目标值 95%',
                sample_path=str(self.samples_dir),
                sample_language='multiple',
                attack_type='unknown',
                root_cause='待分析',
                suggested_fix='分析漏报样本，增强 YARA 规则或 AST 检测',
                status='open',
                related_files=[str(self.rules_dir)]
            )
            issues.append(issue)
            print(f"  📝 记录问题：{issue.id} - {issue.description}")
        
        # 分析特定语言的检测率
        # (可以从扫描报告中提取更详细的信息)
        
        self.issues.extend(issues)
        return issues
    
    def generate_optimization_suggestions(self, issues: List[IssueRecord]) -> Dict:
        """生成优化建议"""
        print("\n" + "=" * 70)
        print("💡 生成优化建议")
        print("=" * 70)
        
        suggestions = {
            'rules': [],
            'samples': [],
            'scanner': [],
            'knowledge_base': []
        }
        
        for issue in issues:
            if issue.issue_type == 'detection_failure':
                # YARA 规则优化建议
                suggestions['rules'].append({
                    'type': 'rule_enhancement',
                    'priority': 'high',
                    'suggestion': '分析漏报样本的共有特征，生成针对性 YARA 规则',
                    'action': '运行 optimize_rules.sh 或 scan_full_v2.py 进行规则优化'
                })
                
                # 样本生成建议
                suggestions['samples'].append({
                    'type': 'sample_generation',
                    'priority': 'medium',
                    'suggestion': '为检测率低的攻击类型生成更多变体样本',
                    'action': '使用 variant_generator.py 生成特定攻击类型的样本'
                })
                
                # 扫描器优化建议
                suggestions['scanner'].append({
                    'type': 'scanner_improvement',
                    'priority': 'medium',
                    'suggestion': '考虑增加新的检测引擎 (如 ML 模型、行为分析)',
                    'action': '研究 multi_language_scanner_v4.py 的 AST/JS 分析能力'
                })
        
        # 知识库更新建议
        suggestions['knowledge_base'].append({
            'type': 'documentation',
            'priority': 'high',
            'suggestion': '记录本次训练发现的问题和解决方案',
            'action': f'查看 {self.kb_dir} 目录的知识库文件'
        })
        
        # 打印建议
        for category, items in suggestions.items():
            print(f"\n{category.upper()}:")
            for item in items:
                priority_emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}[item['priority']]
                print(f"  {priority_emoji} [{item['type']}] {item['suggestion']}")
        
        return suggestions
    
    def save_issues(self, issues: List[IssueRecord]):
        """保存问题记录"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        issues_file = self.issues_dir / f"issues_{timestamp}.json"
        
        with open(issues_file, 'w', encoding='utf-8') as f:
            json.dump([asdict(i) for i in issues], f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 问题记录已保存：{issues_file}")
    
    def update_knowledge_base(self, issues: List[IssueRecord], suggestions: Dict):
        """更新知识库"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        kb_file = self.kb_dir / f"training_session_{timestamp}.md"
        
        with open(kb_file, 'w', encoding='utf-8') as f:
            f.write(f"# 训练会话记录 - {timestamp}\n\n")
            f.write(f"**时间**: {datetime.now().isoformat()}\n")
            f.write(f"**样本目录**: {self.samples_dir}\n")
            f.write(f"**规则目录**: {self.rules_dir}\n\n")
            
            f.write("## 发现的问题\n\n")
            for issue in issues:
                f.write(f"### {issue.id} - {issue.issue_type}\n")
                f.write(f"- **严重程度**: {issue.severity}\n")
                f.write(f"- **描述**: {issue.description}\n")
                f.write(f"- **根本原因**: {issue.root_cause or '待分析'}\n")
                f.write(f"- **建议修复**: {issue.suggested_fix or '待制定'}\n\n")
            
            f.write("## 优化建议\n\n")
            for category, items in suggestions.items():
                f.write(f"### {category.upper()}\n")
                for item in items:
                    f.write(f"- [{item['priority']}] {item['suggestion']}\n")
                f.write("\n")
            
            f.write("## 经验教训\n\n")
            f.write("### 扫描器设计注意事项\n")
            f.write("1. YARA 规则需要定期更新和验证\n")
            f.write("2. 多语言支持需要考虑不同语言的特性\n")
            f.write("3. 性能优化很重要 (并发、缓存)\n")
            f.write("4. 误报率控制与检测率的平衡\n\n")
            
            f.write("### 样本生成注意事项\n")
            f.write("1. 样本需要覆盖多种攻击类型和变体\n")
            f.write("2. 包含足够的良性样本用于对比测试\n")
            f.write("3. 样本应该有清晰的标签和元数据\n\n")
            
            f.write("### 规则设计注意事项\n")
            f.write("1. 规则要有特异性，避免过于宽泛\n")
            f.write("2. 使用分级规则 (L1/L2/L3) 平衡性能和准确率\n")
            f.write("3. 定期用新样本验证规则效果\n")
        
        print(f"💾 知识库已更新：{kb_file}")
    
    def run_training_session(self) -> TrainingSession:
        """运行完整训练会话"""
        session_id = f"TRAIN-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        print("\n" + "=" * 70)
        print(f"🎯 训练提升 Agent - 会话 {session_id}")
        print("=" * 70)
        
        self.session = TrainingSession(
            session_id=session_id,
            start_time=datetime.now().isoformat(),
            end_time='',
            total_samples=0,
            scanned_samples=0,
            detection_rate=0,
            issues_found=0,
            issues_fixed=0,
            optimizations_made=[],
            knowledge_base_updated=False
        )
        
        # 步骤 1: 运行基准扫描
        scan_results = self.run_benchmark_scan('ultimate_v2')
        
        if 'error' not in scan_results:
            self.session.total_samples = scan_results.get('total_samples', 0)
            self.session.scanned_samples = scan_results.get('total_samples', 0)
            self.session.detection_rate = scan_results.get('detection_rate', 0)
        
        # 步骤 2: 分析失败案例
        issues = self.analyze_failures(scan_results)
        self.session.issues_found = len(issues)
        
        # 步骤 3: 生成优化建议
        suggestions = self.generate_optimization_suggestions(issues)
        
        # 步骤 4: 保存问题记录
        self.save_issues(issues)
        
        # 步骤 5: 更新知识库
        self.update_knowledge_base(issues, suggestions)
        self.session.knowledge_base_updated = True
        
        # 步骤 6: 生成训练报告
        self.session.end_time = datetime.now().isoformat()
        report_file = self.reports_dir / f"training_report_{session_id}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(self.session), f, indent=2, ensure_ascii=False)
        
        # 打印摘要
        print("\n" + "=" * 70)
        print("📊 训练会话摘要")
        print("=" * 70)
        print(f"会话 ID: {session_id}")
        print(f"总样本数：{self.session.total_samples}")
        print(f"检测率：{self.session.detection_rate:.1f}%")
        print(f"发现问题：{self.session.issues_found} 个")
        print(f"知识库已更新：{'✅' if self.session.knowledge_base_updated else '❌'}")
        print(f"报告已保存：{report_file}")
        print("=" * 70)
        
        return self.session

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='🎯 训练提升 Agent')
    parser.add_argument('--project', default='/home/cdy/.openclaw/workspace/agent-security-skill-scanner-master',
                       help='项目目录')
    parser.add_argument('--benchmark', default='/home/cdy/Desktop/security-benchmark',
                       help='Benchmark 目录')
    parser.add_argument('--samples', default='/home/cdy/Desktop/security-benchmark/samples/from-templates',
                       help='样本目录')
    parser.add_argument('--rules', default='rules/scanner_v3/yara',
                       help='规则目录')
    parser.add_argument('--session', action='store_true',
                       help='运行完整训练会话')
    
    args = parser.parse_args()
    
    project_dir = Path(args.project)
    rules_dir = project_dir / args.rules if not Path(args.rules).is_absolute() else Path(args.rules)
    
    # 创建训练 Agent
    agent = TrainingAgent(
        project_dir=project_dir,
        benchmark_dir=args.benchmark,
        rules_dir=str(rules_dir),
        samples_dir=args.samples
    )
    
    if args.session:
        # 运行完整训练会话
        agent.run_training_session()
    else:
        # 仅运行扫描测试
        results = agent.run_benchmark_scan()
        print(f"\n扫描结果：{results}")

if __name__ == '__main__':
    main()
