#!/usr/bin/env python3
"""
全量测试监控脚本
实时查看测试进度
"""

import time
import glob
import json
from pathlib import Path
from datetime import datetime

def monitor():
    scanner_dir = Path.home() / ".openclaw/workspace/agent-security-skill-scanner-master"
    reports_dir = scanner_dir / "reports" / "enhanced"
    
    print("=" * 60)
    print("📊 全量测试监控")
    print("=" * 60)
    print(f"总样本库：65,533 个 (49,636 恶意 + 15,897 良性)")
    print(f"预计耗时：3-4 小时")
    print("=" * 60)
    
    last_progress = None
    
    while True:
        # 查找最新进度报告
        progress_files = list(reports_dir.glob("progress_*.json"))
        if progress_files:
            latest = max(progress_files, key=lambda x: x.stat().st_mtime)
            try:
                with open(latest) as f:
                    progress = json.load(f)
                
                # 只在进度变化时输出
                current_tested = progress.get('total_tested', 0)
                if current_tested != last_progress:
                    last_progress = current_tested
                    
                    total = 65533
                    percent = (current_tested / total * 100) if total > 0 else 0
                    elapsed = progress.get('elapsed_seconds', 0)
                    speed = current_tested / elapsed if elapsed > 0 else 0
                    
                    eta_seconds = (total - current_tested) / speed if speed > 0 else 0
                    eta_hours = eta_seconds / 3600
                    
                    tp = progress.get('tp', 0)
                    fn = progress.get('fn', 0)
                    tn = progress.get('tn', 0)
                    fp = progress.get('fp', 0)
                    
                    dr = tp / (tp + fn) * 100 if (tp + fn) > 0 else 0
                    fpr = fp / (fp + tn) * 100 if (fp + tn) > 0 else 0
                    
                    print(f"\n[{datetime.now().strftime('%H:%M:%S')}]")
                    print(f"进度：{current_tested:,}/{total:,} ({percent:.1f}%)")
                    print(f"速度：{speed:.1f} 样本/秒")
                    print(f"预计剩余：{eta_hours:.1f} 小时")
                    print(f"\n当前结果:")
                    print(f"  恶意样本：{tp:,}/{tp+fn:,} (DR: {dr:.1f}%)")
                    print(f"  良性样本：{tn:,}/{tn+fp:,} (FP: {fpr:.1f}%)")
                    print(f"  总检测率：{dr:.1f}%")
                    print(f"  总误报率：{fpr:.1f}%")
            except Exception as e:
                pass
        
        time.sleep(30)  # 每 30 秒检查一次

if __name__ == '__main__':
    try:
        monitor()
    except KeyboardInterrupt:
        print("\n\n监控已停止")
