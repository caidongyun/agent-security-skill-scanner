#!/usr/bin/env python3
"""
HE-005~008: 可观测性 + 日志系统 + 指标监控 + 告警系统
集成实现
"""

import json
import logging
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from collections import defaultdict
from enum import Enum


# ========== HE-006: 日志系统 ==========

class LogLevel(Enum):
    """日志等级"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class LogEntry:
    """日志条目"""
    timestamp: str
    level: LogLevel
    message: str
    module: str
    context: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            'timestamp': self.timestamp,
            'level': self.level.value,
            'message': self.message,
            'module': self.module,
            'context': self.context,
        }


class StructuredLogger:
    """结构化日志器"""
    
    def __init__(self, name: str, log_file: str = "app.log"):
        self.name = name
        self.log_file = Path(log_file)
        self.entries: List[LogEntry] = []
        
        # 配置 Python logging
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # 文件处理器
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.DEBUG)
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 格式化
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def log(self, level: LogLevel, message: str, **context):
        """记录日志"""
        entry = LogEntry(
            timestamp=datetime.now().isoformat(),
            level=level,
            message=message,
            module=self.name,
            context=context,
        )
        self.entries.append(entry)
        
        # Python logging
        log_func = getattr(self.logger, level.value)
        log_func(f"{message} | {json.dumps(context)}")
    
    def debug(self, message: str, **context):
        self.log(LogLevel.DEBUG, message, **context)
    
    def info(self, message: str, **context):
        self.log(LogLevel.INFO, message, **context)
    
    def warning(self, message: str, **context):
        self.log(LogLevel.WARNING, message, **context)
    
    def error(self, message: str, **context):
        self.log(LogLevel.ERROR, message, **context)
    
    def critical(self, message: str, **context):
        self.log(LogLevel.CRITICAL, message, **context)
    
    def query(self, level: Optional[LogLevel] = None,
             start_time: Optional[str] = None,
             limit: int = 100) -> List[Dict]:
        """查询日志"""
        entries = self.entries
        
        if level:
            entries = [e for e in entries if e.level == level]
        
        if start_time:
            entries = [e for e in entries if e.timestamp >= start_time]
        
        return [e.to_dict() for e in entries[-limit:]]


# ========== HE-007: 指标监控 ==========

@dataclass
class Metric:
    """指标"""
    name: str
    value: float
    timestamp: str
    tags: Dict = field(default_factory=dict)
    type: str = "gauge"  # gauge, counter, histogram


class MetricsCollector:
    """指标收集器"""
    
    def __init__(self):
        self.metrics: Dict[str, List[Metric]] = defaultdict(list)
        self.counters: Dict[str, int] = defaultdict(int)
    
    def gauge(self, name: str, value: float, **tags):
        """记录 gauge 指标"""
        metric = Metric(
            name=name,
            value=value,
            timestamp=datetime.now().isoformat(),
            tags=tags,
            type="gauge",
        )
        self.metrics[name].append(metric)
    
    def counter(self, name: str, value: int = 1, **tags):
        """记录 counter 指标"""
        self.counters[name] += value
        
        metric = Metric(
            name=name,
            value=self.counters[name],
            timestamp=datetime.now().isoformat(),
            tags=tags,
            type="counter",
        )
        self.metrics[name].append(metric)
    
    def histogram(self, name: str, value: float, **tags):
        """记录 histogram 指标"""
        metric = Metric(
            name=name,
            value=value,
            timestamp=datetime.now().isoformat(),
            tags=tags,
            type="histogram",
        )
        self.metrics[name].append(metric)
    
    def timer(self, name: str):
        """计时器装饰器"""
        def decorator(func: Callable) -> Callable:
            def wrapper(*args, **kwargs):
                start = time.time()
                try:
                    return func(*args, **kwargs)
                finally:
                    elapsed = (time.time() - start) * 1000  # ms
                    self.histogram(f"{name}_duration_ms", elapsed)
            return wrapper
        return decorator
    
    def get_metrics(self, name: Optional[str] = None,
                   start_time: Optional[str] = None,
                   limit: int = 100) -> List[Dict]:
        """获取指标"""
        if name:
            metrics = self.metrics.get(name, [])
        else:
            metrics = [m for ms in self.metrics.values() for m in ms]
        
        if start_time:
            metrics = [m for m in metrics if m.timestamp >= start_time]
        
        return [
            {
                'name': m.name,
                'value': m.value,
                'timestamp': m.timestamp,
                'tags': m.tags,
                'type': m.type,
            }
            for m in metrics[-limit:]
        ]
    
    def get_summary(self) -> Dict:
        """获取指标摘要"""
        summary = {
            'counters': dict(self.counters),
            'gauges': {},
            'histograms': {},
        }
        
        for name, metrics in self.metrics.items():
            if not metrics:
                continue
            
            latest = metrics[-1]
            if latest.type == "gauge":
                summary['gauges'][name] = latest.value
            elif latest.type == "histogram":
                values = [m.value for m in metrics[-100:]]
                summary['histograms'][name] = {
                    'count': len(values),
                    'min': min(values),
                    'max': max(values),
                    'avg': sum(values) / len(values),
                }
        
        return summary


# ========== HE-008: 告警系统 ==========

class AlertSeverity(Enum):
    """告警严重性"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Alert:
    """告警"""
    id: str
    severity: AlertSeverity
    title: str
    message: str
    timestamp: str
    source: str
    tags: Dict = field(default_factory=dict)
    acknowledged: bool = False
    resolved: bool = False
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'severity': self.severity.value,
            'title': self.title,
            'message': self.message,
            'timestamp': self.timestamp,
            'source': self.source,
            'tags': self.tags,
            'acknowledged': self.acknowledged,
            'resolved': self.resolved,
        }


