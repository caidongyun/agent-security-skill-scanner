# 🔍 skillscanner 沙箱模块分析报告

**时间**: 2026-03-17 20:01  
**项目**: agent-security-skill-scanner  
**状态**: ❌ 沙箱模块缺失

---

## 📊 搜索结果

### 目录扫描

```bash
# 搜索 sandbox 相关目录
find skills/agent-security-skill-scanner -name "*sandbox*"
结果：❌ 无

# 搜索行为分析相关
find skills/agent-security-skill-scanner -name "*behavior*" -o -name "*analysis*"
结果：❌ 无
```

### 代码扫描

```bash
# 搜索沙箱相关代码
grep -r "sandbox\|沙箱" expert_mode/*.py
结果：❌ 无

# 搜索执行相关
grep -r "execute\|运行\|执行" sample_explorer.py
结果：⚠️ 仅有样本探索逻辑，无实际执行
```

### 文档扫描

```bash
# 搜索文档中的沙箱设计
grep -r "sandbox\|沙箱\|行为分析\|动态分析" docs/*.md expert_mode/*.md
结果：❌ 无专门沙箱设计文档
```

---

## ❌ 结论：沙箱模块不存在

**skillscanner (agent-security-skill-scanner) 项目中：**

| 功能 | 状态 | 说明 |
|------|------|------|
| **恶意代码检测** | ✅ | 静态规则检测 |
| **行为分析沙箱** | ❌ | 未实现 |
| **动态执行环境** | ❌ | 未实现 |
| **样本隔离执行** | ❌ | 未实现 |
| **系统调用监控** | ⚠️ | Runtime Monitor 部分实现 |

---

## 🎯 当前能力 vs 缺失能力

### ✅ 已有能力

| 模块 | 功能 | 实现方式 |
|------|------|----------|
| **lingshun_v5.py** | 静态规则检测 | 正则表达式匹配 |
| **defender_lingshun.py** | 入口防护 | Prompt/代码扫描 |
| **runtime/monitor.py** | 系统调用监控 | auditd/strace |
| **dlp/check.py** | 出口过滤 | 敏感数据检测 |

**特点**: **静态检测为主，缺少动态行为分析**

---

### ❌ 缺失的沙箱能力

| 能力 | 重要性 | 说明 |
|------|--------|------|
| **恶意代码动态执行** | 🔴 高 | 在隔离环境中运行样本 |
| **行为轨迹记录** | 🔴 高 | 记录文件/网络/进程操作 |
| **系统调用追踪** | 🔴 高 | 监控 execve/open/connect 等 |
| **网络行为分析** | 🔴 高 | 检测 C2 通信、数据外传 |
| **文件操作监控** | 🟡 中 | 检测敏感文件访问 |
| **注册表监控** | 🟡 中 | Windows 环境 |
| **内存行为分析** | 🟢 低 | 高级功能 |

---

## 🏗️ 沙箱架构设计

### 完整沙箱系统架构

