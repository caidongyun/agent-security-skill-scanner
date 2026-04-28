
## 🔍 威胁分析模型建议

### 1. MITRE ATLAS (Adversarial Threat Landscape for AI Systems)
**适用场景**: AI/LLM 特定攻击检测
**技术映射**:
- T0001: Active Scanning
- T0007: Search Open Websites/Domains
- T0009: Malicious Prompt
- T0010: LLM Target Discovery

**集成方式**:
```yaml
mitre_mapping:
  - technique_id: T0009
    tactic: Initial Access
    detection_rule: YAML-PIN-*
```

### 2. OWASP LLM Top 10
**适用场景**: LLM 应用安全风险
**分类**:
- LLM01: Prompt Injection
- LLM02: Insecure Output Handling
- LLM03: Training Data Poisoning
- LLM04: Model Denial of Service
- LLM05: Supply Chain Vulnerabilities

**集成方式**:
```yaml
owasp_llm_category: LLM01
severity_mapping:
  LLM01: CRITICAL
  LLM04: HIGH
```

### 3. STRIDE (Spoofing, Tampering, Repudiation, Information Disclosure, DoS, Elevation of Privilege)
**适用场景**: 云原生/K8s 威胁建模
**映射**:
- DoS → resource_exhaustion, cpu_hog
- Tampering → memory_pollution, false_memories
- Elevation → privileged, hostPath

### 4. Kill Chain (Cyber Kill Chain for AI)
**阶段**:
1. Reconnaissance → scanning, enumeration
2. Weaponization → tool_poisoning, prompt_injection
3. Delivery → remote_load, supply_chain
4. Exploitation → code_execution, credential_theft
5. Installation → persistence, systemd
6. C2 → c2_server, callback
7. Actions → data_exfil, resource_exhaustion

### 5. D3FEND (NIST Cybersecurity Framework)
**防御技术映射**:
- Detect → 当前规则系统
- Deny → 白名单机制
- Disrupt → 运行时阻断
- Deceive → 蜜罐配置

---

## 📊 规则投入评估

### 当前状态
- 规则数：44 条
- 检出率：83.3%
- 误报率：0.0%

### 投入建议

#### 方案 A: 保守优化 (推荐)
- **新增规则**: 10 条 (针对漏报的 resource_attack)
- **预期检出率**: 95%+
- **风险**: 低 (规则基于明确攻击声明)
- **成本**: 低

#### 方案 B: 激进优化
- **新增规则**: 30+ 条 (覆盖所有 MITRE ATLAS 技术)
- **预期检出率**: 98%+
- **风险**: 中 (可能增加误报)
- **成本**: 中

#### 方案 C: LLM 增强
- **规则数**: 保持 44 条
- **新增**: LLM 二次确认 (中置信度样本)
- **预期检出率**: 90%+
- **预期误报率**: 0%
- **成本**: 高 (LLM API 调用)

### 推荐方案：A + C 混合
1. 立即添加 10 条 resource_attack 规则 (方案 A)
2. 对中置信度样本启用 LLM 确认 (方案 C)
3. 预期效果：检出率 95%+, 误报率 0%

---

## ✅ Week 1 结论

**成果**:
- ✅ 误报率从 70.6% 降至 0%
- ✅ 检出率从 56.2% 提升至 83.3%
- ✅ 建立 44 条 YAML 专用规则
- ✅ 识别 10 类攻击模式

**待优化**:
- ⚠️ 检出率还需提升 11.7% (83.3% → 95%)
- ⚠️ 需补充 resource_attack 相关规则

**下一步**:
1. 添加 4 条 resource_attack 规则
2. 验证检出率 ≥95%
3. 准备 Week 2: LLM 集成
