# 样本生成器 v2.0 - 实施路线图 (完整)

**版本**: v2.0.0  
**创建时间**: 2026-03-25  
**状态**: ✅ 完整设计

---

## 📋 Phase 2: 增强功能 (Week 3-4)

### Week 3: LLM 集成 + 多语言扩展

#### 任务清单

```
Day 1-3: LLM 生成器
  □ 实现 LLM 客户端封装 (支持 OpenAI/Qwen/本地模型)
  □ 实现提示词模板系统
  □ 实现语义保持验证
  □ 集成到生成流程

Day 4-5: 多语言扩展 - Go
  □ 实现 Go 语言样本生成器
  □ 创建 Go 攻击场景模板 (10+)
  □ 生成 Go 样本 (50+)

Day 6-7: 多语言扩展 - Ruby/PHP
  □ 实现 Ruby 样本生成器
  □ 实现 PHP 样本生成器
  □ 创建攻击场景模板 (各 10+)
  □ 生成样本 (各 50+)
```

**交付物**:
- [ ] `generators/llm_generator.py`
- [ ] `languages/go.py`
- [ ] `languages/ruby.py`
- [ ] `languages/php.py`
- [ ] LLM 提示词模板库
- [ ] 新增样本 200+

---

### Week 4: 攻击场景扩展

**目标**: 新增 7 类现代攻击场景

**任务清单**:
```
Day 1-2: 容器逃逸场景
  □ 研究容器逃逸技术 (Docker/K8s)
  □ 创建样本模板 (5+)
  □ 生成样本 (30+)

Day 3-4: 云凭据窃取场景
  □ 研究 AWS/Azure/GCP 凭据窃取
  □ 创建样本模板 (5+)
  □ 生成样本 (30+)

Day 5: CI/CD 投毒场景
  □ 研究 GitHub Actions/GitLab CI 投毒
  □ 创建样本模板 (3+)
  □ 生成样本 (20+)

Day 6: 模型投毒场景
  □ 研究 AI 模型投毒技术
  □ 创建样本模板 (3+)
  □ 生成样本 (20+)

Day 7: 区块链攻击场景
  □ 研究钱包/智能合约攻击
  □ 创建样本模板 (3+)
  □ 生成样本 (20+)
```

**交付物**:
- [ ] `scenarios/container_escape.yaml`
- [ ] `scenarios/cloud_credential.yaml`
- [ ] `scenarios/cicd_poisoning.yaml`
- [ ] `scenarios/model_poisoning.yaml`
- [ ] `scenarios/blockchain_attack.yaml`
- [ ] 新增样本 120+

---

## 📋 Phase 3: 高级功能 (Week 5-8)

### Week 5: 对抗生成器

**目标**: 实现生成器 vs 检测器对抗

**任务清单**:
```
Day 1-2: 检测器接口
  □ 定义检测器接口规范
  □ 实现 mock 检测器
  □ 集成真实检测器 (Scanner v3)

Day 3-5: 对抗算法实现
  □ 实现弱点分析器
  □ 实现针对性变换
  □ 实现迭代优化循环

Day 6-7: 测试与优化
  □ 运行对抗测试
  □ 收集绕过样本
  □ 分析检测盲区
```

**交付物**:
- [ ] `generators/adversarial_generator.py`
- [ ] 检测器接口定义
- [ ] 对抗测试报告
- [ ] 高难度样本库 (50+)

---

### Week 6: 跨语言移植

**目标**: 实现跨语言攻击逻辑移植

**任务清单**:
```
Day 1-3: 移植规则定义
  □ 定义 Python→PowerShell 规则
  □ 定义 Python→JavaScript 规则
  □ 定义 Python→Go 规则

Day 4-5: 移植器实现
  □ 实现 AST 解析器
  □ 实现代码映射引擎
  □ 实现目标语言生成

Day 6-7: 验证与测试
  □ 验证功能等价性
  □ 批量移植测试
  □ 生成多语言样本
```

**交付物**:
- [ ] `generators/cross_language.py`
- [ ] 跨语言移植规则库
- [ ] 多语言样本集 (100+)

---

### Week 7: 自动化测试集成

**目标**: 实现 CI/CD 自动化测试

