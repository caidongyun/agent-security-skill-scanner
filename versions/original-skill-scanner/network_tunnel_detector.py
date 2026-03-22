#!/usr/bin/env python3
"""
🌐 网络穿透检测模块
==================
检测第三方公开网络穿透方案，识别风险边界破坏

支持检测:
- frp / frpc (Fast Reverse Proxy)
- ngrok / ngrok-agent
- Cloudflare Tunnel (cloudflared)
- Tailscale
- ZeroTier
- nps / npc
- reGeorg / reDuh
- EarthWorm (ew)
- Termux + ssh
- 其他内网穿透工具

风险策略:
- 企业用户：高风险边界破坏，立即阻断 + 告警
- 个人用户：中风险提醒，需用户确认并记录
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime


# ========== 网络穿透工具特征库 ==========

NETWORK_TUNNEL_PATTERNS = {
    # === frp 系列 ===
    "frp": {
        "name": "frp (Fast Reverse Proxy)",
        "risk": "HIGH",
        "patterns": [
            r"frpc\s+(start|reload|verify)",
            r"frps\s+-c",
            r"\.ini.*server_addr",
            r"server_addr\s*=\s*\d+\.\d+\.\d+\.\d+",
            r"token\s*=\s*[a-zA-Z0-9]+",
            r"\[common\].*server_port",
            r"frp\.ini",
            r"frpc\.ini",
            r"./frpc\s+-c",
            r"./frps\s+-c",
        ],
        "files": [
            "frpc.ini",
            "frps.ini",
            "frpc.toml",
            "frps.toml",
        ],
        "ports": [7000, 7001, 6000, 6001],  # 默认端口
        "description": "开源高性能反向代理，常用于内网穿透"
    },
    
    # === ngrok 系列 ===
    "ngrok": {
        "name": "ngrok",
        "risk": "HIGH",
        "patterns": [
            r"ngrok\s+(http|tcp|tls)",
            r"ngrok\s+config",
            r"ngrok\.yml",
            r"ngrok\.yaml",
            r"authtoken\s+[a-zA-Z0-9]+",
            r"region\s+(us|eu|ap|au|sa|jp|in)",
            r"./ngrok\s+http\s+\d+",
            r"ngrok-agent",
        ],
        "files": [
            ".ngrok2/ngrok.yml",
            ".ngrok/ngrok.yml",
        ],
        "ports": [4040, 4443],  # Web 界面端口
        "description": "知名内网穿透工具，提供公开隧道"
    },
    
    # === Cloudflare Tunnel ===
    "cloudflare_tunnel": {
        "name": "Cloudflare Tunnel (cloudflared)",
        "risk": "MEDIUM",
        "patterns": [
            r"cloudflared\s+tunnel",
            r"cloudflared\s+access",
            r"cloudflared\s+login",
            r"tunnel\s+--url",
            r"tunnel\s+run",
            r"credentials-file.*\.json",
            r"tunnel\.json",
            r"config\.yml.*tunnel",
        ],
        "files": [
            ".cloudflared/*.json",
            "config.yml",
        ],
        "ports": [443, 8443],
        "description": "Cloudflare 官方隧道工具，企业常用"
    },
    
    # === Tailscale ===
    "tailscale": {
        "name": "Tailscale",
        "risk": "LOW",
        "patterns": [
            r"tailscale\s+up",
            r"tailscale\s+connect",
            r"tailscale\s+share",
            r"tailscaled",
            r"tsnet",
            r"tailscale.*--login-server",
        ],
        "files": [
            "/var/lib/tailscale/",
            ".tailscale/",
        ],
        "ports": [41641, 8340],
        "description": "基于 WireGuard 的 Mesh VPN，相对安全"
    },
    
    # === ZeroTier ===
    "zerotier": {
        "name": "ZeroTier",
        "risk": "LOW",
        "patterns": [
            r"zerotier-cli\s+join",
            r"zerotier-one",
            r"zerotier-id",
            r"zerotier-network",
        ],
        "files": [
            "/var/lib/zerotier-one/",
            ".zerotier/",
        ],
        "ports": [9993],
        "description": "P2P VPN 网络，开源可控"
    },
    
    # === nps/npc ===
    "nps": {
        "name": "nps (NPS Proxy Server)",
        "risk": "HIGH",
        "patterns": [
            r"nps\s+-config",
            r"npc\s+-server",
            r"nps\.conf",
            r"npc\.conf",
            r"vkey\s*=\s*[a-zA-Z0-9]+",
            r"bridge_port\s*=",
        ],
        "files": [
            "conf/nps.conf",
            "conf/npc.conf",
        ],
        "ports": [8024, 8080, 80],
        "description": "轻量级高性能内网穿透代理"
    },
    
    # === reGeorg/reDuh ===
    "regeorg": {
        "name": "reGeorg/reDuh",
        "risk": "CRITICAL",
        "patterns": [
            r"reGeorg",
            r"reDuh",
            r"tunnel\.(aspx|php|jsp)",
            r"socks\.proxy",
            r"reGeorgSocksProxy",
        ],
        "files": [
            "tunnel.aspx",
            "tunnel.php",
            "tunnel.jsp",
        ],
        "ports": [8080, 1080],
        "description": "渗透测试工具，高风险攻击特征"
    },
    
    # === EarthWorm ===
    "earthworm": {
        "name": "EarthWorm (ew)",
        "risk": "CRITICAL",
        "patterns": [
            r"ew\s+-s",
            r"ew\s+-d",
            r"ew\s+-f",
            r"ew\s+-g",
            r"ew\s+-l",
            r"ew\s+-r",
            r"ew\s+-v",
            r"ew\s+-e",
        ],
        "files": [
            "ew",
            "ew.exe",
        ],
        "ports": [8888, 9999],
        "description": "内网穿透神器，攻击者常用"
    },
    
    # === Termux + ssh ===
    "termux_ssh": {
        "name": "Termux + SSH",
        "risk": "MEDIUM",
        "patterns": [
            r"termux-setup-storage",
            r"pkg\s+install\s+openssh",
            r"sshd\s+start",
            r"ssh\s+root@",
            r"ssh\s+-R",
            r"ssh\s+-L",
            r"ssh\s+-D",
        ],
        "files": [
            ".termux/",
            "com.termux/",
        ],
        "ports": [8022, 22],
        "description": "Android Termux 配合 SSH 穿透"
    },
    
    # === 通用 SOCKS/HTTP 代理 ===
    "proxy_tools": {
        "name": "通用代理工具",
        "risk": "MEDIUM",
        "patterns": [
            r"proxychains",
            r"proxychains\.conf",
            r"socks4\s+\d+\.\d+\.\d+\.\d+",
            r"socks5\s+\d+\.\d+\.\d+\.\d+",
            r"http_proxy\s*=",
            r"https_proxy\s*=",
            r"all_proxy\s*=",
            r"ss-local",
            r"ss-server",
            r"shadowsocks",
        ],
        "files": [
            "proxychains.conf",
        ],
        "ports": [1080, 8080, 8388],
        "description": "通用代理工具，可能用于隐蔽通信"
    },
}


# ========== 风险策略配置 ==========

RISK_POLICY = {
    # 企业用户策略
    "enterprise": {
        "HIGH": {
            "action": "BLOCK",
            "alert": True,
            "log": True,
            "message": "🚨 检测到企业网络边界破坏风险！{tool_name} 可能导致内网暴露，已阻断。"
        },
        "MEDIUM": {
            "action": "WARN",
            "alert": True,
            "log": True,
            "message": "⚠️ 警告：检测到 {tool_name}，可能存在网络边界风险，请确认是否授权。"
        },
        "LOW": {
            "action": "INFO",
            "alert": False,
            "log": True,
            "message": "ℹ️ 提示：检测到 {tool_name}，已记录。"
        },
        "CRITICAL": {
            "action": "BLOCK",
            "alert": True,
            "log": True,
            "escalate": True,
            "message": "🚨🚨 严重威胁！检测到 {tool_name} 攻击工具，立即阻断并上报安全团队！"
        }
    },
    
    # 个人用户策略
    "personal": {
        "HIGH": {
            "action": "CONFIRM",
            "alert": True,
            "log": True,
            "message": "⚠️ 提醒：检测到 {tool_name}，可能暴露您的内网。确认继续使用吗？"
        },
        "MEDIUM": {
            "action": "CONFIRM",
            "alert": False,
            "log": True,
            "message": "ℹ️ 提示：检测到 {tool_name}，请确认是否了解风险。"
        },
        "LOW": {
            "action": "INFO",
            "alert": False,
            "log": False,
            "message": None  # 不提示
        },
        "CRITICAL": {
            "action": "BLOCK",
            "alert": True,
            "log": True,
            "message": "🚨 危险工具！{tool_name} 常用于攻击，已阻断。"
        }
    }
}


class NetworkTunnelDetector:
    """网络穿透检测器"""
    
    def __init__(self, user_type: str = "personal"):
        """
        初始化检测器
        
        Args:
            user_type: 用户类型 ("enterprise" | "personal")
        """
        self.user_type = user_type
        self.policy = RISK_POLICY.get(user_type, RISK_POLICY["personal"])
        self.detection_log = []
        
        # 加载日志文件路径
        self.log_file = Path(__file__).parent / "logs" / "tunnel_detection.log"
        self.log_file.parent.mkdir(exist_ok=True)
    
    def detect(self, input_text: str, file_context: Optional[str] = None) -> Dict:
        """
        检测网络穿透工具
        
        Args:
            input_text: 输入文本
            file_context: 可选的文件路径上下文
        
        Returns:
            {
                "detected": bool,
                "tool_name": str,
                "risk_level": str,
                "action": str,
                "message": str,
                "requires_confirmation": bool
            }
        """
        result = {
            "detected": False,
            "tool_name": None,
            "risk_level": "SAFE",
            "action": "ALLOW",
            "message": None,
            "requires_confirmation": False
        }
        
        # 检测工具匹配
        for tool_id, tool_info in NETWORK_TUNNEL_PATTERNS.items():
            matched = False
            
            # 检查文本模式
            for pattern in tool_info["patterns"]:
                if re.search(pattern, input_text, re.IGNORECASE):
                    matched = True
                    break
            
            # 检查文件上下文
            if not matched and file_context:
                for file_pattern in tool_info["files"]:
                    if file_pattern in file_context:
                        matched = True
                        break
            
            if matched:
                result["detected"] = True
                result["tool_name"] = tool_info["name"]
                result["risk_level"] = tool_info["risk"]
                
                # 获取对应策略
                policy = self.policy.get(tool_info["risk"], self.policy.get("MEDIUM"))
                result["action"] = policy["action"]
                result["requires_confirmation"] = (policy["action"] == "CONFIRM")
                
                # 生成提示消息
                if policy.get("message"):
                    result["message"] = policy["message"].format(
                        tool_name=tool_info["name"],
                        risk=tool_info["risk"],
                        description=tool_info["description"]
                    )
                
                # 记录日志
                if policy.get("log", True):
                    self._log_detection(tool_id, tool_info, input_text, file_context)
                
                # 如果需要告警
                if policy.get("alert", False):
                    self._send_alert(tool_id, tool_info)
                
                break
        
        return result
    
    def _log_detection(self, tool_id: str, tool_info: Dict, 
                       input_text: str, file_context: Optional[str]):
        """记录检测日志"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_type": self.user_type,
            "tool_id": tool_id,
            "tool_name": tool_info["name"],
            "risk_level": tool_info["risk"],
            "input_preview": input_text[:200] if input_text else "",
            "file_context": file_context
        }
        
        self.detection_log.append(log_entry)
        
        # 写入文件
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"日志写入失败：{e}")
    
    def _send_alert(self, tool_id: str, tool_info: Dict):
        """发送告警（可扩展到实际告警系统）"""
        alert = {
            "type": "NETWORK_TUNNEL_DETECTED",
            "severity": tool_info["risk"],
            "tool": tool_info["name"],
            "timestamp": datetime.now().isoformat(),
            "user_type": self.user_type
        }
        
        # 这里可以集成实际告警系统
        # 如：发送邮件、Slack、企业微信等
        print(f"🚨 告警：{json.dumps(alert, ensure_ascii=False)}")
    
    def confirm_action(self, tool_id: str, confirmed: bool) -> Dict:
        """
        处理用户确认
        
        Args:
            tool_id: 工具 ID
            confirmed: 用户是否确认
        
        Returns:
            {
                "allowed": bool,
                "message": str
            }
        """
        if confirmed:
            # 用户确认，记录并允许
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "action": "USER_CONFIRMED",
                "tool_id": tool_id,
                "user_type": self.user_type
            }
            
            # 保存到确认记录
            confirm_log = Path(__file__).parent / "logs" / "user_confirmations.json"
            confirmations = []
            
            if confirm_log.exists():
                with open(confirm_log, "r", encoding="utf-8") as f:
                    confirmations = json.load(f)
            
            confirmations.append(log_entry)
            
            with open(confirm_log, "w", encoding="utf-8") as f:
                json.dump(confirmations, f, indent=2, ensure_ascii=False)
            
            return {
                "allowed": True,
                "message": "✅ 已记录您的确认，继续执行。"
            }
        else:
            # 用户拒绝，阻断
            return {
                "allowed": False,
                "message": "❌ 已取消操作。"
            }
    
    def get_detection_stats(self) -> Dict:
        """获取检测统计"""
        total = len(self.detection_log)
        by_tool = {}
        by_risk = {}
        
        for entry in self.detection_log:
            tool = entry["tool_id"]
            risk = entry["risk_level"]
            
            by_tool[tool] = by_tool.get(tool, 0) + 1
            by_risk[risk] = by_risk.get(risk, 0) + 1
        
        return {
            "total_detections": total,
            "by_tool": by_tool,
            "by_risk": by_risk,
            "user_type": self.user_type
        }


