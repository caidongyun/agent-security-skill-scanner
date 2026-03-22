#!/usr/bin/env python3
"""
🚀 灵顺 V5 + agent-defender 联合持续研发系统
==============================================
功能:
- 同时运行灵顺 V5 和 agent-defender 研发循环
- 自动同步研究成果
- 联合质量评估
- 性能监控
- 加速模式 (可配置间隔)
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import threading


class JointResearch:
    """联合研发系统"""
    
    def __init__(self, round_interval: int = 300):
        self.round_interval = round_interval  # 轮次间隔 (秒)
        self.expert_mode = Path(__file__).parent
        self.agent_defender = self.expert_mode.parent / "agent-defender"
        
        self.state_file = self.expert_mode / ".joint_research_state.json"
        self.log_file = self.expert_mode / "logs" / "joint_research.log"
        
        self.state = self.load_state()
        self.round = self.state.get('round', 0)
        self.setup_logging()
    
    def setup_logging(self):
        """设置日志"""
        self.log_file.parent.mkdir(exist_ok=True)
        
        import logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("JointResearch")
    
    def load_state(self) -> Dict:
        """加载状态"""
        if self.state_file.exists():
            with open(self.state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            'round': 0,
            'started_at': None,
            'last_round': None,
            'lingshun_metrics': {},
            'defender_metrics': {},
            'sync_status': {}
        }
    
    def save_state(self):
        """保存状态"""
        self.state['round'] = self.round
        self.state['last_round'] = datetime.now().isoformat()
        
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)
    
    def run_lingshun_round(self) -> Dict:
        """运行灵顺 V5 一轮"""
        self.logger.info("\n" + "="*60)
        self.logger.info("🛡️ 灵顺 V5 第 {} 轮研发".format(self.round + 1))
        self.logger.info("="*60)
        
        start_time = time.time()
        metrics = {}
        
        # 运行灵顺 V5 守护进程一轮
        daemon_script = self.expert_mode / "lingshun_daemon.py"
        
        if daemon_script.exists():
            try:
                result = subprocess.run(
                    ['python3', str(daemon_script), '--run-once'],
                    cwd=str(self.expert_mode),
                    capture_output=True,
                    text=True,
                    timeout=self.round_interval
                )
                
                metrics['success'] = (result.returncode == 0)
                metrics['output'] = result.stdout
                metrics['error'] = result.stderr
                
                if result.returncode == 0:
                    self.logger.info("✅ 灵顺 V5 轮次完成")
                else:
                    self.logger.warning(f"⚠️ 灵顺 V5 轮次失败：{result.stderr}")
                    
            except subprocess.TimeoutExpired:
                metrics['success'] = False
                metrics['error'] = "超时"
                self.logger.warning("⚠️ 灵顺 V5 轮次超时")
        else:
            metrics['success'] = False
            metrics['error'] = "未找到守护进程脚本"
            self.logger.warning("⚠️ 未找到灵顺 V5 守护进程")
        
        elapsed = time.time() - start_time
        metrics['elapsed'] = elapsed
        
        self.state['lingshun_metrics'] = metrics
        return metrics
    
    def run_defender_round(self) -> Dict:
        """运行 agent-defender 一轮"""
        self.logger.info("\n" + "="*60)
        self.logger.info("🛡️ agent-defender 第 {} 轮研发".format(self.round + 1))
        self.logger.info("="*60)
        
        start_time = time.time()
        metrics = {}
        
        # 运行 defender 研发脚本
        research_script = self.agent_defender / "research_daemon.py"
        
        if research_script.exists():
            try:
                result = subprocess.run(
                    ['python3', str(research_script), '--run-once'],
                    cwd=str(self.agent_defender),
                    capture_output=True,
                    text=True,
                    timeout=self.round_interval
                )
                
                metrics['success'] = (result.returncode == 0)
                metrics['output'] = result.stdout
                metrics['error'] = result.stderr
                
                if result.returncode == 0:
                    self.logger.info("✅ agent-defender 轮次完成")
                else:
                    self.logger.warning(f"⚠️ agent-defender 轮次失败：{result.stderr}")
                    
            except subprocess.TimeoutExpired:
                metrics['success'] = False
                metrics['error'] = "超时"
                self.logger.warning("⚠️ agent-defender 轮次超时")
        else:
            metrics['success'] = False
            metrics['error'] = "未找到研发脚本"
            self.logger.warning("⚠️ 未找到 agent-defender 研发脚本")
        
        elapsed = time.time() - start_time
        metrics['elapsed'] = elapsed
        
        self.state['defender_metrics'] = metrics
        return metrics
    
    def sync_results(self) -> Dict:
        """同步研究成果"""
        self.logger.info("\n" + "="*60)
        self.logger.info("🔄 同步研究成果")
        self.logger.info("="*60)
        
        sync_script = self.agent_defender / "sync_from_lingshun.py"
        metrics = {}
        
        if sync_script.exists():
            try:
                result = subprocess.run(
                    ['python3', str(sync_script)],
                    cwd=str(self.agent_defender),
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                
                metrics['success'] = (result.returncode == 0)
                metrics['output'] = result.stdout
                
                if result.returncode == 0:
                    self.logger.info("✅ 研究成果已同步到 agent-defender")
                else:
                    self.logger.warning(f"⚠️ 同步失败：{result.stderr}")
                    
            except subprocess.TimeoutExpired:
                metrics['success'] = False
                metrics['error'] = "超时"
                self.logger.warning("⚠️ 同步超时")
        else:
            metrics['success'] = False
            metrics['error'] = "未找到同步脚本"
            self.logger.warning("⚠️ 未找到同步脚本")
        
        self.state['sync_status'] = metrics
        return metrics
    
    def assess_quality(self) -> Dict:
        """联合质量评估"""
        self.logger.info("\n" + "="*60)
        self.logger.info("📊 联合质量评估")
        self.logger.info("="*60)
        
        assessment = {
            'lingshun_score': 0,
            'defender_score': 0,
            'sync_score': 0,
            'total_score': 0
        }
        
        # 灵顺 V5 评分
        lingshun = self.state.get('lingshun_metrics', {})
        if lingshun.get('success'):
            assessment['lingshun_score'] += 50
        
        # agent-defender 评分
        defender = self.state.get('defender_metrics', {})
        if defender.get('success'):
            assessment['defender_score'] += 50
        
        # 同步评分
        sync = self.state.get('sync_status', {})
        if sync.get('success'):
            assessment['sync_score'] += 50
        
        # 总分
        assessment['total_score'] = (
            assessment['lingshun_score'] +
            assessment['defender_score'] +
            assessment['sync_score']
        ) / 3
        
        self.logger.info(f"  灵顺 V5 评分：{assessment['lingshun_score']}/50")
        self.logger.info(f"  agent-defender 评分：{assessment['defender_score']}/50")
        self.logger.info(f"  同步评分：{assessment['sync_score']}/50")
        self.logger.info(f"  综合评分：{assessment['total_score']:.1f}/50")
        
        self.state['quality_assessment'] = assessment
        return assessment
    
    def run_round(self):
        """运行完整一轮"""
        self.round += 1
        
        self.logger.info("\n" + "="*80)
        self.logger.info("🚀 联合研发第 {} 轮开始".format(self.round))
        self.logger.info("="*80)
        
        start_time = time.time()
        
        # 步骤 1: 灵顺 V5 研发
        self.run_lingshun_round()
        
        # 步骤 2: agent-defender 研发
        self.run_defender_round()
        
        # 步骤 3: 同步研究成果
        self.sync_results()
        
        # 步骤 4: 质量评估
        self.assess_quality()
        
        elapsed = time.time() - start_time
        
        self.logger.info("\n" + "="*80)
        self.logger.info("✅ 第 {} 轮完成，总耗时 {:.1f} 秒".format(self.round, elapsed))
        self.logger.info("="*80 + "\n")
        
        self.save_state()
    
    def run_continuous(self):
        """持续运行"""
        self.logger.info("\n" + "="*80)
        self.logger.info("🚀 启动联合持续研发系统")
        self.logger.info("="*80)
        self.logger.info(f"轮次间隔：{self.round_interval} 秒")
        self.logger.info(f"开始时间：{datetime.now().isoformat()}")
        self.logger.info("="*80 + "\n")
        
        self.state['started_at'] = datetime.now().isoformat()
        self.save_state()
        
        try:
            while True:
                self.run_round()
                
                # 等待下一轮
                if self.round_interval > 0:
                    self.logger.info(f"⏳ 等待 {self.round_interval} 秒后开始下一轮...")
                    time.sleep(self.round_interval)
                    
        except KeyboardInterrupt:
            self.logger.info("\n\n👋 收到停止信号，优雅退出...")
            self.save_state()
            self.logger.info("✅ 状态已保存")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='灵顺 V5 + agent-defender 联合持续研发系统')
    parser.add_argument('--interval', '-i', type=int, default=300,
                       help='轮次间隔 (秒)，默认 300 秒')
    parser.add_argument('--run-once', action='store_true',
                       help='只运行一轮')
    
    args = parser.parse_args()
    
    research = JointResearch(round_interval=args.interval)
    
    if args.run_once:
        research.run_round()
    else:
        research.run_continuous()


if __name__ == "__main__":
    main()
