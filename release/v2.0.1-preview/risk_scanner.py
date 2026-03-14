#!/usr/bin/env python3
"""
Risk Scanner - 风险行为扫描器
基于 RISK_RULES.md 实现 9 大类危险行为检测
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass, field
from enum import Enum


class RiskLevel(Enum):
    """风险等级"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ActionType(Enum):
    """处置动作"""
    ALLOW = "ALLOW"  # 允许执行
    WARN = "WARN"  # 警告 + 记录
    BLOCK = "BLOCK"  # 拦截 + 告警
    TERMINATE = "TERMINATE"  # 立即终止


@dataclass
class RiskFinding:
    """风险发现"""
    rule_id: str
    category: str
    risk_level: RiskLevel
    score: int
    description: str
    evidence: str
    line_number: int = 0


@dataclass
class RiskResult:
    """风险评估结果"""
    total_score: int = 0
    risk_level: RiskLevel = RiskLevel.LOW
    action: ActionType = ActionType.ALLOW
    findings: List[RiskFinding] = field(default_factory=list)
    summary: Dict = field(default_factory=dict)


class RiskScanner:
    """风险扫描器"""

    def __init__(self, rules_file: str = None):
        self.rules = self._load_rules(rules_file)
        self.findings = []

    def _load_rules(self, rules_file: str = None) -> Dict:
        """加载风险规则"""
        if rules_file is None:
            rules_file = Path(__file__).parent / "rules" / "RISK_RULES.md"

        # 内置规则 (基于 RISK_RULES.md)
        rules = {
            "credential_theft": {
                "risk_level": RiskLevel.CRITICAL,
                "base_score": 50,
                "patterns": [
                    r"open\s*\(\s*['\"]~?/\.ssh/",
                    r"open\s*\(\s*['\"]~?/\.aws/",
                    r"open\s*\(\s*['\"]~?/\.config/",
                    r"os\.environ\s*\[\s*['\"](.*KEY|.*SECRET|.*TOKEN|.*PASSWORD)",
                    r"glob\s*\(\s*['\"].*\.ssh/",
                    r"~?/\.ssh/id_rsa",
                    r"~?/\.aws/credentials",
                    r"~?/\.config/gcloud",
                    r"~?/\.azure",
                    r"\.env",
                    r"~?/\.netrc",
                    r"~?/\.git-credentials",
                    r"~?/\.npmrc",
                    r"~?/\.pypirc",
                    r"kubeconfig",
                    r"docker.*config\.json",
                ]
            },
            "data_exfiltration": {
                "risk_level": RiskLevel.CRITICAL,
                "base_score": 50,
                "patterns": [
                    r"curl\s+.*-d\s+@",
                    r"curl\s+.*-X\s+POST",
                    r"wget\s+.*--post-",
                    r"requests\.post\s*\([^)]*http",
                    r"urllib\.request\.urlopen\s*\([^)]*http",
                    r"dns\.query\s*\([^)]*TXT",
                    r"icmp.*send",
                    r"hooks\.slack\.com",
                    r"discordapp\.com/api/webhooks",
                    r"s3\.amazonaws\.com.*PUT",
                    r"telegram\.org/bot.*sendMessage",
                    r"pastebin\.com/api",
                ]
            },
            "identity_hijack": {
                "risk_level": RiskLevel.CRITICAL,
                "base_score": 50,
                "patterns": [
                    r"open\s*\(\s*['\"]SOUL\.md['\"]",
                    r"open\s*\(\s*['\"]IDENTITY\.md['\"]",
                    r"open\s*\(\s*['\"]USER\.md['\"]",
                    r"open\s*\(\s*['\"]HEARTBEAT\.md['\"]",
                    r"open\s*\(\s*['\"]MEMORY\.md['\"]",
                    r"write\s*\(\s*['\"]SOUL\.md['\"]",
                    r"edit\s*\(\s*['\"]IDENTITY\.md['\"]",
                    r"system_prompt\s*=",
                    r"persona\s*=",
                    r"role\s*=\s*['\"]malicious",
                ]
            },
            "code_injection": {
                "risk_level": RiskLevel.CRITICAL,
                "base_score": 50,
                "patterns": [
                    r"eval\s*\(\s*user",
                    r"eval\s*\(\s*input",
                    r"exec\s*\(\s*user",
                    r"exec\s*\(\s*input",
                    r"os\.system\s*\([^)]*\$",
                    r"os\.system\s*\([^)]*%",
                    r"subprocess.*shell\s*=\s*True",
                    r"pickle\.loads\s*\(",
                    r"yaml\.load\s*\([^)]*Loader",
                    r"__import__\s*\([^)]*\$",
                    r"getattr\s*\([^)]*\$",
                    r"compile\s*\([^)]*exec",
                ]
            },
            "covert_communication": {
                "risk_level": RiskLevel.HIGH,
                "base_score": 30,
                "patterns": [
                    r"http://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}",
                    r"https://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}",
                    r"socket\.connect\s*\(\s*\(\s*['\"]\d{1,3}\.",
                    r"requests\..*\d{1,3}\.\d{1,3}\.",
                    r":\s*4444",
                    r":\s*5555",
                    r":\s*6666",
                    r":\s*7777",
                    r":\s*8080",
                    r":\s*9999",
                    r"requests\..*verify\s*=\s*False",
                    r"ssl\.wrap_socket\s*\([^)]*unknown",
                ]
            },
            "privilege_escalation": {
                "risk_level": RiskLevel.HIGH,
                "base_score": 30,
                "patterns": [
                    r"sudo\s+",
                    r"su\s+-",
                    r"chmod\s+\+s",
                    r"chmod\s+4777",
                    r"chmod\s+777",
                    r"usermod\s+-aG\s+sudo",
                    r"passwd\s+root",
                    r"/etc/sudoers",
                    r"pkexec",
                    r"doas",
                ]
            },
            "obfuscation": {
                "risk_level": RiskLevel.HIGH,
                "base_score": 30,
                "patterns": [
                    r"base64\.b64decode\s*\([^)]*\)",
                    r"exec\s*\(\s*base64",
                    r"eval\s*\(\s*base64",
                    r"zlib\.decompress\s*\(",
                    r"gzip\.decompress\s*\(",
                    r"chr\s*\(\s*0x",
                    r"\\x[0-9a-f]{2}",
                    r"\\u[0-9a-f]{4}",
                    r"str_rot13\s*\(",
                    r"xor\s*\(",
                    r"AES\.new\s*\(",
                    r"RC4\s*\(",
                ]
            },
            "system_destruction": {
                "risk_level": RiskLevel.CRITICAL,
                "base_score": 50,
                "patterns": [
                    r"rm\s+-rf\s+/",
                    r"rm\s+-rf\s+\*",
                    r"shred\s+",
                    r"dd\s+if=/dev/zero",
                    r"mkfs\.",
                    r"> /etc/passwd",
                    r"> /etc/shadow",
                    r"rm\s+.*\.log",
                    r"history\s+-c",
                    r"systemctl\s+stop\s+ssh",
                    r"ufw\s+disable",
                    r"selinux.*disable",
                ]
            },
            "session_hijack": {
                "risk_level": RiskLevel.CRITICAL,
                "base_score": 50,
                "patterns": [
                    r"browser\.get_cookies\s*\(",
                    r"document\.cookie",
                    r"localStorage\.",
                    r"sessionStorage\.",
                    r"indexedDB\.",
                    r"~?/\.mozilla/firefox.*cookies",
                    r"~?/\.config/google-chrome.*Cookies",
                    r"~?/\.config/chromium.*Cookies",
                    r"Login\s+Data",
                    r"webapps\.sqlite",
                    r"jwt.*token",
                    r"oauth.*token",
                    r"session.*token",
                ]
            },
        }

        return rules

    def scan(self, code: str) -> RiskResult:
        """扫描代码"""
        self.findings = []
        result = RiskResult()

        # 逐类扫描
        for category, rule in self.rules.items():
            findings = self._scan_category(code, category, rule)
            self.findings.extend(findings)

        # 计算总分
        result.findings = self.findings
        result.total_score = sum(f.score for f in self.findings)

        # 确定风险等级
        result.risk_level = self._calculate_risk_level(result.total_score)

        # 确定处置动作
        result.action = self._determine_action(result.risk_level)

        # 生成摘要
        result.summary = self._generate_summary()

        return result

    def _scan_category(self, code: str, category: str, rule: Dict) -> List[RiskFinding]:
        """扫描单个类别"""
        findings = []

        for pattern in rule["patterns"]:
            matches = re.finditer(pattern, code, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                # 计算行号
                line_number = code[:match.start()].count('\n') + 1

                finding = RiskFinding(
                    rule_id=f"{category.upper()}-{len(findings)+1:03d}",
                    category=category,
                    risk_level=rule["risk_level"],
                    score=rule["base_score"],
                    description=f"检测到 {category} 风险行为",
                    evidence=match.group(0)[:100],
                    line_number=line_number
                )
                findings.append(finding)

        return findings

    def _calculate_risk_level(self, total_score: int) -> RiskLevel:
        """计算风险等级"""
        if total_score == 0:
            return RiskLevel.LOW
        elif total_score <= 30:
            return RiskLevel.LOW
        elif total_score <= 60:
            return RiskLevel.MEDIUM
        elif total_score <= 100:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL

    def _determine_action(self, risk_level: RiskLevel) -> ActionType:
        """确定处置动作"""
        action_map = {
            RiskLevel.LOW: ActionType.ALLOW,
            RiskLevel.MEDIUM: ActionType.WARN,
            RiskLevel.HIGH: ActionType.BLOCK,
            RiskLevel.CRITICAL: ActionType.TERMINATE,
        }
        return action_map.get(risk_level, ActionType.WARN)

    def _generate_summary(self) -> Dict:
        """生成摘要"""
        summary = {
            "total_findings": len(self.findings),
            "by_category": {},
            "by_risk_level": {
                "CRITICAL": 0,
                "HIGH": 0,
                "MEDIUM": 0,
                "LOW": 0,
            }
        }

        for finding in self.findings:
            # 按类别统计
            cat = finding.category
            if cat not in summary["by_category"]:
                summary["by_category"][cat] = 0
            summary["by_category"][cat] += 1

            # 按风险等级统计
            level = finding.risk_level.value
            summary["by_risk_level"][level] += 1

        return summary

    def print_report(self, result: RiskResult):
        """打印报告"""
        print("\n" + "="*60)
        print("🔍 风险扫描报告")
        print("="*60)
        print()
        print(f"总风险评分：{result.total_score}")
        print(f"风险等级：{self._get_emoji(result.risk_level)} {result.risk_level.value}")
        print(f"处置动作：{self._get_action_emoji(result.action)} {result.action.value}")
        print()

        if result.findings:
            print(f"发现 {len(result.findings)} 个风险项:")
            print()

            # 按风险等级排序
            sorted_findings = sorted(
                result.findings,
                key=lambda x: x.risk_level.value,
                reverse=True
            )

            for i, finding in enumerate(sorted_findings[:10], 1):  # 只显示前 10 个
                print(f"{i}. {self._get_emoji(finding.risk_level)} [{finding.category}]")
                print(f"   规则：{finding.rule_id}")
                print(f"   证据：{finding.evidence}")
                print(f"   行号：{finding.line_number}")
                print()

        print("="*60)

    def _get_emoji(self, risk_level: RiskLevel) -> str:
        """获取风险等级 emoji"""
        emoji_map = {
            RiskLevel.CRITICAL: "🔴",
            RiskLevel.HIGH: "🟠",
            RiskLevel.MEDIUM: "🟡",
            RiskLevel.LOW: "🟢",
        }
        return emoji_map.get(risk_level, "⚪")

    def _get_action_emoji(self, action: ActionType) -> str:
        """获取处置动作 emoji"""
        emoji_map = {
            ActionType.TERMINATE: "🛑",
            ActionType.BLOCK: "🚫",
            ActionType.WARN: "⚠️",
            ActionType.ALLOW: "✅",
        }
        return emoji_map.get(action, "❓")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="Risk Scanner - 风险行为扫描器")
    parser.add_argument("--file", "-f", help="扫描文件")
    parser.add_argument("--code", "-c", help="扫描代码字符串")
    parser.add_argument("--json", "-j", action="store_true", help="JSON 输出")

    args = parser.parse_args()

    scanner = RiskScanner()

    # 获取代码
    if args.file:
        with open(args.file, "r") as f:
            code = f.read()
    elif args.code:
        code = args.code
    else:
        # 从 stdin 读取
        code = sys.stdin.read()

    # 扫描
    result = scanner.scan(code)

    # 输出
    if args.json:
        print(json.dumps({
            "total_score": result.total_score,
            "risk_level": result.risk_level.value,
            "action": result.action.value,
            "findings": [
                {
                    "rule_id": f.rule_id,
                    "category": f.category,
                    "risk_level": f.risk_level.value,
                    "score": f.score,
                    "description": f.description,
                    "evidence": f.evidence,
                    "line_number": f.line_number
                }
                for f in result.findings
            ],
            "summary": result.summary
        }, indent=2))
    else:
        scanner.print_report(result)

    # 返回码
    if result.action == ActionType.TERMINATE:
        return 3
    elif result.action == ActionType.BLOCK:
        return 2
    elif result.action == ActionType.WARN:
        return 1
    else:
        return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