# ========== 导出函数 ==========

def detect_tunnel(input_text: str, user_type: str = "personal", 
                  file_context: Optional[str] = None) -> Dict:
    """
    快捷检测函数
    
    Args:
        input_text: 输入文本
        user_type: 用户类型 ("enterprise" | "personal")
        file_context: 文件上下文
    
    Returns:
        检测结果字典
    """
    detector = NetworkTunnelDetector(user_type=user_type)
    return detector.detect(input_text, file_context)


if __name__ == "__main__":
    # 测试
    print("=" * 60)
    print("🌐 网络穿透检测测试")
    print("=" * 60)
    
    test_cases = [
        # frp 测试
        ("frpc start -c frpc.ini", "enterprise"),
        ("./frpc -c frpc.ini", "personal"),
        
        # ngrok 测试
        ("ngrok http 8080", "enterprise"),
        ("ngrok http 8080", "personal"),
        
        # Tailscale 测试
        ("tailscale up --login-server https://myserver.com", "enterprise"),
        
        # EarthWorm 测试 (CRITICAL)
        ("ew -s rcsocks -l 1080 -e 8888", "enterprise"),
        ("ew -s rcsocks -l 1080 -e 8888", "personal"),
        
        # SSH 反向隧道
        ("ssh -R 8080:localhost:80 user@remote.com", "personal"),
    ]
    
    for input_text, user_type in test_cases:
        result = detect_tunnel(input_text, user_type=user_type)
        print(f"\n输入：{input_text}")
        print(f"用户类型：{user_type}")
        print(f"结果：{json.dumps(result, ensure_ascii=False, indent=2)}")
    
    print("\n" + "=" * 60)
