#!/usr/bin/env python3
"""
自动化执行器 - 带异常超时管理
"""

import os
import sys
import json
import time
import signal
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Callable, Dict, Any

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/automation_runner.log')
    ]
)
logger = logging.getLogger('AutomationRunner')

# 超时配置
DEFAULT_TIMEOUT = 3600  # 1 小时
TASK_TIMEOUTS = {
    'T1.1': 7200,  # 2 小时
    'T1.2': 14400,  # 4 小时
    'T1.3': 7200,  # 2 小时
    'T2.1': 14400,  # 4 小时
    'T2.2': 28800,  # 8 小时
    'T2.3': 14400,  # 4 小时
    'T3.1': 10800,  # 3 小时
    'T4.1': 14400,  # 4 小时
    'T5.1': 10800,  # 3 小时
    'T5.2': 10800,  # 3 小时
    'T6.1': 10800,  # 3 小时
    'T6.2': 7200,  # 2 小时
    'T7.1': 10800,  # 3 小时
    'T7.2': 7200,  # 2 小时
}

# 重试配置
MAX_RETRIES = 3
RETRY_DELAY = 60  # 1 分钟


class TimeoutError(Exception):
    """任务超时异常"""
    pass


class TaskExecutionError(Exception):
    """任务执行异常"""
    pass


def timeout_handler(signum, frame):
    """超时信号处理"""
    raise TimeoutError("任务执行超时")


def with_timeout(timeout_seconds: int):
    """超时装饰器"""
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            # 设置超时信号
            old_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout_seconds)
            
            try:
                result = func(*args, **kwargs)
                signal.alarm(0)  # 取消超时
                return result
            except TimeoutError:
                logger.error(f"任务 {func.__name__} 执行超时 ({timeout_seconds}s)")
                raise
            finally:
                signal.signal(signal.SIGALRM, old_handler)
        
        return wrapper
    return decorator


