#!/usr/bin/env python3
"""
Round 18: 并行执行器

功能:
1. 多进程扫描
2. 负载均衡
3. 容错处理
"""

import multiprocessing as mp
from multiprocessing import Pool, cpu_count
import json
import time
from pathlib import Path
from typing import Dict, List
from datetime import datetime

SCANNER_V3 = Path.home() / ".openclaw" / "workspace" / "agent-security-skill-scanner-V3"

def scan_file_worker(args):
    """扫描文件工作进程"""
    file_path, dangerous_modules, dangerous_funcs = args
    
    try:
        import ast
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            source = f.read()
        tree = ast.parse(source)
        
        risk_score = 0
        findings = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in dangerous_modules:
                        risk_score += dangerous_modules[alias.name]
                        findings.append({'type': 'import', 'module': alias.name})
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in dangerous_funcs:
                        risk_score += dangerous_funcs[node.func.id]
                        findings.append({'type': 'call', 'func': node.func.id})
        
        return {
            'file': str(file_path),
            'risk_score': min(100, risk_score),
            'malicious': risk_score >= 55,
            'findings': findings
        }
    except Exception as e:
        return {'file': str(file_path), 'error': str(e), 'risk_score': 0}

class ParallelExecutor:
    """并行执行器"""
    
    def __init__(self, num_workers: int = None):
        self.num_workers = num_workers or cpu_count()
        self.dangerous_modules = {
            'subprocess': 30, 'socket': 25, 'requests': 20,
            'base64': 25, 'pickle': 30, 'ctypes': 35,
        }
        self.dangerous_funcs = {'eval': 40, 'exec': 40, 'compile': 35, '__import__': 25}
    
    def scan_directory(self, dir_path: Path) -> Dict:
        """并行扫描目录"""
        py_files = list(dir_path.rglob('*.py'))
        total = len(py_files)
        
        # 准备任务
        tasks = [
            (str(f), self.dangerous_modules, self.dangerous_funcs)
            for f in py_files
        ]
        
        start_time = time.time()
        
        # 并行执行
        with Pool(processes=self.num_workers) as pool:
            results = list(pool.imap(scan_file_worker, tasks, chunksize=10))
        
        end_time = time.time()
        
        # 统计
        malicious = sum(1 for r in results if r.get('malicious'))
        errors = sum(1 for r in results if r.get('error'))
        
        return {
            'executor': 'Round 18 Parallel Executor v1',
            'completed_at': datetime.now().isoformat(),
            'workers': self.num_workers,
            'total_files': total,
            'malicious_files': malicious,
            'safe_files': total - malicious - errors,
            'errors': errors,
            'detection_rate': f"{malicious/total*100:.1f}%" if total > 0 else "0%",
            'performance': {
                'total_time_seconds': round(end_time - start_time, 2),
                'files_per_second': round(total / (end_time - start_time), 1) if end_time > start_time else 0,
                'avg_time_per_file_ms': round((end_time - start_time) / total * 1000, 3) if total > 0 else 0
            },
            'results': results
        }

def main():
    print("=" * 60)
    print("Round 18: 并行执行器性能测试")
    print("=" * 60)
    
    samples_dir = SCANNER_V3 / 'samples' / 'high_fidelity'
    
    if not samples_dir.exists():
        print(f"❌ 样本目录不存在：{samples_dir}")
        return
    
    executor = ParallelExecutor()
    
    print(f"\n🚀 并行扫描 ({executor.num_workers} 进程)...")
    result = executor.scan_directory(samples_dir)
    
    print(f"\n📊 扫描完成:")
    print(f"  总文件：{result['total_files']}")
    print(f"  恶意：{result['malicious_files']}")
    print(f"  安全：{result['safe_files']}")
    print(f"  错误：{result['errors']}")
    print(f"  检出率：{result['detection_rate']}")
    print(f"\n⚡ 性能:")
    print(f"  总耗时：{result['performance']['total_time_seconds']}秒")
    print(f"  扫描速度：{result['performance']['files_per_second']} 文件/秒")
    print(f"  平均耗时：{result['performance']['avg_time_per_file_ms']}ms/文件")
    
    # 保存报告
    report_dir = SCANNER_V3 / 'round18'
    report_dir.mkdir(exist_ok=True)
    
    report_path = report_dir / 'ROUND18_PARALLEL_RESULT.json'
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 报告：{report_path}")
    
    return result

if __name__ == '__main__':
    main()
