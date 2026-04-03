# 📐 规则与样本质量提升方案

**版本**: v1.0  
**日期**: 2026-03-29  
**目标**: 检测率 95.8% → 98%+, 误报率保持 0%

---

## 📊 当前资产盘点

### **规则库**
```
位置：rules/scanner_v3/yara/
文件数：17 个
大小：3.7MB
估计规则数：400-600 条

分类:
- persistence_rules.yar ✅ (已增强)
- data_exfil_rules.yar ✅ (新增，100% 检测率)
- bash_rules.yar
- credential_theft_rules.yar
- powershell_rules.yar
- privilege_escalation_rules.yar
- ... (其他)
```

### **样本库**
```
位置：samples/
大小：3.0MB
分类:
- benign/          - 良性样本
- malicious/       - 恶意样本 (8 大类)
- generated/       - 生成的样本
- high_fidelity/   - 高保真样本
- js_malicious/    - JS 恶意样本
- js_safe/         - JS 安全样本
- programming/     - 编程样本
- white/           - 白样本
```

---

## 🎯 质量提升策略

### **策略 1: 本地已有资源深度挖掘 (优先级 🔴 最高)**

#### **1.1 失败样本分析**
```bash
# 步骤
1. 从 benchmark 结果中提取未检出样本
2. 分析未检出原因
3. 针对性补充规则
4. 验证效果

# 预期收益
- 检测率 95.8% → 97%
- 工作量：1-2 天
```

#### **1.2 样本变体生成**
```bash
# 利用已有的样本生成器
expert_mode/samples/generators/

# 对每个成功检出的样本生成 5-10 个变体
- 变量重命名
- 代码重排序
- 添加噪声
- 等价替换

# 预期收益
- 样本库 710 → 2000+
- 提升模型泛化能力
```

#### **1.3 规则复用与优化**
```bash
# 检查现有规则
- 删除重复规则
- 合并相似规则
- 优化性能瓶颈

# 预期收益
- 规则性能提升 20%
- 减少误报
```

---

### **策略 2: 行业权威资源引进 (优先级 🟡 高)**

#### **2.1 MITRE ATLAS 威胁情报**
```
资源：https://atlas.mitre.org/
内容：AI/ML 攻击战术技术

实施:
1. 爬取 MITRE ATLAS 所有 AI 攻击模式
2. 映射到现有规则体系
3. 生成对应检测规则
4. 创建测试样本

预期收益:
- 新增 50-100 条规则
- 覆盖 AI 特有攻击类型
- 工作量：3-5 天
```

#### **2.2 OWASP Top 10 for LLM**
```
资源：https://owasp.org/www-project-top-10-for-large-language-model-applications/

实施:
1. 分析 OWASP LLM Top 10
2. 为每类威胁创建检测规则
3. 生成对应测试样本

预期收益:
- 新增 30-50 条规则
- 行业标准对齐
```

#### **2.3 开源威胁情报**
```
资源列表:
- GitHub Security Advisory
- NVD CVE Database
- VirusTotal Intelligence
- YARA Rules Repository (https://github.com/Neo23x0/signature-base)

实施:
1. 收集 AI/Agent 相关规则
2. 转换为统一格式
3. 测试验证
4. 合并到规则库

预期收益:
- 新增 100-200 条规则
- 借鉴成熟规则
```

---

### **策略 3: 理论规则方法论建设 (优先级 🟢 中)**

#### **3.1 攻击模式分类学**
```
目标：建立 AI Agent 攻击的系统分类

分类维度:
1. 按攻击阶段
   - 侦察 (Reconnaissance)
   - 武器化 (Weaponization)
   - 投递 (Delivery)
   - 利用 (Exploitation)
   - 安装 (Installation)
   - C2 通信 (Command & Control)
   - 目标行动 (Actions on Objectives)

2. 按攻击对象
   - 模型层 (Model Layer)
   - 数据层 (Data Layer)
   - 应用层 (Application Layer)
   - 基础设施层 (Infrastructure Layer)

3. 按 MITRE ATLAS
   - 初始访问 (TA0001)
   - 执行 (TA0002)
   - 持久化 (TA0003)
   - 特权提升 (TA0004)
   - 防御规避 (TA0005)
   - 凭证访问 (TA0006)
   - 发现 (TA0007)
   - 横向移动 (TA0008)
   - 收集 (TA0009)
   - C2 (TA0011)
   - 影响 (TA0040)

预期收益:
- 系统化规则体系
- 发现规则盲区
- 指导规则开发
```

#### **3.2 规则质量标准**
```
规则编写规范:
1. 命名规范
   - PERS_<Technique>_<Variant>
   - 例如：PERS_WMI_Process_v2

2. 元数据标准
   - severity: critical/high/medium/low
   - mitre: Txxxx.xxx
   - author: 作者名
   - date: 创建日期
   - description: 清晰描述
   - falsepositives: 已知误报场景
   - references: 参考链接

3. 测试要求
   - 至少 3 个恶意样本验证
   - 至少 5 个良性样本验证
   - 误报率 <1%

4. 性能要求
   - 单规则匹配时间 <10ms
   - 避免复杂正则

预期收益:
- 规则质量提升
- 维护成本降低
```

