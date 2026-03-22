#!/usr/bin/env python3
"""
结果分析器
分析规则执行结果，计算检测率、误报率、F1 Score 等指标
"""

import json
import statistics
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

BASE_DIR = Path('/home/cdy/.openclaw/workspace/skills/agent-security-skill-scanner/expert_mode/round8')
TEST_CASES_DIR = BASE_DIR / 'test_cases'
RESULTS_DIR = BASE_DIR / 'results'
REPORTS_DIR = BASE_DIR / 'reports'


class ResultAnalyzer:
    """结果分析器"""
    
    def __init__(self):
        self.test_cases = []
        self.results = []
        self.analysis = {}
    
    def load_test_cases(self, path: str = None) -> List[Dict]:
        """加载测试用例"""
        if path is None:
            path = TEST_CASES_DIR / 'all_test_cases.json'
        
        with open(path, 'r', encoding='utf-8') as f:
            self.test_cases = json.load(f)
        
        # 创建 ID 到测试用例的映射
        self.test_case_map = {tc['test_case_id']: tc for tc in self.test_cases}
        return self.test_cases
    
    def load_results(self, path: str = None) -> List[Dict]:
        """加载执行结果"""
        if path is None:
            path = RESULTS_DIR / 'execution_results.json'
        
        with open(path, 'r', encoding='utf-8') as f:
            self.results = json.load(f)
        
        return self.results
    
    def calculate_confusion_matrix(self) -> Dict[str, int]:
        """
        计算混淆矩阵
        
        Returns:
            TP: 真阳性 (正确检测到的攻击)
            TN: 真阴性 (正确放行的正常样本)
            FP: 假阳性 (误报)
            FN: 假阴性 (漏报)
        """
        cm = {'TP': 0, 'TN': 0, 'FP': 0, 'FN': 0, 'UNCLEAR': 0}
        
        for result in self.results:
            test_case_id = result['test_case_id']
            detected = result.get('detected', False)
            
            # 获取期望结果
            test_case = self.test_case_map.get(test_case_id)
            if not test_case:
                continue
            
            expected = test_case['expected_result']
            
            # 边界样本 (expected=None) 单独统计
            if expected is None:
                cm['UNCLEAR'] += 1
                continue
            
            # 计算混淆矩阵
            if expected and detected:
                cm['TP'] += 1  # 真阳性
            elif not expected and not detected:
                cm['TN'] += 1  # 真阴性
            elif not expected and detected:
                cm['FP'] += 1  # 假阳性 (误报)
            elif expected and not detected:
                cm['FN'] += 1  # 假阴性 (漏报)
        
        return cm
    
    def calculate_metrics(self) -> Dict[str, float]:
        """
        计算评估指标
        
        Returns:
            包含各种评估指标的字典
        """
        cm = self.calculate_confusion_matrix()
        
        # 检测率 (Recall / Sensitivity)
        # TP / (TP + FN) - 实际为阳性的样本中有多少被正确检测
        if cm['TP'] + cm['FN'] > 0:
            detection_rate = cm['TP'] / (cm['TP'] + cm['FN'])
        else:
            detection_rate = 0.0
        
        # 特异性 (Specificity)
        # TN / (TN + FP) - 实际为阴性的样本中有多少被正确识别
        if cm['TN'] + cm['FP'] > 0:
            specificity = cm['TN'] / (cm['TN'] + cm['FP'])
        else:
            specificity = 0.0
        
        # 精确率 (Precision)
        # TP / (TP + FP) - 检测为阳性的样本中有多少是真的阳性
        if cm['TP'] + cm['FP'] > 0:
            precision = cm['TP'] / (cm['TP'] + cm['FP'])
        else:
            precision = 0.0
        
        # 误报率 (False Positive Rate)
        # FP / (FP + TN) - 实际为阴性的样本中有多少被误报
        if cm['FP'] + cm['TN'] > 0:
            false_positive_rate = cm['FP'] / (cm['FP'] + cm['TN'])
        else:
            false_positive_rate = 0.0
        
        # F1 Score
        # 2 * Precision * Recall / (Precision + Recall)
        if precision + detection_rate > 0:
            f1_score = 2 * precision * detection_rate / (precision + detection_rate)
        else:
            f1_score = 0.0
        
        # 准确率 (Accuracy)
        # (TP + TN) / (TP + TN + FP + FN)
        total = cm['TP'] + cm['TN'] + cm['FP'] + cm['FN']
        if total > 0:
            accuracy = (cm['TP'] + cm['TN']) / total
        else:
            accuracy = 0.0
        
        return {
            'detection_rate': detection_rate,
            'detection_rate_pct': round(detection_rate * 100, 2),
            'specificity': specificity,
            'specificity_pct': round(specificity * 100, 2),
            'precision': precision,
            'precision_pct': round(precision * 100, 2),
            'false_positive_rate': false_positive_rate,
            'false_positive_rate_pct': round(false_positive_rate * 100, 2),
            'f1_score': f1_score,
            'f1_score_pct': round(f1_score * 100, 2),
            'accuracy': accuracy,
            'accuracy_pct': round(accuracy * 100, 2),
            'confusion_matrix': cm
        }
    
    def analyze_by_attack_type(self) -> Dict[str, Dict]:
        """按攻击类型分析"""
        analysis = {}
        
        for attack_type in ['tool_poisoning', 'remote_load', 'data_exfil', 
                           'prompt_injection', 'resource_exhaustion', 'memory_pollution']:
            # 筛选该攻击类型的结果
            attack_results = [
                r for r in self.results 
                if self.test_case_map.get(r['test_case_id'], {}).get('attack_type') == attack_type
            ]
            
            if not attack_results:
                continue
            
            # 计算该攻击类型的指标
            cm = {'TP': 0, 'TN': 0, 'FP': 0, 'FN': 0}
            
            for result in attack_results:
                test_case = self.test_case_map.get(result['test_case_id'])
                if not test_case:
                    continue
                
                expected = test_case['expected_result']
                if expected is None:
                    continue
                
                detected = result.get('detected', False)
                
                if expected and detected:
                    cm['TP'] += 1
                elif not expected and not detected:
                    cm['TN'] += 1
                elif not expected and detected:
                    cm['FP'] += 1
                elif expected and not detected:
                    cm['FN'] += 1
            
            # 计算检测率
            if cm['TP'] + cm['FN'] > 0:
                detection_rate = cm['TP'] / (cm['TP'] + cm['FN'])
            else:
                detection_rate = 0.0
            
            # 计算误报率
            if cm['FP'] + cm['TN'] > 0:
                fpr = cm['FP'] / (cm['FP'] + cm['TN'])
            else:
                fpr = 0.0
            
            analysis[attack_type] = {
                'total': len(attack_results),
                'true_positives': cm['TP'],
                'true_negatives': cm['TN'],
                'false_positives': cm['FP'],
                'false_negatives': cm['FN'],
                'detection_rate': round(detection_rate * 100, 2),
                'false_positive_rate': round(fpr * 100, 2)
            }
        
        return analysis
    
    def analyze_by_rule_type(self) -> Dict[str, Dict]:
        """按规则类型分析"""
        analysis = {}
        
        # 按触发规则类型分组
        rule_stats = {}
        for result in self.results:
            triggered_rules = result.get('triggered_rules', [])
            for rule in triggered_rules:
                rule_type = rule.get('rule_type', 'unknown')
                if rule_type not in rule_stats:
                    rule_stats[rule_type] = {'triggered': 0, 'results': []}
                rule_stats[rule_type]['triggered'] += 1
                rule_stats[rule_type]['results'].append(result)
        
        for rule_type, stats in rule_stats.items():
            # 计算该规则类型的效果
            correct = sum(1 for r in stats['results'] if r.get('detected', False))
            analysis[rule_type] = {
                'triggered_count': stats['triggered'],
                'detection_rate': round(correct / len(stats['results']) * 100, 2) if stats['results'] else 0
            }
        
        return analysis
    
    def calculate_performance_stats(self) -> Dict[str, float]:
        """计算性能统计 (p50/p90/p99)"""
        latencies = []
        
        for result in self.results:
            latency_ms = result.get('latency_ms', 0)
            if latency_ms > 0:
                latencies.append(latency_ms)
        
        if not latencies:
            return {
                'p50_ms': 0,
                'p90_ms': 0,
                'p99_ms': 0,
                'avg_ms': 0,
                'min_ms': 0,
                'max_ms': 0
            }
        
        latencies.sort()
        n = len(latencies)
        
        return {
            'p50_ms': round(latencies[int(n * 0.50)], 2),
            'p90_ms': round(latencies[int(n * 0.90)], 2),
            'p99_ms': round(latencies[min(int(n * 0.99), n-1)], 2),
            'avg_ms': round(statistics.mean(latencies), 2),
            'min_ms': round(min(latencies), 2),
            'max_ms': round(max(latencies), 2)
        }
    
    def identify_problem_rules(self) -> List[Dict]:
        """识别问题规则"""
        problem_rules = []
        
        # 统计每个规则的误报和漏报
        rule_stats = {}
        for result in self.results:
            triggered_rules = result.get('triggered_rules', [])
            test_case = self.test_case_map.get(result['test_case_id'])
            
            if not test_case:
                continue
            
            expected = test_case['expected_result']
            detected = result.get('detected', False)
            
            for rule in triggered_rules:
                rule_id = rule.get('rule_id', 'unknown')
                if rule_id not in rule_stats:
                    rule_stats[rule_id] = {
                        'rule_id': rule_id,
                        'rule_type': rule.get('rule_type', 'unknown'),
                        'false_positives': 0,
                        'true_positives': 0,
                        'false_negatives': 0,
                        'true_negatives': 0
                    }
                
                if expected is None:
                    continue
                
                if expected and detected:
                    rule_stats[rule_id]['true_positives'] += 1
                elif not expected and not detected:
                    rule_stats[rule_id]['true_negatives'] += 1
                elif not expected and detected:
                    rule_stats[rule_id]['false_positives'] += 1
                elif expected and not detected:
                    rule_stats[rule_id]['false_negatives'] += 1
        
        # 找出误报率高的规则
        for rule_id, stats in rule_stats.items():
            total = stats['true_positives'] + stats['false_positives']
            if total > 0:
                fpr = stats['false_positives'] / total
                if fpr > 0.1:  # 误报率超过 10%
                    problem_rules.append({
                        'rule_id': rule_id,
                        'rule_type': stats['rule_type'],
                        'false_positive_rate': round(fpr * 100, 2),
                        'false_positives': stats['false_positives'],
                        'true_positives': stats['true_positives'],
                        'issue': 'high_false_positive_rate'
                    })
        
        # 找出漏报率高的规则
        for rule_id, stats in rule_stats.items():
            total = stats['true_positives'] + stats['false_negatives']
            if total > 0:
                fnr = stats['false_negatives'] / total
                if fnr > 0.3:  # 漏报率超过 30%
                    problem_rules.append({
                        'rule_id': rule_id,
                        'rule_type': stats['rule_type'],
                        'false_negative_rate': round(fnr * 100, 2),
                        'false_negatives': stats['false_negatives'],
                        'true_positives': stats['true_positives'],
                        'issue': 'high_false_negative_rate'
                    })
        
        return problem_rules
    
    def count_passed_rules(self) -> Dict[str, int]:
        """统计通过的规则数"""
        # 简单判断：如果整体检测率>80% 且误报率<20%，认为规则通过
        metrics = self.calculate_metrics()
        
        passed = 0
        total = 0
        
        # 按攻击类型统计
        by_attack = self.analyze_by_attack_type()
        for attack_type, stats in by_attack.items():
            total += 1
            if stats['detection_rate'] >= 80 and stats['false_positive_rate'] <= 20:
                passed += 1
        
        return {
            'passed': passed,
            'total': total,
            'pass_rate': round(passed / total * 100, 2) if total > 0 else 0
        }
    
    def run_analysis(self) -> Dict[str, Any]:
        """运行完整分析"""
        print("加载测试用例...")
        self.load_test_cases()
        
        print("加载执行结果...")
        self.load_results()
        
        print("计算评估指标...")
        metrics = self.calculate_metrics()
        
        print("按攻击类型分析...")
        by_attack = self.analyze_by_attack_type()
        
        print("按规则类型分析...")
        by_rule = self.analyze_by_rule_type()
        
        print("计算性能统计...")
        performance = self.calculate_performance_stats()
        
        print("识别问题规则...")
        problem_rules = self.identify_problem_rules()
        
        print("统计通过规则...")
        passed_rules = self.count_passed_rules()
        
        self.analysis = {
            'analysis_timestamp': datetime.now().isoformat(),
            'total_test_cases': len(self.test_cases),
            'total_results': len(self.results),
            'overall_metrics': metrics,
            'by_attack_type': by_attack,
            'by_rule_type': by_rule,
            'performance_stats': performance,
            'problem_rules': problem_rules,
            'passed_rules': passed_rules
        }
        
        return self.analysis
    
    def save_analysis(self, output_path: str = None) -> str:
        """保存分析结果"""
        if output_path is None:
            REPORTS_DIR.mkdir(parents=True, exist_ok=True)
            output_path = REPORTS_DIR / 'analysis_results.json'
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.analysis, f, indent=2, ensure_ascii=False)
        
        return str(output_path)


