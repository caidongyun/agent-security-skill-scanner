#!/usr/bin/env python3
"""
HE-003: 安全护栏
Guardrails AI 集成，权限控制，安全审计
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum


class RiskLevel(Enum):
    """风险等级"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class PermissionType(Enum):
    """权限类型"""
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    ADMIN = "admin"


@dataclass
class SecurityRule:
    """安全规则"""
    id: str
    name: str
    description: str
    pattern: str
    risk_level: RiskLevel
    action: str  # allow, deny, warn
    enabled: bool = True


@dataclass
class AuditLog:
    """审计日志"""
    id: str
    timestamp: str
    user_id: str
    action: str
    resource: str
    result: str  # success, denied, warning
    risk_level: Optional[RiskLevel] = None
    details: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'timestamp': self.timestamp,
            'user_id': self.user_id,
            'action': self.action,
            'resource': self.resource,
            'result': self.result,
            'risk_level': self.risk_level.value if self.risk_level else None,
            'details': self.details,
        }


class Guardrails:
    """安全护栏"""
    
    def __init__(self, rules_file: str = "security_rules.json"):
        self.rules: Dict[str, SecurityRule] = {}
        self.rules_file = Path(rules_file)
        self.audit_logs: List[AuditLog] = []
        self._load_rules()
    
    def _load_rules(self):
        """加载安全规则"""
        if self.rules_file.exists():
            with open(self.rules_file) as f:
                data = json.load(f)
                for rule_data in data.get('rules', []):
                    rule = SecurityRule(
                        id=rule_data['id'],
                        name=rule_data['name'],
                        description=rule_data['description'],
                        pattern=rule_data['pattern'],
                        risk_level=RiskLevel(rule_data['risk_level']),
                        action=rule_data['action'],
                        enabled=rule_data.get('enabled', True),
                    )
                    self.rules[rule.id] = rule
        else:
            self._init_default_rules()
    
    def _init_default_rules(self):
        """初始化默认规则"""
        default_rules = [
            SecurityRule(
                id="rule_001",
                name="禁止危险命令执行",
                description="禁止执行 rm -rf 等危险命令",
                pattern=r"rm\s+-rf\s+/",
                risk_level=RiskLevel.CRITICAL,
                action="deny",
            ),
            SecurityRule(
                id="rule_002",
                name="禁止敏感文件访问",
                description="禁止访问/etc/passwd 等敏感文件",
                pattern=r"/etc/(passwd|shadow|sudoers)",
                risk_level=RiskLevel.HIGH,
                action="deny",
            ),
            SecurityRule(
                id="rule_003",
                name="警告：网络请求",
                description="网络请求需要记录日志",
                pattern=r"(requests|urllib|socket)\.",
                risk_level=RiskLevel.MEDIUM,
                action="warn",
            ),
        ]
        
        for rule in default_rules:
            self.rules[rule.id] = rule
        
        # 保存默认规则
        self._save_rules()
    
    def _save_rules(self):
        """保存规则"""
        data = {
            'rules': [
                {
                    'id': rule.id,
                    'name': rule.name,
                    'description': rule.description,
                    'pattern': rule.pattern,
                    'risk_level': rule.risk_level.value,
                    'action': rule.action,
                    'enabled': rule.enabled,
                }
                for rule in self.rules.values()
            ]
        }
        
        with open(self.rules_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def validate(self, content: str, user_id: str = "anonymous",
                resource: str = "unknown") -> tuple[bool, Optional[str]]:
        """验证内容"""
        import re
        
        for rule in self.rules.values():
            if not rule.enabled:
                continue
            
            if re.search(rule.pattern, content):
                # 记录审计日志
                self._log_audit(
                    user_id=user_id,
                    action="validate",
                    resource=resource,
                    result="denied" if rule.action == "deny" else "warning",
                    risk_level=rule.risk_level,
                    details={
                        'rule_id': rule.id,
                        'rule_name': rule.name,
                        'matched_pattern': rule.pattern,
                    },
                )
                
                if rule.action == "deny":
                    return False, f"违反安全规则：{rule.name}"
                elif rule.action == "warn":
                    # 警告但允许
                    pass
        
        return True, None
    
    def _log_audit(self, user_id: str, action: str, resource: str,
                  result: str, risk_level: Optional[RiskLevel] = None,
                  details: Dict = None):
        """记录审计日志"""
        log = AuditLog(
            id=hashlib.md5(f"{user_id}{action}{datetime.now().isoformat()}".encode()).hexdigest()[:16],
            timestamp=datetime.now().isoformat(),
            user_id=user_id,
            action=action,
            resource=resource,
            result=result,
            risk_level=risk_level,
            details=details or {},
        )
        self.audit_logs.append(log)
    
    def get_audit_logs(self, user_id: Optional[str] = None,
                      limit: int = 100) -> List[Dict]:
        """获取审计日志"""
        logs = self.audit_logs
        if user_id:
            logs = [log for log in logs if log.user_id == user_id]
        
        return [log.to_dict() for log in logs[-limit:]]
    
    def export_audit_logs(self, filename: str = "audit_logs.json"):
        """导出审计日志"""
        with open(filename, 'w') as f:
            json.dump([log.to_dict() for log in self.audit_logs], f, indent=2)


class PermissionManager:
    """权限管理器"""
    
    def __init__(self):
        self.permissions: Dict[str, Dict[str, List[PermissionType]]] = {}
    
    def grant_permission(self, user_id: str, resource: str,
                        permission: PermissionType):
        """授予权限"""
        if user_id not in self.permissions:
            self.permissions[user_id] = {}
        
        if resource not in self.permissions[user_id]:
            self.permissions[user_id][resource] = []
        
        if permission not in self.permissions[user_id][resource]:
            self.permissions[user_id][resource].append(permission)
    
    def revoke_permission(self, user_id: str, resource: str,
                         permission: PermissionType):
        """撤销权限"""
        if user_id in self.permissions and resource in self.permissions[user_id]:
            if permission in self.permissions[user_id][resource]:
                self.permissions[user_id][resource].remove(permission)
    
    def check_permission(self, user_id: str, resource: str,
                        permission: PermissionType) -> bool:
        """检查权限"""
        if user_id not in self.permissions:
            return False
        
        if resource not in self.permissions[user_id]:
            return False
        
        return permission in self.permissions[user_id][resource]
    
    def has_admin(self, user_id: str) -> bool:
        """检查是否管理员"""
        return self.check_permission(user_id, "*", PermissionType.ADMIN)


def main():
    """主函数 - 演示"""
    print("="*60)
    print("HE-003: 安全护栏演示")
    print("="*60)
    
    # 初始化
    guardrails = Guardrails()
    perm_manager = PermissionManager()
    
    # 演示 1: 验证安全规则
    print("\n1. 验证安全规则...")
    
    # 正常内容
    valid, error = guardrails.validate("print('hello')", "user1", "code.py")
    print(f"   正常代码：{'✅ 通过' if valid else f'❌ {error}'}")
    
    # 危险内容
    valid, error = guardrails.validate("rm -rf /", "user1", "code.py")
    print(f"   危险命令：{'✅ 通过' if valid else f'❌ {error}'}")
    
    # 演示 2: 权限管理
    print("\n2. 权限管理...")
    
    # 授予权限
    perm_manager.grant_permission("user1", "file1.txt", PermissionType.READ)
    perm_manager.grant_permission("user1", "file1.txt", PermissionType.WRITE)
    perm_manager.grant_permission("admin1", "*", PermissionType.ADMIN)
    
    # 检查权限
    print(f"   user1 读 file1.txt: {perm_manager.check_permission('user1', 'file1.txt', PermissionType.READ)}")
    print(f"   user1 写 file1.txt: {perm_manager.check_permission('user1', 'file1.txt', PermissionType.WRITE)}")
    print(f"   user1 执行 file1.txt: {perm_manager.check_permission('user1', 'file1.txt', PermissionType.EXECUTE)}")
    print(f"   admin1 管理员：{perm_manager.has_admin('admin1')}")
    
    # 演示 3: 审计日志
    print("\n3. 审计日志...")
    
    logs = guardrails.get_audit_logs()
    print(f"   审计日志数量：{len(logs)}")
    for log in logs[:3]:
        print(f"   - {log['timestamp']}: {log['action']} ({log['result']})")
    
    # 导出审计日志
    guardrails.export_audit_logs("demo_audit_logs.json")
    print(f"   已导出到 demo_audit_logs.json")
    
    # 清理
    Path("demo_audit_logs.json").unlink(missing_ok=True)
    
    print("\n" + "="*60)
    print("✅ HE-003 安全护栏演示完成")
    print("="*60)


if __name__ == '__main__':
    main()
