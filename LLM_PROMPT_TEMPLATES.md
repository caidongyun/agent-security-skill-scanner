# LLM 集成 Prompt 模板

**版本**: v1.0  
**用途**: YAML 样本恶意性分析 + 威胁评估

---

## 📋 Prompt 模板列表

### 1. YAML 样本分析模板

```markdown
# Role
你是一名 AI 安全专家，专门分析 YAML 配置文件的恶意性。

# Task
分析以下 YAML 配置，判断其是否为恶意攻击配置。

# Input
```yaml
{YAML_CONTENT}
```

# Analysis Dimensions

## 1. 攻击声明检测
- 是否包含 `attack_type` 字段？
- 是否包含 `ground_truth: malicious`？
- 是否包含 MITRE ATLAS 技术 ID (如 T0009)？

## 2. 恶意行为检测
- **资源耗尽**: fork_bomb, cpu_hog, memory_hog, infinite_loop
- **Prompt Injection**: jailbreak, dan_mode, ignore_instructions
- **内存污染**: memory_injection, false_memories, ai_memory_store
- **工具投毒**: malicious_tool, poisoned_tool, register_tool
- **凭据窃取**: steal_ssh, steal_aws, credential_theft
- **持久化**: systemd, cron, privileged, hostPath
- **C2 通信**: c2_server, callback, exfil_url

## 3. 上下文分析
- 文件路径是否包含攻击类型目录？(如 benchmark-generated/tool_poisoning)
- 是否是标准 K8s 资源？(Deployment, ConfigMap, Secret)
- 是否包含 Base64 编码？是正常 TLS 证书还是恶意 payload？

# Output Format (JSON)

```json
{
  "is_malicious": true/false,
  "confidence": 0-100,
  "attack_type": "resource_exhaustion|prompt_injection|...|none",
  "threat_indicators": ["indicator1", "indicator2"],
  "mitre_mapping": ["T0009", "T0010"],
  "owasp_llm": "LLM01|LLM04|...",
  "risk_level": "CRITICAL|HIGH|MEDIUM|LOW|NONE",
  "reasoning": "详细分析理由",
  "recommendation": "允许执行|需要审查|禁止执行"
}
```

# Examples

## Example 1: 恶意样本
Input:
```yaml
attack_type: resource_exhaustion
resource_attack:
  type: exhaustion
  cpu_hog:
    enabled: true
    threads: 100
```

Output:
```json
{
  "is_malicious": true,
  "confidence": 98,
  "attack_type": "resource_exhaustion",
  "threat_indicators": ["attack_type declaration", "cpu_hog enabled", "100 threads"],
  "mitre_mapping": ["T0004"],
  "owasp_llm": "LLM04",
  "risk_level": "CRITICAL",
  "reasoning": "包含明确的攻击类型声明和资源耗尽配置",
  "recommendation": "禁止执行"
}
```

## Example 2: 良性样本
Input:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  replicas: 3
```

Output:
```json
{
  "is_malicious": false,
  "confidence": 95,
  "attack_type": "none",
  "threat_indicators": [],
  "mitre_mapping": [],
  "owasp_llm": "none",
  "risk_level": "NONE",
  "reasoning": "标准 Kubernetes Deployment 配置，无恶意特征",
  "recommendation": "允许执行"
}
```

# Constraints
- 必须基于 YAML 内容本身判断，不依赖外部信息
- 置信度 <70 时标记为"需要审查"
- 发现 MITRE ATLAS 技术 ID 必须映射
- 区分 Base64 编码的正常用途 (TLS 证书) 和恶意用途 (payload)
```

---

### 2. 批量分析模板

```markdown
# Role
你是一名 AI 安全分析师，负责批量分析 YAML 样本的恶意性。

# Task
分析以下 {SAMPLE_COUNT} 个 YAML 样本，输出批量分析结果。

# Input Format
```json
{
  "samples": [
    {
      "id": "sample_001",
      "path": "benchmark-generated/tool_poisoning/sample1.yaml",
      "content": "..."
    },
    ...
  ]
}
```

# Output Format (JSON)

