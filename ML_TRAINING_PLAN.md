# ML 模型训练计划

**创建时间**: 2026-03-25  
**优先级**: 中（规则检测已可用，ML 为增强功能）

---

## 📊 现状

| 项目 | 状态 | 说明 |
|------|------|------|
| 训练脚本 | ✅ 就绪 | `round24/ml/train.py` |
| 特征提取器 | ✅ 就绪 | `round24/features/feature_extractor.py` |
| 样本数据 | ✅ 710 个 | 恶意 + 良性样本 |
| 模型文件 | ❌ 缺失 | 需要训练 |
| 依赖包 | ⚠️ 待安装 | xgboost, lightgbm, scikit-learn |

---

## 🎯 训练目标

| 指标 | 目标值 |
|------|--------|
| 检测率 | ≥98% |
| 误报率 | <2% |
| 未知变体检测提升 | +50% |
| 单文件扫描延迟 | <1ms |

---

## 📋 训练步骤

### 1. 安装依赖

```bash
cd ~/.openclaw/workspace/agent-security-skill-scanner-master

pip install xgboost lightgbm scikit-learn pandas numpy joblib
```

### 2. 特征提取

```bash
cd round24/features
python3 feature_extractor.py ../../samples/ --output dataset.csv
```

**输出**: `dataset.csv` (包含 710 个样本 × 27 个特征)

### 3. 训练模型

```bash
cd ../ml
mkdir -p models
python3 train.py --data ../features/dataset.csv --output models/scanner_v3_ml_fusion.pkl
```

**输出**: `models/scanner_v3_ml_fusion.pkl` (融合模型)

### 4. 验证模型

```bash
python3 evaluate.py --model models/scanner_v3_ml_fusion.pkl --test-data ../features/test.csv
```

**预期输出**:
- 检测率 ≥98%
- 误报率 <2%
- AUC-ROC ≥0.99

### 5. 集成到扫描器

```bash
# 修改 config.yaml
ml:
  enabled: true
  model_path: "round24/ml/models/scanner_v3_ml_fusion.pkl"
  threshold: 0.5
  weight: 0.4
```

---

## 🔧 训练脚本说明

### `train.py` 核心逻辑

```python
# 1. 加载数据
df = pd.read_csv(dataset_path)

# 2. 特征工程
X = df[feature_columns]
y = df['label']

# 3. 数据集划分 (70/15/15)
X_train, X_val, X_test = train_test_split(...)

# 4. 训练 XGBoost
xgb_model = XGBClassifier(**xgb_params)
xgb_model.fit(X_train, y_train)

# 5. 训练 LightGBM
lgb_model = LGBMClassifier(**lgb_params)
lgb_model.fit(X_train, y_train)

# 6. 融合模型 (加权平均)
ensemble = {
    'xgboost': xgb_model,
    'lightgbm': lgb_model,
    'weights': [0.5, 0.5]
}

# 7. 保存模型
joblib.dump(ensemble, output_path)
```

### 27 个特征维度

详见 `round24/features/feature_extractor.py`:
- AST 结构特征 (10 个)
- 代码行为特征 (7 个)
- 字符串特征 (5 个)
- 文件操作特征 (3 个)
- 统计特征 (2 个)

---

## ⏱️ 预计时间

| 步骤 | 预计时间 |
|------|---------|
| 安装依赖 | 2-3 分钟 |
| 特征提取 | 1-2 分钟 (710 个样本) |
| 模型训练 | 2-3 分钟 |
| 模型验证 | 30 秒 |
| **总计** | **5-8 分钟** |

---

## 📁 输出文件

```
round24/ml/
├── models/
│   ├── scanner_v3_ml_fusion.pkl  # 融合模型（主）
│   ├── scanner_v3_xgboost.pkl    # XGBoost（备份）
│   └── scanner_v3_lightgbm.pkl   # LightGBM（备份）
├── reports/
│   ├── training_report.md        # 训练报告
│   └── evaluation_metrics.json   # 评估指标
└── train.py                      # 训练脚本
```

---

## ✅ 验证清单

训练完成后执行:

```bash
# 1. 模型文件存在
ls -lh round24/ml/models/scanner_v3_ml_fusion.pkl

# 2. 测试扫描（恶意样本）
python3 multi_language_scanner.py samples/malicious/ --model round24/ml/models/scanner_v3_ml_fusion.pkl

# 3. 测试扫描（良性样本）
python3 multi_language_scanner.py samples/benign/ --model round24/ml/models/scanner_v3_ml_fusion.pkl

# 4. 查看报告
cat reports/ml_evaluation_report.md
```

---

## 🚨 常见问题

### Q1: 依赖安装失败
```bash
# 使用国内镜像
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple xgboost lightgbm scikit-learn
```

### Q2: 训练数据不足
```bash
# 检查样本数量
find samples/ -name "*.py" | wc -l
# 至少需要 100+ 样本
```

### Q3: 模型效果不佳
```bash
# 调整超参数
# 编辑 train.py，修改 xgb_params 和 lgb_params
# 增加训练轮数 (n_estimators)
```

---

## 📝 后续优化

1. **增量训练**: 新样本出现时，无需重新训练全部数据
2. **特征优化**: 根据误报案例调整特征权重
3. **模型压缩**: 使用 ONNX 格式加速推理
4. **多语言扩展**: 支持 JS/Shell/PowerShell 的专用模型

---

## 🔗 相关文档

- `round24/features/feature_extractor.py` - 特征提取器
- `round24/ml/train.py` - 训练脚本
- `round24/ROUND24_REPORT.md` - Round 24 完整报告
- `FUNCTIONAL_SCAN_REPORT.md` - 功能扫描报告

---

**执行命令** (一键训练):
```bash
cd ~/.openclaw/workspace/agent-security-skill-scanner-master
./train_ml.sh  # 待创建
```
