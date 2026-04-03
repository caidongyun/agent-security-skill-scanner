# 编排工具调研报告

**调研时间**: 2026-03-25  
**目标**: 选择适合样本生成/扫描任务的编排工具

---

## 📊 执行摘要

### 推荐方案

| 场景 | 推荐工具 | 理由 |
|------|---------|------|
| **简单任务编排** | GNU Make + Bash | 零依赖，易上手 |
| **复杂工作流** | **Prefect** | Python 原生，轻量 |
| **企业级调度** | Apache Airflow | 成熟稳定，生态好 |
| **安全自动化** | Shuffle (SOAR) | 安全专用，集成多 |
| **AI Agent 编排** | LangGraph | AI 原生，支持多 Agent |

**我们的选择**: **Prefect v2** + **自定义编排器**

---

## 1️⃣ 通用工作流编排工具

### 1.1 Apache Airflow

**官网**: https://airflow.apache.org/  
**GitHub**: 32k+ stars  
**语言**: Python

**特点**:
```yaml
优点:
  - 成熟稳定 (2014 年至今)
  - 丰富的操作符库
  - Web UI 完善
  - 支持定时调度
  - 任务依赖管理强大

缺点:
  - 重量级 (需要数据库)
  - 学习曲线陡峭
  - 动态工作流支持弱
  - 资源消耗大
```

**适用场景**: 企业级 ETL、定时批处理

**示例 DAG**:
```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

def generate_samples():
    # 生成样本逻辑
    pass

def scan_samples():
    # 扫描逻辑
    pass

def generate_report():
    # 生成报告
    pass

with DAG('sample_generation', schedule_interval='@daily') as dag:
    t1 = PythonOperator(task_id='generate', python_callable=generate_samples)
    t2 = PythonOperator(task_id='scan', python_callable=scan_samples)
    t3 = PythonOperator(task_id='report', python_callable=generate_report)
    
    t1 >> t2 >> t3
```

---

### 1.2 Prefect

**官网**: https://prefect.io/  
**GitHub**: 15k+ stars  
**语言**: Python

**特点**:
```yaml
优点:
  - Python 原生 (装饰器定义)
  - 轻量级 (无需数据库)
  - 动态工作流支持
  - 错误处理完善
  - 免费云版本
  - 学习曲线平缓

缺点:
  - 社区较小
  - 高级功能需付费
```

**适用场景**: **我们的首选** - Python 项目编排

**示例 Flow**:
```python
from prefect import flow, task
from prefect.task_runners import ConcurrentTaskRunner

@task
def generate_samples(language: str, count: int):
    """生成样本"""
    from generators.cli import generate
    return generate(language, count)

@task
def scan_samples(sample_paths: list):
    """扫描样本"""
    from scanner.cli import scan
    return scan(sample_paths)

@task
def generate_report(scan_results: list):
    """生成报告"""
    from reports.generator import create
    return create(scan_results)

@flow(task_runner=ConcurrentTaskRunner())
def sample_pipeline():
    # 生成多语言样本
    py_samples = generate_samples("python", 100)
    ps_samples = generate_samples("powershell", 50)
    js_samples = generate_samples("javascript", 50)
    
    # 并行扫描
    all_samples = [py_samples, ps_samples, js_samples]
    scan_results = scan_samples.map(all_samples)
    
    # 生成报告
    report = generate_report(scan_results)
    return report

if __name__ == "__main__":
    sample_pipeline()
```

**部署**:
```bash
# 本地运行
python pipeline.py

# 启动 Prefect Server
prefect server start

# 部署 Flow
prefect deploy sample_pipeline.py

# 定时调度
prefect deployment build sample_pipeline.py:sample_pipeline \
  --name "daily-generation" \
  --schedule "0 2 * * *" \
  --apply
```

---

### 1.3 Dagster

**官网**: https://dagster.io/  
**GitHub**: 8k+ stars  
**语言**: Python

**特点**:
```yaml
优点:
  - 数据感知 (Data Assets)
  - 开发体验好
  - 测试友好
  - 类型安全

缺点:
  - 概念复杂
  - 文档分散
```

**适用场景**: 数据管道、ML 流水线

---

### 1.4 Luigi

**官网**: https://luigi.readthedocs.io/  
**GitHub**: 17k+ stars  
**语言**: Python

**特点**:
```yaml
优点:
  - Spotify 出品
  - 简单轻量
  - 无需额外服务

缺点:
  - UI 简陋
  - 错误处理弱
  - 动态工作流支持差
```

---

## 2️⃣ 安全自动化编排工具

### 2.1 Shuffle

**官网**: https://shuffler.io/  
**GitHub**: 2k+ stars  
**语言**: Go/React

**特点**:
```yaml
优点:
  - 安全专用 (SOAR)
  - 200+ 安全应用集成
  - Web UI 可视化编排
  - 支持自定义 App
  - 免费开源

缺点:
  - 需要 Docker 部署
  - 学习曲线中等
  - 文档不够完善
```

**适用场景**: 安全事件响应、威胁情报自动化

