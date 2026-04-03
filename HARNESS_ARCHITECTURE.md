# 🦾 灵顺融合版 - Harness Engineering 架构

**灵感来源**: LangGraph + Guardrails AI + AutoGen + Temporal + SOAR  
**创建时间**: 2026-04-03  
**目标**: 打造恶意代码扫描自动化 Harness

---

## 🎯 Harness Engineering 核心理念

> **Harness = 安全带 + 流水线 + 调度器 + 护栏 + 可复现执行引擎**
>
> **不是让 Agent 更聪明，而是让 Agent 更稳、可控、可复盘、可大规模部署**

---

## 📋 Harness 8 大核心能力

| 能力 | 说明 | 实现方案 |
|------|------|----------|
| **1. 任务编排** | DAG/状态机/工作流 | LangGraph |
| **2. 状态持久化** | Checkpoint/断点恢复 | LangGraph Checkpointer |
| **3. 工具封装** | 权限隔离/安全调用 | Guardrails AI |
| **4. 重试降级** | 超时/熔断/限流 | Temporal |
| **5. 护栏约束** | 输出校验/风险拦截 | Pydantic AI + Guardrails |
| **6. 多 Agent** | 分工/调度/协作 | AutoGen/Swarm |
| **7. 可观测性** | 日志/指标/回溯 | LangGraph Observability |
| **8. 闭环迭代** | 交付物校验/修正 | SOAR Playbook |

---

## 🏭 灵顺 Harness 架构 (融合行业最佳)

```
┌─────────────────────────────────────────────────────────────┐
│              【调度层】Harness Engine (LangGraph)            │
│  - 状态机驱动                                                │
│  - DAG 执行引擎                                              │
│  - Checkpoint 断点恢复                                       │
│  - 循环/条件/子图/并行                                       │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│           【Agent 层】Multi-Agent Team (AutoGen)             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ 解析 Agent  │  │ 静态 Agent  │  │ 动态 Agent  │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ 分析 Agent  │  │ 报告 Agent  │  │ 评审 Agent  │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│  (专家分工 + 发言规则 + 人在回路)                             │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│            【工具层】Tool Sandbox (Guardrails)               │
│  - YARA 规则扫描                                             │
│  - AST 静态分析                                              │
│  - 沙箱执行                                                  │
│  - 文件操作 (权限隔离)                                       │
│  - 报告生成                                                  │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│           【护栏层】Trust & Safety (Pydantic AI)             │
│  - 输出强格式校验                                            │
│  - 风险行为拦截                                              │
│  - 幻觉抑制                                                  │
│  - 安全边界定义                                              │
│  - 权限检查                                                  │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│          【执行层】Distributed Engine (Temporal)             │
│  - 全链路重试                                                │
│  - 超时/熔断/限流                                            │
│  - 分布式任务                                                │
│  - 可回溯                                                    │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 关键模块设计

### 模块 1: Harness Engine (LangGraph)

**灵感**: LangGraph 状态机 + Checkpoint

```python
from langgraph.graph import StateGraph, END
from langgraph.checkpoint import MemorySaver
from typing import TypedDict, Annotated, List

class ScanState(TypedDict):
    """扫描状态"""
    sample_path: str
    current_step: str
    completed_steps: List[str]
    results: dict
    errors: List[str]
    confidence: float