```
┌─────────────────────────────────────────────────────────┐
│              skillscanner 沙箱系统                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌───────────────┐     ┌───────────────┐               │
│  │  样本管理模块  │────▶│  沙箱调度器    │               │
│  │  Sample Mgr   │     │  Scheduler     │               │
│  └───────────────┘     └───────┬───────┘               │
│                                 │                       │
│         ┌───────────────────────┼───────────────────┐   │
│         │                       │                   │   │
│         ▼                       ▼                   ▼   │
│  ┌─────────────┐        ┌─────────────┐     ┌─────────┐│
│  │ Python 沙箱  │        │  Shell 沙箱  │     │ JS 沙箱 ││
│  │ (Docker)    │        │ (Docker)    │     │(Node.js)││
│  └──────┬──────┘        └──────┬──────┘     └────┬────┘│
│         │                      │                  │     │
│         └──────────────────────┼──────────────────┘     │
│                                │                        │
│                                ▼                        │
│                    ┌─────────────────────┐             │
│                    │   行为监控层         │             │
│                    │  Behavior Monitor   │             │
│                    │ - 系统调用追踪       │             │
│                    │ - 文件操作记录       │             │
│                    │ - 网络行为分析       │             │
│                    │ - 进程树监控         │             │
│                    └──────────┬──────────┘             │
│                               │                       │
│                               ▼                       │
│                    ┌─────────────────────┐             │
│                    │   行为分析报告       │             │
│                    │  Behavior Report    │             │
│                    │ - IOC 提取           │             │
│                    │ - TTPs 映射          │             │
│                    │ - 风险评分           │             │
│                    └─────────────────────┘             │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 建议的目录结构

```
expert_mode/
├── sandbox/                          # 沙箱模块 (新增)
│   ├── __init__.py
│   ├── manager.py                    # 沙箱管理器
│   ├── scheduler.py                  # 沙箱调度器
│   │
│   ├── environments/                 # 沙箱环境
│   │   ├── __init__.py
│   │   ├── docker_python.py          # Python Docker 沙箱
│   │   ├── docker_shell.py           # Shell Docker 沙箱
│   │   ├── docker_nodejs.py          # Node.js Docker 沙箱
│   │   └── qemu_vm.py                # QEMU 虚拟机 (可选)
│   │
│   ├── monitoring/                   # 行为监控 (新增)
│   │   ├── __init__.py
│   │   ├── syscall_tracer.py         # 系统调用追踪
│   │   ├── file_monitor.py           # 文件操作监控
│   │   ├── network_monitor.py        # 网络行为分析
│   │   ├── process_monitor.py        # 进程树监控
│   │   └── registry_monitor.py       # 注册表监控 (Windows)
│   │
│   ├── analysis/                     # 行为分析 (新增)
│   │   ├── __init__.py
│   │   ├── behavior_analyzer.py      # 行为分析引擎
│   │   ├── ioc_extractor.py          # IOC 提取
│   │   ├── tt mapper.py              # MITRE ATT&CK 映射
│   │   └── risk_scorer.py            # 风险评分
│   │
│   ├── reports/                      # 分析报告 (新增)
│   │   └── behavior_report.py        # 报告生成
│   │
│   └── configs/                      # 配置文件 (新增)
│       ├── sandbox_policy.json       # 沙箱策略
│       ├── docker-compose.yml        # Docker 配置
│       └── seccomp_profile.json      # seccomp 配置
│
├── samples/                          # 样本库 (已有，待填充)
│   ├── pending/                      # 待分析样本
│   ├── analyzed/                     # 已分析样本
│   └── archive/                      # 归档样本
│
├── results/                          # 分析结果 (新增)
│   ├── behavior_reports/             # 行为分析报告
│   ├── ioc_database/                 # IOC 数据库
│   └── statistics/                   # 统计分析
│
└── ...
```

---

## 🔧 核心模块实现

### 1. 沙箱管理器 (sandbox/manager.py)

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
沙箱管理器 - 恶意代码行为分析核心
"""

import os
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime

from .environments.docker_python import DockerPythonSandbox
from .environments.docker_shell import DockerShellSandbox
from .environments.docker_nodejs import DockerNodeJSSandbox
from .monitoring.syscall_tracer import SyscallTracer
from .monitoring.file_monitor import FileMonitor
from .monitoring.network_monitor import NetworkMonitor
from .analysis.behavior_analyzer import BehaviorAnalyzer
from .reports.behavior_report import BehaviorReportGenerator

logger = logging.getLogger(__name__)

class SandboxManager:
    """沙箱管理器"""
    
    def __init__(self, config_path: str = "configs/sandbox_policy.json"):
        self.config = self._load_config(config_path)
        self.sandboxes = {}
        self.monitors = {}
        self.results_dir = "results/behavior_reports"
        os.makedirs(self.results_dir, exist_ok=True)
    
    def _load_config(self, config_path: str) -> dict:
        """加载沙箱配置"""
        default_config = {
            "timeout": 60,  # 执行超时 (秒)
            "memory_limit": "512m",
            "cpu_limit": 0.5,
            "network_enabled": False,  # 默认禁用网络
            "file_access": ["./sandbox_data"],
            "max_processes": 10,
            "auto_cleanup": True
        }
        
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
                default_config.update(config)
        
        return default_config
    
    def create_sandbox(self, sample_type: str, sample_id: str) -> object:
        """创建沙箱环境"""
        if sample_type == "python":
            sandbox = DockerPythonSandbox(sample_id, self.config)
        elif sample_type == "shell":
            sandbox = DockerShellSandbox(sample_id, self.config)
        elif sample_type == "javascript":
            sandbox = DockerNodeJSSandbox(sample_id, self.config)
        else:
            raise ValueError(f"不支持的样本类型：{sample_type}")
        
        self.sandboxes[sample_id] = sandbox
        return sandbox
    
    def execute_sample(self, sample_id: str, sample_code: str) -> Dict:
        """执行样本并监控行为"""
        logger.info(f"开始执行样本：{sample_id}")
        
        # 1. 创建沙箱
        sandbox = self.create_sandbox(
            sample_type=self._detect_sample_type(sample_code),
            sample_id=sample_id
        )
        
        # 2. 启动监控
        tracer = SyscallTracer(sandbox.container_id)
        file_mon = FileMonitor(sandbox.container_id)
        net_mon = NetworkMonitor(sandbox.container_id)
        
        tracer.start()
        file_mon.start()
        net_mon.start()
        
        # 3. 执行样本
        try:
            result = sandbox.execute(sample_code, timeout=self.config['timeout'])
        except Exception as e:
            logger.error(f"样本执行失败：{e}")
            result = {"error": str(e)}
        
        # 4. 停止监控
        tracer.stop()
        file_mon.stop()
        net_mon.stop()
        
        # 5. 收集行为数据
        behavior_data = {
            "sample_id": sample_id,
            "execution_result": result,
            "syscalls": tracer.get_events(),
            "file_operations": file_mon.get_events(),
            "network_activities": net_mon.get_events()
        }
        
        # 6. 行为分析
        analyzer = BehaviorAnalyzer(behavior_data)
        analysis_result = analyzer.analyze()
        
        # 7. 生成报告
        report_gen = BehaviorReportGenerator(analysis_result)
        report_path = report_gen.generate_report(
            output_dir=self.results_dir,
            sample_id=sample_id
        )
        
        # 8. 清理沙箱
        if self.config['auto_cleanup']:
            sandbox.destroy()
        
        logger.info(f"样本分析完成：{sample_id}, 报告：{report_path}")
        
        return {
            "sample_id": sample_id,
            "report_path": report_path,
            "analysis": analysis_result
        }
    
    def _detect_sample_type(self, code: str) -> str:
        """检测样本类型"""
        if code.startswith("#!") and "bash" in code:
            return "shell"
        elif "import " in code or "def " in code:
            return "python"
        elif "function " in code or "const " in code:
            return "javascript"
        else:
            return "python"  # 默认
```

