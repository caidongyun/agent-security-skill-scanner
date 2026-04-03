# 📦 沙箱模块架构深度分析

**时间**: 2026-03-17 20:35  
**项目**: agent-security-skill-scanner / expert_mode  
**版本**: v5.0 (沙箱增强版)

---

## 🏗️ 架构设计分析

### 用户提供的目录结构

```
expert_mode/
├── sandbox/                          # 沙箱模块 (新增)
│   ├── manager.py                    # 沙箱管理器
│   ├── environments/                 # 沙箱环境
│   │   ├── docker_python.py          # Python Docker 沙箱
│   │   ├── docker_shell.py           # Shell Docker 沙箱
│   │   └── docker_nodejs.py          # Node.js Docker 沙箱
│   ├── monitoring/                   # 行为监控
│   │   ├── syscall_tracer.py         # 系统调用追踪
│   │   ├── file_monitor.py           # 文件操作监控
│   │   └── network_monitor.py        # 网络行为分析
│   ├── analysis/                     # 行为分析
│   │   ├── behavior_analyzer.py      # 行为分析引擎
│   │   └── risk_scorer.py            # 风险评分
│   └── reports/                      # 分析报告
│       └── behavior_report.py        # 报告生成
│
├── samples/                          # 样本库
│   ├── pending/                      # 待分析
│   └── analyzed/                     # 已分析
│
└── results/                          # 分析结果
    └── behavior_reports/             # 行为报告
```

---

## ✅ 设计优点

### 1. 模块化清晰 ⭐⭐⭐⭐⭐

```
sandbox/
├── manager.py         # 统一入口，单责任
├── environments/      # 环境隔离，可扩展
├── monitoring/        # 监控独立，可替换
├── analysis/          # 分析解耦，可测试
└── reports/           # 报告生成，可定制
```

**优势**:
- ✅ 单一职责原则 (SRP)
- ✅ 开闭原则 (OCP) - 易扩展新环境
- ✅ 依赖倒置 (DIP) - 监控/分析可插拔

---

### 2. 多语言支持 ⭐⭐⭐⭐⭐

```
environments/
├── docker_python.py   # Python 样本
├── docker_shell.py    # Shell 样本
└── docker_nodejs.py   # Node.js 样本
```

**扩展路径**:
```python
# 未来可添加
├── docker_powershell.py  # PowerShell
├── docker_vbs.py         # VBS
├── docker_java.py        # Java
└── docker_dotnet.py      # .NET
```

---

### 3. 完整监控链路 ⭐⭐⭐⭐⭐

```
执行 → 监控 → 分析 → 报告
  ↓      ↓      ↓      ↓
样本  系统调用  行为模式  JSON/HTML
      文件操作  风险评分  PDF/Markdown
      网络行为  IOC 提取
```

**监控维度**:
- ✅ 系统调用 (execve, fork, clone)
- ✅ 文件操作 (read, write, delete)
- ✅ 网络行为 (socket, connect, send/recv)

---

## ⚠️ 潜在问题

### 问题 1: 缺少样本预处理

**当前结构**:
```
samples/
├── pending/      # 待分析
└── analyzed/     # 已分析
```

**缺失**:
- ❌ 样本采集模块
- ❌ 样本分类/标记
- ❌ 样本去重
- ❌ 样本版本管理

**建议**:
```
samples/
├── incoming/         # 新采集 (原始)
├── staging/          # 预处理中
├── ready/            # 待分析 (已分类)
├── pending/          # 排队中
├── analyzing/        # 分析中 (锁定)
├── analyzed/         # 已完成
│   ├── benign/       # 良性
│   ├── suspicious/   # 可疑
│   └── malicious/    # 恶意
└── quarantine/       # 隔离 (高风险)
```

---

### 问题 2: 缺少配置管理

**缺失**:
- ❌ 沙箱配置文件
- ❌ 监控规则配置
- ❌ 分析策略配置
- ❌ 资源限制配置