class MalwareScanHarness:
    """恶意代码扫描 Harness"""
    
    def __init__(self):
        # 1. 创建状态图
        self.workflow = StateGraph(ScanState)
        
        # 2. 定义节点
        self.workflow.add_node("parse", self.parse_sample)
        self.workflow.add_node("static_analysis", self.static_analysis)
        self.workflow.add_node("dynamic_analysis", self.dynamic_analysis)
        self.workflow.add_node("aggregate", self.aggregate_results)
        self.workflow.add_node("report", self.generate_report)
        self.workflow.add_node("review", self.auto_review)
        
        # 3. 定义边 (DAG)
        self.workflow.set_entry_point("parse")
        self.workflow.add_edge("parse", "static_analysis")
        self.workflow.add_edge("static_analysis", "dynamic_analysis")
        self.workflow.add_edge("dynamic_analysis", "aggregate")
        self.workflow.add_conditional_edges(
            "aggregate",
            self.should_review,
            {
                "needs_review": "review",
                "done": "report"
            }
        )
        self.workflow.add_edge("review", "report")
        self.workflow.add_edge("report", END)
        
        # 4. 创建 Checkpointer (断点恢复)
        self.checkpointer = MemorySaver()
        
        # 5. 编译
        self.app = self.workflow.compile(checkpointer=self.checkpointer)
    
    def execute(self, sample_path: str, thread_id: str = "default") -> dict:
        """执行扫描"""
        
        # 初始状态
        initial_state = {
            "sample_path": sample_path,
            "current_step": "parse",
            "completed_steps": [],
            "results": {},
            "errors": [],
            "confidence": 0.0,
        }
        
        # 执行 (支持断点恢复)
        config = {"configurable": {"thread_id": thread_id}}
        final_state = self.app.invoke(initial_state, config)
        
        return final_state
    
    def should_review(self, state: ScanState) -> str:
        """条件判断：是否需要人工评审"""
        
        # 置信度低 → 需要评审
        if state["confidence"] < 0.8:
            return "needs_review"
        
        # 有错误 → 需要评审
        if len(state["errors"]) > 0:
            return "needs_review"
        
        return "done"
    
    async def parse_sample(self, state: ScanState) -> dict:
        """解析样本"""
        # 实现解析逻辑
        pass
    
    async def static_analysis(self, state: ScanState) -> dict:
        """静态分析"""
        # 实现静态分析逻辑
        pass
    
    async def dynamic_analysis(self, state: ScanState) -> dict:
        """动态分析"""
        # 实现动态分析逻辑
        pass
    
    async def aggregate_results(self, state: ScanState) -> dict:
        """汇总结果"""
        # 实现汇总逻辑
        pass
    
    async def generate_report(self, state: ScanState) -> dict:
        """生成报告"""
        # 实现报告生成逻辑
        pass
    
    async def auto_review(self, state: ScanState) -> dict:
        """自动评审"""
        # 实现评审逻辑
        pass
```

---

### 模块 2: Multi-Agent Team (AutoGen)

**灵感**: AutoGen GroupChat + GroupManager

```python
from autogen import ConversableAgent, GroupChat, GroupChatManager

class MalwareAnalysisTeam:
    """恶意代码分析团队"""
    
    def __init__(self):
        # 1. 创建专家 Agent
        self.parser_agent = ConversableAgent(
            name="ParserAgent",
            system_message="你是样本解析专家，负责解析恶意代码样本结构",
        )
        
        self.static_agent = ConversableAgent(
            name="StaticAgent",
            system_message="你是静态分析专家，负责 YARA/AST/控制流分析",
        )
        
        self.dynamic_agent = ConversableAgent(
            name="DynamicAgent",
            system_message="你是动态分析专家，负责沙箱执行/行为监控",
        )
        
        self.analyst_agent = ConversableAgent(
            name="AnalystAgent",
            system_message="你是分析专家，负责综合分析/威胁评估",
        )
        
        self.reporter_agent = ConversableAgent(
            name="ReporterAgent",
            system_message="你是报告专家，负责生成标准化报告",
        )
        
        self.reviewer_agent = ConversableAgent(
            name="ReviewerAgent",
            system_message="你是评审专家，负责质量把关/纠错",
        )
        
        # 2. 创建群聊
        self.group_chat = GroupChat(
            agents=[
                self.parser_agent,
                self.static_agent,
                self.dynamic_agent,
                self.analyst_agent,
                self.reporter_agent,
                self.reviewer_agent,
            ],
            messages=[],
            max_round=10,
            speaker_selection_method="round_robin",  # 轮流发言
        )
        
        # 3. 创建管理员
        self.manager = GroupChatManager(
            groupchat=self.group_chat,
            llm_config={"config_list": [...]},
        )
    
    async def analyze(self, sample: dict) -> dict:
        """执行团队分析"""
        
        # 启动群聊
        await self.parser_agent.initiate_chat(
            self.manager,
            message=f"请分析样本：{sample['path']}",
        )
        
        # 获取分析结果
        result = self.extract_result(self.group_chat.messages)
        
        return result
    
    def extract_result(self, messages: List[dict]) -> dict:
        """从对话中提取结果"""
        # 实现结果提取逻辑
        pass
