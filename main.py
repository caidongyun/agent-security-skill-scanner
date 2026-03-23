#!/usr/bin/env python3
"""
V3 Multi-Agent Security Scanner - 统一入口

整合 7 个 Agent 的安全检测系统
"""

import asyncio
import argparse
import sys
from pathlib import Path
from datetime import datetime

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from agents.orchestrator import OrchestratorAgent
from agents.detector_agent import DetectorAgent
from agents.analyzer_agent import AnalyzerAgent
from agents.rule_agent import RuleAgent
from agents.intel_agent import IntelAgent
from agents.reporter_agent import ReporterAgent
from agents.sample_generator_agent import SampleGeneratorAgent
from agents.base_agent import Task, Result


class V3Scanner:
    """V3 多 Agent 安全扫描器"""
    
    def __init__(self):
        self.orchestrator = OrchestratorAgent()
        self.agents = {}
        self.results = {}
    
    async def initialize(self):
        """初始化所有 Agent"""
        print("\n🚀 初始化 V3 Multi-Agent System...")
        print("=" * 50)
        
        # 注册所有 Agent
        await self._register_agent("detector", DetectorAgent())
        await self._register_agent("analyzer", AnalyzerAgent())
        await self._register_agent("rule", RuleAgent())
        await self._register_agent("intel", IntelAgent())
        await self._register_agent("reporter", ReporterAgent())
        await self._register_agent("sample_generator", SampleGeneratorAgent())
        
        print(f"\n✅ 已注册 {len(self.agents)} 个 Agent")
        return self
    
    async def _register_agent(self, name: str, agent):
        """注册 Agent"""
        capabilities = getattr(agent, 'capabilities', [])
        self.orchestrator.register_agent(agent, capabilities)
        self.agents[name] = agent
        agent_name = getattr(agent, 'name', agent.agent_id)
        print(f"  ✅ {name}: {agent_name}")
    
    async def scan(self, target: str, options: dict = None) -> dict:
        """执行扫描"""
        options = options or {}
        
        print(f"\n🔍 开始扫描: {target}")
        print("=" * 50)
        
        results = {
            'target': target,
            'timestamp': datetime.now().isoformat(),
            'detections': [],
            'analysis': {},
            'intel': {},
            'report': None
        }
        
        # 1. 检测阶段
        print("\n📡 阶段 1: 安全检测...")
        detector_result = await self.agents["detector"].execute(Task(
            type="scan",
            parameters={"target": target}
        ))
        
        if detector_result.success:
            results['detections'] = detector_result.data.get('results', [])
            print(f"  ✅ 检测完成: {len(results.get('detections', []))} 个结果")
        
        # 2. 分析阶段
        if options.get('deep_analysis', True):
            print("\n🔬 阶段 2: 深度分析...")
            analyzer_result = await self.agents["analyzer"].execute(Task(
                type="analyze",
                parameters={"target": target}
            ))
            
            if analyzer_result.success:
                results['analysis'] = analyzer_result.data
                print(f"  ✅ 分析完成: 风险评分 {analyzer_result.data.get('risk_score', 0):.2f}")
        
        # 3. 规则匹配
        print("\n📋 阶段 3: 规则匹配...")
        rule_result = await self.agents["rule"].execute(Task(
            type="match",
            parameters={"target": target}
        ))
        
        if rule_result.success:
            matched = rule_result.data.get('matched_rules', 0)
            results['rule_matches'] = matched if isinstance(matched, list) else matched
            matched = rule_result.data.get('matched_rules', 0)
        print(f"  ✅ 匹配完成: {matched} 条规则")
        
        # 4. 威胁情报
        if options.get('intel_check', True):
            print("\n🎯 阶段 4: 威胁情报检查...")
            intel_result = await self.agents["intel"].execute(Task(
                type="analyze",
                parameters={"target": target}
            ))
            
            if intel_result.success:
                results['intel'] = intel_result.data
                print(f"  ✅ 情报完成: 威胁评分 {intel_result.data.get('threat_score', 0):.2f}")
        
        # 5. 生成报告
        if options.get('generate_report', True):
            print("\n📊 阶段 5: 生成报告...")
            report_result = await self.agents["reporter"].execute(Task(
                type="generate",
                parameters={
                    "scan_results": results['detections'],
                    "format": "markdown"
                }
            ))
            
            if report_result.success:
                results['report'] = report_result.data
                print(f"  ✅ 报告生成: {report_result.data.get('report_file')}")
        
        self.results = results
        return results
    
    async def generate_samples(self, count: int = 10, mode: str = "batch") -> dict:
        """生成测试样本"""
        print(f"\n🎲 生成样本 (模式: {mode})...")
        
        if mode == "intel":
            result = await self.agents["sample_generator"].execute(Task(
                type="generate_from_intel",
                parameters={"count": count}
            ))
        elif mode == "apt":
            result = await self.agents["sample_generator"].execute(Task(
                type="generate_apt",
                parameters={"count": count, "apt_group": "generic"}
            ))
        elif mode == "cve":
            result = await self.agents["sample_generator"].execute(Task(
                type="generate_cve",
                parameters={"count": count}
            ))
        else:
            result = await self.agents["sample_generator"].execute(Task(
                type="generate_batch",
                parameters={
                    "languages": ["python"],
                    "attack_types": ["tool_poisoning", "remote_load", "data_exfil"],
                    "count": count // 3
                }
            ))
        
        if result.success:
            print(f"  ✅ 生成完成: {result.data.get('generated_count', 0)} 个样本")
        
        return result.data if result.success else {}
    
    async def collect_intel(self, sources: list = None) -> dict:
        """采集威胁情报"""
        sources = sources or ["github", "mitre", "cve"]
        
        print(f"\n🎯 采集威胁情报: {sources}")
        
        result = await self.agents["intel"].execute(Task(
            type="collect",
            parameters={"sources": sources}
        ))
        
        if result.success:
            print(f"  ✅ 采集完成")
            total = sum(len(v) for v in result.data.values() if isinstance(v, list))
            print(f"     总计: {total} 条情报")
        
        return result.data if result.success else {}
    
    def get_status(self) -> dict:
        """获取系统状态"""
        status = {
            'orchestrator': self.orchestrator.get_stats(),
            'agents': {}
        }
        
        for name, agent in self.agents.items():
            if hasattr(agent, 'get_status'):
                status['agents'][name] = agent.get_status()
            elif hasattr(agent, 'get_stats'):
                status['agents'][name] = agent.get_stats()
            else:
                status['agents'][name] = {'name': getattr(agent, 'name', name)}
        
        return status


