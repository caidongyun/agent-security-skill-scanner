# 样本生成器 v2.0 - 任务拆分与编排工具调研

**时间**: 2026-03-25  
**目标**: 拆分任务 + 选择编排工具

---

## 📋 第一部分：任务拆分

### Epic 1: 样本生成器增强

#### Story 1.1: LLM 增强生成器 (P0 - Week 1-2)

```yaml
task_id: GEN-001
name: LLM 增强生成器
priority: P0
estimate: 3 days

subtasks:
  - id: GEN-001-1
    name: LLM 客户端封装
    estimate: 4h
    files:
      - generators/llm_client.py
    acceptance:
      - 支持 OpenAI/Qwen/本地模型
      - 统一的 API 接口
      - 错误处理和重试
  
  - id: GEN-001-2
    name: 提示词模板系统
    estimate: 6h
    files:
      - generators/prompts/
      - generators/prompt_templates.yaml
    acceptance:
      - 10+ 种变换类型模板
      - 支持变量替换
      - 支持多语言
  
  - id: GEN-001-3
    name: 语义保持验证
    estimate: 8h
    files:
      - generators/semantic_validator.py
    acceptance:
      - AST 相似度检查
      - 行为特征验证
      - 阈值可配置
  
  - id: GEN-001-4
    name: 集成测试
    estimate: 6h
    files:
      - tests/test_llm_generator.py
    acceptance:
      - 生成 100 个样本
      - 质量评分 75+
      - 多样性 60+
```

#### Story 1.2: 多态引擎 (P0 - Week 2-3)

```yaml
task_id: GEN-002
name: 多态引擎
priority: P0
estimate: 4 days

subtasks:
  - id: GEN-002-1
    name: 命名方案生成器
    estimate: 4h
    files:
      - obfuscation/naming_generator.py
    acceptance:
      - 5 种命名风格
      - 可自定义风格
      - 冲突检测
  
  - id: GEN-002-2
    name: 控制流随机化
    estimate: 8h
    files:
      - obfuscation/control_flow_random.py
    acceptance:
      - if/else 变换
      - loop 变换
      - 控制流等价验证
  
  - id: GEN-002-3
    name: 数据流混淆
    estimate: 6h
    files:
      - obfuscation/data_flow_obfuscate.py
    acceptance:
      - 变量重定向
      - 常量加密
      - 运行时解密
  
  - id: GEN-002-4
    name: 垃圾代码插入
    estimate: 4h
    files:
      - obfuscation/garbage_insert.py
    acceptance:
      - 死代码生成
      - 不改变语义
      - 可配置密度
```

#### Story 1.3: 供应链攻击场景 (P0 - Week 2-3)

```yaml
task_id: GEN-003
name: 供应链攻击场景
priority: P0
estimate: 5 days

subtasks:
  - id: GEN-003-1
    name: 依赖混淆模板
    estimate: 6h
    files:
      - scenarios/supply_chain/dependency_confusion.yaml
    acceptance:
      - npm/pip/gem 支持
      - 5 个变体
      - 检测规则
  
  - id: GEN-003-2
    name: Typosquatting 模板
    estimate: 4h
    files:
      - scenarios/supply_chain/typosquatting.yaml
    acceptance:
      - 4 种 typo 模式
      - 自动生成变体
      - 检测规则
  
  - id: GEN-003-3
    name: CI/CD 投毒模板
    estimate: 8h
    files:
      - scenarios/supply_chain/ci_cd_poisoning.yaml
    acceptance:
      - GitHub Actions
      - GitLab CI
      - Jenkins
      - 各 5 个变体
  
  - id: GEN-003-4
    name: Docker 镜像篡改
    estimate: 6h
    files:
      - scenarios/supply_chain/docker_tampering.yaml
    acceptance:
      - 基础镜像后