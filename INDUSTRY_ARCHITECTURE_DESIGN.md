# 🏭 灵顺融合版 - 企业级架构设计

**灵感来源**: The AI Scientist + Salesforce Agentforce + LangGraph + BioMARS  
**创建时间**: 2026-04-03  
**目标**: 打造企业级自动化研究系统

---

## 🎯 核心架构 (融合行业最佳实践)

```
┌─────────────────────────────────────────────────────────────┐
│                    【规划层】Planner Agent                   │
│  - 任务拆解 DAG (The AI Scientist)                          │
│  - 动态调度 (Salesforce Atlas)                              │
│  - 研究空白发现 (切问学术)                                   │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                  【执行层】Worker Agents                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ 研究 Agent  │  │ 代码 Agent  │  │ 实验 Agent  │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ 写作 Agent  │  │ 测试 Agent  │  │ 评审 Agent  │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│  (BioMARS 分层多 Agent 分工)                                 │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                  【校验层】Evaluator Agent                   │
│  - 自动评审 (The AI Scientist)                              │
│  - 指令校验 (BioMARS CodeChecker)                           │
│  - 质量门禁 (灵顺质量门禁)                                   │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                    【工具层】Tool Chain                      │
│  - 文献检索 API (The AI Scientist)                          │
│  - 代码沙箱 (The AI Scientist)                              │
│  - 实验集群 (切问学术)                                       │
│  - 版本控制 (OpenAI Harness)                                │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                  【护栏层】Trust Layer                       │
│  - 安全审计 (Salesforce Einstein Trust Layer)               │
│  - 权限隔离 (Salesforce Agentforce)                         │
│  - 脱敏处理 (Salesforce Agentforce)                         │
│  - 人工介入 (Salesforce Agentforce)                         │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                    【状态层】State Management                │
│  - Checkpoint (LangGraph checkpointer)                      │
│  - 持久化 (LangGraph 外部存储)                               │
│  - 断点恢复 (LangGraph 中断恢复)                             │
│  - 上下文管理 (DeepAgents 上下文清洗)                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 关键模块设计

### 模块 1: Planner Agent (规划层)

**灵感**: The AI Scientist + Salesforce Atlas

```python
class ResearchPlanner:
    """研究规划器"""
    
    def __init__(self):
        self.dag_templates = {
            'security_research': self.security_research_dag,
            'rule_development': self.rule_development_dag,
            'paper_writing': self.paper_writing_dag,
        }
    
    def plan(self, task: ResearchTask) -> ResearchPlan:
        """生成研究计划"""
        
        # 1. 任务拆解 (DAG)
        dag = self.dag_templates[task.type]()
        
        # 2. 依赖分析
        dependencies = self.analyze_dependencies(dag)
        
        # 3. 资源分配
        resources = self.allocate_resources(dag)
        
        # 4. 时间估算
        timeline = self.estimate_timeline(dag)
        
        return ResearchPlan(
            dag=dag,
            dependencies=dependencies,
            resources=resources,
            timeline=timeline,
        )
    
    def security_research_dag(self) -> DAG:
        """安全研究流程 (固定流水线，不可跳步)"""
        return DAG([
            Step('literature_review', '文献调研'),
            Step('threat_analysis', '威胁分析'),
            Step('sample_collection', '样本收集'),
            Step('rule_development', '规则开发'),
            Step('testing', '测试验证'),
            Step('evaluation', '评估报告'),
            Step('review', '自动评审'),
        ])
```

---

### 模块 2: Worker Agents (执行层)

**灵感**: BioMARS 三层 Agent 分工

```python
class ResearchWorker(BaseAgent):
    """研究工作 Agent"""
    
    def __init__(self, specialty: str):
        super().__init__(name=f'ResearchWorker_{specialty}')
        self.specialty = specialty
    
    async def execute(self, step: Step) -> StepResult:
        """执行研究步骤"""
        
        # 1. 环境准备
        env = await self.prepare_environment(step)
        
        # 2. 执行任务
        result = await self.run_task(step, env)
        
        # 3. 结果验证
        verified = await self.verify_result(result)
        
        return StepResult(
            success=verified,
            output=result,
            checkpoint=self.save_checkpoint(result),
        )


