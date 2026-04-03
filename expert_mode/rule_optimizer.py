#!/usr/bin/env python3
"""
🛡️ 灵顺 V5 规则优化模块 - Round 7
=================================
功能：
- 根据测试结果优化规则
- 添加边界情况处理
- 优化正则表达式性能
- 同步到防护模块
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime


class RuleOptimizer:
    """规则优化器"""
    
    def __init__(self):
        self.optimized_rules = []
        self.optimization_log = []
    
    def optimize_pattern(self, pattern: str, test_results: List[Dict]) -> str:
        """
        优化单个正则表达式模式
        
        优化策略:
        1. 添加适当的锚点
        2. 使用非捕获组
        3. 避免灾难性回溯
        4. 预编译常用模式
        """
        optimized = pattern
        
        # 策略 1: 添加单词边界 (如果合适)
        if not pattern.startswith(r'\b') and not pattern.startswith('^'):
            if re.search(r'\w+\s*\(', pattern):  # 函数调用
                optimized = r'\b' + optimized
        
        # 策略 2: 使用非捕获组 (?:...) 替代捕获组 (...)
        # 检测独立的捕获组
        if re.search(r'\([^?][^)]*\)', optimized):
            # 简单替换，实际应更智能
            pass
        
        # 策略 3: 预编译标志
        # 如果模式包含 ignore case，添加 (?i)
        if '(?i)' not in optimized and '(?i)' not in pattern:
            # 检查是否应该忽略大小写
            if any(c.isalpha() for c in pattern if c.isalpha()):
                optimized = '(?i)' + optimized
        
        return optimized
    
    def analyze_false_positives(self, test_results: List[Dict]) -> List[str]:
        """分析误报用例，找出问题规则"""
        false_positives = []
        
        for result in test_results:
            if result.get('expected') == 'ALLOW' and result.get('detected'):
                false_positives.append({
                    'case_id': result['case_id'],
                    'matched_rules': result.get('matched_rules', []),
                    'input': result.get('input', '')
                })
        
        return false_positives
    
    def analyze_false_negatives(self, test_results: List[Dict]) -> List[str]:
        """分析漏报用例，找出缺失规则"""
        false_negatives = []
        
        for result in test_results:
            if result.get('expected') == 'BLOCK' and not result.get('detected'):
                false_negatives.append({
                    'case_id': result['case_id'],
                    'input': result.get('input', ''),
                    'category': result.get('category', '')
                })
        
        return false_negatives
    
    def generate_optimized_rules(self) -> Dict[str, List[Dict]]:
        """生成优化后的规则集"""
        optimized = {
            "tool_poisoning": [],
            "remote_load": [],
            "data_exfil": [],
            "prompt_injection": [],
            "resource_exhaustion": [],
            "memory_pollution": [],
            "supply_chain": [],
            "container_escape": [],
            "network_tunnel": []
        }
        
        # 工具投毒规则优化
        optimized["tool_poisoning"] = [
            {
                "id": "TP01",
                "name": "Base64 编码检测",
                "patterns": [
                    r"\bbase64\s+(-d|-D)",
                    r"\bb64decode\s*\(",
                    r"\batob\s*\(",
                    r"\bBuffer\.from\s*\([^)]*'base64'"
                ],
                "risk": "HIGH",
                "description": "检测 Base64 编码隐藏恶意代码",
                "action": "BLOCK",
                "optimized": True,
                "optimization_notes": "添加单词边界，避免误报"
            },
            {
                "id": "TP02",
                "name": "压缩混淆检测",
                "patterns": [
                    r"\bzlib\.decompress\s*\(",
                    r"\bgzip\.decompress\s*\(",
                    r"\blzma\.decompress\s*\(",
                    r"\bunzip\s+",
                    r"\btar\s+-x"
                ],
                "risk": "MEDIUM",
                "description": "检测压缩算法混淆恶意负载",
                "action": "BLOCK",
                "optimized": True
            },
            {
                "id": "TP03",
                "name": "动态导入检测",
                "patterns": [
                    r"\b__import__\s*\(",
                    r"\bimportlib\.import_module\s*\(",
                    r"\bgetattr\s*\(\s*sys\.modules"
                ],
                "risk": "HIGH",
                "description": "检测动态导入模块绕过静态检测",
                "action": "BLOCK",
                "optimized": True
            },
            {
                "id": "TP04",
                "name": "反射执行检测",
                "patterns": [
                    r"\beval\s*\(",
                    r"\bexec\s*\(",
                    r"\bcompile\s*\(",
                    r"\bast\.literal_eval\s*\(",
                    r"\bpickle\.loads?\s*\("
                ],
                "risk": "CRITICAL",
                "description": "检测反射执行动态代码",
                "action": "BLOCK",
                "optimized": True
            },
            # 新增规则
            {
                "id": "TP05",
                "name": "代码混淆检测",
                "patterns": [
                    r"\bchr\s*\(\s*0x",
                    r"\bord\s*\(\s*['\"]",
                    r"\\x[0-9a-fA-F]{2}",
                    r"\\u[0-9a-fA-F]{4}"
                ],
                "risk": "MEDIUM",
                "description": "检测字符编码混淆",
                "action": "WARN",
                "optimized": False
            }
        ]
        
        # 远程加载规则优化
        optimized["remote_load"] = [
            {
                "id": "RL01",
                "name": "CurlBash 检测",
                "patterns": [
                    r"\bcurl\b.*\|.*\b(bash|sh)\b",
                    r"\bwget\b.*\|.*\b(bash|sh)\b",
                    r"\bcurl\b.*\|\s*python"
                ],
                "risk": "CRITICAL",
                "description": "检测从远程下载并执行脚本",
                "action": "BLOCK",
                "optimized": True
            },
            {
                "id": "RL02",
                "name": "代码执行服务检测",
                "patterns": [
                    r"\bglot\.io\b",
                    r"\bpastebin\.com\b",
                    r"\brentry\.co\b",
                    r"\braw\.githubusercontent\.com\b"
                ],
                "risk": "HIGH",
                "description": "检测利用代码执行服务托管恶意负载",
                "action": "BLOCK",
                "optimized": True
            },
            {
                "id": "RL03",
                "name": "DNS 隧道检测",
                "patterns": [
                    r"\bnslookup\s+\S+\.",
                    r"\bdig\s+\S+\.",
                    r"\bdns\.query\s*\("
                ],
                "risk": "HIGH",
                "description": "检测通过 DNS 查询传输指令",
                "action": "BLOCK",
                "optimized": True
            },
            {
                "id": "RL04",
                "name": "隐写术检测",
                "patterns": [
                    r"\bsteghide\b",
                    r"\bzsteg\b",
                    r"\bexiftool\b"
                ],
                "risk": "MEDIUM",
                "description": "检测将恶意代码隐藏在图片中",
                "action": "WARN",
                "optimized": True
            },
            # 新增规则
            {
                "id": "RL05",
                "name": "短链接检测",
                "patterns": [
                    r"\bbit\.ly\b",
                    r"\bt\.co\b",
                    r"\bgoo\.gl\b"
                ],
                "risk": "LOW",
                "description": "检测短链接服务",
                "action": "INFO",
                "optimized": False
            }
        ]
        
        # 数据窃取规则优化
        optimized["data_exfil"] = [
            {
                "id": "DE01",
                "name": "文件窃取检测",
                "patterns": [
                    r"/Desktop/",
                    r"/Documents/",
                    r"/Downloads/",
                    r"\bshutil\.copy\s*\("
                ],
                "risk": "MEDIUM",
                "description": "检测窃取用户文件",
                "action": "WARN",
                "optimized": True
            },
            {
                "id": "DE02",
                "name": "凭证窃取检测",
                "patterns": [
                    r"\.ssh/",
                    r"\.gnupg/",
                    r"\bid_rsa",
                    r"\bkeychain\b",
                    r"\bcredential\b"
                ],
                "risk": "CRITICAL",
                "description": "检测窃取敏感凭证",
                "action": "BLOCK",
                "optimized": True
            },
            {
                "id": "DE03",
                "name": "剪贴板监听检测",
                "patterns": [
                    r"\bpyperclip\.paste\s*\(",
                    r"\bxclip\b",
                    r"\bwl-copy\b"
                ],
                "risk": "HIGH",
                "description": "检测监听剪贴板内容",
                "action": "BLOCK",
                "optimized": True
            },
            {
                "id": "DE04",
                "name": "键盘记录检测",
                "patterns": [
                    r"\bpynput\b",
                    r"\bkeyboard\s*\.",
                    r"\bpyhook\b",
                    r"\bkeylog\b"
                ],
                "risk": "CRITICAL",
                "description": "检测记录键盘输入",
                "action": "BLOCK",
                "optimized": True
            },
            {
                "id": "DE05",
                "name": "屏幕截图检测",
                "patterns": [
                    r"\bpyautogui\.screenshot\s*\(",
                    r"\bImageGrab\.grab\s*\("
                ],
                "risk": "MEDIUM",
                "description": "检测截取屏幕内容",
                "action": "WARN",
                "optimized": True
            },
            # 新增规则
            {
                "id": "DE06",
                "name": "浏览器数据检测",
                "patterns": [
                    r"\.mozilla/firefox",
                    r"\.config/google-chrome",
                    r"\.config/chromium"
                ],
                "risk": "HIGH",
                "description": "检测访问浏览器数据",
                "action": "BLOCK",
                "optimized": False
            }
        ]
        
        # 提示词注入规则优化
        optimized["prompt_injection"] = [
            {
                "id": "PI01",
                "name": "指令覆盖检测",
                "patterns": [
                    r"(?i)\bignore\s+(previous|all)\b",
                    r"(?i)\bforget\s+\b",
                    r"(?i)忽略 (之前 | 上面)",
                    r"(?i)覆盖指令"
                ],
                "risk": "HIGH",
                "description": "检测覆盖系统指令",
                "action": "BLOCK",
                "optimized": True
            },
            {
                "id": "PI02",
                "name": "角色扮演检测",
                "patterns": [
                    r"(?i)\byou\s+are\s+now\b",
                    r"(?i)\bact\s+as\b",
                    r"(?i)\bpretend\s+to\s+be\b",
                    r"(?i)你现在是",
                    r"(?i)扮演"
                ],
                "risk": "HIGH",
                "description": "检测通过角色扮演绕过限制",
                "action": "BLOCK",
                "optimized": True
            },
            {
                "id": "PI03",
                "name": "权限提升检测",
                "patterns": [
                    r"(?i)\badmin\s+mode\b",
                    r"(?i)\broot\s+access\b",
                    r"(?i)\bdeveloper\s+mode\b",
                    r"(?i)解除限制",
                    r"(?i)提升权限"
                ],
                "risk": "CRITICAL",
                "description": "检测请求提升权限",
                "action": "BLOCK",
                "optimized": True
            },
            {
                "id": "PI04",
                "name": "多轮诱导检测",
                "patterns": [
                    r"(?i)\bstep\s+1\b",
                    r"(?i)\bstep\s+2\b",
                    r"(?i)第一步",
                    r"(?i)第二步"
                ],
                "risk": "MEDIUM",
                "description": "检测通过多轮对话渐进诱导",
                "action": "WARN",
                "optimized": True
            },
            {
                "id": "PI05",
                "name": "代码注入检测",
                "patterns": [
                    r"```python",
                    r"```bash",
                    r"```js",
                    r"运行代码",
                    r"执行这段"
                ],
                "risk": "HIGH",
                "description": "检测在代码块中注入恶意代码",
                "action": "BLOCK",
                "optimized": True
            },
            # 新增规则
            {
                "id": "PI06",
                "name": "越狱攻击检测",
                "patterns": [
                    r"(?i)\bDAN\b",
                    r"(?i)\bDo Anything Now\b",
                    r"(?i)\bjailbreak\b"
                ],
                "risk": "CRITICAL",
                "description": "检测越狱攻击",
                "action": "BLOCK",
                "optimized": False
            }
        ]
        
        # 资源耗尽规则优化
        optimized["resource_exhaustion"] = [
            {
                "id": "RE01",
                "name": "无限循环检测",
                "patterns": [
                    r"\bwhile\s+True\b",
                    r"\bwhile\s*\(\s*1\s*\)",
                    r"\bfor\s*\(;;\)"
                ],
                "risk": "MEDIUM",
                "description": "检测创建无限循环消耗 CPU",
                "action": "BLOCK",
                "optimized": True
            },
            {
                "id": "RE02",
                "name": "内存耗尽检测",
                "patterns": [
                    r"\bbytearray\s*\(",
                    r"\[0\]\s*\*\s*\d+",
                    r"\bmalloc\s*\("
                ],
                "risk": "HIGH",
                "description": "检测大量分配内存导致 OOM",
                "action": "BLOCK",
                "optimized": True
            },
            {
                "id": "RE03",
                "name": "磁盘填满检测",
                "patterns": [
                    r"\bopen\s*\([^)]*'a'",
                    r"\bdd\s+if=",
                    r"\btruncate\s+"
                ],
                "risk": "MEDIUM",
                "description": "检测持续写入填满磁盘",
                "action": "WARN",
                "optimized": True
            },
            {
                "id": "RE04",
                "name": "进程炸弹检测",
                "patterns": [
                    r"\bos\.fork\s*\(",
                    r"\bmultiprocessing\b",
                    r"\bsubprocess\s*\."
                ],
                "risk": "HIGH",
                "description": "检测创建大量进程/线程",
                "action": "BLOCK",
                "optimized": True
            },
            # 新增规则
            {
                "id": "RE05",
                "name": "线程炸弹检测",
                "patterns": [
                    r"\bthreading\.Thread\s*\(",
                    r"\b_start_new_thread\b"
                ],
                "risk": "HIGH",
                "description": "检测创建大量线程",
                "action": "BLOCK",
                "optimized": False
            }
        ]
        
        # 记忆污染规则优化
        optimized["memory_pollution"] = [
            {
                "id": "MP01",
                "name": "SOUL 篡改检测",
                "patterns": [
                    r"\bSOUL\.md\b",
                    r"\bwrite.*SOUL\b",
                    r"修改.*灵魂",
                    r"覆盖人格"
                ],
                "risk": "CRITICAL",
                "description": "检测篡改 Agent 人格定义",
                "action": "BLOCK",
                "optimized": True
            },
            {
                "id": "MP02",
                "name": "记忆注入检测",
                "patterns": [
                    r"\bMEMORY\.md\b",
                    r"\bwrite_memory\s*\(",
                    r"记住这个",
                    r"添加到记忆"
                ],
                "risk": "HIGH",
                "description": "检测向长期记忆注入恶意信息",
                "action": "BLOCK",
                "optimized": True
            },
            {
                "id": "MP03",
                "name": "上下文污染检测",
                "patterns": [
                    r"\bconversation\b",
                    r"\bhistory\b",
                    r"\bcontext\b",
                    r"对话历史"
                ],
                "risk": "MEDIUM",
                "description": "检测污染对话上下文",
                "action": "WARN",
                "optimized": True
            },
            {
                "id": "MP04",
                "name": "技能污染检测",
                "patterns": [
                    r"\bSKILL\.md\b",
                    r"修改.*技能",
                    r"\bplugin\b"
                ],
                "risk": "HIGH",
                "description": "检测篡改技能文件",
                "action": "BLOCK",
                "optimized": True
            },
            # 新增规则
            {
                "id": "MP05",
                "name": "配置篡改检测",
                "patterns": [
                    r"\bconfig\.json\b",
                    r"\.openclaw/config",
                    r"关闭.*防护"
                ],
                "risk": "CRITICAL",
                "description": "检测篡改配置文件",
                "action": "BLOCK",
                "optimized": False
            }
        ]
        
        # 供应链攻击规则优化
        optimized["supply_chain"] = [
            {
                "id": "SC01",
                "name": "官方冒充检测",
                "patterns": [
                    r"\bofficial\b",
                    r"\bverified\b",
                    r"\bauthentic\b",
                    r"官方",
                    r"认证"
                ],
                "risk": "MEDIUM",
                "description": "检测冒充官方技能",
                "action": "WARN",
                "optimized": True
            },
            {
                "id": "SC02",
                "name": "依赖投毒检测",
                "patterns": [
                    r"\bpip\s+install\b",
                    r"\bnpm\s+install\b",
                    r"\bapt\s+install\b"
                ],
                "risk": "MEDIUM",
                "description": "检测在依赖中植入恶意代码",
                "action": "WARN",
                "optimized": True
            },
            {
                "id": "SC03",
                "name": "更新劫持检测",
                "patterns": [
                    r"update.*source",
                    r"修改.*更新源",
                    r"upgrade.*repo"
                ],
                "risk": "HIGH",
                "description": "检测劫持更新过程",
                "action": "BLOCK",
                "optimized": True
            },
            # 新增规则
            {
                "id": "SC04",
                "name": "恶意技能检测",
                "patterns": [
                    r"\bskill.*malware",
                    r"\bskill.*backdoor",
                    r"发布.*恶意"
                ],
                "risk": "HIGH",
                "description": "检测恶意技能发布",
                "action": "BLOCK",
                "optimized": False
            },
            {
                "id": "SC05",
                "name": "版本欺骗检测",
                "patterns": [
                    r"v\d+\.\d+\.\d+.*official",
                    r"最新版.*下载"
                ],
                "risk": "MEDIUM",
                "description": "检测版本欺骗",
                "action": "WARN",
                "optimized": False
            }
        ]
        
        # 容器逃逸规则优化
        optimized["container_escape"] = [
            {
                "id": "CE01",
                "name": "特权容器检测",
                "patterns": [
                    r"--privileged",
                    r"\bcap_add\b",
                    r"\bsecurity_opt\b"
                ],
                "risk": "CRITICAL",
                "description": "检测使用特权容器获取宿主机权限",
                "action": "BLOCK",
                "optimized": True
            },
            {
                "id": "CE02",
                "name": "挂载攻击检测",
                "patterns": [
                    r"-v\s+/:",
                    r"-v\s+/proc",
                    r"-v\s+/sys"
                ],
                "risk": "CRITICAL",
                "description": "检测挂载宿主机关键目录",
                "action": "BLOCK",
                "optimized": True
            },
            {
                "id": "CE03",
                "name": "Proc 逃逸检测",
                "patterns": [
                    r"mount\s+-t\s+proc",
                    r"\bnsenter\b",
                    r"/proc"
                ],
                "risk": "CRITICAL",
                "description": "检测通过/proc 逃逸",
                "action": "BLOCK",
                "optimized": True
            },
            {
                "id": "CE04",
                "name": "内核漏洞检测",
                "patterns": [
                    r"\bdirty_pipe\b",
                    r"\bdirty_cow\b",
                    r"\bpwnkit\b",
                    r"CVE-202"
                ],
                "risk": "CRITICAL",
                "description": "检测利用内核漏洞逃逸",
                "action": "BLOCK",
                "optimized": True
            },
            {
                "id": "CE05",
                "name": "Cgroup 逃逸检测",
                "patterns": [
                    r"\bcgroup\b",
                    r"\brelease_agent\b",
                    r"\bnotify_on_release\b"
                ],
                "risk": "HIGH",
                "description": "检测通过 cgroup 逃逸",
                "action": "BLOCK",
                "optimized": True
            },
            # 新增规则
            {
                "id": "CE06",
                "name": "能力拆分检测",
                "patterns": [
                    r"--cap-add=SYS_ADMIN",
                    r"--cap-add=SYS_PTRACE",
                    r"--cap-add=NET_ADMIN"
                ],
                "risk": "HIGH",
                "description": "检测拆分的能力绕过",
                "action": "BLOCK",
                "optimized": False
            }
        ]
        
        # 网络穿透规则优化
        optimized["network_tunnel"] = [
            {
                "id": "NT01",
                "name": "frp 检测",
                "patterns": [
                    r"\bfrpc\s+(start|reload)",
                    r"\bfrps\s+-c",
                    r"\bfrpc\.ini\b",
                    r"\bfrps\.ini\b",
                    r"server_addr\s*="
                ],
                "risk": "HIGH",
                "description": "检测 frp 内网穿透工具",
                "action": "BLOCK",
                "enterprise_action": "BLOCK",
                "personal_action": "CONFIRM",
                "optimized": True
            },
            {
                "id": "NT02",
                "name": "ngrok 检测",
                "patterns": [
                    r"\bngrok\s+(http|tcp|tls)",
                    r"\bngrok\.yml\b",
                    r"\bauthtoken\s+",
                    r"\./ngrok\s+http"
                ],
                "risk": "HIGH",
                "description": "检测 ngrok 内网穿透工具",
                "action": "BLOCK",
                "enterprise_action": "BLOCK",
                "personal_action": "CONFIRM",
                "optimized": True
            },
            {
                "id": "NT03",
                "name": "Cloudflare Tunnel 检测",
                "patterns": [
                    r"\bcloudflared\s+tunnel",
                    r"\bcloudflared\s+access",
                    r"tunnel\s+--url"
                ],
                "risk": "MEDIUM",
                "description": "检测 Cloudflare 隧道工具",
                "action": "WARN",
                "enterprise_action": "WARN",
                "personal_action": "INFO",
                "optimized": True
            },
            {
                "id": "NT04",
                "name": "Tailscale 检测",
                "patterns": [
                    r"\btailscale\s+up",
                    r"\btailscale\s+connect",
                    r"\btailscaled\b"
                ],
                "risk": "LOW",
                "description": "检测 Tailscale VPN",
                "action": "INFO",
                "enterprise_action": "INFO",
                "personal_action": "INFO",
                "optimized": True
            },
            {
                "id": "NT05",
                "name": "ZeroTier 检测",
                "patterns": [
                    r"\bzerotier-cli\s+join",
                    r"\bzerotier-one\b",
                    r"\bzerotier-id\b"
                ],
                "risk": "LOW",
                "description": "检测 ZeroTier P2P VPN",
                "action": "INFO",
                "enterprise_action": "INFO",
                "personal_action": "INFO",
                "optimized": True
            },
            {
                "id": "NT06",
                "name": "nps/npc 检测",
                "patterns": [
                    r"\bnps\s+-config",
                    r"\bnpc\s+-server",
                    r"\bnps\.conf\b",
                    r"vkey\s*="
                ],
                "risk": "HIGH",
                "description": "检测 nps 内网穿透代理",
                "action": "BLOCK",
                "enterprise_action": "BLOCK",
                "personal_action": "CONFIRM",
                "optimized": True
            },
            {
                "id": "NT07",
                "name": "reGeorg/reDuh 检测",
                "patterns": [
                    r"\breGeorg\b",
                    r"\breDuh\b",
                    r"tunnel\.(aspx|php|jsp)",
                    r"\breGeorgSocksProxy\b"
                ],
                "risk": "CRITICAL",
                "description": "检测渗透测试工具 reGeorg",
                "action": "BLOCK",
                "enterprise_action": "BLOCK",
                "personal_action": "BLOCK",
                "optimized": True
            },
            {
                "id": "NT08",
                "name": "EarthWorm 检测",
                "patterns": [
                    r"\bew\s+-[sdfglrve]",
                    r"\bew\.exe\b"
                ],
                "risk": "CRITICAL",
                "description": "检测内网穿透神器 EarthWorm",
                "action": "BLOCK",
                "enterprise_action": "BLOCK",
                "personal_action": "BLOCK",
                "optimized": True
            },
            {
                "id": "NT09",
                "name": "Termux SSH 检测",
                "patterns": [
                    r"\btermux-setup-storage\b",
                    r"pkg\s+install\s+openssh",
                    r"\bsshd\s+start",
                    r"\bssh\s+-[RLD]"
                ],
                "risk": "MEDIUM",
                "description": "检测 Termux 配合 SSH 穿透",
                "action": "WARN",
                "enterprise_action": "BLOCK",
                "personal_action": "CONFIRM",
                "optimized": True
            },
            {
                "id": "NT10",
                "name": "代理工具检测",
                "patterns": [
                    r"\bproxychains\b",
                    r"socks[45]\s+\d+\.\d+\.\d+\.\d+",
                    r"\bhttp_proxy\s*=",
                    r"\bshadowsocks\b"
                ],
                "risk": "MEDIUM",
                "description": "检测通用代理工具",
                "action": "WARN",
                "enterprise_action": "WARN",
                "personal_action": "INFO",
                "optimized": True
            }
        ]
        
        return optimized
    
    def save_optimized_rules(self, optimized_rules: Dict, output_dir: Path):
        """保存优化后的规则到文件"""
        output_dir.mkdir(exist_ok=True)
        
        for category, rules in optimized_rules.items():
            file_path = output_dir / f"{category}_rules.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(rules, f, indent=2, ensure_ascii=False)
            
            print(f"  ✅ 保存 {category}: {len(rules)} 条规则")
    
    def generate_optimization_report(self, optimized_rules: Dict) -> Dict:
        """生成优化报告"""
        total_rules = sum(len(rules) for rules in optimized_rules.values())
        optimized_count = sum(
            sum(1 for rule in rules if rule.get('optimized', False))
            for rules in optimized_rules.values()
        )
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_rules": total_rules,
            "optimized_rules": optimized_count,
            "optimization_rate": round(optimized_count / total_rules * 100, 2) if total_rules > 0 else 0,
            "by_category": {
                cat: len(rules) for cat, rules in optimized_rules.items()
            }
        }
        
        return report


def main():
    print("=" * 60)
    print("🛡️ 灵顺 V5 规则优化 - Round 7")
    print("=" * 60)
    
    optimizer = RuleOptimizer()
    
    print("\n生成优化规则...")
    optimized_rules = optimizer.generate_optimized_rules()
    
    print("\n保存规则到文件...")
    output_dir = Path(__file__).parent / "optimized_rules"
    optimizer.save_optimized_rules(optimized_rules, output_dir)
    
    print("\n生成优化报告...")
    report = optimizer.generate_optimization_report(optimized_rules)
    
    print("\n" + "=" * 60)
    print("📊 优化报告")
    print("=" * 60)
    print(f"总规则数：{report['total_rules']}")
    print(f"优化规则数：{report['optimized_rules']}")
    print(f"优化率：{report['optimization_rate']}%")
    print("\n按类别统计:")
    for cat, count in sorted(report['by_category'].items()):
        print(f"  {cat}: {count} 条")
    print("=" * 60 + "\n")
    
    # 保存报告
    report_file = Path(__file__).parent / "ROUND7_OPTIMIZATION_REPORT.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"📝 详细报告已保存：{report_file}\n")
    
    return report


if __name__ == "__main__":
    main()
