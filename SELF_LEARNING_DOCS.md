# 🧠 HROS 领域自学习能力

## 核心能力

### 1️⃣ 自动评估 (Self-Assessment)

**SWOT 分析**:
- **优势 (Strengths)**: 识别现有优势
- **劣势 (Weaknesses)**: 发现短板
- **机会 (Opportunities)**: 探索提升空间
- **威胁 (Threats)**: 预判风险

**评估维度**:
- 检测率、误报率、F1 Score
- 规则覆盖率 (按攻击类型)
- 性能指标 (扫描速度)
- 知识完整性

---

### 2️⃣ 自动探索 (Self-Exploration)

**探索方向**:
1. **规则覆盖盲点分析**
   - 检测率 <95% 的攻击类型
   - 未被覆盖的新攻击手法
   
2. **失败样本分析**
   - 漏报样本模式挖掘
   - 误报样本特征分析
   
3. **威胁情报扫描**
   - MITRE ATT&CK/ATLAS 更新
   - CVE 漏洞库
   - GitHub 安全研究
   - 安全博客/报告

---

### 3️⃣ 自动挖掘 (Self-Mining)

**挖掘内容**:
1. **规则优化方案**
   - 现有规则改进
   - 规则组合优化
   
2. **新攻击模式**
   - 从样本中提取特征
   - 从威胁情报中提取 TTPs
   
3. **新检测规则**
   - 自动生成 YARA 规则
   - 自动生成 Sigma 规则

---

### 4️⃣ 自动提升 (Self-Improvement)

**提升流程**:
```
评估 → 探索 → 挖掘 → 实施 → 验证
  ↓                              ↑
  └────────── 反馈循环 ──────────┘
```

**实施内容**:
- 添加新规则
- 优化现有规则
- 更新测试用例
- 运行验证测试

---

## 使用方式

### 运行完整自学习周期

```bash
python3 ros_self_learner.py
```

**输出**:
```
🧠 HROS 领域自学习引擎 - 完整周期
============================================================

🧠 步骤 1: 自动评估 (SWOT 分析)
  ✅ 优势：3 个
  ⚠️  劣势：2 个
  💡 机会：4 个
  📋 行动计划：2 项

🔍 步骤 2: 自动探索学习机会
  🔍 探索规则覆盖盲点...
    💡 发现：persistence 检测率 90% < 95%
  🔍 分析检测失败样本...
    💡 发现：Base64 编码绕过检测
  🔍 扫描威胁情报...
    💡 发现：MITRE ATLAS: 新增 AI 模型投毒攻击
  ✅ 共发现 5 个学习机会

⛏️ 步骤 3: 自动挖掘提升方案
  ✅ 优化规则：persistence_rules.yar
  ✅ 挖掘新模式：Base64+Exec 双层编码检测
  ✅ 创建检测规则：rule_20260328
  ✅ 挖掘完成

🚀 步骤 4: 自动提升实施
  ✅ 添加规则：Auto_20260328
  ✅ 优化规则：persistence_rules.yar
  🧪 运行测试验证...
  ✅ 测试验证通过

📊 自学习周期总结
============================================================
✅ 评估完成：3 个优势，2 个劣势
✅ 探索完成：5 个学习机会
✅ 挖掘完成：1 条新规则，1 条优化
✅ 提升完成：1 条添加，1 条优化
============================================================
```

---

### 单独运行某个步骤

```python
from ros_self_learner import DomainSelfLearner

learner = DomainSelfLearner()

# 只运行评估
assessment = learner.auto_assess()

# 只运行探索
opportunities = learner.auto_explore()

# 只运行挖掘
mined = learner.auto_mine(opportunities)

# 只运行提升
improvement = learner.auto_improve(mined)
```

---

## 知识源集成

### 内置知识源

| 知识源 | 类型 | 更新频率 |
|--------|------|---------|
| MITRE ATT&CK | TTPs | 实时 |
| MITRE ATLAS | AI 威胁 | 实时 |
| CVE Details | 漏洞 | 每日 |
| GitHub Security | 利用代码 | 实时 |

### 自定义知识源

```python
# 添加自定义知识源
THREAT_INTEL_SOURCES.append({
    'name': '自定义威胁情报',
    'url': 'https://your-intel-feed.com',
    'type': 'custom'
})
```

---

## 学习历史

### 历史记录位置

```
ros_meta/self_learning/
├── learning_history.json    # 完整历史记录
└── self_learning_report.json # 最新报告
```

### 查看历史

```python
import json
from pathlib import Path

history = json.loads(
    Path('ros_meta/self_learning/learning_history.json').read_text()
)

print(f"共 {len(history['opportunities'])} 个学习机会")
print(f"共 {len(history['assessments'])} 次评估")
```

---

## 自动化配置

### 定时自学习

```bash
# 每天凌晨 2 点运行自学习
echo "0 2 * * * cd /home/cdy/.openclaw/workspace/agent-security-skill-scanner-master && python3 ros_self_learner.py >> ros_logs/self_learning.log 2>&1" | crontab -
```

### 事件触发自学习

```python
# 检测率下降时触发自学习
if current_rate < baseline_rate - 2:
    learner.run_full_cycle()
```

---

## 与其他组件集成

### 与 ros_cycle.py 集成

```python
# 在 ros_cycle.py 的反思环节调用自学习
def step_reflect(before, after, tasks):
    # ... 原有逻辑 ...
    
    # 如果检测率下降，触发自学习
    if after['detection_rate'] < before['detection_rate']:
        learner = DomainSelfLearner()
        learner.run_full_cycle()
```

### 与 ros_eval.py 集成

```python
# 在评估基准中增加自学习维度
evaluator = RosEvaluator()
learner = DomainSelfLearner()

# 运行评估
metrics = evaluator.run_benchmark()

# 运行自学习
learning_result = learner.run_full_cycle()

# 综合报告
report = {
    'performance': metrics,
    'learning': learning_result
}
```

---

## 优势

### 对比手动优化

| 维度 | 手动 | 自学习 |
|------|------|--------|
| 响应速度 | 天/周级 | 分钟级 |
| 覆盖范围 | 有限 | 全面 |
| 持续性 | 间断 | 持续 |
| 知识积累 | 分散 | 系统化 |

### 自学习特点

- ✅ **主动性**: 主动发现问题，而非被动响应
- ✅ **持续性**: 7x24 小时持续学习
- ✅ **系统性**: SWOT→探索→挖掘→提升闭环
- ✅ **可追溯**: 完整历史记录

---

**版本**: v1.0  
**创建日期**: 2026-03-28  
**状态**: ✅ 已集成到 HROS 框架
