#!/usr/bin/env python3
"""
样本验证脚本 - 验证 752 个样本的检测率

测试:
1. 方案 B 样本 (497 个恶意)
2. 方案 C 样本 (255 个行业)
3. 总计 752 个样本
"""

import os
import json
from pathlib import Path
from datetime import datetime

class SampleValidator:
    """样本验证器"""
    
    def __init__(self, samples_dir: str, industry_dir: str):
        self.samples_dir = Path(samples_dir)
        self.industry_dir = Path(industry_dir)
        
        # 恶意样本目录
        self.malicious_dirs = [
            'tool_poisoning',
            'remote_load',
            'data_exfiltration',
            'prompt_injection',
            'resource_exhaustion',
            'memory_pollution',
            'supply_chain',
            'credential_theft',
            'persistence',
            'evasion',
        ]
    
    def count_samples(self, base_dir: Path, dirs: list = None):
        """统计样本数量"""
        if dirs is None:
            dirs = self.malicious_dirs
        
        total = 0
        by_type = {}
        
        for dir_name in dirs:
            dir_path = base_dir / dir_name
            if not dir_path.exists():
                continue
            
            # 统计所有代码文件
            count = 0
            for ext in ['*.txt', '*.py', '*.js', '*.go', '*.sh', '*.yaml']:
                count += len(list(dir_path.glob(ext)))
            
            if count > 0:
                by_type[dir_name] = count
                total += count
        
        return total, by_type
    
    def validate(self):
        """执行验证"""
        print("=" * 60)
        print("🔍 样本验证 - 检测率测试准备")
        print("=" * 60)
        print()
        
        # 1. 统计方案 B 样本
        print("📊 方案 B - 重新生成样本")
        total_b, by_type_b = self.count_samples(self.samples_dir)
        print(f"   总计：{total_b} 个样本")
        for at, count in sorted(by_type_b.items()):
            print(f"   - {at}: {count}")
        print()
        
        # 2. 统计方案 C 样本
        print("📊 方案 C - 行业数据集")
        industry_dirs = [
            'tool_poisoning', 'evasion', 'resource_exhaustion',
            'data_exfiltration', 'remote_load', 'prompt_injection',
            'credential_theft', 'persistence', 'supply_chain',
            'memory_pollution', 'data_exfil'
        ]
        total_c, by_type_c = self.count_samples(self.industry_dir, industry_dirs)
        print(f"   总计：{total_c} 个样本")
        for at, count in sorted(by_type_c.items()):
            print(f"   - {at}: {count}")
        print()
        
        # 3. 总计
        grand_total = total_b + total_c
        print("=" * 60)
        print(f"📈 总计：{grand_total} 个样本")
        print("=" * 60)
        print()
        
        # 4. 生成验证报告
        report = {
            "timestamp": datetime.now().isoformat(),
            "scheme_b": {
                "total": total_b,
                "by_type": by_type_b
            },
            "scheme_c": {
                "total": total_c,
                "by_type": by_type_c
            },
            "grand_total": grand_total
        }
        
        report_file = Path("/home/cdy/.openclaw/workspace/agent-security-skill-scanner-master/reports/SAMPLE_VALIDATION_REPORT.json")
        report_file.write_text(json.dumps(report, indent=2, ensure_ascii=False))
        print(f"📁 验证报告：{report_file}")
        
        # 5. 输出扫描命令
        print()
        print("=" * 60)
        print("🚀 下一步：执行扫描器验证")
        print("=" * 60)
        print()
        print("使用以下命令验证检测率:")
        print()
        print(f"cd /home/cdy/.openclaw/workspace/agent-security-skill-scanner-master")
        print(f"python3 scanner-master/ros-scanner-v2.py \\")
        print(f"  --samples {self.samples_dir} \\")
        print(f"  --industry {self.industry_dir} \\")
        print(f"  --output reports/final_detection_test.json")
        print()
        
        return report

if __name__ == "__main__":
    samples_dir = "/home/cdy/.openclaw/workspace/agent-security-skill-scanner-master/samples/malicious"
    industry_dir = "/home/cdy/.openclaw/workspace/agent-security-skill-scanner-master/samples/industry-datasets"
    
    validator = SampleValidator(samples_dir, industry_dir)
    validator.validate()
