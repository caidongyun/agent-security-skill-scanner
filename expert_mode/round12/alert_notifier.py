#!/usr/bin/env python3
"""
Round 12 - 告警通知模块

支持飞书、钉钉、邮件等多种通知渠道
"""

import os
import json
import smtplib
import requests
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ============== 配置 ==============

BASE_DIR = Path(__file__).parent.parent
CONFIG_FILE = BASE_DIR / "round12" / "config.yaml"

# ============== 通知配置 ==============

class NotificationConfig:
    """通知配置"""
    
    def __init__(self):
        self.feishu_webhook = os.environ.get('FEISHU_WEBHOOK', '')
        self.dingtalk_webhook = os.environ.get('DINGTALK_WEBHOOK', '')
        self.email_smtp_server = os.environ.get('EMAIL_SMTP_SERVER', '')
        self.email_smtp_port = int(os.environ.get('EMAIL_SMTP_PORT', '587'))
        self.email_username = os.environ.get('EMAIL_USERNAME', '')
        self.email_password = os.environ.get('EMAIL_PASSWORD', '')
        self.email_recipients = os.environ.get('EMAIL_RECIPIENTS', '').split(',')
        
        # 从配置文件加载 (如果存在)
        self._load_from_config()
    
    def _load_from_config(self):
        """从配置文件加载"""
        import yaml
        
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE) as f:
                config = yaml.safe_load(f)
                
                alerts_config = config.get('alerts', {})
                
                feishu = alerts_config.get('feishu', {})
                if feishu.get('enabled') and feishu.get('webhook'):
                    self.feishu_webhook = feishu['webhook']
                
                dingtalk = alerts_config.get('dingtalk', {})
                if dingtalk.get('enabled') and dingtalk.get('webhook'):
                    self.dingtalk_webhook = dingtalk['webhook']
                
                email = alerts_config.get('email', {})
                if email.get('enabled'):
                    self.email_smtp_server = email.get('smtp_server', self.email_smtp_server)
                    self.email_smtp_port = email.get('smtp_port', self.email_smtp_port)
                    self.email_username = email.get('username', self.email_username)
                    self.email_password = email.get('password', self.email_password)
                    self.email_recipients = email.get('recipients', self.email_recipients)

# ============== 告警消息 ==============

class AlertMessage:
    """告警消息"""
    
    def __init__(self, detection_result: Dict):
        self.detection = detection_result
        self.timestamp = datetime.now()
        self.level = self._calculate_level()
    
    def _calculate_level(self) -> str:
        """计算告警级别"""
        severity = self.detection.get('severity', 'medium')
        level_map = {
            'critical': 'P0',
            'high': 'P1',
            'medium': 'P2',
            'low': 'P3',
        }
        return level_map.get(severity, 'P2')
    
    def to_feishu(self) -> Dict:
        """转换为飞书消息格式"""
        severity_colors = {
            'critical': 'red',
            'high': 'orange',
            'medium': 'yellow',
            'low': 'blue',
        }
        
        color = severity_colors.get(self.detection.get('severity', 'medium'), 'gray')
        
        return {
            "msg_type": "interactive",
            "card": {
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": f"🚨 安全告警 - {self.level}"
                    },
                    "template": color
                },
                "elements": [
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": f"""**文件**: `{self.detection.get('file_path', 'unknown')}`
**威胁类型**: {self.detection.get('attack_type', 'unknown')}
**触发规则**: {self.detection.get('rule_name', 'unknown')}
**严重程度**: {self.detection.get('severity', 'unknown')}
**置信度**: {self.detection.get('confidence', 0) * 100:.1f}%
**时间**: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"""
                        }
                    },
                    {
                        "tag": "action",
                        "actions": [
                            {
                                "tag": "button",
                                "text": {
                                    "tag": "plain_text",
                                    "content": "查看详情"
                                },
                                "type": "primary",
                                "url": "http://localhost:8080/alerts"
                            }
                        ]
                    }
                ]
            }
        }
    
    def to_dingtalk(self) -> Dict:
        """转换为钉钉消息格式"""
        return {
            "msgtype": "markdown",
            "markdown": {
                "title": f"🚨 安全告警 - {self.level}",
                "text": f"""## 🚨 安全告警 - {self.level}

**文件**: `{self.detection.get('file_path', 'unknown')}`
**威胁类型**: {self.detection.get('attack_type', 'unknown')}
**触发规则**: {self.detection.get('rule_name', 'unknown')}
**严重程度**: {self.detection.get('severity', 'unknown')}
**置信度**: {self.detection.get('confidence', 0) * 100:.1f}%
**时间**: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}