class CodeWorker(ResearchWorker):
    """代码工作 Agent"""
    
    async def run_task(self, step: Step, env: Environment) -> CodeResult:
        """执行代码任务"""
        
        # 1. 代码沙箱执行
        sandbox = CodeSandbox(env)
        result = await sandbox.execute(step.code)
        
        # 2. 代码审查
        review = await self.code_review(result.code)
        
        return CodeResult(
            code=result.code,
            tests=result.tests,
            review=review,
        )
```

---

### 模块 3: Evaluator Agent (校验层)

**灵感**: The AI Scientist 自动评审 + BioMARS CodeChecker

```python
class ResearchEvaluator:
    """研究评估器"""
    
    def __init__(self):
        self.criteria = {
            'novelty': self.evaluate_novelty,
            'correctness': self.evaluate_correctness,
            'completeness': self.evaluate_completeness,
            'reproducibility': self.evaluate_reproducibility,
        }
    
    async def evaluate(self, research: ResearchResult) -> EvaluationReport:
        """评估研究成果"""
        
        scores = {}
        feedback = []
        
        for criterion, evaluator in self.criteria.items():
            score, fb = await evaluator(research)
            scores[criterion] = score
            feedback.append(fb)
        
        # 综合评分
        overall_score = sum(scores.values()) / len(scores)
        
        # 是否通过
        passed = overall_score >= 0.8
        
        return EvaluationReport(
            overall_score=overall_score,
            scores=scores,
            feedback=feedback,
            passed=passed,
            suggestions=self.generate_suggestions(feedback),
        )
    
    async def evaluate_correctness(self, research: ResearchResult) -> tuple[float, str]:
        """评估正确性"""
        
        # 1. 代码审查
        code_review = await self.code_review(research.code)
        
        # 2. 测试覆盖
        test_coverage = await self.check_test_coverage(research.tests)
        
        # 3. 结果验证
        result_verification = await self.verify_results(research.results)
        
        score = (code_review.score * 0.4 + 
                 test_coverage * 0.3 + 
                 result_verification * 0.3)
        
        feedback = f"正确性评分：{score:.2f}\n"
        feedback += f"- 代码审查：{code_review.score:.2f}\n"
        feedback += f"- 测试覆盖：{test_coverage:.2f}\n"
        feedback += f"- 结果验证：{result_verification:.2f}\n"
        
        return score, feedback
```

---

### 模块 4: State Management (状态层)

**灵感**: LangGraph checkpointer + DeepAgents 上下文管理

```python
class ResearchStateManager:
    """研究状态管理器"""
    
    def __init__(self, storage: StateStorage):
        self.storage = storage
        self.checkpointer = Checkpointer(storage)
    
    async def save_checkpoint(self, plan: ResearchPlan, state: ResearchState):
        """保存检查点"""
        
        checkpoint = {
            'plan_id': plan.id,
            'current_step': state.current_step,
            'completed_steps': state.completed_steps,
            'results': state.results,
            'context': self.compress_context(state.context),
            'timestamp': datetime.now().isoformat(),
        }
        
        await self.checkpointer.save(plan.id, checkpoint)
    
    async def restore_checkpoint(self, plan_id: str) -> ResearchState:
        """恢复检查点"""
        
        checkpoint = await self.checkpointer.load(plan_id)
        
        return ResearchState(
            current_step=checkpoint['current_step'],
            completed_steps=checkpoint['completed_steps'],
            results=checkpoint['results'],
            context=checkpoint['context'],
        )
    
    def compress_context(self, context: Dict) -> Dict:
        """上下文压缩 (防爆炸)"""
        
        # 1. 自动摘要
        summary = self.auto_summarize(context)
        
        # 2. 大结果外存
        large_results = self.extract_large_results(context)
        for key, value in large_results.items():
            external_id = self.store_external(value)
            context[key] = f'external:{external_id}'
        
        # 3. 保留关键信息
        compressed = {
            'summary': summary,
            'key_findings': context.get('key_findings', []),
            'decisions': context.get('decisions', []),
        }
        
        return compressed