---

### 2. Docker Python 沙箱 (sandbox/environments/docker_python.py)

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Docker Python 沙箱环境
"""

import docker
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class DockerPythonSandbox:
    """Python Docker 沙箱"""
    
    def __init__(self, sample_id: str, config: Dict):
        self.sample_id = sample_id
        self.config = config
        self.client = docker.from_env()
        self.container = None
        self.image = "python:3.10-slim"
    
    def create(self):
        """创建沙箱容器"""
        logger.info(f"创建 Python 沙箱：{self.sample_id}")
        
        self.container = self.client.containers.run(
            self.image,
            command="tail -f /dev/null",  # 保持运行
            detach=True,
            name=f"sandbox_{self.sample_id}",
            network_disabled=not self.config.get('network_enabled', False),
            mem_limit=self.config.get('memory_limit', '512m'),
            cpu_quota=int(self.config.get('cpu_limit', 0.5) * 100000),
            pids_limit=self.config.get('max_processes', 10),
            volumes={
                self._get_sandbox_data_path(): {'bind': '/sandbox', 'mode': 'rw'}
            },
            read_only=True,
            tmpfs={
                '/tmp': f'size=100M',
                '/var/tmp': f'size=50M'
            },
            security_opt=[
                'no-new-privileges:true',
                f'seccomp={self._get_seccomp_profile()}'
            ],
            cap_drop=['ALL'],
            cap_add=['SYS_PTRACE']  # 允许 strace
        )
        
        logger.info(f"沙箱创建成功：{self.container.id}")
        return self.container
    
    def execute(self, code: str, timeout: int = 60) -> Dict:
        """执行 Python 代码"""
        if not self.container:
            self.create()
        
        # 将代码写入容器
        code_path = "/sandbox/sample.py"
        self.container.exec_run(
            cmd=['sh', '-c', f'cat > {code_path}'],
            stdin=True,
            data=code.encode()
        )
        
        # 执行代码
        result = self.container.exec_run(
            cmd=['python3', '-u', code_path],
            demux=True,
            tty=False,
            stream=True
        )
        
        # 收集输出
        stdout = b""
        stderr = b""
        
        for chunk in result.output[0]:
            stdout += chunk
        for chunk in result.output[1]:
            stderr += chunk
        
        return {
            "exit_code": result.exit_code,
            "stdout": stdout.decode('utf-8', errors='ignore'),
            "stderr": stderr.decode('utf-8', errors='ignore'),
            "timeout": False
        }
    
    def destroy(self):
        """销毁沙箱"""
        if self.container:
            logger.info(f"销毁沙箱：{self.container.id}")
            self.container.remove(force=True)
            self.container = None
    
    def _get_sandbox_data_path(self) -> str:
        """获取沙箱数据目录"""
        return f"./sandbox_data/{self.sample_id}"
    
    def _get_seccomp_profile(self) -> str:
        """获取 seccomp 配置文件路径"""
        return "./configs/seccomp_profile.json"
```

---

### 3. 系统调用追踪 (sandbox/monitoring/syscall_tracer.py)

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统调用追踪 - 使用 strace
"""

