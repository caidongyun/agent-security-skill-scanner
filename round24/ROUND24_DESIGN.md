# Round 24: 机器学习增强检测 - 设计文档

**状态**: 🔄 规划中  
**启动时间**: 2026-03-24 21:40  
**预计完成**: 2-3 小时

---

## 🎯 目标

使用机器学习技术增强现有检测能力，提高泛化能力和未知威胁检测。

---

## 📋 核心需求

### 功能需求

| 需求 | 说明 | 优先级 |
|------|------|--------|
| **特征提取** | 从代码中提取 ML 特征 | 🔴 高 |
| **模型训练** | 基于 695 样本训练分类器 | 🔴 高 |
| **预测接口** | 集成到多语言扫描器 | 🔴 高 |
| **模型持久化** | 保存/加载训练好的模型 | 🔴 高 |
| **可解释性** | 解释为什么判定为恶意 | 🟡 中 |

### 质量要求

- **准确率**: ≥95% (交叉验证)
- **召回率**: ≥95% (恶意样本检出)
- **误报率**: <3% (安全样本误判)
- **预测速度**: <10ms/文件
- **模型大小**: <50MB

---

## 🏗️ 技术架构

### ML 增强架构

```
代码文件
    ↓
特征提取 (词法 + 语法 + 语义)
    ↓
[ML 模型预测]
    ↓
传统检测器 (规则 +AST+ 行为)
    ↓
融合决策 (加权投票)
    ↓
最终结果
```

### 特征工程

#### 1. 词法特征 (Lexical Features)

```python
- API 调用频率 (危险 API / 总 API)
- 字符串熵值 (检测混淆/编码)
- 代码行数/字符数
- 注释比例
- 特殊字符密度
- 关键字密度 (eval, exec, system 等)
```

#### 2. 语法特征 (Syntactic Features)

```python
- AST 节点类型分布
- AST 深度/宽度
- 控制流复杂度
- 嵌套深度
- 函数/方法数量
- 参数数量统计
```

#### 3. 语义特征 (Semantic Features)

```python
- 数据流模式
- 控制流模式
- 危险操作序列
- 行为意图评分
- MITRE 技术覆盖数
```

#### 4. 统计特征 (Statistical Features)

```python
- 词频分布 (TF-IDF)
- N-gram 特征
- 操作码序列
- 字节熵值
```

---

## 🤖 模型选择

### 候选模型对比

| 模型 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| **Random Forest** | 可解释性好，不易过拟合 | 对高维稀疏特征效果一般 | 基线模型 |
| **XGBoost** | 准确率高，支持缺失值 | 调参复杂 | 主力模型 |
| **LightGBM** | 训练速度快，内存占用低 | 小样本可能过拟合 | 大规模数据 |
| **Neural Network** | 特征学习能力强 | 需要大量数据，黑盒 | 深度特征 |
| **SVM** | 小样本效果好 | 大规模数据慢 | 二分类基线 |

### 推荐方案

**XGBoost + LightGBM 融合**

- 训练速度快
- 准确率高
- 支持特征重要性
- 可解释性较好

---

## 📊 数据集

### 训练集构成

| 类别 | 数量 | 来源 |
|------|------|------|
| **恶意样本** | 657 | Scanner V3 样本库 |
| **安全样本** | 38 | Scanner V3 样本库 |
| **额外安全样本** | ~300 | 开源项目 (requests, flask 等) |
| **总计** | ~995 | 多来源 |

### 数据增强

```python
# 恶意样本变体生成
- 变量重命名
- 字符串编码 (Base64/Hex)
- 控制流平坦化
- 插入无害代码 (数据增强)

# 安全样本变体生成
- 不同编码风格
- 不同库的使用
- 不同功能场景
```

### 数据集划分

```
训练集：70% (~700 样本)
验证集：15% (~150 样本)
测试集：15% (~150 样本)
```

---

## 🚀 实施步骤

### Step 1: 特征提取器实现 (40 分钟)

```python
# features/
├── lexical_features.py      # 词法特征
├── syntactic_features.py    # 语法特征 (AST)
├── semantic_features.py     # 语义特征
├── statistical_features.py  # 统计特征
└── feature_extractor.py     # 统一特征提取
```

### Step 2: 模型训练 (30 分钟)

```python
# ml/
├── train.py                 # 训练脚本
├── model.py                 # 模型定义
├── evaluate.py              # 评估脚本
└── models/                  # 保存的模型
    └── scanner_v3_ml.model
```

### Step 3: 集成到扫描器 (20 分钟)

```python
# 修改 multi_language_scanner.py
class MultiLanguageScanner:
    def __init__(self):
        self.ml_model = MLClassifier()  # 新增
    
    def scan_file(self, file_path: str):
        # 传统检测
        traditional_result = self.traditional_detect(...)
        
        # ML 预测
        ml_result = self.ml_model.predict(...)
        
        # 融合决策
        final_result = self.fuse_results(traditional_result, ml_result)
```

### Step 4: 测试验证 (30 分钟)

```python
# 测试内容
- 准确率/召回率/F1 分数
- 交叉验证 (5-fold)
- 混淆矩阵
- ROC 曲线
- 特征重要性分析
```