#### **3.3 样本质量标准**
```
样本分级:
- L1 (基础): 简单攻击模式，适合入门测试
- L2 (进阶): 包含绕过技术，适合进阶测试
- L3 (高级): 真实攻击场景，适合生产测试

样本多样性:
- 语言多样性：Python/JS/Shell/PS/Java/Go
- 平台多样性：Windows/Linux/macOS/Cloud
- 攻击类型多样性：覆盖 MITRE ATLAS 所有类别

样本标注:
- attack_type: 攻击类型
- mitre: MITRE 映射
- difficulty: L1/L2/L3
- source: 样本来源
- verified: 是否已验证检出

预期收益:
- 样本库质量提升
- 测试覆盖全面
```

---

## 🛠️ 实施计划

### **阶段 1: 本地优化 (Week 1-2, 现在进行)**
```
目标：检测率 95.8% → 97%

任务:
- [x] Data Exfil 优化 (90% → 100%)
- [ ] Persistence 优化 (90% → 98%)
- [ ] Credential Theft 优化 (100% 保持)
- [ ] 失败样本分析
- [ ] 样本变体生成 (710 → 1500)

交付物:
- 新增规则 50 条
- 新增样本 800 个
- 检测率 ≥97%
```

### **阶段 2: 行业资源引进 (Week 3-6)**
```
目标：检测率 97% → 98.5%

任务:
- [ ] MITRE ATLAS 规则转化 (50 条)
- [ ] OWASP LLM Top 10 规则 (30 条)
- [ ] GitHub Security 规则 (50 条)
- [ ] VirusTotal 规则学习 (20 条)
- [ ] 行业样本收集 (500 个)

交付物:
- 新增规则 150 条
- 新增样本 500 个
- 检测率 ≥98.5%
```

### **阶段 3: 方法论建设 (Week 7-10)**
```
目标：建立系统化规则体系

任务:
- [ ] AI Agent 攻击分类学 v1.0
- [ ] 规则编写规范 v1.0
- [ ] 样本质量标准 v1.0
- [ ] 规则质量审查流程
- [ ] 自动化测试框架

交付物:
- 标准文档 3 个
- 规则覆盖率 100%
- 误报率 <0.5%
```

---

## 📈 成功指标

| 指标 | 当前 | Week 2 | Week 6 | Week 10 |
|------|------|--------|--------|---------|
| **检测率** | 95.8% | 97% | 98.5% | 99% |
| **误报率** | 0% | <0.5% | <0.5% | <0.3% |
| **规则数** | ~600 | 650 | 800 | 1000+ |
| **样本数** | 710 | 1500 | 2000 | 3000+ |
| **规则覆盖率** | 60% | 75% | 90% | 100% |
| **性能 (p99)** | <50ms | <40ms | <30ms | <20ms |

---

## 🚀 立即执行 (今天)

### **任务 1: 失败样本分析 (2 小时)**
```bash
# 1. 提取未检出样本
python3 -c "
import json
data = json.load(open('benchmark_result_v3.json'))
# 分析 by_attack_type 中 detection_rate < 100% 的
print('需要优化的攻击类型:')
for k, v in data['by_attack_type'].items():
    if v['rate'] < 1.0:
        print(f'  {k}: {v[\"rate\"]*100:.1f}%')
"

# 2. 分析样本内容
# 3. 补充规则
# 4. 验证效果
```

### **任务 2: 样本变体生成 (3 小时)**
```bash
# 使用已有的样本生成器
cd expert_mode/samples/generators/
python3 sample_generator.py --count=500 --variations=5

# 验证生成的样本
python3 benchmark/benchmark_v3.py --rules rules/scanner_v3/yara/all_rules_v9.yar
```

### **任务 3: MITRE ATLAS 规则映射 (2 小时)**
```bash
# 1. 访问 https://atlas.mitre.org/
# 2. 导出所有 AI 攻击技术
# 3. 映射到现有规则
# 4. 识别规则盲区
```

---

## 💡 资源推荐

### **威胁情报源**
1. MITRE ATLAS - https://atlas.mitre.org/
2. OWASP LLM Top 10 - https://owasp.org/www-project-top-10-for-large-language-model-applications/
3. GitHub Security Advisory - https://github.com/advisories
4. NVD CVE - https://nvd.nist.gov/

### **规则资源**
1. YARA Rules - https://github.com/Neo23x0/signature-base
2. Sigma Rules - https://github.com/SigmaHQ/sigma
3. Detection Rules - https://github.com/elastic/detection-rules

### **样本资源**
1. Juliet Test Suite - https://samate.nist.gov/SARD/test-suites
2. VX Heaven - 恶意软件样本 (需申请)
3. theZoo - https://github.com/ytisf/theZoo

---

## 📊 周报告模板

```markdown
## 规则与样本质量周报 (Week X)

### 核心指标
- 检测率：XX% (↑/↓ X%)
- 误报率：X% (目标 <0.5%)
- 规则数：XXX 条 (新增 XX 条)
- 样本数：XXXX 个 (新增 XXX 个)

### 本周完成
- ✅ 任务 1
- ✅ 任务 2

### 下周计划
- [ ] 任务 3
- [ ] 任务 4

### 风险与问题
- ⚠️ 问题描述
```

---

**下一步**: 立即执行失败样本分析和样本变体生成，今天内将检测率提升至 97%+！
