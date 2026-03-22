# 📋 Skill Scanner 任务测绘系统

## 一、任务分解

### 1.1 主任务：Skill Scanner 规则优化

| 任务 ID | 攻击类型 | 规则数 | 状态 | 进度 |
|---------|----------|--------|------|------|
| TASK-01 | tool_poisoning | 15 | ⏳ 待开始 | 0/15 |
| TASK-02 | remote_load | 12 | ⏳ 待开始 | 0/12 |
| TASK-03 | data_exfil | 10 | ⏳ 待开始 | 0/10 |
| TASK-04 | prompt_injection | 10 | ⏳ 待开始 | 0/10 |
| TASK-05 | resource_exhaustion | 8 | ⏳ 待开始 | 0/8 |
| TASK-06 | memory_pollution | 6 | ⏳ 待开始 | 0/6 |
| TASK-07 | supply_chain | 5 | ⏳ 待开始 | 0/5 |

---

## 二、任务详情

### TASK-01: Tool Poisoning (工具投毒)

**目标**: 检测恶意工具/依赖投毒攻击

**规则清单**:
| 规则 ID | 名称 | 类型 | 状态 | 测试 |
|---------|------|------|------|------|
| TP-RUNTIME-001 | Base64 解码 | runtime | ⏳ | - |
| TP-RUNTIME-002 | Eval/Exec 执行 | runtime | ⏳ | - |
| TP-RUNTIME-003 | 动态导入 | runtime | ⏳ | - |
| TP-RUNTIME-004 | Pickle 反序列化 | runtime | ⏳ | - |
| TP-YARA-001 | Shell 命令执行 | yara | ⏳ | - |
| TP-YARA-002 | 恶意脚本 | yara | ⏳ | - |
| TP-SIGMA-001 | NPM 恶意脚本 | sigma | ⏳ | - |
| TP-SIGMA-002 | PyPI 恶意包 | sigma | ⏳ | - |
| TP-IOC-001 | 恶意域名 | ioc | ⏳ | - |
| TP-IOC-002 | 恶意 IP | ioc | ⏳ | - |
| TP-DLP-001 | 凭证外传 | dlp | ⏳ | - |
| TP-DLP-002 | 密钥外传 | dlp | ⏳ | - |

**测试用例**:
- NPM postinstall 恶意脚本
- Python setup.py 投毒
- 恶意依赖检测
- 动态代码执行

---

### TASK-02: Remote Load (远程加载)

**目标**: 检测远程代码加载攻击

**规则清单**:
| 规则 ID | 名称 | 类型 | 状态 |
|---------|------|------|------|
| RL-RUNTIME-001 | curl \| bash | runtime | ⏳ |
| RL-RUNTIME-002 | wget \| bash | runtime | ⏳ |
| RL-RUNTIME-003 | 远程 import | runtime | ⏳ |
| RL-YARA-001 | Pastebin 加载 | yara | ⏳ |
| RL-YARA-002 | 第三方代码 | yara | ⏳ |
| RL-SIGMA-001 | 恶意下载 | sigma | ⏳ |
| RL-IOC-001 | 恶意 URL | ioc | ⏳ |
| RL-IOC-002 | 恶意域名 | ioc | ⏳ |

---

### TASK-03: Data Exfiltration (数据外传)

**目标**: 检测敏感数据外传

**规则清单**:
| 规则 ID | 名称 | 类型 | 状态 |
|---------|------|------|------|
| DE-RUNTIME-001 | 目录遍历 | runtime | ⏳ |
| DE-RUNTIME-002 | 敏感路径访问 | runtime | ⏳ |
| DE-RUNTIME-003 | 剪贴板读取 | runtime | ⏳ |
| DE-RUNTIME-004 | 键盘记录 | runtime | ⏳ |
| DE-YARA-001 | SSH 密钥访问 | yara | ⏳ |
| DE-SIGMA-001 | 数据压缩外传 | sigma | ⏳ |
| DE-IOC-001 | 恶意 C2 | ioc | ⏳ |
| DE-DLP-001 | 凭证外传 | dlp | ⏳ |
| DE-DLP-002 | 信用卡外传 | dlp | ⏳ |
| DE-DLP-003 | PII 外传 | dlp | ⏳ |