---

## 📈 验收标准

### 模型性能

- [ ] 准确率 ≥95%
- [ ] 召回率 ≥95%
- [ ] F1 分数 ≥95%
- [ ] AUC ≥0.98
- [ ] 误报率 <3%

### 性能指标

- [ ] 预测速度 <10ms/文件
- [ ] 模型大小 <50MB
- [ ] 训练时间 <30 分钟
- [ ] 内存占用 <500MB

### 功能完整性

- [ ] 特征提取器实现
- [ ] 模型训练脚本
- [ ] 模型评估报告
- [ ] 集成到多语言扫描器
- [ ] 可解释性报告 (特征重要性)

---

## 🎯 预期效果

### 检测能力提升

| 场景 | 传统检测 | ML 增强 | 提升 |
|------|----------|--------|------|
| **已知攻击** | 100% | 100% | - |
| **未知变体** | 70-80% | 90-95% | +20% |
| **混淆代码** | 60-70% | 85-90% | +25% |
| **0-day 攻击** | 50-60% | 75-85% | +25% |

### 误报率控制

| 样本类型 | 传统检测 | ML 增强 | 改进 |
|----------|----------|--------|------|
| 系统脚本 | 0% | 0% | - |
| 开源项目 | 1-2% | <1% | -50% |
| 企业脚本 | 2-3% | <2% | -33% |

---

## 📊 特征重要性分析 (预期)

```python
# Top 20 重要特征 (预期)
1. dangerous_api_count          - 危险 API 调用次数
2. string_entropy               - 字符串熵值
3. ast_depth                    - AST 深度
4. eval_exec_ratio              - eval/exec 使用频率
5. encoded_string_count         - 编码字符串数量
6. control_flow_complexity      - 控制流复杂度
7. suspicious_import_count      - 可疑导入数量
8. obfuscation_score            - 混淆评分
9. data_flow_risk               - 数据流风险评分
10. behavior_pattern_match      - 行为模式匹配度
11. ngram_anomaly               - N-gram 异常度
12. special_char_density        - 特殊字符密度
13. nested_depth                - 嵌套深度
14. function_count              - 函数数量
15. parameter_count             - 参数数量
16. comment_ratio               - 注释比例
17. line_count                  - 代码行数
18. unique_tokens               - 唯一 token 数
19. api_sequence_entropy        - API 序列熵
20. mitre_technique_count       - MITRE 技术覆盖数
```

---

## 🛠️ 技术栈

### Python 库

```
xgboost>=1.7.0
lightgbm>=3.3.0
scikit-learn>=1.2.0
joblib>=1.2.0       # 模型持久化
numpy>=1.23.0
pandas>=1.5.0
```

### 可选增强

```
shap>=0.41.0        # 模型可解释性
matplotlib>=3.6.0   # 可视化
seaborn>=0.12.0     # 统计可视化
```

---

## 📁 文件结构

```
round24/
├── ROUND24_DESIGN.md           # 设计文档 (本文件)
├── features/
│   ├── lexical_features.py     # 词法特征提取
│   ├── syntactic_features.py   # 语法特征提取
│   ├── semantic_features.py    # 语义特征提取
│   ├── statistical_features.py # 统计特征提取
│   └── feature_extractor.py    # 统一特征提取器
├── ml/
│   ├── train.py                # 模型训练
│   ├── model.py                # 模型定义
│   ├── evaluate.py             # 模型评估
│   └── models/                 # 保存的模型
├── integration/
│   └── ml_classifier.py        # ML 分类器 (集成到扫描器)
├── test_ml_detection.py        # ML 检测测试
├── reports/
│   └── ROUND24_REPORT.md       # 完成报告
└── ROUND24_COMPLETION.md       # 完成检查清单
```

---

## 🎓 创新点

### 1. 融合检测

```
最终决策 = 0.6 × 传统检测 + 0.4 × ML 预测

优势:
- 保留规则检测的可解释性
- 增加 ML 的泛化能力
- 降低单一方法的误报
```

### 2. 多语言特征共享

```
Python/JS/Shell/PowerShell → 统一特征空间

优势:
- 跨语言知识迁移
- 减少重复训练
- 提高小语种效果
```

### 3. 增量学习

```
新样本 → 增量更新模型 → 无需重新训练

优势:
- 持续改进
- 适应新威胁
- 降低维护成本
```

---

## ⚠️ 风险与挑战

### 挑战 1: 样本不平衡

**问题**: 恶意样本 657 vs 安全样本 38

**解决方案**:
- SMOTE 过采样
- 欠采样安全样本
- 类别权重调整
- 收集更多安全样本

### 挑战 2: 特征维度灾难

**问题**: 特征过多导致过拟合

**解决方案**:
- 特征选择 (基于重要性)
- PCA 降维
- 正则化 (L1/L2)
- 交叉验证

### 挑战 3: 模型可解释性

**问题**: ML 模型是黑盒

**解决方案**:
- SHAP 值分析
- 特征重要性排序
- 决策树可视化
- 保留传统检测作为解释依据

---

**准备启动 Round 24！** 🚀

下一步：实现特征提取器 → 训练模型 → 集成测试