async def main():
    parser = argparse.ArgumentParser(description='V3 Multi-Agent Security Scanner')
    parser.add_argument('command', choices=['scan', 'generate', 'intel', 'status'],
                      help='命令: scan=扫描, generate=生成样本, intel=采集情报, status=状态')
    parser.add_argument('--target', '-t', type=str, help='扫描目标')
    parser.add_argument('--count', '-c', type=int, default=10, help='生成数量')
    parser.add_argument('--mode', '-m', type=str, default='batch',
                       choices=['batch', 'intel', 'apt', 'cve'],
                       help='生成模式')
    parser.add_argument('--no-analysis', action='store_true', help='跳过深度分析')
    parser.add_argument('--no-intel', action='store_true', help='跳过情报检查')
    parser.add_argument('--no-report', action='store_true', help='跳过报告生成')
    
    args = parser.parse_args()
    
    # 创建扫描器
    scanner = V3Scanner()
    await scanner.initialize()
    
    if args.command == 'scan':
        if not args.target:
            print("❌ 错误: 扫描需要 --target 参数")
            return
        
        options = {
            'deep_analysis': not args.no_analysis,
            'intel_check': not args.no_intel,
            'generate_report': not args.no_report
        }
        
        results = await scanner.scan(args.target, options)
        
        print("\n" + "=" * 50)
        print("📊 扫描结果摘要")
        print("=" * 50)
        print(f"目标: {results['target']}")
        print(f"检测数: {len(results.get('detections', []))}")
        if results.get('analysis'):
            print(f"风险评分: {results['analysis'].get('risk_score', 0):.2f}")
        if results.get('rule_matches'):
            print(f"规则匹配: {results.get('rule_matches', 0)} 条")
        if results.get('intel'):
            print(f"威胁评分: {results['intel'].get('threat_score', 0):.2f}")
        print("=" * 50)
    
    elif args.command == 'generate':
        result = await scanner.generate_samples(args.count, args.mode)
        print(f"\n✅ 样本生成完成: {result.get('generated_count', 0)} 个")
    
    elif args.command == 'intel':
        sources = ['github', 'mitre', 'cve']
        result = await scanner.collect_intel(sources)
        print(f"\n✅ 情报采集完成")
    
    elif args.command == 'status':
        status = scanner.get_status()
        print("\n📊 V3 系统状态")
        print("=" * 50)
        orch = status['orchestrator']
        print(f"Orchestrator: {orch.get('agent_id', 'orchestrator')}")
        print(f"Registered Agents: {len(status['agents'])}")
        for name, agent_status in status['agents'].items():
            print(f"  - {name}: {agent_status.get('status', 'unknown')}")
        print("=" * 50)


if __name__ == '__main__':
    asyncio.run(main())