---
请及时处理！"""
            }
        }
    
    def to_email(self) -> Dict:
        """转换为邮件内容"""
        subject = f"[{self.level}] 安全告警 - {self.detection.get('attack_type', 'unknown')}"
        
        body = f"""
<html>
<body>
<h2>🚨 安全告警 - {self.level}</h2>

<table border="1" cellpadding="10">
    <tr><td><strong>文件</strong></td><td><code>{self.detection.get('file_path', 'unknown')}</code></td></tr>
    <tr><td><strong>威胁类型</strong></td><td>{self.detection.get('attack_type', 'unknown')}</td></tr>
    <tr><td><strong>触发规则</strong></td><td>{self.detection.get('rule_name', 'unknown')}</td></tr>
    <tr><td><strong>严重程度</strong></td><td>{self.detection.get('severity', 'unknown')}</td></tr>
    <tr><td><strong>置信度</strong></td><td>{self.detection.get('confidence', 0) * 100:.1f}%</td></tr>
    <tr><td><strong>文件哈希</strong></td><td><code>{self.detection.get('file_hash', 'N/A')}</code></td></tr>
    <tr><td><strong>时间</strong></td><td>{self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</td></tr>
</table>

<h3>建议操作</h3>
<ol>
    <li>隔离文件，不要执行</li>
    <li>扫描关联文件</li>
    <li>检查系统日志</li>
    <li>查看 <a href="http://localhost:8080/alerts">仪表板</a> 获取详情</li>
</ol>

<hr>
<p style="color: gray; font-size: 12px;">
这是自动生成的安全告警，请勿回复。
</p>
</body>
</html>
"""
        
        return {
            'subject': subject,
            'body': body,
        }

# ============== 通知发送器 ==============

class AlertNotifier:
    """告警通知发送器"""
    
    def __init__(self, config: Optional[NotificationConfig] = None):
        self.config = config or NotificationConfig()
        self.sent_count = 0
        self.failed_count = 0
    
    def send(self, detection_result: Dict, channels: Optional[List[str]] = None) -> Dict:
        """发送告警"""
        message = AlertMessage(detection_result)
        results = {}
        
        # 确定发送渠道
        if channels is None:
            channels = self._get_channels_for_level(message.level)
        
        # 飞书
        if 'feishu' in channels and self.config.feishu_webhook:
            results['feishu'] = self._send_feishu(message)
        
        # 钉钉
        if 'dingtalk' in channels and self.config.dingtalk_webhook:
            results['dingtalk'] = self._send_dingtalk(message)
        
        # 邮件
        if 'email' in channels and self.config.email_smtp_server:
            results['email'] = self._send_email(message)
        
        return results
    
    def _get_channels_for_level(self, level: str) -> List[str]:
        """根据级别获取发送渠道"""
        channel_map = {
            'P0': ['feishu', 'dingtalk', 'email'],
            'P1': ['feishu', 'email'],
            'P2': ['email'],
            'P3': [],
        }
        return channel_map.get(level, ['email'])
    
    def _send_feishu(self, message: AlertMessage) -> Dict:
        """发送飞书消息"""
        try:
            payload = message.to_feishu()
            response = requests.post(
                self.config.feishu_webhook,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                self.sent_count += 1
                return {'success': True, 'status_code': response.status_code}
            else:
                self.failed_count += 1
                return {'success': False, 'status_code': response.status_code, 'error': response.text}
        
        except Exception as e:
            self.failed_count += 1
            return {'success': False, 'error': str(e)}
    
    def _send_dingtalk(self, message: AlertMessage) -> Dict:
        """发送钉钉消息"""
        try:
            payload = message.to_dingtalk()
            response = requests.post(
                self.config.dingtalk_webhook,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('errcode') == 0:
                    self.sent_count += 1
                    return {'success': True}
                else:
                    self.failed_count += 1
                    return {'success': False, 'error': result.get('errmsg')}
            else:
                self.failed_count += 1
                return {'success': False, 'status_code': response.status_code}
        
        except Exception as e:
            self.failed_count += 1
            return {'success': False, 'error': str(e)}
    
    def _send_email(self, message: AlertMessage) -> Dict:
        """发送邮件"""
        try:
            email_content = message.to_email()
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = email_content['subject']
            msg['From'] = self.config.email_username
            msg['To'] = ', '.join(self.config.email_recipients)
            
            msg.attach(MIMEText(email_content['body'], 'html'))
            
            server = smtplib.SMTP(self.config.email_smtp_server, self.config.email_smtp_port)
            server.starttls()
            server.login(self.config.email_username, self.config.email_password)
            server.sendmail(
                self.config.email_username,
                self.config.email_recipients,
                msg.as_string()
            )
            server.quit()
            
            self.sent_count += 1
            return {'success': True}
        
        except Exception as e:
            self.failed_count += 1
            return {'success': False, 'error': str(e)}
    
    def get_stats(self) -> Dict:
        """获取发送统计"""
        return {
            'sent': self.sent_count,
            'failed': self.failed_count,
            'success_rate': self.sent_count / (self.sent_count + self.failed_count) * 100 if (self.sent_count + self.failed_count) > 0 else 0
        }

# ============== 主函数 ==============

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Round 12 告警通知")
    parser.add_argument('--test-feishu', action='store_true', help='测试飞书通知')
    parser.add_argument('--test-dingtalk', action='store_true', help='测试钉钉通知')
    parser.add_argument('--test-email', action='store_true', help='测试邮件通知')
    parser.add_argument('--test-all', action='store_true', help='测试所有通知')
    parser.add_argument('--config', action='store_true', help='显示配置状态')
    
    args = parser.parse_args()
    
    config = NotificationConfig()
    notifier = AlertNotifier(config)
    
    if args.config:
        print("📋 通知配置状态:")
        print(f"  飞书 Webhook: {'✅' if config.feishu_webhook else '❌'}")
        print(f"  钉钉 Webhook: {'✅' if config.dingtalk_webhook else '❌'}")
        print(f"  邮件 SMTP: {'✅' if config.email_smtp_server else '❌'}")
        print(f"  邮件收件人: {config.email_recipients if config.email_recipients else '[]'}")
        return
    
    # 测试数据
    test_detection = {
        'file_path': '/tmp/test_malware.py',
        'attack_type': 'remote_load',
        'severity': 'high',
        'rule_name': '测试规则 - curl|bash 模式',
        'confidence': 0.95,
        'file_hash': 'abc123def456',
    }
    
    if args.test_feishu:
        print("🧪 测试飞书通知...")
        result = notifier.send(test_detection, ['feishu'])
        print(f"  结果：{result}")
    
    if args.test_dingtalk:
        print("🧪 测试钉钉通知...")
        result = notifier.send(test_detection, ['dingtalk'])
        print(f"  结果：{result}")
    
    if args.test_email:
        print("🧪 测试邮件通知...")
        result = notifier.send(test_detection, ['email'])
        print(f"  结果：{result}")
    
    if args.test_all:
        print("🧪 测试所有通知渠道...")
        results = notifier.send(test_detection)
        for channel, result in results.items():
            status = "✅" if result.get('success') else "❌"
            print(f"  {status} {channel}: {result}")
    
    # 显示统计
    if any([args.test_feishu, args.test_dingtalk, args.test_email, args.test_all]):
        stats = notifier.get_stats()
        print(f"\n📊 发送统计:")
        print(f"  成功：{stats['sent']}")
        print(f"  失败：{stats['failed']}")
        print(f"  成功率：{stats['success_rate']:.1f}%")

if __name__ == "__main__":
    main()
