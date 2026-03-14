#!/usr/bin/env python3
"""
并行扫描加速器 - 多线程并发扫描
功能:
1. 多文件并行扫描
2. 增量扫描支持
3. 进度实时显示
4. 结果实时输出

用法:
    python3 parallel_scanner.py --dir ../samples/real_skills --threads 8
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from threading import Lock

# 导入检测器
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print_lock = Lock()

def log(msg):
    with print_lock:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

class ParallelScanner:
    """并行扫描器"""
    
    def __init__(self, threads=8):
        self.threads = threads
        self.results = []
        self.progress = 0
        self.total = 0
        self.lock = Lock()
        
    def scan_file(self, file_path):
        """扫描单个文件"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            risk_score = 0
            issues = []
            
            # 风险模式检测
            import re
            patterns = [
                (r'eval\s*\(', 20, '代码执行'),
                (r'exec\s*\(', 20, '代码执行'),
                (r'os\.system\s*\(', 15, '命令执行'),
                (r'subprocess\.', 10, '子进程'),
                (r'__import__\s*\(', 15, '动态导入'),
                (r'base64\.b64decode', 12, '编码混淆'),
                (r'password\s*=', 10, '密码硬编码'),
                (r'token\s*=', 10, 'Token 硬编码'),
                (r'api[_-]?key\s*=', 15, 'API Key 硬编码'),
                (r'secret\s*=', 10, '密钥硬编码'),
                (r'socket\.', 10, '网络套接字'),
                (r'popen\s*\(', 12, 'Shell 执行'),
                (r'requests\.post.*password', 15, '凭据发送'),
                (r'chmod\s+777', 20, '权限过宽'),
                (r'sudo\s+.*-S', 10, 'sudo 提权'),
            ]
            
            for pattern, score, desc in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    risk_score += score * len(matches)
                    issues.append({'type': desc, 'count': len(matches)})
            
            # 严重级别
            if risk_score >= 50:
                severity = 'CRITICAL'
            elif risk_score >= 30:
                severity = 'HIGH'
            elif risk_score >= 15:
                severity = 'MEDIUM'
            else:
                severity = 'LOW'
            
            return {
                'file': file_path,
                'risk_score': risk_score,
                'severity': severity,
                'issues': issues,
                'lines': len(content.split('\n'))
            }
            
        except Exception as e:
            return {
                'file': file_path,
                'error': str(e),
                'risk_score': 0,
                'severity': 'LOW',
                'issues': []
            }
    
    def scan_directory(self, directory, progress_interval=10):
        """并行扫描目录"""
        
        # 收集文件
        files = []
        for root, dirs, filenames in os.walk(directory):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules', 'venv']]
            for f in filenames:
                if not f.startswith(".") and f.endswith(('.py', '.sh', '.js', '.ts')):
                    files.append(os.path.join(root, f))
        
        self.total = len(files)
        log(f"📂 待扫描: {self.total} 个文件, {self.threads} 线程")
        
        start_time = time.time()
        
        # 并行扫描
        results = []
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = {executor.submit(self.scan_file, f): f for f in files}
            
            for i, future in enumerate(as_completed(futures)):
                result = future.result()
                results.append(result)
                
                # 进度显示
                self.progress = i + 1
                if self.progress % progress_interval == 0 or self.progress == self.total:
                    elapsed = time.time() - start_time
                    speed = self.progress / elapsed if elapsed > 0 else 0
                    log(f"   进度: {self.progress}/{self.total} ({self.progress*100//self.total}%) - {speed:.1f} 文件/秒")
        
        elapsed = time.time() - start_time
        log(f"✅ 扫描完成: {self.total} 文件, 耗时 {elapsed:.1f}秒, 速度 {self.total/elapsed:.1f} 文件/秒")
        
        return results
    
    def generate_report(self, results, output_path="scan_result.json"):
        """生成扫描报告"""
        
        # 统计
        critical = sum(1 for r in results if r['severity'] == 'CRITICAL')
        high = sum(1 for r in results if r['severity'] == 'HIGH')
        medium = sum(1 for r in results if r['severity'] == 'MEDIUM')
        low = sum(1 for r in results if r['severity'] == 'LOW')
        
        # 过滤有问题的
        issues = [r for r in results if r['risk_score'] > 0]
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_files': len(results),
            'total_issues': len(issues),
            'critical': critical,
            'high': high,
            'medium': medium,
            'low': low,
            'issues': sorted(issues, key=lambda x: x['risk_score'], reverse=True)
        }
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        log(f"📊 报告已保存: {output_path}")
        return report

def main():
    parser = argparse.ArgumentParser(description="并行扫描器")
    parser.add_argument("--dir", default="../samples/real_skills", help="扫描目录")
    parser.add_argument("--threads", type=int, default=8, help="线程数")
    parser.add_argument("--output", default="scan_result.json", help="输出文件")
    
    args = parser.parse_args()
    
    # 解析相对路径
    base_dir = os.path.dirname(os.path.abspath(__file__))
    scan_dir = args.dir if os.path.isabs(args.dir) else os.path.join(base_dir, args.dir)
    
    log("🚀 并行扫描器启动")
    
    scanner = ParallelScanner(threads=args.threads)
    results = scanner.scan_directory(scan_dir)
    report = scanner.generate_report(results, args.output)
    
    print(f"\n{'='*50}")
    print(f"📊 扫描结果:")
    print(f"   总文件: {report['total_files']}")
    print(f"   总问题: {report['total_issues']}")
    print(f"   🔴 严重: {report['critical']}")
    print(f"   🟠 高危: {report['high']}")
    print(f"   🟡 中危: {report['medium']}")
    print(f"   🟢 低危: {report['low']}")
    print(f"{'='*50}")

if __name__ == "__main__":
    main()
