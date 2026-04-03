#!/usr/bin/env python3
"""
超时监控和告警系统
监控长时间运行任务，超时自动告警/终止
"""

import os
import sys
import time
import signal
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict


class TimeoutMonitor:
    """超时监控器"""
    
    def __init__(self, config_file: str = "logs/timeout_config.json"):
        self.config_file = Path(config_file)
        self.config = self.load_config()
        
        # 默认超时配置 (秒)
        self.defaults = {
            'single_scan_timeout': 300,      # 单个样本扫描超时 (5 分钟)
            'batch_timeout': 3600,           # 批次测试超时 (1 小时)
            'full_test_timeout': 14400,      # 全量测试超时 (4 小时)
            'agent_timeout': 600,            # Agent 执行超时 (10 分钟)
            'no_progress_timeout': 300,      # 无进度超时 (5 分钟)
        }
    
    def load_config(self) -> Dict:
        """加载配置"""
        if self.config_file.exists():
            with open(self.config_file) as f:
                return json.load(f)
        return {}
    
    def save_config(self):
        """保存配置"""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def set_timeout(self, task_id: str, timeout_seconds: int):
        """设置任务超时"""
        self.config[task_id] = {
            'start_time': datetime.now().isoformat(),
            'timeout': timeout_seconds,
            'status': 'running',
        }
        self.save_config()
    
    def check_timeout(self, task_id: str) -> tuple[bool, float]:
        """检查是否超时"""
        if task_id not in self.config:
            return False, 0.0
        
        task = self.config[task_id]
        start_time = datetime.fromisoformat(task['start_time'])
        elapsed = (datetime.now() - start_time).total_seconds()
        timeout = task['timeout']
        
        progress = elapsed / timeout * 100
        
        if elapsed > timeout:
            task['status'] = 'timeout'
            self.save_config()
            return True, progress
        
        return False, progress
    
    def update_progress(self, task_id: str, current: int, total: int):
        """更新进度"""
        if task_id in self.config:
            self.config[task_id]['progress'] = {
                'current': current,
                'total': total,
                'percent': current / total * 100,
                'updated_at': datetime.now().isoformat(),
            }
            self.save_config()
    
    def check_no_progress(self, task_id: str) -> bool:
        """检查是否无进度 (卡死)"""
        if task_id not in self.config:
            return False
        
        task = self.config[task_id]
        if 'progress' not in task:
            return False
        
        last_update = datetime.fromisoformat(task['progress']['updated_at'])
        elapsed = (datetime.now() - last_update).total_seconds()
        
        if elapsed > self.defaults['no_progress_timeout']:
            return True
        
        return False
    
    def send_alert(self, task_id: str, alert_type: str, message: str):
        """发送告警"""
        alert = {
            'task_id': task_id,
            'alert_type': alert_type,
            'message': message,
            'timestamp': datetime.now().isoformat(),
        }
        
        # 写入告警日志
        alert_file = Path("logs/timeout_alerts.log")
        alert_file.parent.mkdir(parents=True, exist_ok=True)
        with open(alert_file, 'a') as f:
            f.write(json.dumps(alert) + '\n')
        
        # 打印告警
        print(f"\n🚨 超时告警 [{alert_type}]: {message}")
        
        # TODO: 可以集成邮件/短信/飞书告警
    
    def complete_task(self, task_id: str):
        """完成任务"""
        if task_id in self.config:
            self.config[task_id]['status'] = 'completed'
            self.config[task_id]['end_time'] = datetime.now().isoformat()
            self.save_config()


