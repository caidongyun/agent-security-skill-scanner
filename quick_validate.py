#!/usr/bin/env python3
"""
简单批量扫描器 - 验证检测率
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
import subprocess

def scan_samples():
    """扫描所有样本"""
    base_dir = Path("/home/cdy/.openclaw/workspace/agent-security-skill-scanner-master")
    samples_dir = base_dir / "samples"
    rules_file = base_dir / "scanner-master" / "output" / "rules" / "scanner_master_rules.yar"
    
    if not rules_file.exists():
        print(f"❌ 规则文件不存在：{rules_file}")
        return
    
    print("=" * 60)
    print("🔍 批量扫描验证")
    print("=" * 60)
    print()
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "total_scanned": 0,
        "total_detected": 0,
        "by_type": {}
    }
    
    # 扫描恶意样本目录
    malicious_dirs = [
        'tool_poisoning', 'remote_load', 'data_exfiltration',
        'prompt_injection', 'resource_exhaustion', 'memory_pollution',
        'supply_chain', 'credential_theft', 'persistence', 'evasion'
    ]
    
    for dir_name in malicious_dirs:
        dir_path = samples_dir / "malicious" / dir_name
        if not dir_path.exists():
            continue
        
        print(f"扫描 {dir_name}...")
        sample_files = list(dir_path.glob("*.txt"))
        detected = 0
        
        for sample_file in sample_files[:10]:  # 每类扫描前 10 个
            results["total_scanned"] += 1
            
            # 调用 yara 扫描
            try:
                cmd = ["yara", str(rules_file), str(sample_file)]
                output = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                
                if output.stdout.strip():
                    detected += 1
                    results["total_detected"] += 1
            except Exception as e:
                print(f"  ⚠️ 扫描失败 {sample_file.name}: {e}")
        
        dir_results = {
            "scanned": len(sample_files[:10]),
            "detected": detected,
            "rate": f"{detected/len(sample_files[:10])*100:.1f}%" if sample_files else "0%"
        }
        results["by_type"][dir_name] = dir_results
        print(f"  ✅ {detected}/{len(sample_files[:10])} ({dir_results['rate']})")
    
    # 计算总体检测率
    if results["total_scanned"] > 0:
        overall_rate = results["total_detected"] / results["total_scanned"] * 100
        results["overall_detection_rate"] = f"{overall_rate:.2f}%"
    
    # 保存结果
    report_file = base_dir / "reports" / "DETECTION_VALIDATION_REPORT.json"
    report_file.write_text(json.dumps(results, indent=2, ensure_ascii=False))
    
    print()
    print("=" * 60)
    print("📊 验证结果")
    print("=" * 60)
    print(f"总扫描：{results['total_scanned']} 个样本")
    print(f"总检出：{results['total_detected']} 个")
    print(f"检测率：{results.get('overall_detection_rate', 'N/A')}")
    print()
    print(f"📁 报告：{report_file}")

if __name__ == "__main__":
    scan_samples()
