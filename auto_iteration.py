#!/usr/bin/env python3
"""
自动化持续迭代系统 - 样本采集、检测、评估、反思、优化循环
功能:
    并行执行样本采集 → 检测 → 评估 → 反思 → 优化
    持续迭代直到目标样本数

用法:
    python3 auto_iteration.py --target 5000 --parallel 8
"""

import os
import sys
import json
import time
import subprocess
import argparse
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE = os.path.expanduser("~/.openclaw/workspace")

class AutoIteration:
    """自动化迭代系统"""
    
    def __init__(self, target=5000, parallel=8):
        self.target = target
        self.parallel = parallel
        self.iteration = 0
        self.stats = {
            'total_samples': 0,
            'malicious': 0,
            'benign': 0,
            'detection_rate': 0,
            'false_positive_rate': 0,
            'f1_score': 0,
            'iterations': []
        }
        
    def collect_samples(self, keywords=None, count=50):
        """采集样本"""
        if keywords is None:
            keywords = ["security", "agent", "tool", "automation", "ai", "assistant"]
        
        log(f"📦 第 {self.iteration + 1} 轮样本采集...")
        
        cmd = [
            "python3", 
            f"{SCRIPTS_DIR}/real_skill_collector.py",
            "--keywords"
        ] + keywords + [
            "--limit", str(count),
            "--parallel", str(self.parallel)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # 统计采集数量
        samples_dir = f"{WORKSPACE}/skills/agent-security-skill-scanner/scripts/samples/real_skills"
        if os.path.exists(samples_dir):
            files = [f for f in os.listdir(samples_dir) if f.endswith(('.py', '.js', '.sh'))]
            return len(files)
        
        return 0
    
    def run_detection(self):
        """运行检测"""
        log("🔍 运行检测...")
        
        # 并行扫描
        cmd = [
            "python3",
            f"{SCRIPTS_DIR}/parallel_scanner.py",
            "--dir", "samples/real_skills",
            "--threads", str(self.parallel),
            "--output", f"iteration_{self.iteration}_scan.json"
        ]
        
        subprocess.run(cmd, capture_output=True)
        
        # 静态分析
        cmd = [
            "python3",
            f"{SCRIPTS_DIR}/static_analyzer.py",
            "--dir", "samples/real_skills",
            "--output", f"iteration_{self.iteration}_static.json"
        ]
        
        subprocess.run(cmd, capture_output=True)
        
        # 动态检测
        cmd = [
            "python3",
            f"{SCRIPTS_DIR}/dynamic_detector.py",
            "--dir", "samples/real_skills",
            "--output", f"iteration_{self.iteration}_dynamic.json"
        ]
        
        subprocess.run(cmd, capture_output=True)
        
        return True
    
    def evaluate(self):
        """评估检测能力"""
        log("📊 评估检测能力...")
        
        cmd = [
            "python3",
            f"{SCRIPTS_DIR}/evaluation_metrics.py",
            "--malicious-dir", "samples/external/malicious",
            "--benign-dir", "samples/external/benign",
            "--output", f"iteration_{self.iteration}_eval.json"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # 解析结果
        eval_file = f"{SCRIPTS_DIR}/iteration_{self.iteration}_eval.json"
        if os.path.exists(eval_file):
            with open(eval_file) as f:
                data = json.load(f)
                metrics = data.get('metrics', {})
                return {
                    'accuracy': metrics.get('accuracy', 0),
                    'precision': metrics.get('precision', 0),
                    'recall': metrics.get('recall', 0),
                    'f1_score': metrics.get('f1_score', 0),
                    'detection_rate': metrics.get('detection_rate', 0),
                    'false_positive_rate': metrics.get('false_positive_rate', 0)
                }
        
        return {}
    
    def reflect_and_optimize(self, eval_result):
        """反思与优化"""
        log("💡 反思与优化...")
        
        improvements = []
        
        # 根据评估结果优化
        f1 = eval_result.get('f1_score', 0)
        recall = eval_result.get('recall', 0)
        
        if recall < 90:
            improvements.append("召回率低，增加检测规则")
        
        if f1 < 90:
            improvements.append("F1 低，调整阈值")
        
        # 生成优化建议
        suggestions = []
        
        # 1. 如果样本不足，继续采集
        if self.stats['total_samples'] < self.target:
            suggestions.append({
                'action': 'collect_more',
                'reason': f"样本不足 ({self.stats['total_samples']}/{self.target})",
                'count': min(100, self.target - self.stats['total_samples'])
            })
        
        # 2. 如果检测率低，增加规则
        if recall < 95:
            suggestions.append({
                'action': 'enhance_detection',
                'reason': f"检测率低 ({recall}%)"
            })
        
        # 3. 定期生成外部样本
        if self.iteration % 3 == 0:
            suggestions.append({
                'action': 'generate_samples',
                'reason': "周期性补充合成样本"
            })
        
        return suggestions
    
    def generate_external_samples(self):
        """生成外部样本"""
        log("🎲 生成合成样本...")
        
        cmd = [
            "python3",
            f"{SCRIPTS_DIR}/external_malware_collector.py",
            "--malicious", "20",
            "--benign", "20"
        ]
        
        subprocess.run(cmd, capture_output=True)
    
    def count_samples(self):
        """统计样本数量"""
        samples_dir = f"{WORKSPACE}/skills/agent-security-skill-scanner/scripts/samples"
        
        total = 0
        malicious = 0
        benign = 0
        
        for category in ['real_skills', 'external']:
            category_dir = f"{samples_dir}/{category}"
            if not os.path.exists(category_dir):
                continue
            
            for subdir in ['malicious', 'benign']:
                path = f"{category_dir}/{subdir}"
                if os.path.exists(path):
                    files = [f for f in os.listdir(path) if f.endswith(('.py', '.js', '.sh'))]
                    count = len(files)
                    total += count
                    if subdir == 'malicious':
                        malicious += count
                    else:
                        benign += count
            
            # real_skills 算作良性
            real_dir = f"{category_dir}/real_skills"
            if os.path.exists(real_dir):
                files = [f for f in os.listdir(real_dir) if f.endswith(('.py', '.js', '.sh'))]
                total += len(files)
                benign += len(files)
        
        self.stats['total_samples'] = total
        self.stats['malicious'] = malicious
        self.stats['benign'] = benign
        
        return total
    
    def run_iteration(self):
        """执行单次迭代"""
        self.iteration += 1
        log(f"\n{'='*60}")
        log(f"🔄 第 {self.iteration} 次迭代")
        log(f"{'='*60}")
        
        start_time = time.time()
        
        # 1. 采集样本
        new_samples = self.collect_samples(count=30)
        
        # 2. 统计样本
        total = self.count_samples()
        log(f"📊 样本统计: 共 {total} 个 (恶意: {self.stats['malicious']}, 良性: {self.stats['benign']})")
        
        # 3. 运行检测
        self.run_detection()
        
        # 4. 评估
        eval_result = self.evaluate()
        
        # 5. 记录结果
        iteration_result = {
            'iteration': self.iteration,
            'timestamp': datetime.now().isoformat(),
            'samples': total,
            'evaluation': eval_result,
            'duration': time.time() - start_time
        }
        
        self.stats['iterations'].append(iteration_result)
        
        # 6. 反思优化
        suggestions = self.reflect_and_optimize(eval_result)
        
        log(f"\n📈 评估结果:")
        log(f"   准确率: {eval_result.get('accuracy', 0)}%")
        log(f"   F1 Score: {eval_result.get('f1_score', 0)}%")
        log(f"   召回率: {eval_result.get('recall', 0)}%")
        
        log(f"\n💡 优化建议:")
        for s in suggestions:
            log(f"   - {s['action']}: {s['reason']}")
        
        # 周期性生成样本
        if self.iteration % 3 == 0:
            self.generate_external_samples()
        
        return total >= self.target, suggestions
    
    def run(self, max_iterations=100):
        """运行完整迭代"""
        log("🚀 自动化持续迭代系统启动")
        log(f"🎯 目标样本数: {self.target}")
        
        # 初始样本统计
        self.count_samples()
        
        for i in range(max_iterations):
            done, suggestions = self.run_iteration()
            
            if done:
                log(f"\n✅ 达成目标! 共 {self.stats['total_samples']} 个样本")
                break
            
            # 执行优化建议
            for suggestion in suggestions:
                if suggestion['action'] == 'collect_more':
                    self.collect_samples(count=suggestion['count'])
                elif suggestion['action'] == 'generate_samples':
                    self.generate_external_samples()
            
            # 保存进度
            self.save_progress()
        
        # 最终统计
        self.print_summary()
        
        return self.stats
    
    def save_progress(self):
        """保存进度"""
        progress_file = f"{SCRIPTS_DIR}/iteration_progress.json"
        with open(progress_file, 'w') as f:
            json.dump(self.stats, f, indent=2)
    
    def print_summary(self):
        """打印总结"""
        log(f"\n{'='*60}")
        log(f"📊 迭代总结")
        log(f"{'='*60}")
        log(f"   总迭代次数: {self.iteration}")
        log(f"   样本总数: {self.stats['total_samples']}")
        log(f"   恶意样本: {self.stats['malicious']}")
        log(f"   良性样本: {self.stats['benign']}")
        
        if self.stats['iterations']:
            last = self.stats['iterations'][-1]
            eval_result = last.get('evaluation', {})
            log(f"\n   最后评估:")
            log(f"   - 准确率: {eval_result.get('accuracy', 0)}%")
            log(f"   - F1 Score: {eval_result.get('f1_score', 0)}%")
            log(f"   - 召回率: {eval_result.get('recall', 0)}%")

def main():
    parser = argparse.ArgumentParser(description="自动化持续迭代系统")
    parser.add_argument("--target", type=int, default=5000, help="目标样本数")
    parser.add_argument("--parallel", type=int, default=8, help="并行数")
    parser.add_argument("--max-iterations", type=int, default=100, help="最大迭代次数")
    
    args = parser.parse_args()
    
    iteration = AutoIteration(target=args.target, parallel=args.parallel)
    iteration.run(max_iterations=args.max_iterations)

if __name__ == "__main__":
    main()
