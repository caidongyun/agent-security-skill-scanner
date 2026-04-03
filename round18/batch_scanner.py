#!/usr/bin/env python3
"""
Round 18: 批量扫描器

优化:
1. 批量读取文件
2. 流式处理
3. 结果聚合
"""

import ast
import json
import time
from pathlib import Path
from typing import Dict, List, Generator
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

SCANNER_V3 = Path.home() / ".openclaw" / "workspace" / "agent-security-skill-scanner-V3"

# 危险模块和函数
DANGEROUS_MODULES = {
    'subprocess': 30, 'socket': 25, 'requests': 20,
    'base64': 25, 'pickle': 30, 'ctypes': 35,
}
DANGEROUS_FUNCS = {'eval': 40, 'exec': 40, 'compile': 35, '__import__': 25}

class BatchScanner:
    """批量扫描器"""
    
    def __init__(self, batch_size: int = 100):
        self.batch_size = batch_size
        self.cache = {}
    
    def scan_file(self, file_path: Path) -> Dict:
        """扫描单个文件"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                source = f.read()
            tree = ast.parse(source)
        except SyntaxError:
            return {'file': str(file_path), 'error': 'SyntaxError', 'risk_score': 0}
        
        risk_score = 0
        findings = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in DANGEROUS_MODULES:
                        risk_score += DANGEROUS_MODULES[alias.name]
                        findings.append({'type': 'import', 'module': alias.name})
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in DANGEROUS_FUNCS:
                        risk_score += DANGEROUS_FUNCS[node.func.id]
                        findings.append({'type': 'call', 'func': node.func.id})
        
        return {
            'file': str(file_path),
            'risk_score': min(100, risk_score),
            'malicious': risk_score >= 55,
            'findings': findings
        }
    
    def scan_batch(self, files: List[Path]) -> List[Dict]:
        """批量扫描"""
        results = []
        for file_path in files:
            result = self.scan_file(file_path)
            results.append(result)
        return results
    
    def scan_directory(self, dir_path: Path, use_parallel: bool = True, 
                       max_workers: int = 4) -> Dict:
        """扫描目录 (支持并行)"""
        py_files = list(dir_path.rglob('*.py'))
        total = len(py_files)
        
        start_time = time.time()
        results = []
        
        if use_parallel:
            # 并行扫描
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_file = {executor.submit(self.scan_file, f): f for f in py_files}
                
                for i, future in enumerate(as_completed(future_to_file), 1):
                    result = future.result()
                    results.append(result)
                    
                    if i % 100 == 0:
                        elapsed = time.time() - start_time
                        rate = i / elapsed
                        print(f"  进度：{i}/{total} ({rate:.0f} 文件/秒)")
        else:
            # 串行扫描
            for i, py_file in enumerate(py_files, 1):
                result = self.scan_file(py_file)
                results.append(result)
                
                if i % 100 == 0:
                    elapsed = time.time() - start_time
                    rate = i / elapsed
                    print(f"  进度：{i}/{total} ({rate:.0f} 文件/秒)")
        
        end_time = time.time()
        
        # 统计
        malicious = sum(1 for r in results if r.get('malicious'))
        errors = sum(1 for r in results if r.get('error'))
        
        return {
            'scanner': 'Round 18 Batch Scanner v1',
            'completed_at': datetime.now().isoformat(),
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
    print("Round 18: 批量扫描器性能测试")
    print("=" * 60)
    
    samples_dir = SCANNER_V3 / 'samples' / 'high_fidelity'
    
    if not samples_dir.exists():
        print(f"❌ 样本目录不存在：{samples_dir}")
        return
    
    scanner = BatchScanner()
    
    # 测试并行扫描
    print("\n🚀 并行扫描 (4 工作线程)...")
    result_parallel = scanner.scan_directory(samples_dir, use_parallel=True, max_workers=4)
    
    print(f"\n📊 扫描完成:")
    print(f"  总文件：{result_parallel['total_files']}")
    print(f"  恶意：{result_parallel['malicious_files']}")
    print(f"  安全：{result_parallel['safe_files']}")
    print(f"  错误：{result_parallel['errors']}")
    print(f"  检出率：{result_parallel['detection_rate']}")
    print(f"\n⚡ 性能:")
    print(f"  总耗时：{result_parallel['performance']['total_time_seconds']}秒")
    print(f"  扫描速度：{result_parallel['performance']['files_per_second']} 文件/秒")
    print(f"  平均耗时：{result_parallel['performance']['avg_time_per_file_ms']}ms/文件")
    
    # 保存报告
    report_dir = SCANNER_V3 / 'round18'
    report_dir.mkdir(exist_ok=True)
    
    report_path = report_dir / 'ROUND18_SCAN_RESULT.json'
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(result_parallel, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 报告：{report_path}")
    
    return result_parallel

if __name__ == '__main__':
    main()