**建议**:
```
sandbox/
├── config/
│   ├── sandbox.yaml       # 沙箱配置
│   ├── monitoring.yaml    # 监控配置
│   ├── analysis.yaml      # 分析配置
│   └── environments/      # 环境配置
│       ├── python.yaml
│       ├── shell.yaml
│       └── nodejs.yaml
```

---

### 问题 3: 缺少状态管理

**问题**: 沙箱执行状态如何追踪？

**建议**:
```
sandbox/
├── state/
│   ├── queue.json         # 执行队列
│   ├── active.json        # 活跃沙箱
│   ├── completed.json     # 已完成
│   └── failed.json        # 失败记录
```

---

### 问题 4: 缺少错误处理

**场景**:
- 沙箱启动失败
- 样本执行超时
- 监控模块异常
- 分析引擎崩溃

**建议**:
```
sandbox/
├── exceptions.py          # 自定义异常
├── retry.py               # 重试机制
└── health.py              # 健康检查
```

---

## 🔧 核心模块详细设计

### 1. manager.py - 沙箱管理器

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sandbox Manager - 沙箱统一管理器
负责样本调度、环境选择、结果聚合
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
    
    def _load_config(self, config_path: str) -> Dict:
        """加载配置"""
        default_config = {
            "sandbox": {
                "max_concurrent": 10,
                "timeout": 60,
                "memory_limit": "512m",
                "cpu_limit": 0.5,
            },
            "monitoring": {
                "trace_syscalls": True,
                "trace_files": True,
                "trace_network": True,
            },
            "analysis": {
                "min_risk_threshold": 30,
                "high_risk_threshold": 70,
            },
            "storage": {
                "samples_dir": "samples",
                "results_dir": "results",
                "reports_dir": "results/behavior_reports",
            }
        }
        
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                import yaml
                user_config = yaml.safe_load(f)
                # 深度合并配置
                self._merge_config(default_config, user_config)
        
        return default_config
    
    def _init_environments(self) -> Dict:
        """初始化沙箱环境"""
        return {
            'python': PythonSandbox(self.config),
            'shell': ShellSandbox(self.config),
            'nodejs': NodeJSSandbox(self.config),
        }
    
    def _init_monitors(self) -> List:
        """初始化监控器"""
        monitors = []
        
        if self.config['monitoring'].get('trace_syscalls'):
            monitors.append(SyscallTracer())
        if self.config['monitoring'].get('trace_files'):
            monitors.append(FileMonitor())
        if self.config['monitoring'].get('trace_network'):
            monitors.append(NetworkMonitor())
        
        return monitors
    
    def submit(self, sample_path: str, sample_type: str = None) -> str:
        """提交样本进行分析"""
        sample_id = self._generate_sample_id(sample_path)
        
        # 自动检测类型
        if not sample_type:
            sample_type = self._detect_sample_type(sample_path)
        
        # 加入队列
        self.queue.append({
            'id': sample_id,
            'path': sample_path,
            'type': sample_type,
            'submitted_at': datetime.now().isoformat(),
            'status': 'pending'
        })
        
        logger.info(f"样本提交：{sample_id} ({sample_type})")
        return sample_id
    
    def analyze(self, sample_id: str) -> Dict:
        """执行样本分析"""
        # 查找样本
        sample = self._find_sample(sample_id)
        if not sample:
            raise ValueError(f"样本不存在：{sample_id}")
        
        # 选择环境
        env = self.environments.get(sample['type'])
        if not env:
            raise ValueError(f"不支持的样本类型：{sample['type']}")
        
        # 启动监控
        for monitor in self.monitors:
            monitor.start(sample_id)
        
        # 执行样本
        logger.info(f"开始分析：{sample_id}")
        exec_result = env.execute(sample['path'])
        
        # 停止监控
        monitor_data = {}
        for monitor in self.monitors:
            monitor_data[monitor.name] = monitor.stop(sample_id)
        
        # 行为分析
        behavior = self.analyzer.analyze(exec_result, monitor_data)
        
        # 风险评分
        risk_score = self.scorer.score(behavior)
        
        # 生成报告
        report = BehaviorReport(
            sample_id=sample_id,
            behavior=behavior,
            risk_score=risk_score,
            exec_result=exec_result
        )
        
        # 保存结果
        self._save_result(sample_id, report)
        
        logger.info(f"分析完成：{sample_id} (风险评分：{risk_score})")
        return report.to_dict()
    
    def _generate_sample_id(self, sample_path: str) -> str:
        """生成样本 ID"""
        import hashlib
        with open(sample_path, 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()[:16]
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"SAMPLE_{timestamp}_{file_hash}"
    
    def _detect_sample_type(self, sample_path: str) -> str:
        """检测样本类型"""
        ext_map = {
            '.py': 'python',
            '.sh': 'shell',
            '.bash': 'shell',
            '.js': 'nodejs',
            '.jsx': 'nodejs',
            '.ts': 'nodejs',
        }
        
        ext = Path(sample_path).suffix.lower()
        return ext_map.get(ext, 'python')  # 默认 Python
    
    def _find_sample(self, sample_id: str) -> Dict:
        """查找样本"""
        for sample in self.queue:
            if sample['id'] == sample_id:
                return sample
        return None
    
    def _save_result(self, sample_id: str, report: BehaviorReport):
        """保存结果"""
        reports_dir = Path(self.config['storage']['reports_dir'])
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        report_path = reports_dir / f"{sample_id}.json"
        with open(report_path, 'w') as f:
            json.dump(report.to_dict(), f, indent=2)
        
        logger.info(f"报告保存：{report_path}")
    
    def _merge_config(self, base: Dict, override: Dict):
        """深度合并配置"""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value
    
    def status(self) -> Dict:
        """获取管理器状态"""
        return {
            'queue_length': len(self.queue),
            'active_count': len(self.active),
            'completed_count': len(self.completed),
            'environments': list(self.environments.keys()),
            'monitors': [m.name for m in self.monitors],
        }
```

---

### 2. syscall_tracer.py - 系统调用追踪

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Syscall Tracer - 系统调用追踪器
使用 ptrace 或 audit 系统调用
"""

import os
import ctypes
import logging
from typing import Dict, List
from datetime import datetime

logger = logging.getLogger(__name__)

# Linux 系统调用号 (x86_64)
SYSCALL_NAMES = {
    0: 'read',
    1: 'write',
    2: 'open',
    3: 'close',
    59: 'execve',
    57: 'fork',
    56: 'clone',
    41: 'socket',
    42: 'connect',
    49: 'bind',
    50: 'listen',
    43: 'accept',
    87: 'rename',
    82: 'unlink',
    83: 'mkdir',
    84: 'rmdir',
    165: 'mount',
    166: 'umount2',
    101: 'ptrace',
    102: 'getuid',
    104: 'getgid',
    117: 'setuid',
    119: 'setgid',
}

class SyscallTracer:
    """系统调用追踪器"""
    
    def __init__(self):
        self.name = 'syscall_tracer'
        self.traces = {}
        self.suspicious_calls = {
            'execve': 50,    # 高风险
            'fork': 30,
            'clone': 30,
            'socket': 40,
            'connect': 50,
            'unlink': 40,    # 删除文件
            'rename': 30,
            'mount': 60,
            'ptrace': 70,    # 调试/注入
            'setuid': 50,
            'setgid': 50,
        }
    
    def start(self, sample_id: str):
        """开始追踪"""
        self.traces[sample_id] = {
            'start_time': datetime.now().isoformat(),
            'calls': [],
            'risk_score': 0,
        }
        logger.info(f"SyscallTracer 启动：{sample_id}")
    
    def record(self, sample_id: str, syscall_num: int, args: tuple):
        """记录系统调用"""
        if sample_id not in self.traces:
            return
        
        syscall_name = SYSCALL_NAMES.get(syscall_num, f'unknown_{syscall_num}')
        
        trace = self.traces[sample_id]
        trace['calls'].append({
            'timestamp': datetime.now().isoformat(),
            'syscall': syscall_name,
            'syscall_num': syscall_num,
            'args': args,
        })
        
        # 计算风险分
        if syscall_name in self.suspicious_calls:
            trace['risk_score'] += self.suspicious_calls[syscall_name]
            logger.warning(f"可疑系统调用：{syscall_name} (样本：{sample_id})")
    
    def stop(self, sample_id: str) -> Dict:
        """停止追踪并返回结果"""
        if sample_id not in self.traces:
            return {}
        
        trace = self.traces[sample_id]
        trace['end_time'] = datetime.now().isoformat()
        trace['total_calls'] = len(trace['calls'])
        
        # 去重统计
        call_counts = {}
        for call in trace['calls']:
            name = call['syscall']
            call_counts[name] = call_counts.get(name, 0) + 1
        
        trace['call_summary'] = call_counts
        trace['risk_score'] = min(100, trace['risk_score'])
        
        logger.info(f"SyscallTracer 完成：{sample_id} ({trace['total_calls']} 次调用)")
        return trace
    
    def get_suspicious(self, sample_id: str) -> List[Dict]:
        """获取可疑调用"""
        if sample_id not in self.traces:
            return []
        
        return [
            call for call in self.traces[sample_id]['calls']
            if call['syscall'] in self.suspicious_calls
        ]
```

---

### 3. behavior_analyzer.py - 行为分析引擎

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Behavior Analyzer - 行为分析引擎
基于规则的行为模式识别
"""

import re
from typing import Dict, List

class BehaviorAnalyzer:
    """行为分析引擎"""
    
    def __init__(self):
        self.patterns = self._load_patterns()
    
    def _load_patterns(self) -> Dict:
        """加载行为模式"""
        return {
            'file_access': {
                'sensitive_paths': [
                    r'/etc/passwd',
                    r'/etc/shadow',
                    r'\.ssh/',
                    r'\.gnupg/',
                    r'/etc/cron\.d/',
                    r'/etc/systemd/system/',
                ],
                'weight': 30
            },
            'network': {
                'suspicious_ports': [4444, 5555, 6666, 8080, 31337],
                'c2_patterns': [
                    r'beacon',
                    r'callback',
                    r'c2',
                    r'command_and_control',
                ],
                'weight': 40
            },
            'persistence': {
                'indicators': [
                    r'schtasks',
                    r'crontab',
                    r'systemd',
                    r'rc\.local',
                    r'init\.d',
                ],
                'weight': 50
            },
            'defense_evasion': {
                'indicators': [
                    r'taskkill',
                    r'net\s+stop',
                    r'Set-MpPreference',
                    r'iptables.*-F',
                    r'rm.*\.log',
                ],
                'weight': 60
            },
            'privilege_escalation': {
                'indicators': [
                    r'sudo',
                    r'su\s+-',
                    r'setuid',
                    r'chmod.*\+s',
                    r'cap_setuid',
                ],
                'weight': 70
            }
        }
    
    def analyze(self, exec_result: Dict, monitor_data: Dict) -> Dict:
        """分析行为"""
        behavior = {
            'file_access': self._analyze_file_access(monitor_data),
            'network': self._analyze_network(monitor_data),
            'persistence': self._analyze_persistence(monitor_data),
            'defense_evasion': self._analyze_evasion(monitor_data),
            'privilege_escalation': self._analyze_priv_esc(monitor_data),
            'summary': {},
        }
        
        # 生成摘要
        behavior['summary'] = self._generate_summary(behavior)
        
        return behavior
    
    def _analyze_file_access(self, monitor_data: Dict) -> Dict:
        """分析文件访问"""
        result = {'accessed': [], 'sensitive': [], 'risk_score': 0}
        
        file_calls = monitor_data.get('file_monitor', {}).get('calls', [])
        for call in file_calls:
            path = call.get('path', '')
            result['accessed'].append(path)
            
            for pattern in self.patterns['file_access']['sensitive_paths']:
                if re.search(pattern, path):
                    result['sensitive'].append(path)
                    result['risk_score'] += self.patterns['file_access']['weight']
        
        return result
    
    def _analyze_network(self, monitor_data: Dict) -> Dict:
        """分析网络行为"""
        result = {'connections': [], 'suspicious': [], 'risk_score': 0}
        
        net_calls = monitor_data.get('network_monitor', {}).get('connections', [])
        for conn in net_calls:
            result['connections'].append(conn)
            
            port = conn.get('port', 0)
            if port in self.patterns['network']['suspicious_ports']:
                result['suspicious'].append(conn)
                result['risk_score'] += self.patterns['network']['weight']
        
        return result
    
    def _analyze_persistence(self, monitor_data: Dict) -> Dict:
        """分析持久化行为"""
        return self._check_indicators(
            monitor_data,
            'persistence',
            ['syscall_tracer', 'file_monitor']
        )
    
    def _analyze_evasion(self, monitor_data: Dict) -> Dict:
        """分析防御规避"""
        return self._check_indicators(
            monitor_data,
            'defense_evasion',
            ['syscall_tracer', 'file_monitor']
        )
    
    def _analyze_priv_esc(self, monitor_data: Dict) -> Dict:
        """分析权限提升"""
        return self._check_indicators(
            monitor_data,
            'privilege_escalation',
            ['syscall_tracer']
        )
    
    def _check_indicators(self, monitor_data: Dict, category: str, sources: List) -> Dict:
        """检查行为指标"""
        result = {'indicators': [], 'risk_score': 0}
        
        for source in sources:
            data = monitor_data.get(source, {}).get('calls', [])
            for call in data:
                content = str(call)
                for indicator in self.patterns[category]['indicators']:
                    if re.search(indicator, content, re.IGNORECASE):
                        result['indicators'].append({
                            'category': category,
                            'indicator': indicator,
                            'source': source,
                        })
                        result['risk_score'] += self.patterns[category]['weight']
        
        return result
    
    def _generate_summary(self, behavior: Dict) -> Dict:
        """生成行为摘要"""
        total_risk = sum(
            behavior[cat].get('risk_score', 0)
            for cat in behavior.keys()
            if isinstance(behavior[cat], dict)
        )
        
        return {
            'total_risk_score': min(100, total_risk),
            'categories_detected': [
                cat for cat in behavior.keys()
                if isinstance(behavior[cat], dict) and behavior[cat].get('risk_score', 0) > 0
            ],
            'severity': self._classify_severity(total_risk),
        }
    
    def _classify_severity(self, score: int) -> str:
        """分类严重程度"""
        if score >= 80:
            return 'critical'
        elif score >= 60:
            return 'high'
        elif score >= 40:
            return 'medium'
        elif score >= 20:
            return 'low'
        else:
            return 'minimal'
```

---

## 📋 完整目录结构 (增强版)

```
expert_mode/
├── sandbox/
│   ├── __init__.py
│   ├── manager.py                    # ⭐ 沙箱管理器
│   ├── exceptions.py                 # 自定义异常
│   ├── health.py                     # 健康检查
│   │
│   ├── config/
│   │   ├── sandbox.yaml              # 沙箱配置
│   │   ├── monitoring.yaml           # 监控配置
│   │   └── environments/
│   │       ├── python.yaml
│   │       ├── shell.yaml
│   │       └── nodejs.yaml
│   │
│   ├── environments/
│   │   ├── __init__.py
│   │   ├── base.py                   # 基类
│   │   ├── docker_python.py          # Python 沙箱
│   │   ├── docker_shell.py           # Shell 沙箱
│   │   ├── docker_nodejs.py          # Node.js 沙箱
│   │   └── lightweight.py            # 轻量级 (可选)
│   │
│   ├── monitoring/
│   │   ├── __init__.py
│   │   ├── base.py                   # 监控基类
│   │   ├── syscall_tracer.py         # ⭐ 系统调用追踪
│   │   ├── file_monitor.py           # ⭐ 文件监控
│   │   └── network_monitor.py        # ⭐ 网络监控
│   │
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── behavior_analyzer.py      # ⭐ 行为分析
│   │   ├── risk_scorer.py            # ⭐ 风险评分
│   │   └── ioc_extractor.py          # IOC 提取
│   │
│   ├── reports/
│   │   ├── __init__.py
│   │   ├── behavior_report.py        # ⭐ 报告生成
│   │   ├── html_template.html        # HTML 模板
│   │   └── markdown_template.md      # Markdown 模板
│   │
│   └── state/
│       ├── queue.json                # 执行队列
│       ├── active.json               # 活跃沙箱
│       └── completed.json            # 已完成
│
├── samples/
│   ├── incoming/                     # 新采集
│   ├── staging/                      # 预处理
│   ├── ready/                        # 待分析
│   ├── pending/                      # 排队中
│   ├── analyzing/                    # 分析中
│   └── analyzed/
│       ├── benign/
│       ├── suspicious/
│       └── malicious/
│
├── results/
│   ├── behavior_reports/             # 行为报告
│   ├── ioc_reports/                  # IOC 报告
│   └── summaries/                    # 汇总报告
│
└── tests/
    ├── test_sandbox.py
    ├── test_monitors.py
    └── test_analyzer.py
```

---

## 🎯 实施建议

### Phase 1: 核心功能 (1-2 周)

```bash
# 1. 创建基础结构
mkdir -p expert_mode/sandbox/{environments,monitoring,analysis,reports}

# 2. 实现核心模块
# - manager.py
# - docker_python.py
# - syscall_tracer.py
# - behavior_analyzer.py

# 3. 测试
python -m pytest tests/test_sandbox.py
```

### Phase 2: 增强功能 (2-3 周)

- 添加更多环境 (PowerShell, VBS, Java)
- 实现轻量级沙箱
- IOC 提取模块
- HTML/PDF 报告

### Phase 3: 集成 (1 周)

- 与灵顺 V5 集成
- 自动化流水线
- 与 agent-defender / agent-dlp 联动

---

## 📊 与灵顺 V5 集成

```python
# lingshun_v5.py 中调用沙箱
from sandbox.manager import SandboxManager

class LingshunV5:
    def __init__(self):
        self.sandbox = SandboxManager()
    
    def analyze_sample(self, sample_path: str):
        # 1. 静态分析
        static_result = self.static_scan(sample_path)
        
        # 2. 动态分析 (沙箱)
        if static_result['risk'] > 30:
            sample_id = self.sandbox.submit(sample_path)
            dynamic_result = self.sandbox.analyze(sample_id)
        else:
            dynamic_result = None
        
        # 3. 综合评估
        return self._combine_results(static_result, dynamic_result)
```

---

## 🎉 总结

### 架构评分

| 维度 | 评分 | 说明 |
|------|------|------|
| **模块化** | ⭐⭐⭐⭐⭐ | 清晰的职责分离 |
| **可扩展** | ⭐⭐⭐⭐⭐ | 易添加新环境/监控器 |
| **可测试** | ⭐⭐⭐⭐ | 模块独立，易单元测试 |
| **完整性** | ⭐⭐⭐⭐ | 缺少配置/状态管理 |
| **生产就绪** | ⭐⭐⭐ | 需补充错误处理 |

### 建议优先级

1. 🔴 **立即**: 补充配置管理和状态管理
2. 🟡 **短期**: 实现核心模块 (manager, environments, monitors)
3. 🟢 **中期**: 添加更多环境支持和 IOC 提取
4. 🔵 **长期**: 与灵顺 V5 深度集成

---

**时间**: 2026-03-17 20:35  
**状态**: 📊 架构分析完成  
**推荐**: 按 Phase 1-3 分阶段实施

🎯 **是否立即开始创建沙箱模块？** 🚀
