#!/usr/bin/env python3
"""
Agent Security Multi-Agent System - 主程序入口
"""

import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from agents.orchestrator import OrchestratorAgent
from agents.detector_agent import DetectorAgent
from agents.base_agent import Task


async def main():
    """主函数"""
    print("="*60)
    print("🤖 Agent Security Multi-Agent System v2.0")
    print("="*60)
    
    # 创建协调器
    orchestrator = OrchestratorAgent()
    
    # 创建并注册 Agent
    detector = DetectorAgent()
    orchestrator.register_agent(detector, capabilities=["scan", "detect", "analyze"])
    
    print(f"\n✅ 已注册 Agent:")
    print(f"   - {detector.agent_id} (capabilities: scan, detect, analyze)")
    
    # 创建测试任务
    task = Task(
        type="scan",
        parameters={
            "target": str(Path.home() / ".openclaw/workspace"),
        }
    )
    
    print(f"\n📋 执行任务：{task.id}")
    print(f"   类型：{task.type}")
    print(f"   目标：{task.parameters['target']}")
    
    # 执行任务
    print(f"\n🚀 开始执行...")
    result = await orchestrator.execute(task)
    
    # 显示结果
    print(f"\n{'✅ 成功' if result.success else '❌ 失败'}")
    print(f"结果：{result.data}")
    
    # 显示状态
    print(f"\n📊 系统状态:")
    status = orchestrator.get_status()
    print(f"   注册 Agent: {status['registered_agents']}")
    print(f"   完成任务：{status['completed_tasks']}")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    asyncio.run(main())
