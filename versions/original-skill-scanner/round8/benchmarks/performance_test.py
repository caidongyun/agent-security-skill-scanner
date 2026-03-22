#!/usr/bin/env python3
"""
性能基准测试 (Performance Benchmark)

功能:
- 执行规则引擎性能基准测试
- 测量不同负载下的性能表现
- 生成性能基准报告
- 识别性能瓶颈

@author: Agent Security Skill Scanner
@version: 1.0.0
@date: 2026-03-19
"""

import sys
import time
import json
import statistics
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

# 添加框架路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'framework'))

from rule_executor import RuleExecutor
from test_case_generator import TestCaseGenerator


class PerformanceBenchmark:
    """性能基准测试器"""
    
    def __init__(self, output_dir: str = None):
        """
        初始化基准测试器
        
        Args:
            output_dir: 输出目录
        """
        self.output_dir = Path(output_dir) if output_dir else Path(__file__).parent.parent / 'reports'
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.executor = RuleExecutor(max_workers=4)
        self.generator = TestCaseGenerator()
        self.results = []
    
    def run_benchmark(self, iterations: int = 100) -> Dict[str, Any]:
        """
        运行基准测试
        
        Args:
            iterations: 迭代次数
            
        Returns:
            基准测试结果
        """
        print(f"开始基准测试 - {iterations} 次迭代")
        
        # 加载规则
        print("加载规则...")
        rules = self.executor.load_rules()
        print(f"已加载 {len(rules)} 条规则")
        
        # 生成测试用例
        print("生成测试用例...")
        test_cases = self.generator.generate_all_test_cases()
        print(f"已生成 {len(test_cases)} 个测试用例")
        
        # 预热
        print("预热执行引擎...")
        for tc in test_cases[:10]:
            self.executor.execute_test_case(tc)
        self.executor.reset_metrics()
        
        # 执行基准测试
        print(f"执行 {iterations} 次迭代...")
        all_times = []
        by_type_times = {}
        
        for i in range(iterations):
            # 随机选择测试用例
            tc = test_cases[i % len(test_cases)]
            start = time.perf_counter()
            result = self.executor.execute_test_case(tc)
            end = time.perf_counter()
            
            exec_time = (end - start) * 1000  # 转换为毫秒
            all_times.append(exec_time)
            
            attack_type = tc['attack_type']
            if attack_type not in by_type_times:
                by_type_times[attack_type] = []
            by_type_times[attack_type].append(exec_time)
            
            if (i + 1) % 20 == 0:
                print(f"  进度：{i + 1}/{iterations}")
        
        # 计算统计
        sorted_times = sorted(all_times)
        n = len(sorted_times)
        
        benchmark_results = {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'iterations': iterations,
                'rules_count': len(rules),
                'test_cases_count': len(test_cases)
            },
            'overall': {
                'total_executions': n,
                'min_ms': round(min(sorted_times), 3),
                'max_ms': round(max(sorted_times), 3),
                'mean_ms': round(statistics.mean(sorted_times), 3),
                'median_ms': round(statistics.median(sorted_times), 3),
                'std_dev_ms': round(statistics.stdev(sorted_times), 3) if n > 1 else 0,
                'p50_ms': round(sorted_times[int(n * 0.50)], 3),
                'p75_ms': round(sorted_times[int(n * 0.75)], 3),
                'p90_ms': round(sorted_times[int(n * 0.90)], 3),
                'p95_ms': round(sorted_times[int(n * 0.95)], 3),
                'p99_ms': round(sorted_times[int(n * 0.99)], 3),
                'p999_ms': round(sorted_times[int(n * 0.999)], 3) if n > 1000 else sorted_times[-1]
            },
            'by_attack_type': {},
            'throughput': {
                'executions_per_second': round(n / (sum(sorted_times) / 1000), 2),
                'avg_time_per_execution_ms': round(sum(sorted_times) / n, 3)
            },
            'target_compliance': {
                'p99_target_ms': 50,
                'p99_actual_ms': round(sorted_times[int(n * 0.99)], 3),
                'passed': sorted_times[int(n * 0.99)] < 50
            }
        }
        
        # 按攻击类型统计
        for attack_type, times in by_type_times.items():
            sorted_type_times = sorted(times)
            nt = len(sorted_type_times)
            benchmark_results['by_attack_type'][attack_type] = {
                'count': nt,
                'mean_ms': round(statistics.mean(sorted_type_times), 3),
                'p50_ms': round(sorted_type_times[int(nt * 0.50)], 3),
                'p95_ms': round(sorted_type_times[int(nt * 0.95)], 3),
                'p99_ms': round(sorted_type_times[int(nt * 0.99)], 3) if nt > 10 else sorted_type_times[-1]
            }
        
        self.results = benchmark_results
        return benchmark_results
    
    def run_load_test(self, concurrent_users: List[int] = None) -> Dict[str, Any]:
        """
        运行负载测试
        
        Args:
            concurrent_users: 并发用户数列表
            
        Returns:
            负载测试结果
        """
        if concurrent_users is None:
            concurrent_users = [1, 2, 4, 8, 16]
        
        print("开始负载测试...")
        
        # 生成测试用例
        test_cases = self.generator.generate_all_test_cases()
        
        load_results = {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'test_cases_count': len(test_cases)
            },
            'results': []
        }
        
        for users in concurrent_users:
            print(f"  测试并发用户数：{users}")
            
            executor = RuleExecutor(max_workers=users)
            executor.load_rules()
            
            times = []
            start = time.perf_counter()
            
            # 并发执行
            with ThreadPoolExecutor(max_workers=users) as pool:
                futures = [
                    pool.submit(executor.execute_test_case, tc)
                    for tc in test_cases
                ]
                for future in as_completed(futures):
                    result = future.result()
                    times.append(result.get('execution_time_ms', 0))
            
            end = time.perf_counter()
            total_time = end - start
            
            sorted_times = sorted(times)
            n = len(sorted_times)
            
            load_results['results'].append({
                'concurrent_users': users,
                'total_executions': n,
                'total_time_seconds': round(total_time, 3),
                'throughput_eps': round(n / total_time, 2),
                'min_ms': round(min(sorted_times), 3),
                'max_ms': round(max(sorted_times), 3),
                'avg_ms': round(sum(sorted_times) / n, 3),
                'p50_ms': round(sorted_times[int(n * 0.50)], 3),
                'p95_ms': round(sorted_times[int(n * 0.95)], 3),
                'p99_ms': round(sorted_times[int(n * 0.99)], 3)
            })
        
        return load_results
    
    def run_stress_test(self, duration_seconds: int = 60) -> Dict[str, Any]:
        """
        运行压力测试
        
        Args:
            duration_seconds: 测试持续时间
            
        Returns:
            压力测试结果
        """
        print(f"开始压力测试 - 持续 {duration_seconds} 秒")
        
        # 生成测试用例
        test_cases = self.generator.generate_all_test_cases()
        
        executor = RuleExecutor(max_workers=8)
        executor.load_rules()
        
        start = time.perf_counter()
        end_time = start + duration_seconds
        
        executions = 0
        errors = 0
        times = []
        
        while time.perf_counter() < end_time:
            tc = test_cases[executions % len(test_cases)]
            try:
                result = executor.execute_test_case(tc)
                times.append(result.get('execution_time_ms', 0))
                executions += 1
            except Exception as e:
                errors += 1
        
        total_time = time.perf_counter() - start
        
        stress_results = {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'duration_seconds': round(total_time, 3),
                'target_duration_seconds': duration_seconds
            },
            'summary': {
                'total_executions': executions,
                'errors': errors,
                'error_rate': round(errors / executions * 100, 2) if executions > 0 else 0,
                'throughput_eps': round(executions / total_time, 2),
                'avg_time_ms': round(sum(times) / len(times), 3) if times else 0
            }
        }
        
        if times:
            sorted_times = sorted(times)
            n = len(sorted_times)
            stress_results['performance'] = {
                'min_ms': round(min(sorted_times), 3),
                'max_ms': round(max(sorted_times), 3),
                'p50_ms': round(sorted_times[int(n * 0.50)], 3),
                'p95_ms': round(sorted_times[int(n * 0.95)], 3),
                'p99_ms': round(sorted_times[int(n * 0.99)], 3)
            }
        
        return stress_results
    
    def save_results(self, results: Dict[str, Any], filename: str = None) -> str:
        """
        保存测试结果
        
        Args:
            results: 测试结果
            filename: 文件名
            
        Returns:
            保存的文件路径
        """
        if filename is None:
            filename = f"benchmark_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        output_path = self.output_dir / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"结果已保存：{output_path}")
        return str(output_path)
    
    def print_summary(self, results: Dict[str, Any]):
        """打印结果摘要"""
        print("\n" + "=" * 60)
        print("性能基准测试摘要")
        print("=" * 60)
        
        if 'overall' in results:
            overall = results['overall']
            print(f"\n总体性能:")
            print(f"  执行次数：{overall['total_executions']}")
            print(f"  最小延迟：{overall['min_ms']:.3f}ms")
            print(f"  最大延迟：{overall['max_ms']:.3f}ms")
            print(f"  平均延迟：{overall['mean_ms']:.3f}ms")
            print(f"  P50 延迟：{overall['p50_ms']:.3f}ms")
            print(f"  P95 延迟：{overall['p95_ms']:.3f}ms")
            print(f"  P99 延迟：{overall['p99_ms']:.3f}ms")
            
            print(f"\n吞吐量:")
            print(f"  {results['throughput']['executions_per_second']} 执行/秒")
            
            print(f"\n目标达成:")
            p99_target = results['target_compliance']['p99_target_ms']
            p99_actual = results['target_compliance']['p99_actual_ms']
            passed = results['target_compliance']['passed']
            status = "✅" if passed else "❌"
            print(f"  {status} P99 < {p99_target}ms: {p99_actual:.3f}ms")
        
        print("=" * 60 + "\n")


def main():
    """主函数"""
    print("=" * 60)
    print("Round 8 性能基准测试")
    print("=" * 60)
    print()
    
    benchmark = PerformanceBenchmark()
    
    # 运行基准测试
    print("[1/3] 运行基准测试...")
    benchmark_results = benchmark.run_benchmark(iterations=300)
    benchmark.print_summary(benchmark_results)
    benchmark.save_results(benchmark_results, 'benchmark_results.json')
    
    # 运行负载测试
    print("[2/3] 运行负载测试...")
    load_results = benchmark.run_load_test([1, 2, 4, 8])
    benchmark.save_results(load_results, 'load_test_results.json')
    
    # 运行压力测试
    print("[3/3] 运行压力测试...")
    stress_results = benchmark.run_stress_test(duration_seconds=30)
    benchmark.save_results(stress_results, 'stress_test_results.json')
    
    print("\n✅ 所有性能测试完成!")
    print(f"\n结果保存在：{benchmark.output_dir}")


if __name__ == '__main__':
    main()
