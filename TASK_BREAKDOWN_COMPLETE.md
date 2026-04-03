# 样本生成器 v2.0 - 完整任务拆分

**时间**: 2026-03-25  
**总工作量**: 约 120-160 小时  
**周期**: 8 周 (Phase 1-3)

---

## 📊 任务总览

### Epic 分解

```
样本生成器 v2.0
├── Epic 1: 样本生成器增强 (45h)
├── Epic 2: 扫描器规则增强 (35h)
├── Epic 3: 编排器实现 (25h)
├── Epic 4: 测试与质量 (20h)
└── Epic 5: 文档与部署 (15h)
```

---

## Epic 1: 样本生成器增强 (45h)

### Story 1.1: LLM 增强生成器 (12h)

| Task ID | 任务 | 估算 | 优先级 | 依赖 |
|---------|------|------|--------|------|
| GEN-001-1 | LLM 客户端封装 | 4h | P0 | - |
| GEN-001-2 | 提示词模板系统 | 6h | P0 | GEN-001-1 |
| GEN-001-3 | 语义保持验证 | 8h | P0 | GEN-001-2 |
| GEN-001-4 | 集成测试 | 6h | P0 | GEN-001-3 |

**文件清单**:
```
generators/
├── llm_client.py              # LLM 客户端
├── prompts/
│   ├── __init__.py
│   ├── templates.yaml         # 提示词模板
│   └── transformer.py         # 模板渲染
└── semantic_validator.py      # 语义验证
```

**验收标准**:
- [ ] 支持 3 种 LLM (OpenAI/Qwen/本地)
- [ ] 10+ 种变换模板
- [ ] 生成 100 个样本，质量评分 75+
- [ ] 多样性评分 60+

---

### Story 1.2: 多态引擎 (14h)

| Task ID | 任务 | 估算 | 优先级 | 依赖 |
|---------|------|------|--------|------|
| GEN-002-1 | 命名方案生成器 | 4h | P0 | - |
| GEN-002-2 | 控制流随机化 | 8h | P0 | GEN-002-1 |
| GEN-002-3 | 数据流混淆 | 6h | P0 | GEN-002-2 |
| GEN-002-4 | 垃圾代码插入 | 4h | P1 | GEN-002-3 |

**文件清单**:
```
obfuscation/
├── naming_generator.py        # 命名生成
├── control_flow_random.py     # 控制流随机
├── data_flow_obfuscate.py     # 数据流混淆
└── garbage_insert.py          # 垃圾代码
```

**验收标准**:
- [ ] 5 种命名风格
- [ ] 控制流变换 10+ 种
- [ ] 绕过率提升 30%+

---

### Story 1.3: 供应链攻击场景 (10h)

| Task ID | 任务 | 估算 | 优先级 | 依赖 |
|---------|------|------|--------|------|
| GEN-003-1 | 依赖混淆模板 | 6h | P0 | - |
| GEN-003-2 | Typosquatting 模板 | 4h | P0 | - |
| GEN-003-3 | CI/CD 投毒模板 | 8h | P0 | GEN-003-1 |
| GEN-003-4 | Docker 镜像篡改 | 6h | P1 | GEN-003-3 |

**文件清单**:
```
scenarios/
└── supply_chain/
    ├── dependency_confusion.yaml
    ├── typosquatting.yaml
    ├── ci_cd_poisoning.yaml
    └── docker_tampering.yaml
```

**验收标准**:
- [ ] 4 种攻击场景
- [ ] 每场景 5+ 变体
- [ ] 配套检测规则

---

### Story 1.4: 新语言支持 (9h)

| Task ID | 任务 | 估算 | 优先级 | 依赖 |
|---------|------|------|--------|------|
| GEN-004-1 | Go 语言生成器 | 6h | P0 | - |
| GEN-004-2 | Kubernetes YAML | 6h | P0 | - |
| GEN-004-3 | Terraform HCL | 4h | P1 | GEN-004-2 |
| GEN-004-4 | Swift/AppleScript | 6h | P1 | - |

**文件清单**:
```
languages/
├── go.py
├── kubernetes.py
├── terraform.py
└── swift.py
```

**验收标准**:
- [ ] 每语言 50+ 样本
- [ ] 配套检测规则
- [ ] 质量评分 70+

---

## Epic 2: 扫描器规则增强 (35h)

### Story 2.1: YARA 规则优化 (10h)

| Task ID | 任务 | 估算 | 优先级 | 依赖 |
|---------|------|------|--------|------|
| SCAN-001-1 | 规则模板系统 | 6h | P0 | - |
| SCAN-001-2 | 自动规则生成 | 8h | P0 | SCAN-001-1 |
| SCAN-001-3 | 规则优化压缩 | 6h | P0 | SCAN-001-2 |
| SCAN-001-4 | 规则验证测试 | 4h | P0 | SCAN-001-3 |

**文件清单**:
```
rules/
├── yara/
│   ├── templates.yaml
│   ├── generator.py
│   └── optimizer.py
└── tests/
    └── test_yara_rules.py
```

**验收标准**:
- [ ] 规则生成自动化 80%
- [ ] 规则数量 800+
- [ ] 检测率 98%+
- [ ] 误报率 <2%

---

### Story 2.2: Sigma 规则增强 (8h)

| Task ID | 任务 | 估算 | 优先级 | 依赖 |
|---------|------|------|--------|------|
| SCAN-002-1 | Sigma 规则库扩展 | 6h | P0 | - |
| SCAN-002-2 | 运行时检测 | 8h | P0 | SCAN-002-1 |
| SCAN-002-3 | 日志关联分析 | 6h | P1 | SCAN-002-2 |

**文件清单**:
```
rules/
└── sigma/
    ├── runtime_detection.py
    └── log_correlation.py
```

---

### Story 2.3: ML 增强检测 (12h)

| Task ID | 任务 | 估算 | 优先级 | 依赖 |
|---------|------|------|--------|------|
| SCAN-003-1 | 特征工程优化 | 8h | P0 | - |
| SCAN-003-2 | 模型训练管道 | 10h | P0 | SCAN-003-1 |
| SCAN-003-3 | 模型评估验证 | 6h | P0 | SCAN-003-2 |
| SCAN-003-4 | 模型部署集成 | 8h | P0 | SCAN-003-3 |

**文件清单**:
```
ml/
├── feature_engineering.py
├── train.py
├── evaluate.py
└── deploy.py
```

**验收标准**:
- [ ] 特征维度 40+
- [ ] 检测率 98%+
- [ ] 推理速度