---

### TASK-04: Prompt Injection (提示词注入)

**目标**: 检测提示词注入攻击

**规则清单**:
| 规则 ID | 名称 | 类型 | 状态 |
|---------|------|------|------|
| PI-RUNTIME-001 | 系统提示覆盖 | runtime | ⏳ |
| PI-RUNTIME-002 | 角色扮演 | runtime | ⏳ |
| PI-RUNTIME-003 | 上下文注入 | runtime | ⏳ |
| PI-YARA-001 | 恶意指令 | yara | ⏳ |
| PI-SIGMA-001 | 注入模式 | sigma | ⏳ |
| PI-IOC-001 | 恶意提示库 | ioc | ⏳ |
| PI-DLP-001 | 敏感提示 | dlp | ⏳ |

---

### TASK-05: Resource Exhaustion (资源耗尽)

**目标**: 检测资源耗尽攻击

**规则清单**:
| 规则 ID | 名称 | 类型 | 状态 |
|---------|------|------|------|
| RE-RUNTIME-001 | 无限循环 | runtime | ⏳ |
| RE-RUNTIME-002 | 内存耗尽 | runtime | ⏳ |
| RE-RUNTIME-003 | 文件描述符耗尽 | runtime | ⏳ |
| RE-YARA-001 | 递归爆炸 | yara | ⏳ |
| RE-SIGMA-001 | 资源滥用 | sigma | ⏳ |
| RE-IOC-001 | 恶意挖矿 | ioc | ⏳ |

---

### TASK-06: Memory Pollution (内存污染)

**目标**: 检测内存污染攻击

**规则清单**:
| 规则 ID | 名称 | 类型 | 状态 |
|---------|------|------|------|
| MP-RUNTIME-001 | 缓冲区溢出 | runtime | ⏳ |
| MP-RUNTIME-002 | 竞态条件 | runtime | ⏳ |
| MP-RUNTIME-003 | 内存泄漏 | runtime | ⏳ |
| MP-YARA-001 | 不安全指针 | yara | ⏳ |
| MP-SIGMA-001 | 污染检测 | sigma | ⏳ |
| MP-IOC-001 | 恶意内存工具 | ioc | ⏳ |

---

### TASK-07: Supply Chain (供应链攻击)

**目标**: 检测供应链攻击

**规则清单**:
| 规则 ID | 名称 | 类型 | 状态 |
|---------|------|------|------|
| SC-RUNTIME-001 | 恶意依赖 | runtime | ⏳ |
| SC-RUNTIME-002 | Typosquatting | runtime | ⏳ |
| SC-YARA-001 | 恶意包检测 | yara | ⏳ |
| SC-SIGMA-001 | 供应链异常 | sigma | ⏳ |
| SC-IOC-001 | 恶意仓库 | ioc | ⏳ |

---

## 三、任务状态机

```
⏳ 待开始 → 🔬 进行中 → ✅ 已完成
                     ↘ → ❌ 阻塞中
```

---

## 四、执行命令

```bash
# 查看所有任务
python3 task_mapper.py --list

# 查看任务详情
python3 task_mapper.py --task TASK-01

# 开始任务
python3 task_mapper.py --start TASK-01

# 运行任务中的规则测试
python3 task_mapper.py --run TASK-01 --rule TP-RUNTIME-001

# 完成规则
python3 task_mapper.py --complete TASK-01 --rule TP-RUNTIME-001

# 生成报告
python3 task_mapper.py --report
```

---

## 五、进度追踪

```
TASK-01: Tool Poisoning     [████████░░░░░░░░░░] 40% (6/15)
TASK-02: Remote Load        [░░░░░░░░░░░░░░░░░░░] 0% (0/12)
TASK-03: Data Exfiltration  [░░░░░░░░░░░░░░░░░░░] 0% (0/10)
...
```

---

## 六、任务依赖

```
TASK-01 (工具投毒)
    │
    ├── 依赖: 无 → 可独立开始 ✅
    │
    └── 后续任务:
        ├── TASK-03 (数据外传) - 需要理解工具行为
        └── TASK-05 (资源耗尽) - 需要理解执行机制
```

---

开始执行吗？从 TASK-01 (Tool Poisoning) 开始？