def main():
    print("=" * 60)
    print("Round 8 结果分析器")
    print("=" * 60)
    
    analyzer = ResultAnalyzer()
    analysis = analyzer.run_analysis()
    
    # 保存分析结果
    output_path = analyzer.save_analysis()
    print(f"\n分析结果保存到：{output_path}")
    
    # 打印关键指标
    print("\n" + "=" * 60)
    print("关键指标")
    print("=" * 60)
    
    metrics = analysis['overall_metrics']
    print(f"\n检测率 (Detection Rate): {metrics['detection_rate_pct']}%")
    print(f"误报率 (False Positive Rate): {metrics['false_positive_rate_pct']}%")
    print(f"精确率 (Precision): {metrics['precision_pct']}%")
    print(f"F1 Score: {metrics['f1_score_pct']}%")
    print(f"准确率 (Accuracy): {metrics['accuracy_pct']}%")
    
    print("\n混淆矩阵:")
    cm = metrics['confusion_matrix']
    print(f"  TP (真阳性): {cm['TP']}")
    print(f"  TN (真阴性): {cm['TN']}")
    print(f"  FP (假阳性): {cm['FP']}")
    print(f"  FN (假阴性): {cm['FN']}")
    print(f"  UNCLEAR (边界): {cm['UNCLEAR']}")
    
    print("\n性能统计:")
    perf = analysis['performance_stats']
    print(f"  P50: {perf['p50_ms']} ms")
    print(f"  P90: {perf['p90_ms']} ms")
    print(f"  P99: {perf['p99_ms']} ms")
    print(f"  平均：{perf['avg_ms']} ms")
    
    print("\n通过规则:")
    passed = analysis['passed_rules']
    print(f"  通过：{passed['passed']}/{passed['total']} ({passed['pass_rate']}%)")
    
    if analysis['problem_rules']:
        print(f"\n问题规则：{len(analysis['problem_rules'])} 个")
        for pr in analysis['problem_rules'][:5]:
            print(f"  - {pr['rule_id']}: {pr['issue']}")
    
    print("\n✅ 分析完成!")
    
    return analysis


if __name__ == '__main__':
    main()
