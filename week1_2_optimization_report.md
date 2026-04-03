# 🔧 Week 1-2: 检测率优化执行报告

**阶段**: 阶段 0 (能力打磨)  
**时间**: 2026-03-29 至 2026-04-11  
**目标**: 检测率 95.8% → 98%+

---

## 📊 当前状态分析

### **总体指标**
```
总检测率：95.8% (91/95)
误报率：0.0% (0/40)
F1 Score: 97.8
```

### **短板识别**
| 攻击类型 | 检测率 | 失败样本 | 优先级 |
|---------|--------|---------|--------|
| **persistence** | 90.0% (18/20) | 2 个未检出 | 🔴 P0 |
| **data_exfil** | 90.0% (18/20) | 2 个未检出 | 🔴 P0 |
| 其他 7 类 | 100% | 0 | ✅ |

---

## 🎯 优化策略

### **1. persistence 检测优化**

#### **失败样本分析**
```bash
# 失败样本特征
- 样本 1: WMI 持久化 (wmic /node:...)
  当前规则：未覆盖 wmic 命令变体
  
- 样本 2: 注册表 Run 键 (reg add HKLM\...\Run)
  当前规则：仅检测部分注册表路径
```

#### **新增规则计划**
```yaml
# 规则 1: WMI 持久化增强
rule: persistence_wmi_enhanced
  patterns:
    - wmic /node:
    - wmic process call create
    - win32_process.create
  mitre: T1047

# 规则 2: 注册表 Run 键增强
rule: persistence_registry_run_enhanced
  patterns:
    - reg add HKLM\Software\Microsoft\Windows\CurrentVersion\Run
    - reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run
    - New-ItemProperty -Name Run
  mitre: T1547.001

# 规则 3: 计划任务增强
rule: persistence_scheduled_task_enhanced
  patterns:
    - schtasks /create /tn
    - at.exe
    - cron -e
  mitre: T1053.005
```

#### **预期效果**
```
当前：90.0% (18/20)
新增规则后：100% (20/20)
提升：+10%
```

---

### **2. data_exfil 检测优化**

#### **失败样本分析**
```bash
# 失败样本特征
- 样本 1: DNS 隧道 (nslookup -q=TXT ...)
  当前规则：未覆盖 DNS 查询变体
  
- 样本 2: HTTPS 隐蔽外传 (curl -X POST + base64)
  当前规则：仅检测简单 curl 命令
```

#### **新增规则计划**
```yaml
# 规则 1: DNS 隧道增强
rule: data_exfil_dns_tunnel_enhanced
  patterns:
    - nslookup -q=TXT
    - nslookup -type=TXT
    - dns.query(
  mitre: T1048.003

# 规则 2: HTTPS 隐蔽外传
rule: data_exfil_https_covert
  patterns:
    - curl -X POST | base64
    - requests.post( + base64
    - fetch( + btoa(
  mitre: T1041

# 规则 3: 大文件分块外传
rule: data_exfil_chunked_transfer
  patterns:
    - split( | curl
    - chunk + upload
  mitre: T1041
```

#### **预期效果**
```
当前：90.0% (18/20)
新增规则后：100% (20/20)
提升：+10%
```

---

## 🛠️ 执行步骤

### **Step 1: 分析失败样本 (已完成)**
- [x] 识别 persistence 失败样本特征
- [x] 识别 data_exfil 失败样本特征

### **Step 2: 生成新规则 (进行中)**
- [ ] 创建 persistence 增强规则 (3 条)
- [ ] 创建 data_exfil 增强规则 (3 条)

### **Step 3: 测试验证**
- [ ] 运行基准测试
- [ ] 验证检测率 ≥98%
- [ ] 验证误报率保持 0%

### **Step 4: 规则合并**
- [ ] 重新编译规则
- [ ] 生成 all_rules_vX.yar
- [ ] 提交到 git

---

## 📈 成功指标

| 指标 | 当前 | 目标 | 状态 |
|------|------|------|------|
| **总检测率** | 95.8% | ≥98% | 🔴 待达成 |
| **persistence** | 90.0% | 100% | 🔴 待达成 |
| **data_exfil** | 90.0% | 100% | 🔴 待达成 |
| **误报率** | 0.0% | <0.5% | ✅ 已达成 |
| **规则数量** | 559 | 565+ | ⚠️ 待新增 |

---

## 🚀 下一步

**立即执行**:
1. 创建 6 条新规则 (3 persistence + 3 data_exfil)
2. 运行基准测试验证
3. 提交规则更新

预计完成时间：**今天内**

---

**创建日期**: 2026-03-29  
**执行者**: AI Assistant  
**状态**: 进行中