class TestProgressMonitor:
    """测试进度监控器"""
    
    def __init__(self, monitor: TimeoutMonitor):
        self.monitor = monitor
        self.task_id = "full_test"
        self.last_current = 0
        self.start_time = datetime.now()
    
    def update(self, current: int, total: int, tp: int, fn: int):
        """更新进度"""
        # 更新进度
        self.monitor.update_progress(self.task_id, current, total)
        
        # 检查超时
        is_timeout, progress = self.monitor.check_timeout(self.task_id)
        if is_timeout:
            self.monitor.send_alert(
                self.task_id,
                'TIMEOUT',
                f'全量测试超时 (进度 {progress:.1f}%)'
            )
        
        # 检查无进度
        if self.monitor.check_no_progress(self.task_id):
            self.monitor.send_alert(
                self.task_id,
                'NO_PROGRESS',
                f'测试卡死 (当前进度 {current}/{total})'
            )
        
        # 检查进度速度
        speed = 0.0
        eta_hours = 0.0
        if current > self.last_current and current > 100:
            elapsed = (datetime.now() - self.start_time).total_seconds()
            speed = current / elapsed  # 样本/秒
            eta_seconds = (total - current) / speed if speed > 0 else 0
            eta_hours = eta_seconds / 3600
            
            if eta_hours > 4:
                self.monitor.send_alert(
                    self.task_id,
                    'SLOW_PROGRESS',
                    f'进度过慢 (速度 {speed:.2f} 样本/秒，预计还需 {eta_hours:.1f} 小时)'
                )
        
        self.last_current = current
        
        # 打印进度
        percent = current / total * 100
        dr = tp / (tp + fn) * 100 if (tp + fn) > 0 else 0
        print(f"\r[{datetime.now().strftime('%H:%M:%S')}] "
              f"进度：{percent:.1f}% ({current}/{total}) "
              f"检测率：{dr:.1f}% (TP={tp}, FN={fn}) "
              f"速度：{speed:.2f} 样本/秒 "
              f"预计：{eta_hours:.1f} 小时", 
              end='', flush=True)
    
    def complete(self, tp: int, fn: int, tn: int, fp: int):
        """完成测试"""
        self.monitor.complete_task(self.task_id)
        
        # 计算最终结果
        total = tp + fn + tn + fp
        dr = tp / (tp + fn) * 100 if (tp + fn) > 0 else 0
        fpr = fp / (fp + tn) * 100 if (fp + tn) > 0 else 0
        
        elapsed = (datetime.now() - self.start_time).total_seconds()
        hours = elapsed / 3600
        
        print(f"\n\n{'='*60}")
        print(f"✅ 全量测试完成")
        print(f"{'='*60}")
        print(f"总样本：{total:,}")
        print(f"检测率：{dr:.1f}% (TP={tp:,}, FN={fn:,})")
        print(f"误报率：{fpr:.1f}% (FP={fp:,}, TN={tn:,})")
        print(f"耗时：{hours:.2f} 小时")
        print(f"{'='*60}")
        
        # 保存结果
        result = {
            'timestamp': datetime.now().isoformat(),
            'total_samples': total,
            'detection_rate': dr,
            'false_positive_rate': fpr,
            'tp': tp, 'fn': fn, 'tn': tn, 'fp': fp,
            'elapsed_hours': hours,
        }
        
        result_file = Path("logs/full_test_result.json")
        result_file.parent.mkdir(parents=True, exist_ok=True)
        with open(result_file, 'w') as f:
            json.dump(result, f, indent=2)


def main():
    """主函数 - 演示"""
    
    print("="*60)
    print("🔍 超时监控和告警系统演示")
    print("="*60)
    
    # 创建监控器
    monitor = TimeoutMonitor()
    test_monitor = TestProgressMonitor(monitor)
    
    # 设置超时 (4 小时)
    monitor.set_timeout("full_test", 4 * 3600)
    
    # 模拟进度更新
    total = 65533
    for i in range(0, total + 1, 1000):
        tp = int(i * 0.9)
        fn = i - tp
        
        test_monitor.update(i, total, tp, fn)
        time.sleep(0.1)
    
    # 完成
    test_monitor.complete(tp=int(total*0.9), fn=int(total*0.1), tn=0, fp=0)


if __name__ == '__main__':
    main()