```

---

### 模块 5: Trust Layer (护栏层)

**灵感**: Salesforce Einstein Trust Layer

```python
class TrustLayer:
    """信任护栏层"""
    
    def __init__(self):
        self.security_audit = SecurityAudit()
        self.permission_check = PermissionCheck()
        self.data_masking = DataMasking()
    
    async def before_execute(self, action: Action, context: Context) -> bool:
        """执行前安全检查"""
        
        # 1. 权限检查
        if not await self.permission_check.check(action, context.user):
            raise PermissionError(f"无权执行：{action}")
        
        # 2. 安全审计
        audit_result = await self.security_audit.audit(action)
        if not audit_result.passed:
            raise SecurityError(f"安全风险：{audit_result.reason}")
        
        # 3. 数据脱敏
        if action.contains_sensitive_data():
            action.data = await self.data_masking.mask(action.data)
        
        return True
    
    async def after_execute(self, action: Action, result: Result):
        """执行后审计"""
        
        # 1. 记录审计日志
        await self.security_audit.log(action, result)
        
        # 2. 结果审查
        if result.contains_sensitive_data():
            result.data = await self.data_masking.mask(result.data)
        
        # 3. 人工介入检查
        if action.requires_human_review():
            await self.request_human_review(action, result)
```

---

## 🔄 完整工作流程

```python
class AutomatedResearchSystem:
    """自动化研究系统"""
    
    def __init__(self):
        self.planner = ResearchPlanner()
        self.workers = {
            'research': ResearchWorker('research'),
            'code': CodeWorker('code'),
            'experiment': ExperimentWorker('experiment'),
            'writing': WritingWorker('writing'),
        }
        self.evaluator = ResearchEvaluator()
        self.state_manager = ResearchStateManager(storage=FileSystemStorage())
        self.trust_layer = TrustLayer()
    
    async def execute(self, task: ResearchTask) -> ResearchResult:
        """执行研究任务"""
        
        # 1. 规划
        plan = await self.planner.plan(task)
        
        # 2. 恢复检查点 (如果有)
        state = await self.state_manager.restore_checkpoint(plan.id)
        
        # 3. 执行研究步骤
        for step in plan.dag.steps:
            if state.is_completed(step):
                continue
            
            # 信任层检查
            await self.trust_layer.before_execute(step, task.context)
            
            # 选择 Worker
            worker = self.select_worker(step)
            
            # 执行
            result = await worker.execute(step)
            
            # 评估
            evaluation = await self.evaluator.evaluate(result)
            
            if not evaluation.passed:
                # 修正
                result = await self.correct(result, evaluation.suggestions)
            
            # 保存检查点
            state.update(step, result)
            await self.state_manager.save_checkpoint(plan, state)
            
            # 信任层审计
            await self.trust_layer.after_execute(step, result)
        
        # 4. 最终评估
        final_result = ResearchResult(
            task=task,
            steps=state.completed_steps,
            outputs=state.results,
        )
        
        final_evaluation = await self.evaluator.evaluate(final_result)
        
        return final_result
```

---

## 📊 与行业方案对比

| 特性 | The AI Scientist | Salesforce Agentforce | 灵顺融合版 |
|------|-----------------|---------------------|-----------|
| **规划层** | ✅ 四阶段闭环 | ✅ Atlas 动态调度 | ✅ 融合两者 |
| **执行层** | ✅ 实验执行 | ✅ 企业级 Agent | ✅ BioMARS 分工 |
| **校验层** | ✅ 自动评审 | ✅ Trust Layer | ✅ 双重校验 |
| **状态管理** | ✅ Checkpoint | ❌ | ✅ LangGraph 方案 |
| **安全护栏** | ❌ | ✅ Einstein Trust | ✅ 完整实现 |
| **异步调度** | ❌ | ✅ | ✅ LangGraph 方案 |
| **上下文管理** | ❌ | ❌ | ✅ DeepAgents 方案 |

**灵顺融合版优势**:
- ✅ 集百家之长
- ✅ 企业级安全
- ✅ 长任务支持
- ✅ 状态可恢复
- ✅ 上下文防爆炸

---

## 🚀 实施计划

### 阶段 1: 基础架构 (1-2 周)
- [ ] 实现 Planner Agent
- [ ] 实现 State Management
- [ ] 实现 Trust Layer

### 阶段 2: Worker Agents (2-3 周)
- [ ] 实现 Research Worker
- [ ] 实现 Code Worker
- [ ] 实现 Experiment Worker

### 阶段 3: Evaluator (1-2 周)
- [ ] 实现自动评审
- [ ] 实现质量门禁
- [ ] 实现修正机制

### 阶段 4: 集成测试 (1 周)
- [ ] 端到端测试
- [ ] 性能优化
- [ ] 文档完善

**总工作量**: 5-8 周

---

**开始打造企业级自动化研究系统！** 🚀