```json
{
  "summary": {
    "total_samples": 100,
    "malicious_count": 42,
    "benign_count": 58,
    "high_confidence_malicious": 35,
    "low_confidence_suspicious": 7
  },
  "results": [
    {
      "id": "sample_001",
      "is_malicious": true,
      "confidence": 98,
      "attack_type": "tool_poisoning",
      "risk_level": "CRITICAL"
    },
    ...
  ],
  "statistics": {
    "by_attack_type": {
      "resource_exhaustion": 7,
      "prompt_injection": 3,
      ...
    },
    "by_risk_level": {
      "CRITICAL": 20,
      "HIGH": 15,
      ...
    }
  }
}
```

# Processing Rules
1. 优先检测攻击声明 (attack_type, ground_truth)
2. 高置信度 (≥90) 直接判定
3. 中置信度 (70-89) 需要 2+ 威胁指标
4. 低置信度 (<70) 标记为"需要人工审查"
5. 标准 K8s 资源默认良性 (除非发现恶意配置)
```

---

### 3. 威胁评估模板

```markdown
# Role
你是一名威胁情报分析师，负责评估 AI 安全威胁的严重性。

# Task
对检测到的恶意 YAML 配置进行威胁评估和分级。

# Input
```yaml
{YAML_CONTENT}
```

# Threat Assessment Framework

## 1. MITRE ATLAS 映射
- **T0001**: Active Scanning
- **T0007**: Search Open Websites/Domains
- **T0009**: Malicious Prompt
- **T0010**: LLM Target Discovery

## 2. OWASP LLM Top 10 映射
- **LLM01**: Prompt Injection
- **LLM02**: Insecure Output Handling
- **LLM03**: Training Data Poisoning
- **LLM04**: Model Denial of Service
- **LLM05**: Supply Chain Vulnerabilities

## 3. STRIDE 威胁分类
- **Spoofing**: 身份伪造
- **Tampering**: 数据篡改
- **Repudiation**: 抵赖
- **Information Disclosure**: 信息泄露
- **DoS**: 拒绝服务
- **Elevation of Privilege**: 权限提升

## 4. Kill Chain 阶段
1. Reconnaissance (侦察)
2. Weaponization (武器化)
3. Delivery (投递)
4. Exploitation (利用)
5. Installation (安装)
6. C2 (命令与控制)
7. Actions (目标行动)

# Output Format (JSON)

```json
{
  "threat_assessment": {
    "severity": "CRITICAL|HIGH|MEDIUM|LOW",
    "cvss_score": 7.5,
    "mitre_atlas": ["T0009"],
    "owasp_llm": ["LLM01"],
    "stride": ["Tampering", "DoS"],
    "kill_chain_stage": "Weaponization",
    "attack_complexity": "LOW|MEDIUM|HIGH",
    "required_privileges": "NONE|USER|ADMIN",
    "user_interaction": "NONE|REQUIRED",
    "scope_change": "UNCHANGED|CHANGED"
  },
  "impact_assessment": {
    "confidentiality": "NONE|LOW|MEDIUM|HIGH",
    "integrity": "NONE|LOW|MEDIUM|HIGH",
    "availability": "NONE|LOW|MEDIUM|HIGH",
    "affected_assets": ["LLM Model", "User Data", "System Resources"]
  },
  "remediation": {
    "immediate_actions": ["Block execution", "Quarantine file"],
    "long_term_actions": ["Update detection rules", "User training"],
    "detection_improvements": ["Add pattern for X", "Reduce false positives for Y"]
  }
}
```
```

---

### 4. 规则优化建议模板

```markdown
# Role
你是一名 AI 安全规则工程师，负责优化检测规则。

# Task
基于误报/漏报样本分析，提出规则优化建议。

# Input
```json
{
  "false_positives": [
    {"file": "sample1.yaml", "content": "...", "matched_rules": ["YAML-REX-001"]}
  ],
  "false_negatives": [
    {"file": "sample2.yaml", "content": "...", "missed_patterns": ["resource_attack"]}
  ]
}
```

# Analysis Process

## 1. 误报分析
- 为什么这些良性样本被误报？
- 规则的哪些部分过于宽泛？
- 如何修改规则避免误报？

## 2. 漏报分析
- 为什么这些恶意样本未被检出？
- 缺少哪些检测模式？
- 需要新增哪些规则？

## 3. 规则优化建议
- **保留**: 高置信度规则 (误报率<5%)
- **修改**: 中置信度规则 (误报率 5-20%)
- **移除**: 低置信度规则 (误报率>20%)
- **新增**: 针对漏报的攻击模式