class AlertManager:
    """告警管理器"""
    
    def __init__(self):
        self.alerts: List[Alert] = []
        self.alert_handlers: Dict[AlertSeverity, List[Callable]] = defaultdict(list)
        self.alert_counter = 0
    
    def register_handler(self, severity: AlertSeverity,
                        handler: Callable):
        """注册告警处理器"""
        self.alert_handlers[severity].append(handler)
    
    def send_alert(self, severity: AlertSeverity, title: str,
                  message: str, source: str = "system",
                  **tags) -> str:
        """发送告警"""
        self.alert_counter += 1
        
        alert = Alert(
            id=f"alert_{self.alert_counter}",
            severity=severity,
            title=title,
            message=message,
            timestamp=datetime.now().isoformat(),
            source=source,
            tags=tags,
        )
        
        self.alerts.append(alert)
        
        # 触发处理器
        for handler in self.alert_handlers.get(severity, []):
            try:
                handler(alert)
            except Exception as e:
                print(f"❌ 告警处理器失败：{e}")
        
        return alert.id
    
    def acknowledge_alert(self, alert_id: str, user_id: str) -> bool:
        """确认告警"""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.acknowledged = True
                alert.tags['acknowledged_by'] = user_id
                alert.tags['acknowledged_at'] = datetime.now().isoformat()
                return True
        return False
    
    def resolve_alert(self, alert_id: str) -> bool:
        """解决告警"""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.resolved = True
                alert.tags['resolved_at'] = datetime.now().isoformat()
                return True
        return False
    
    def get_alerts(self, severity: Optional[AlertSeverity] = None,
                  acknowledged: Optional[bool] = None,
                  resolved: Optional[bool] = None,
                  limit: int = 100) -> List[Dict]:
        """获取告警"""
        alerts = self.alerts
        
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        
        if acknowledged is not None:
            alerts = [a for a in alerts if a.acknowledged == acknowledged]
        
        if resolved is not None:
            alerts = [a for a in alerts if a.resolved == resolved]
        
        return [a.to_dict() for a in alerts[-limit:]]
    
    def get_unacknowledged(self) -> List[Dict]:
        """获取未确认告警"""
        return self.get_alerts(acknowledged=False, resolved=False)
    
    def get_unresolved(self) -> List[Dict]:
        """获取未解决告警"""
        return self.get_alerts(resolved=False)


# ========== HE-005: 可观测性 (集成) ==========