import subprocess
import threading
import logging
import re
from typing import List, Dict
from collections import defaultdict

logger = logging.getLogger(__name__)

class SyscallTracer:
    """系统调用追踪器"""
    
    def __init__(self, container_id: str):
        self.container_id = container_id
        self.strace_process = None
        self.events = []
        self.thread = None
        self.running = False
        
        # 关注的系统调用
        self.traced_syscalls = [
            'execve', 'fork', 'vfork', 'clone',  # 进程
            'open', 'openat', 'read', 'write', 'close',  # 文件
            'socket', 'connect', 'bind', 'listen', 'accept',  # 网络
            'unlink', 'rename', 'mkdir', 'rmdir',  # 文件系统
            'chmod', 'chown', 'access',  # 权限
            'ptrace', 'setuid', 'setgid',  # 提权
        ]
    
    def start(self):
        """启动追踪"""
        logger.info(f"启动系统调用追踪：{self.container_id}")
        
        self.running = True
        self.thread = threading.Thread(target=self._trace_loop)
        self.thread.start()
    
    def _trace_loop(self):
        """追踪循环"""
        cmd = [
            'docker', 'exec', self.container_id,
            'strace', '-f', '-e', 'trace=' + ','.join(self.traced_syscalls),
            '-o', '/tmp/strace.log',
            'python3', '/sandbox/sample.py'
        ]
        
        self.strace_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # 解析 strace 输出
        while self.running:
            try:
                line = self.strace_process.stdout.readline()
                if line:
                    event = self._parse_syscall(line.decode('utf-8'))
                    if event:
                        self.events.append(event)
            except Exception as e:
                logger.error(f"解析系统调用失败：{e}")
                break
        
        self.strace_process.wait()
    
    def _parse_syscall(self, line: str) -> Optional[Dict]:
        """解析系统调用日志"""
        # 示例：open("/etc/passwd", O_RDONLY) = 3
        pattern = r'(\w+)\(([^)]+)\)\s*=\s*(\S+)'
        match = re.match(pattern, line.strip())
        
        if match:
            return {
                "syscall": match.group(1),
                "arguments": match.group(2),
                "return_value": match.group(3),
                "raw": line.strip()
            }
        
        return None
    
    def stop(self):
        """停止追踪"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        if self.strace_process:
            self.strace_process.terminate()
    
    def get_events(self) -> List[Dict]:
        """获取追踪事件"""
        return self.events
```

---

### 4. 行为分析引擎 (sandbox/analysis/behavior_analyzer.py)

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
行为分析引擎
"""

