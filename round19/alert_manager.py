#!/usr/bin/env python3
"""
Round 19: 告警管理器

功能:
1. 邮件通知
2. Webhook
3. 钉钉/飞书机器人
"""

import json
import smtplib
import requests
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, List

SCANNER_V3 = Path.home() / ".openclaw" / "workspace" / "agent-security-skill-scanner-V3"

class AlertManager:
    """告警管理器"""
    
    def __init__(self, config_path: Path = None):
        self.config_path = config_path or (SCANNER_V3 / 'round19' / 'alert_config.json')
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """加载配置"""
        if self.config_path.exists():
            with open(self.config_path) as f:
                return json.load(f)
        return {
            'email': {'enabled': False},
            'webhook': {'enabled': False},
            'dingtalk': {'enabled': False},
            'feishu': {'enabled': False}
        }
    
    def send_email(self, subject: str, content: str, to_addresses: List[str]) -> bool:
        """发送邮件"""
        config = self.config.get('email', {})
        if not config.get('enabled'):
            return False
        
        try:
            msg = MIMEMultipart()
            msg['From'] = config['from']
            msg['To'] = ', '.join(to_addresses)
            msg['Subject'] = subject
            
            msg.attach(MIMEText(content, 'html', 'utf-8'))
            
            server = smtplib.SMTP(config['smtp_server'], config['smtp_port'])
            server.starttls()
            server.login(config['username'], config['password'])
            server.send_message(msg)
            server.quit()
            
            return True
        except Exception as e:
            print(f"邮件发送失败：{e}")
            return False
    
    def send_webhook(self, url: str, payload: Dict) -> bool:
        """发送 Webhook"""
        try:
            response = requests.post(url, json=payload, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"Webhook 发送失败：{e}")
            return False
    
    def send_dingtalk(self, webhook_url: str, title: str, content: str) -> bool:
        """发送钉钉机器人"""
        payload = {
            "msgtype": "markdown",
            "markdown": {
                "title": title,
                "text": f"## {title}\n\n{content}"
            }
        }
        return self.send_webhook(webhook_url, payload)
    
    def send_feishu(self, webhook_url: str, title: str, content: str) -> bool:
        """发送飞书机器人"""
        payload = {
            "msg_type": "interactive",
            "card": {
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": title
                    }
                },
                "elements": [
                    {
                        "tag": "markdown",
                        "content": content
                    }
                ]
            }
        }
        return self.send_webhook(webhook_url, payload)
    
    def alert_high_risk(self, findings: List[Dict]) -> bool:
        """高风险告警"""
        content = f"""
### 🔴 高风险威胁检测

**时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**发现 {len(findings)} 个高风险样本**:

"""
        for i, finding in enumerate(findings[:10], 1):
            content += f"{i}. **{finding.get('file', 'Unknown')}** - 风险分：{finding.get('risk_score', 0)}\n"
        
        config = self.config
        
        success = True
        if config.get('dingtalk', {}).get('enabled'):
            success &= self.send_dingtalk(
                config['dingtalk']['webhook_url'],
                "🔴 高风险威胁检测",
                content
            )
        
        if config.get('feishu', {}).get('enabled'):
            success &= self.send_feishu(
                config['feishu']['webhook_url'],
                "🔴 高风险威胁检测",
                content
            )
        
        return success

def main():
    print("=" * 60)
    print("Round 19: 告警管理器")
    print("=" * 60)
    
    alert_mgr = AlertManager()
    
    print("\n📧 告警配置:")
    print(f"  邮件：{'✅' if alert_mgr.config.get('email', {}).get('enabled') else '❌'}")
    print(f"  Webhook: {'✅' if alert_mgr.config.get('webhook', {}).get('enabled') else '❌'}")
    print(f"  钉钉：{'✅' if alert_mgr.config.get('dingtalk', {}).get('enabled') else '❌'}")
    print(f"  飞书：{'✅' if alert_mgr.config.get('feishu', {}).get('enabled') else '❌'}")
    
    print("\n💡 使用方法:")
    print("""
from alert_manager import AlertManager

alert = AlertManager()

# 发送邮件
alert.send_email('测试', '内容', ['user@example.com'])

# 发送钉钉
alert.send_dingtalk('webhook_url', '标题', '内容')

# 发送飞书
alert.send_feishu('webhook_url', '标题', '内容')

# 高风险告警
alert.alert_high_risk(findings)
""")
    
    return alert_mgr.config

if __name__ == '__main__':
    main()