```

---

### 模块 3: Guardrails (Pydantic AI + Guardrails AI)

**灵感**: Guardrails AI + Pydantic AI 强约束

```python
from pydantic import BaseModel, Field, validator
from guardrails import Guard, OnFailAction
from guardrails.validators import ValidRange, RegexMatch

class ScanResult(BaseModel):
    """扫描结果 (强格式)"""
    
    sample_path: str = Field(..., description="样本路径")
    is_malicious: bool = Field(..., description="是否恶意")
    confidence: float = Field(..., ge=0.0, le=1.0, description="置信度")
    threat_type: str = Field(..., regex="^(malware|trojan|ransomware|none)$")
    iocs: List[str] = Field(default_factory=list, description="IOC 列表")
    risk_score: float = Field(..., ge=0.0, le=10.0, description="风险评分")
    
    @validator('confidence')
    def validate_confidence(cls, v):
        """置信度校验"""
        if v < 0.5:
            raise ValueError("置信度过低，需要人工评审")
        return v
    
    @validator('risk_score')
    def validate_risk_score(cls, v, values):
        """风险评分校验"""
        if v > 8.0 and values['confidence'] < 0.9:
            raise ValueError("高风险但置信度不足")
        return v

class GuardrailsHarness:
    """护栏 Harness"""
    
    def __init__(self):
        # 1. 创建 Guard
        self.guard = Guard.from_pydantic(
            output_class=ScanResult,
            on_fail=OnFailAction.EXCEPTION,  # 失败抛异常
        )
    
    def validate(self, result: dict) -> ScanResult:
        """验证结果"""
        
        # 1. 格式校验
        try:
            validated = self.guard.validate(result)
        except Exception as e:
            # 2. 护栏拦截
            raise GuardrailsError(f"护栏拦截：{e}")
        
        # 3. 风险行为检查
        self.check_risk_behavior(validated)
        
        # 4. 幻觉抑制
        self.suppress_hallucination(validated)
        
        return validated
    
    def check_risk_behavior(self, result: ScanResult):
        """风险行为检查"""
        
        # 检查是否有危险操作
        if result.is_malicious and result.confidence < 0.7:
            raise SecurityError("恶意判定但置信度不足")
    
    def suppress_hallucination(self, result: ScanResult):
        """幻觉抑制"""
        
        # 检查 IOC 是否真实
        for ioc in result.iocs:
            if not self.verify_ioc(ioc):
                result.iocs.remove(ioc)
    
    def verify_ioc(self, ioc: str) -> bool:
        """验证 IOC"""
        # 实现 IOC 验证逻辑
        pass
```

---

### 模块 4: Distributed Engine (Temporal)

**灵感**: Temporal 工业级 Harness

```python
from temporalio import workflow, activity
from temporalio.client import Client
from datetime import timedelta

@activity.defn
async def scan_sample_activity(sample_path: str) -> dict:
    """扫描活动"""
    # 实现扫描逻辑
    pass

@workflow.defn
class MalwareScanWorkflow:
    """扫描工作流"""
    
    @workflow.run
    async def run(self, sample_path: str) -> dict:
        """执行扫描"""
        
        # 1. 解析
        parse_result = await workflow.execute_activity(
            parse_sample_activity,
            sample_path,
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy={
                "initial_interval": 1,
                "maximum_interval": 60,
                "maximum_attempts": 3,
            },
        )
        
        # 2. 静态分析
        static_result = await workflow.execute_activity(
            static_analysis_activity,
            parse_result,
            start_to_close_timeout=timedelta(minutes=10),
        )
        
        # 3. 动态分析
        dynamic_result = await workflow.execute_activity(
            dynamic_analysis_activity,
            static_result,
            start_to_close_timeout=timedelta(minutes=30),
        )
        
        # 4. 汇总
        final_result = await workflow.execute_activity(
            aggregate_activity,
            [parse_result, static_result, dynamic_result],
            start_to_close_timeout=timedelta(minutes=5),
        )
        
        return final_result