import logging
from typing import Dict, List
from collections import defaultdict

logger = logging.getLogger(__name__)

class BehaviorAnalyzer:
    """行为分析引擎"""
    
    def __init__(self, behavior_data: Dict):
        self.data = behavior_data
        self.indicators = []
        self.ttps = []
        self.risk_score = 0
    
    def analyze(self) -> Dict:
        """执行行为分析"""
        logger.info(f"开始行为分析：{self.data.get('sample_id')}")
        
        # 1. 分析系统调用
        self._analyze_syscalls()
        
        # 2. 分析文件操作
        self._analyze_file_operations()
        
        # 3. 分析网络行为
        self._analyze_network()
        
        # 4. 计算风险评分
        self._calculate_risk_score()
        
        # 5. 映射 MITRE ATT&CK
        self._map_to_mitre()
        
        return {
            "sample_id": self.data.get('sample_id'),
            "indicators": self.indicators,
            "ttps": self.ttps,
            "risk_score": self.risk_score,
            "risk_level": self._get_risk_level(),
            "malicious": self.risk_score >= 50
        }
    
    def _analyze_syscalls(self):
        """分析系统调用"""
        syscalls = self.data.get('syscalls', [])
        
        for event in syscalls:
            syscall = event.get('syscall', '')
            
            # 检测恶意行为
            if syscall == 'execve':
                args = event.get('arguments', '')
                if 'curl' in args or 'wget' in args:
                    self.indicators.append({
                        "type": "remote_download",
                        "severity": "high",
                        "description": f"检测到远程下载：{args}"
                    })
                    self.risk_score += 20
            
            elif syscall == 'connect':
                self.indicators.append({
                    "type": "network_connection",
                    "severity": "medium",
                    "description": f"检测到网络连接：{event.get('arguments')}"
                })
                self.risk_score += 10
    
    def _analyze_file_operations(self):
        """分析文件操作"""
        file_ops = self.data.get('file_operations', [])
        
        sensitive_paths = ['/etc/passwd', '/etc/shadow', '.ssh/', '.gnupg/']
        
        for event in file_ops:
            path = event.get('path', '')
            op = event.get('operation', '')
            
            for sensitive in sensitive_paths:
                if sensitive in path:
                    self.indicators.append({
                        "type": "sensitive_file_access",
                        "severity": "critical",
                        "description": f"访问敏感文件：{path} ({op})"
                    })
                    self.risk_score += 30
    
    def _analyze_network(self):
        """分析网络行为"""
        net_activities = self.data.get('network_activities', [])
        
        for activity in net_activities:
            if activity.get('type') == 'outbound':
                self.indicators.append({
                    "type": "outbound_connection",
                    "severity": "medium",
                    "description": f"外连：{activity.get('destination')}"
                })
                self.risk_score += 15
    
    def _calculate_risk_score(self):
        """计算风险评分"""
        # 归一化到 0-100
        self.risk_score = min(100, self.risk_score)
    
    def _get_risk_level(self) -> str:
        """获取风险等级"""
        if self.risk_score >= 80:
            return "critical"
        elif self.risk_score >= 60:
            return "high"
        elif self.risk_score >= 40:
            return "medium"
        elif self.risk_score >= 20:
            return "low"
        else:
            return "safe"
    
    def _map_to_mitre(self):
        """映射到 MITRE ATT&CK"""
        # 根据检测到的行为映射 TTPs
        for indicator in self.indicators:
            if indicator['type'] == 'remote_download':
                self.ttps.append("T1105 - Ingress Tool Transfer")
            elif indicator['type'] == 'sensitive_file_access':
                self.ttps.append("T1005 - Data from Local System")