def with_retry(max_retries: int = MAX_RETRIES, delay: int = RETRY_DELAY):
    """重试装饰器"""
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            last_error = None
            
            for attempt in range(1, max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    logger.warning(f"任务 {func.__name__} 执行失败 (尝试 {attempt}/{max_retries}): {str(e)}")
                    
                    if attempt < max_retries:
                        logger.info(f"等待 {delay} 秒后重试...")
                        time.sleep(delay)
            
            raise TaskExecutionError(f"任务 {func.__name__} 执行失败，已重试 {max_retries} 次：{str(last_error)}")
        
        return wrapper
    return decorator


class AutomationRunner:
    """自动化执行器"""
    
    def __init__(self, workspace_dir: str):
        self.workspace_dir = Path(workspace_dir)
        self.logs_dir = self.workspace_dir / 'logs'
        self.reports_dir = self.workspace_dir / 'reports'
        self.state_file = self.workspace_dir / 'automation_state.json'
        
        # 创建目录
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        # 加载状态
        self.state = self.load_state()
    
    def load_state(self) -> Dict:
        """加载执行状态"""
        if self.state_file.exists():
            with open(self.state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {
                'start_time': None,
                'current_task': None,
                'completed_tasks': [],
                'failed_tasks': [],
                'total_tasks': 14
            }
    
    def save_state(self):
        """保存执行状态"""
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)
    
    def log_task_start(self, task_id: str, task_name: str):
        """记录任务开始"""
        logger.info(f"🚀 开始任务 {task_id}: {task_name}")
        self.state['current_task'] = {
            'id': task_id,
            'name': task_name,
            'start_time': datetime.now().isoformat()
        }
        self.save_state()
    
    def log_task_complete(self, task_id: str, success: bool, output_file: str = None):
        """记录任务完成"""
        if success:
            logger.info(f"✅ 任务 {task_id} 完成")
            self.state['completed_tasks'].append({
                'id': task_id,
                'complete_time': datetime.now().isoformat(),
                'output': output_file
            })
        else:
            logger.error(f"❌ 任务 {task_id} 失败")
            self.state['failed_tasks'].append({
                'id': task_id,
                'fail_time': datetime.now().isoformat()
            })
        
        self.state['current_task'] = None
        self.save_state()
    
    @with_retry
    def execute_task(self, task_id: str, task_func: Callable, timeout: int = None) -> Any:
        """执行任务"""
        if timeout is None:
            timeout = TASK_TIMEOUTS.get(task_id, DEFAULT_TIMEOUT)
        
        # 设置超时
        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(timeout)
        
        try:
            result = task_func()
            signal.alarm(0)
            return result
        except TimeoutError as e:
            logger.error(f"任务 {task_id} 超时 ({timeout}s)")
            raise
        except Exception as e:
            logger.error(f"任务 {task_id} 执行失败：{str(e)}")
            raise
        finally:
            signal.signal(signal.SIGALRM, old_handler)
    
    def run_all(self):
        """执行所有任务"""
        logger.info("=" * 60)
        logger.info("🚀 开始自动化执行 v5.8.0 融合增强")
        logger.info("=" * 60)
        
        self.state['start_time'] = datetime.now().isoformat()
        self.save_state()
        
        # Phase 1: Pattern 增强
        logger.info("\n" + "=" * 60)
        logger.info("Phase 1: Pattern 增强 (Day 1-2)")
        logger.info("=" * 60)
        
        # Task 1.1: Semgrep 规则收集
        self.log_task_start('T1.1', 'Semgrep 规则收集')
        try:
            from tasks import task_1_1_collect_semgrep_rules
            result = self.execute_task('T1.1', task_1_1_collect_semgrep_rules.collect)
            self.log_task_complete('T1.1', True, result.get('output_file'))
        except Exception as e:
            self.log_task_complete('T1.1', False)
            logger.error(f"Task T1.1 失败：{str(e)}")
            # 继续执行下一个任务
        
        # Task 1.2: Pattern 转化
        self.log_task_start('T1.2', 'Pattern 转化')
        try:
            from tasks import task_1_2_transform_patterns
            result = self.execute_task('T1.2', task_1_2_transform_patterns.transform)
            self.log_task_complete('T1.2', True, result.get('output_file'))
        except Exception as e:
            self.log_task_complete('T1.2', False)
            logger.error(f"Task T1.2 失败：{str(e)}")
        
        # Task 1.3: Pattern 测试
        self.log_task_start('T1.3', 'Pattern 单元测试')
        try:
            from tasks import task_1_3_test_patterns
            result = self.execute_task('T1.3', task_1_3_test_patterns.test)
            self.log_task_complete('T1.3', True, result.get('output_file'))
        except Exception as e:
            self.log_task_complete('T1.3', False)
            logger.error(f"Task T1.3 失败：{str(e)}")
        
        # ... 继续执行其他任务
        
        logger.info("\n" + "=" * 60)
        logger.info("🎉 自动化执行完成")
        logger.info("=" * 60)
        
        # 生成最终报告
        self.generate_final_report()
    
    def generate_final_report(self):
        """生成最终报告"""
        report = {
            'start_time': self.state['start_time'],
            'end_time': datetime.now().isoformat(),
            'completed_tasks': len(self.state['completed_tasks']),
            'failed_tasks': len(self.state['failed_tasks']),
            'total_tasks': self.state['total_tasks'],
            'success_rate': len(self.state['completed_tasks']) / self.state['total_tasks'] * 100
        }
        
        report_file = self.reports_dir / 'automation_final_report.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📄 最终报告已保存：{report_file}")
        logger.info(f"成功率：{report['success_rate']:.1f}% ({len(self.state['completed_tasks'])}/{self.state['total_tasks']})")


def main():
    """主函数"""
    workspace_dir = '/home/cdy/.openclaw/workspace/agent-security-skill-scanner-master/release/v5.8.0'
    
    runner = AutomationRunner(workspace_dir)
    runner.run_all()


if __name__ == '__main__':
    main()