class TemporalHarness:
    """Temporal Harness"""
    
    def __init__(self):
        self.client = Client.connect("localhost:7233")
    
    async def execute(self, sample_path: str) -> dict:
        """执行扫描"""
        
        # 启动工作流
        handle = await self.client.start_workflow(
            MalwareScanWorkflow.run,
            sample_path,
            id=f"scan-{sample_path}",
            task_queue="malware-scan",
        )
        
        # 等待结果
        result = await handle.result()
        
        return result
    
    async def retry(self, workflow_id: str) -> dict:
        """重试失败的工作流"""
        
        handle = self.client.get_workflow_handle(workflow_id)
        result = await handle.result()
        
        return result
```

---

## 🔄 完整工作流程

```python
class AutomatedMalwareScanSystem:
    """自动化恶意代码扫描系统"""
    
    def __init__(self):
        # 1. Harness 引擎
        self.harness = MalwareScanHarness()
        
        # 2. 多 Agent 团队
        self.agent_team = MalwareAnalysisTeam()
        
        # 3. 护栏
        self.guardrails = GuardrailsHarness()
        
        # 4. 分布式引擎
        self.temporal = TemporalHarness()
    
    async def scan(self, sample_path: str) -> ScanResult:
        """执行扫描"""
        
        try:
            # 1. Harness 执行
            state = await self.harness.execute(sample_path)
            
            # 2. Agent 团队分析
            agent_result = await self.agent_team.analyze(state)
            
            # 3. 护栏验证
            validated = self.guardrails.validate(agent_result)
            
            # 4. 保存到 Temporal
            await self.temporal.execute(sample_path)
            
            return validated
            
        except GuardrailsError as e:
            # 护栏拦截
            logger.error(f"护栏拦截：{e}")
            raise
        
        except Exception as e:
            # 错误处理
            logger.error(f"扫描失败：{e}")
            raise
```

---

## 📊 学习路线 (按顺序)

| 顺序 | 框架 | 学习内容 | 工作量 |
|------|------|----------|--------|
| **1** | LangGraph | Harness 核心引擎 | 1-2 周 |
| **2** | Guardrails AI | 安全护栏 | 3-5 天 |
| **3** | AutoGen/Swarm | 多 Agent 协作 | 1 周 |
| **4** | Temporal | 生产级分布式 | 1-2 周 |
| **5** | SOAR Playbook | 安全流程范式 | 3-5 天 |

**总工作量**: 5-7 周

---

## 🚀 实施计划

### 阶段 1: LangGraph Harness (1-2 周)
- [ ] 学习 LangGraph 基础
- [ ] 实现扫描状态图
- [ ] 实现 Checkpoint
- [ ] 实现条件边

### 阶段 2: Guardrails (3-5 天)
- [ ] 学习 Guardrails AI
- [ ] 定义 ScanResult 格式
- [ ] 实现护栏校验
- [ ] 实现风险拦截

### 阶段 3: Multi-Agent (1 周)
- [ ] 学习 AutoGen
- [ ] 创建专家 Agent
- [ ] 实现群聊管理
- [ ] 实现结果提取

### 阶段 4: Temporal (1-2 周)
- [ ] 学习 Temporal
- [ ] 定义 Activity
- [ ] 定义 Workflow
- [ ] 实现重试机制

### 阶段 5: 集成测试 (3-5 天)
- [ ] 端到端测试
- [ ] 性能优化
- [ ] 文档完善

---

## 📁 交付文件

**架构设计**: `HARNESS_ARCHITECTURE.md`

**包含**:
- ✅ Harness 8 大核心能力
- ✅ 完整架构图
- ✅ 4 大模块详细设计
- ✅ 代码示例
- ✅ 学习路线
- ✅ 实施计划

---

**开始打造 Harness Engineering 驱动的自动化扫描系统！** 🚀