**示例工作流**:
```
触发器 (新样本上传)
  ↓
步骤 1: YARA 扫描
  ↓
步骤 2: 静态分析
  ↓
步骤 3: 动态分析 (沙箱)
  ↓
步骤 4: 威胁评分
  ↓
步骤 5: 告警通知 (飞书/钉钉)
```

**部署**:
```bash
docker-compose up -d
# 访问 http://localhost:3000
```

---

### 2.2 TheHive + Cortex

**官网**: https://thehive-project.org/  
**GitHub**: 5k+ stars  
**语言**: Scala/Python

**特点**:
```yaml
优点:
  - 完整的安全运营平台
  - Cortex 分析器丰富
  - 案例管理
  - MISP 集成

缺点:
  - 重量级
  - 配置复杂
  - 资源消耗大
```

**适用场景**: SOC 运营、事件管理

---

### 2.3 Wazuh

**官网**: https://wazuh.com/  
**GitHub**: 6k+ stars  
**语言**: C/Python

**特点**:
```yaml
优点:
  - 完整的 XDR 平台
  - 端点检测
  - 日志分析
  - 合规检查

缺点:
  - 学习曲线陡峭
  - 配置复杂
```

**适用场景**: 端点安全、SIEM

---

## 3️⃣ AI Agent 编排工具

### 3.1 LangGraph (LangChain)

**官网**: https://langchain-ai.github.io/langgraph/  
**GitHub**: 75k+ stars (LangChain)  
**语言**: Python

**特点**:
```yaml
优点:
  - AI Agent 原生
  - 支持多 Agent 协作
  - 状态管理
  - 循环/条件工作流
  - 与 LLM 深度集成

缺点:
  - 较新 (2024)
  - 文档快速变化
  - 依赖 LangChain
```

**适用场景**: **AI 驱动的样本生成**

**示例 Graph**:
```python
from langgraph.graph import StateGraph, END
from typing import TypedDict

class AgentState(TypedDict):
    samples: list
    scan_results: list
    report: str

def generate_node(state):
    # LLM 生成样本
    samples = llm_generator.generate()
    return {"samples": samples}

def scan_node(state):
    # 扫描样本
    results = scanner.scan(state["samples"])
    return {"scan_results": results}

def report_node(state):
    # 生成报告
    report = generator.create(state["scan_results"])
    return {"report": report}

# 构建 Graph
workflow = StateGraph(AgentState)
workflow.add_node("generate", generate_node)
workflow.add_node("scan", scan_node)
workflow.add_node("report", report_node)

workflow.set_entry_point("generate")
workflow.add_edge("generate", "scan")
workflow.add_edge("scan", "report")
workflow.add_edge("report", END)

app = workflow.compile()
result = app.invoke({})
```

---

### 3.2 AutoGen (Microsoft)

**官网**: https://microsoft.github.io/autogen/  
**GitHub**: 25k+ stars  
**语言**: Python

**特点**:
```yaml
优点:
  - 多 Agent 对话
  - 代码执行
  - 工具使用
  - 人类反馈

缺点:
  - 资源消耗大
  - 调试困难
```

**适用场景**: 多 Agent 协作任务

---

### 3.3 CrewAI

**官网**: https://crewai.com/  
**GitHub**: 15k+ stars  
**语言**: Python

**特点**:
```yaml
优点:
  - 角色定义清晰
  - 任务导向
  - 易于理解
  - 快速上手

缺点:
  - 功能较简单
  - 定制性弱
```

**示例**:
```python
from crewai import Agent, Task, Crew

# 定义角色
generator_agent = Agent(
    role='恶意样本生成专家',
    goal='生成高质量恶意样本',
    backstory='安全研究员，精通各种攻击技术',
    verbose=True
)

scanner_agent = Agent(
    role='安全检测专家',
    goal='准确检测恶意样本',
    backstory='逆向工程师，擅长静态和动态分析',
    verbose=True
)

# 定义任务
generate_task = Task(
    description='生成 100 个 PowerShell 恶意样本',
    agent=generator_agent
)

scan_task = Task(
    description='扫描生成的样本并生成报告',
    agent=scanner_agent
)

# 组建 Crew
crew = Crew(
    agents=[generator_agent, scanner_agent],
    tasks=[generate_task, scan_task],
    verbose=2
)

result = crew.kickoff()
```

---

## 4️⃣ 自定义编排器

### 4.1 基于 GNU Make

**最简单，零依赖**

```makefile
# Makefile

.PHONY: all generate scan report clean

SAMPLES_DIR := output/samples
RULES_DIR := output/rules
REPORTS_DIR := reports

# 生成样本
generate-python:
	python3 -m generators.cli --language python --count 100 --output $(SAMPLES_DIR)/python/

generate-powershell:
	python3 -m generators.cli --language powershell --count 50 --output $(SAMPLES_DIR)/powershell/

generate: generate-python generate-powershell

# 扫描样本
scan: generate
	python3 multi_language_scanner.py $(SAMPLES_DIR)/ --report --output $(REPORTS_DIR)/

# 生成规则
rules: generate
	python3 -m rules.generator --samples $(SAMPLES_DIR)/ --output $(RULES_DIR)/

# 生成报告
report: scan
	python3 -m reports.generator --input $(REPORTS_DIR)/scan_results.json

# 完整流程
all: generate scan rules report

# 清理
clean:
	rm -rf $(SAMPLES_DIR)/* $(RULES_DIR)/* $(REPORTS_DIR)/*
```