# Output Format (Markdown)

```markdown
## 规则优化建议

### 误报分析
- **主要误报规则**: YAML-REX-001 (误报率 15%)
- **误报原因**: 匹配了正常的 K8s ConfigMap
- **优化建议**: 添加排除条件 (排除 apiVersion: v1, kind: ConfigMap)

### 漏报分析
- **主要漏报类型**: resource_exhaustion (漏检 7 个)
- **漏报原因**: 缺少 resource_attack 模式检测
- **优化建议**: 新增规则 YAML-REX-008 (resource_attack:.*type: exhaustion)

### 新增规则列表
1. YAML-REX-008: resource_attack 检测
2. YAML-REX-009: cpu_hog 检测
3. YAML-REX-010: memory_hog 检测

### 预期效果
- 检出率：83.3% → 95%+
- 误报率：0% → 保持 0%
```
```

---

## 🔧 使用示例

### 示例 1: 单个样本分析

```python
import json
import requests

def analyze_yaml_sample(yaml_content):
    prompt = YAML_ANALYSIS_PROMPT.replace("{YAML_CONTENT}", yaml_content)
    
    response = requests.post(
        "https://api.llm-provider.com/v1/chat/completions",
        json={
            "model": "gpt-4",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
            "response_format": {"type": "json_object"}
        }
    )
    
    result = json.loads(response.json()["choices"][0]["message"]["content"])
    return result

# 使用
yaml_content = """
attack_type: resource_exhaustion
resource_attack:
  type: exhaustion
  cpu_hog:
    enabled: true
"""

result = analyze_yaml_sample(yaml_content)
print(f"恶意：{result['is_malicious']}, 置信度：{result['confidence']}")
```

### 示例 2: 批量分析

```python
def batch_analyze_samples(samples):
    prompt = BATCH_ANALYSIS_PROMPT.replace("{SAMPLE_COUNT}", str(len(samples)))
    prompt = prompt.replace("{SAMPLES_JSON}", json.dumps(samples))
    
    response = requests.post(
        "https://api.llm-provider.com/v1/chat/completions",
        json={
            "model": "gpt-4",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
            "max_tokens": 4000,
            "response_format": {"type": "json_object"}
        }
    )
    
    return json.loads(response.json()["choices"][0]["message"]["content"])

# 使用
samples = [
    {"id": "sample_001", "path": "...", "content": "..."},
    {"id": "sample_002", "path": "...", "content": "..."}
]

results = batch_analyze_samples(samples)
print(f"恶意样本：{results['summary']['malicious_count']}")
```

---

## 📊 成本估算

| 模板 | 输入 Token | 输出 Token | 单次成本 (GPT-4) | 适用场景 |
|------|-----------|-----------|----------------|----------|
| 单个分析 | ~500 | ~200 | $0.01 | 可疑样本确认 |
| 批量分析 | ~5000 | ~1000 | $0.08 | 100 样本批量处理 |
| 威胁评估 | ~800 | ~400 | $0.02 | 高价值样本深度分析 |
| 规则优化 | ~2000 | ~800 | $0.04 | 周/月规则迭代 |

**优化建议**:
1. 只对中置信度 (70-89%) 样本使用 LLM
2. 高置信度 (≥90%) 直接规则判定
3. 低置信度 (<70%) 加入白名单或人工审查
4. 批量分析比单个分析成本更低

---

## 🎯 最佳实践

### 1. Prompt 优化技巧
- **明确角色**: "你是一名 AI 安全专家"
- **结构化输出**: 强制 JSON 格式
- **提供示例**: Few-shot learning
- **限制范围**: 只分析指定维度
- **置信度要求**: 0-100 数值评分

### 2. 成本控制策略
- **分级处理**: 高置信度规则判定，中置信度 LLM 确认
- **批量处理**: 100 样本一批，降低单次成本
- **缓存结果**: 相同样本不重复分析
- **模型选择**: 简单任务用小模型，复杂任务用大模型

### 3. 质量保证
- **人工抽检**: 随机抽查 10% LLM 结果
- **反馈循环**: 误报/漏报反馈给 LLM
- **版本管理**: Prompt 版本化，便于回滚
- **A/B 测试**: 不同 Prompt 效果对比

---

**最后更新**: 2026-04-19  
**维护者**: Security Team