class Observability:
    """可观测性 (集成日志/指标/告警)"""
    
    def __init__(self, name: str = "system"):
        self.name = name
        self.logger = StructuredLogger(name, f"{name}.log")
        self.metrics = MetricsCollector()
        self.alerts = AlertManager()
        
        # 自动告警处理器
        self.alerts.register_handler(
            AlertSeverity.CRITICAL,
            self._critical_alert_handler,
        )
    
    def _critical_alert_handler(self, alert: Alert):
        """严重告警处理"""
        self.logger.critical(
            f"严重告警：{alert.title}",
            alert_id=alert.id,
            message=alert.message,
        )
    
    def trace(self, name: str, func: Callable, *args, **kwargs):
        """追踪函数执行"""
        self.logger.debug(f"开始执行：{name}")
        
        try:
            result = func(*args, **kwargs)
            self.logger.info(f"执行完成：{name}")
            return result
        except Exception as e:
            self.logger.error(f"执行失败：{name}", error=str(e))
            self.alerts.send_alert(
                AlertSeverity.ERROR,
                f"执行失败：{name}",
                str(e),
                source=self.name,
            )
            raise
    
    def get_status(self) -> Dict:
        """获取系统状态"""
        return {
            'name': self.name,
            'metrics': self.metrics.get_summary(),
            'alerts': {
                'total': len(self.alerts.alerts),
                'unacknowledged': len(self.alerts.get_unacknowledged()),
                'unresolved': len(self.alerts.get_unresolved()),
            },
            'logs': {
                'total': len(self.logger.entries),
                'errors': len([e for e in self.logger.entries if e.level == LogLevel.ERROR]),
            },
        }


def main():
    """主函数 - 演示"""
    print("="*60)
    print("HE-005~008: 可观测性 + 日志 + 指标 + 告警演示")
    print("="*60)
    
    # 初始化
    obs = Observability("demo")
    
    # 演示 1: 日志
    print("\n1. 日志系统...")
    obs.logger.info("系统启动", version="1.0.0")
    obs.logger.debug("调试信息", key="value")
    obs.logger.warning("警告信息", warning="something")
    obs.logger.error("错误信息", error="error")
    print(f"   日志条目：{len(obs.logger.entries)}")
    
    # 演示 2: 指标
    print("\n2. 指标监控...")
    obs.metrics.gauge("cpu_usage", 45.5, host="server1")
    obs.metrics.gauge("memory_usage", 67.8, host="server1")
    obs.metrics.counter("requests_total", 1, endpoint="/api")
    obs.metrics.counter("requests_total", 1, endpoint="/api")
    obs.metrics.histogram("request_duration_ms", 123.4)
    obs.metrics.histogram("request_duration_ms", 234.5)
    
    summary = obs.metrics.get_summary()
    print(f"   CPU 使用：{summary['gauges'].get('cpu_usage')}%")
    print(f"   内存使用：{summary['gauges'].get('memory_usage')}%")
    print(f"   请求总数：{summary['counters'].get('requests_total')}")
    
    # 演示 3: 告警
    print("\n3. 告警系统...")
    alert_id = obs.alerts.send_alert(
        AlertSeverity.WARNING,
        "CPU 使用率过高",
        "CPU 使用率超过 80%",
        source="monitor",
        host="server1",
    )
    print(f"   发送告警：{alert_id}")
    
    # 确认告警
    obs.alerts.acknowledge_alert(alert_id, "admin")
    print(f"   确认告警：{alert_id}")
    
    # 解决告警
    obs.alerts.resolve_alert(alert_id)
    print(f"   解决告警：{alert_id}")
    
    # 演示 4: 系统状态
    print("\n4. 系统状态...")
    status = obs.get_status()
    print(f"   日志总数：{status['logs']['total']}")
    print(f"   告警总数：{status['alerts']['total']}")
    print(f"   未解决告警：{status['alerts']['unresolved']}")
    
    # 清理
    Path("demo.log").unlink(missing_ok=True)
    
    print("\n" + "="*60)
    print("✅ HE-005~008 演示完成")
    print("="*60)


if __name__ == '__main__':
    main()
