"""
Orchestrator Agent - 多 Agent 协调器
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import asyncio

from .base_agent import BaseAgent, Task, Result


@dataclass
class AgentAssignment:
    """Agent 任务分配"""
    agent_id: str
    task: Task
    priority: int = 0
    timeout: int = 300  # 5 分钟


class OrchestratorAgent(BaseAgent):
    """协调器 Agent"""
    
    def __init__(self, config: Optional[Dict] = None):
        super().__init__("orchestrator", config)
        self.registered_agents: Dict[str, BaseAgent] = {}
        self.pending_tasks: List[Task] = []
        self.completed_tasks: List[Task] = []
        self.agent_capabilities: Dict[str, List[str]] = {}  # agent_id -> [task_types]
    
    def register_agent(self, agent: BaseAgent, capabilities: List[str]):
        """注册 Agent"""
        self.registered_agents[agent.agent_id] = agent
        self.agent_capabilities[agent.agent_id] = capabilities
        self._log("INFO", f"Registered agent: {agent.agent_id}, capabilities: {capabilities}")
    
    def unregister_agent(self, agent_id: str):
        """注销 Agent"""
        if agent_id in self.registered_agents:
            del self.registered_agents[agent_id]
            del self.agent_capabilities[agent_id]
            self._log("INFO", f"Unregistered agent: {agent_id}")
    
    async def execute(self, task: Task) -> Result:
        """执行任务 - 协调多个 Agent"""
        self.current_task = task
        self.update_status("busy")
        
        try:
            # 1. 解析任务
            parsed = self._parse_task(task)
            
            # 2. 分发给合适的 Agent
            assignments = self._dispatch_task(parsed)
            
            # 3. 收集结果
            results = await self._collect_results(assignments)
            
            # 4. 聚合结果
            final_result = self._aggregate_results(results)
            
            self.completed_tasks.append(task)
            task.status = "completed"
            
            return Result(
                task_id=task.id,
                agent_id=self.agent_id,
                success=True,
                data=final_result,
            )
        
        except Exception as e:
            self._log("ERROR", f"Task execution failed: {e}")
            task.status = "failed"
            task.error = str(e)
            
            return Result(
                task_id=task.id,
                agent_id=self.agent_id,
                success=False,
                error=str(e),
            )
        
        finally:
            self.current_task = None
            self.update_status("idle")
    
    def _parse_task(self, task: Task) -> Task:
        """解析任务"""
        self._log("INFO", f"Parsing task: {task.id}, type: {task.type}")
        # 可以在这里添加任务解析逻辑
        return task
    
    def _dispatch_task(self, task: Task) -> List[AgentAssignment]:
        """分发任务给合适的 Agent"""
        assignments = []
        
        # 查找能处理该任务的 Agent
        for agent_id, capabilities in self.agent_capabilities.items():
            if task.type in capabilities:
                assignment = AgentAssignment(
                    agent_id=agent_id,
                    task=task,
                    priority=0,
                )
                assignments.append(assignment)
                self._log("INFO", f"Dispatched task {task.id} to {agent_id}")
        
        if not assignments:
            self._log("WARNING", f"No agent found for task type: {task.type}")
        
        return assignments
    
    async def _collect_results(self, assignments: List[AgentAssignment]) -> List[Result]:
        """收集 Agent 执行结果"""
        results = []
        
        async def execute_assignment(assignment: AgentAssignment) -> Result:
            agent = self.registered_agents.get(assignment.agent_id)
            if agent:
                try:
                    return await asyncio.wait_for(
                        agent.execute(assignment.task),
                        timeout=assignment.timeout
                    )
                except asyncio.TimeoutError:
                    return Result(
                        task_id=assignment.task.id,
                        agent_id=assignment.agent_id,
                        success=False,
                        error="Timeout",
                    )
            return Result(
                task_id=assignment.task.id,
                agent_id=assignment.agent_id,
                success=False,
                error="Agent not found",
            )
        
        # 并发执行所有分配
        tasks = [execute_assignment(a) for a in assignments]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return results
    
    def _aggregate_results(self, results: List[Result]) -> Dict:
        """聚合结果"""
        aggregated = {
            'total_results': len(results),
            'successful': sum(1 for r in results if isinstance(r, Result) and r.success),
            'failed': sum(1 for r in results if isinstance(r, Result) and not r.success),
            'results': [],
        }
        
        for result in results:
            if isinstance(result, Result):
                aggregated['results'].append({
                    'agent_id': result.agent_id,
                    'success': result.success,
                    'data': result.data,
                    'error': result.error,
                })
            else:
                aggregated['results'].append({
                    'error': str(result),
                })
        
        return aggregated
    
    def get_status(self) -> Dict:
        """获取协调器状态"""
        return {
            'agent_id': self.agent_id,
            'status': self.status,
            'registered_agents': len(self.registered_agents),
            'pending_tasks': len(self.pending_tasks),
            'completed_tasks': len(self.completed_tasks),
            'agent_capabilities': self.agent_capabilities,
        }