**使用**:
```bash
make all          # 完整流程
make generate     # 仅生成样本
make scan         # 生成 + 扫描
make clean        # 清理
```

---

### 4.2 基于 Prefect (推荐)

**平衡灵活性和复杂度**

```python
# orchestrator/pipeline.py

from prefect import flow, task, get_run_logger
from prefect.task_runners import ConcurrentTaskRunner
from datetime import datetime
from pathlib import Path
import json

@task(retries=3, retry_delay_seconds=10)
def generate_samples(language: str, count: int, output_dir: str):
    """生成样本"""
    logger = get_run_logger()
    logger.info(f"Generating {count} {language} samples...")
    
    from generators.cli import generate
    samples = generate(language, count, output_dir)
    
    logger.info(f"Generated {len(samples)} samples")
    return samples

@task(retries=2)
def scan_samples(sample_dirs: list):
    """扫描样本"""
    logger = get_run_logger()
    logger.info(f"Scanning {len(sample_dirs)} directories...")
    
    from scanner.cli import scan_batch
    results = scan_batch(sample_dirs)
    
    logger.info(f"Scan complete: {results['total']} files")
    return results

@task
def generate_rules(samples_dir: str, output_dir: str):
    """生成检测规则"""
    logger = get_run_logger()
    logger.info("Generating detection rules...")
    
    from rules.generator import generate_rules
    rules = generate_rules(samples_dir, output_dir)
    
    logger.info(f"Generated {len(rules)} rules")
    return rules

@task
def create_report(scan_results: dict, rules: list, output_dir: str):
    """生成报告"""
    logger = get_run_logger()
    logger.info("Creating report...")
    
    from reports.generator import create_report
    report_path = create_report(scan_results, rules, output_dir)
    
    logger.info(f"Report saved to {report_path}")
    return report_path

@task
def notify_completion(report_path: str, webhook_url: str = None):
    """通知完成"""
    logger = get_run_logger()
    
    message = f"✅ 样本生成完成\n报告：{report_path}"
    
    if webhook_url:
        import requests
        requests.post(webhook_url, json={"text": message})
    
    logger.info("Notification sent")

@flow(task_runner=ConcurrentTaskRunner())
def sample_generation_pipeline(
    languages: dict = None,
    output_base: str = "output",
    notify: bool = True
):
    """
    样本生成完整流程
    
    Args:
        languages: {"python": 100, "powershell": 50, ...}
        output_base: 输出目录
        notify: 是否通知
    """
    if languages is None:
        languages = {
            "python": 100,
            "powershell": 50,
            "javascript": 50,
            "bash": 30,
        }
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    samples_base = Path(output_base) / "samples" / timestamp
    rules_dir = Path(output_base) / "rules" / timestamp
    reports_dir = Path(output_base) / "reports" / timestamp
    
    # 创建目录
    samples_base.mkdir(parents=True, exist_ok=True)
    
    # 并行生成多语言样本
    sample_tasks = []
    for lang, count in languages.items():
        output_dir = samples_base / lang
        sample_tasks.append(generate_samples(lang, count, str(output_dir)))
    
    sample_results = [t.result() for t in sample_tasks]
    sample_dirs = [str(samples_base / lang) for lang in languages.keys()]
    
    # 扫描样本
    scan_results = scan_samples(sample_dirs)
    
    # 生成规则
    rules = generate_rules(str(samples_base), str(rules_dir))
    
    # 生成报告
    report_path = create_report(scan_results, rules, str(reports_dir))
    
    # 通知
    if notify:
        from config import WEBHOOK_URL
        notify_completion(report_path, WEBHOOK_URL)
    
    return {
        "samples": sample_results,
        "scan": scan_results,
        "rules": rules,
        "report": report_path,
    }

if __name__ == "__main__":
    # 运行流程
    result = sample_generation_pipeline(
        languages={
            "python": 100,
            "powershell": 50,
            "javascript": 50,
            "go": 30,
        },
        output_base="output",
        notify=True
    )
    
    print(f"✅ 完成：{result['report']}")
```

**部署和调度**:
```bash
# 1. 安装 Prefect
pip install prefect

# 2. 启动 Prefect Server (可选)
prefect server start

# 3. 运行流程
python orchestrator/pipeline.py

# 4. 创建部署
prefect deployment build orchestrator/pipeline.py:sample_generation_pipeline \
  --name "daily-sample-gen" \
  --schedule "0 2 * * *" \
  --work-queue "sample-generation" \
  --apply

# 5. 查看运行
prefect deployment run sample-generation-pipeline/daily-sample-gen
```

**配置文件**:
```yaml
# orchestrator/config.yaml

pipeline:
  name: "sample-generation"
  version: "2.0"
  
languages:
  python: 100
  powershell: 50
  javascript: 50
  bash: 30
  go: 30
  batch: 20
  vbs: 20