**任务清单**:
```
Day 1-2: 测试框架
  □ 配置 pytest 测试框架
  □ 编写单元测试
  □ 编写集成测试

Day 3-4: CI 配置
  □ 编写 GitHub Actions 配置
  □ 配置自动化触发
  □ 配置报告生成

Day 5-7: 质量门禁
  □ 配置质量阈值检查
  □ 配置检测率验证
  □ 配置性能测试
```

**交付物**:
- [ ] `testing/` 测试套件
- [ ] `.github/workflows/ci.yml`
- [ ] 测试覆盖率报告 (>85%)
- [ ] CI/CD 流水线

---

### Week 8: Web 界面 + 文档

**目标**: 完成 Web 界面和完整文档

**任务清单**:
```
Day 1-3: Web 界面
  □ 实现 Flask 后端 API
  □ 实现前端界面
  □ 集成生成流程

Day 4-5: API 服务
  □ 实现 RESTful API
  □ 编写 API 文档
  □ 配置认证授权

Day 6-8: 文档完善
  □ 编写用户文档
  □ 编写开发文档
  □ 编写 API 文档
  □ 编写示例教程
```

**交付物**:
- [ ] `web/` Web 界面
- [ ] `api/` API 服务
- [ ] 完整文档体系
- [ ] 示例教程 (10+)

---

## 📊 预期成果汇总

### 样本库增长

| 阶段 | 新增样本 | 累计样本 | 语言覆盖 | 场景覆盖 |
|------|---------|---------|---------|---------|
| **当前** | - | 710 | 4 | 8 |
| **Phase 1** | 200 | 910 | 4 | 8 |
| **Phase 2** | 320 | 1230 | 7 | 12 |
| **Phase 3** | 270 | 1500 | 8 | 15 |

### 功能完成度

| 功能模块 | Phase 1 | Phase 2 | Phase 3 |
|---------|---------|---------|---------|
| 基础生成器 | ✅ | ✅ | ✅ |
| 质量评估 | ✅ | ✅ | ✅ |
| LLM 增强 | - | ✅ | ✅ |
| 多语言支持 | - | ✅ (7) | ✅ (8) |
| 场景扩展 | - | ✅ (12) | ✅ (15) |
| 对抗生成 | - | - | ✅ |
| 跨语言移植 | - | - | ✅ |
| 自动化测试 | - | - | ✅ |
| Web 界面 | - | - | ✅ |

---

## 🛠️ 快速启动指南

### 立即开始 (Phase 1)

```bash
# 1. 创建项目目录
cd ~/.openclaw/workspace/agent-security-skill-scanner-master
mkdir -p sample-generator-v2
cd sample-generator-v2

# 2. 创建目录结构
mkdir -p generators languages scenarios rules quality metadata \
         testing cli utils output/{samples,rules,reports,metadata}

# 3. 创建基础文件
cat > requirements.txt << 'EOF'
PyYAML>=6.0
networkx>=2.8
astpretty>=3.0
openai>=1.0.0
pytest>=7.2.0
pytest-cov>=4.0.0
tqdm>=4.64.0
EOF

# 4. 创建核心模块
touch generators/__init__.py
touch generators/base_generator.py
# ... (按设计文档实现)

# 5. 运行测试
python3 -m pytest testing/ -v
```

---

## 📈 成功指标

### 短期 (Phase 1 完成)

- [ ] 基础生成器可用
- [ ] 质量评分系统运行
- [ ] 生成样本 200+
- [ ] 单元测试覆盖率 >80%

### 中期 (Phase 2 完成)

- [ ] LLM 生成器集成
- [ ] 支持 7 种语言
- [ ] 样本库 1200+
- [ ] 质量评分 75+ 占比 >80%

### 长期 (Phase 3 完成)

- [ ] 对抗生成可用
- [ ] 支持 8 种语言
- [ ] 样本库 1500+
- [ ] CI/CD 自动化
- [ ] Web 界面可用

---

## 🔗 相关文档

- `SAMPLE_GENERATOR_V2_DESIGN.md` - 完整架构设计
- `SAMPLE_GENERATOR_V2_RULES.md` - 规则体系设计
- `ML_TRAINING_PLAN.md` - ML 模型训练计划
- `RELEASE_CHECKLIST.md` - 发布检查清单

---

**设计完成时间**: 2026-03-25  
**下一步**: 开始 Phase 1 实施

🚀 **开始构建下一代样本生成器！**