```

---

### 5. 行为报告生成 (sandbox/reports/behavior_report.py)

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
行为分析报告生成
"""

import json
import os
from datetime import datetime
from typing import Dict

class BehaviorReportGenerator:
    """行为报告生成器"""
    
    def __init__(self, analysis_result: Dict):
        self.result = analysis_result
    
    def generate_report(self, output_dir: str, sample_id: str) -> str:
        """生成报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = os.path.join(output_dir, f"{sample_id}_{timestamp}.json")
        
        report = {
            "report_id": f"RPT-{sample_id}-{timestamp}",
            "generated_at": datetime.now().isoformat(),
            "sample_id": sample_id,
            "summary": {
                "risk_score": self.result['risk_score'],
                "risk_level": self.result['risk_level'],
                "malicious": self.result['malicious'],
                "indicators_count": len(self.result['indicators']),
                "ttps_count": len(self.result['ttps'])
            },
            "indicators": self.result['indicators'],
            "ttps": self.result['ttps'],
            "mitre_mapping": self._generate_mitre_mapping(),
            "recommendations": self._generate_recommendations()
        }
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report_path
    
    def _generate_mitre_mapping(self) -> Dict:
        """生成 MITRE 映射"""
        mapping = {}
        for ttp in self.result['ttps']:
            tactic = ttp.split(' - ')[0]
            technique = ttp.split(' - ')[1]
            
            if tactic not in mapping:
                mapping[tactic] = []
            mapping[tactic].append(technique)
        
        return mapping
    
    def _generate_recommendations(self) -> List[str]:
        """生成建议"""
        recommendations = []
        
        if self.result['malicious']:
            recommendations.append("🔴 建议立即阻断该样本")
            recommendations.append("🔴 建议添加到威胁情报库")
        
        if self.result['risk_score'] >= 80:
            recommendations.append("🔴 高风险样本，需要人工审查")
        
        for indicator in self.result['indicators']:
            if indicator['severity'] == 'critical':
                recommendations.append(f"⚠️ {indicator['description']}")
        
        return recommendations
```

---

## 📋 实施计划

### Phase 1: 基础框架 (本周) 🔴

- [ ] 创建 `sandbox/` 目录结构
- [ ] 实现 `manager.py` 沙箱管理器
- [ ] 实现 `docker_python.py` Python 沙箱
- [ ] 实现 `syscall_tracer.py` 系统调用追踪
- [ ] 实现 `behavior_analyzer.py` 行为分析

### Phase 2: 多语言支持 (2 周内) 🟡

- [ ] 实现 `docker_shell.py` Shell 沙箱
- [ ] 实现 `docker_nodejs.py` Node.js 沙箱
- [ ] 实现 `file_monitor.py` 文件监控
- [ ] 实现 `network_monitor.py` 网络监控

### Phase 3: 集成到灵顺 V5 (1 月内) 🟢

- [ ] 集成到 `lingshun_daemon.py`
- [ ] 集成到 `test_runner.py`
- [ ] 添加沙箱配置
- [ ] 编写使用文档

---

## 🎯 总结

**现状**: ❌ **skillscanner 没有恶意代码行为分析沙箱**

**需要**:
1. ✅ 创建完整的沙箱模块
2. ✅ 实现 Docker 隔离执行
3. ✅ 实现行为监控 (系统调用/文件/网络)
4. ✅ 实现行为分析引擎
5. ✅ 生成行为分析报告
6. ✅ 集成到灵顺 V5 自动循环

---

需要我帮你：
1. **创建 sandbox 目录和基础模块**？
2. **实现 Docker 沙箱环境**？
3. **实现行为监控系统**？
4. **集成到灵顺 V5 守护进程**？

🎯 **skillscanner 缺少恶意代码行为分析沙箱，建议立即补充！** 🚀
