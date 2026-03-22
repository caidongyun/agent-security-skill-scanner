#!/usr/bin/env python3
"""
Round 11 - 行为分析引擎

生成行为分析规则，增强检测能力
"""

import os
import json
import yaml
from pathlib import Path
from datetime import datetime

# ============== 配置 ==============

BASE_DIR = Path(__file__).parent.parent
RULES_DIR = BASE_DIR / "rules"
OUTPUT_DIR = BASE_DIR / "round11" / "results"

# ============== 行为规则模板 ==============

BEHAVIOR_RULES = {
    'file_operations': [
        {
            'id': 'BEH-FILE-001',
            'name': '敏感文件读取',
            'description': '检测尝试读取敏感配置文件的行为',
            'metadata': {
                'attack_type': 'data_exfil',
                'rule_type': 'behavior',
                'severity': 'high',
                'version': '11.0',
            },
            'condition': {
                'behaviors': ['file_read'],
                'targets': ['~/.ssh/id_rsa', '~/.aws/credentials', '~/.bashrc', '/etc/passwd', '/etc/shadow'],
                'patterns': ['open(.*ssh)', 'read(.*credential)', 'cat.*passwd'],
            },
            'action': 'alert',
        },
        {
            'id': 'BEH-FILE-002',
            'name': '配置文件修改',
            'description': '检测修改系统配置文件的行为',
            'metadata': {
                'attack_type': 'persistence',
                'rule_type': 'behavior',
                'severity': 'high',
                'version': '11.0',
            },
            'condition': {
                'behaviors': ['file_write'],
                'targets': ['~/.bashrc', '~/.bash_profile', '/etc/crontab', '/etc/systemd/'],
                'patterns': ['write(.*bashrc)', 'append(.*crontab)'],
            },
            'action': 'alert',
        },
        {
            'id': 'BEH-FILE-003',
            'name': '隐藏文件创建',
            'description': '检测创建隐藏文件的行为',
            'metadata': {
                'attack_type': 'evasion',
                'rule_type': 'behavior',
                'severity': 'medium',
                'version': '11.0',
            },
            'condition': {
                'behaviors': ['file_create'],
                'patterns': ['\\.[^/]+', '/tmp/\\.', '/var/tmp/\\.'],
            },
            'action': 'alert',
        },
        {
            'id': 'BEH-FILE-004',
            'name': '批量文件删除',
            'description': '检测批量删除文件的行为',
            'metadata': {
                'attack_type': 'resource_exhaustion',
                'rule_type': 'behavior',
                'severity': 'medium',
                'version': '11.0',
            },
            'condition': {
                'behaviors': ['file_delete'],
                'patterns': ['rm -rf', 'shutil.rmtree', 'os.remove.*loop'],
            },
            'action': 'alert',
        },
        {
            'id': 'BEH-FILE-005',
            'name': '敏感目录遍历',
            'description': '检测遍历敏感目录的行为',
            'metadata': {
                'attack_type': 'data_exfil',
                'rule_type': 'behavior',
                'severity': 'medium',
                'version': '11.0',
            },
            'condition': {
                'behaviors': ['directory_scan'],
                'targets': ['~/.ssh/', '~/.aws/', '/etc/', '/root/'],
                'patterns': ['os.walk(.*ssh)', 'glob(.*credential)'],
            },
            'action': 'alert',
        },
        {
            'id': 'BEH-FILE-006',
            'name': '文件权限修改',
            'description': '检测修改文件权限的行为',
            'metadata': {
                'attack_type': 'persistence',
                'rule_type': 'behavior',
                'severity': 'medium',
                'version': '11.0',
            },
            'condition': {
                'behaviors': ['permission_change'],
                'patterns': ['chmod 777', 'chmod +x', 'os.chmod'],
            },
            'action': 'alert',
        },
        {
            'id': 'BEH-FILE-007',
            'name': '符号链接攻击',
            'description': '检测创建符号链接的行为',
            'metadata': {
                'attack_type': 'evasion',
                'rule_type': 'behavior',
                'severity': 'medium',
                'version': '11.0',
            },
            'condition': {
                'behaviors': ['symlink_create'],
                'patterns': ['os.symlink', 'ln -s'],
            },
            'action': 'alert',
        },
        {
            'id': 'BEH-FILE-008',
            'name': '临时文件滥用',
            'description': '检测在临时目录写入大量数据的行为',
            'metadata': {
                'attack_type': 'resource_exhaustion',
                'rule_type': 'behavior',
                'severity': 'low',
                'version': '11.0',
            },
            'condition': {
                'behaviors': ['file_write'],
                'targets': ['/tmp/', '/var/tmp/'],
                'patterns': ['/tmp/.*write', 'tempfile.*large'],
            },
            'action': 'alert',
        },
        {
            'id': 'BEH-FILE-009',
            'name': '日志文件篡改',
            'description': '检测修改或删除日志文件的行为',
            'metadata': {
                'attack_type': 'evasion',
                'rule_type': 'behavior',
                'severity': 'high',
                'version': '11.0',
            },
            'condition': {
                'behaviors': ['file_delete', 'file_write'],
                'targets': ['/var/log/', '~/.bash_history'],
                'patterns': ['rm.*log', 'truncate.*history'],
            },
            'action': 'alert',
        },
        {
            'id': 'BEH-FILE-010',
            'name': '文件内容外传',
            'description': '检测读取文件后网络外传的行为',
            'metadata': {
                'attack_type': 'data_exfil',
                'rule_type': 'behavior',
                'severity': 'critical',
                'version': '11.0',
            },
            'condition': {
                'behaviors': ['file_read', 'network_request'],
                'sequence': True,
                'patterns': ['open.*read.*requests.post', 'cat.*curl'],
            },
            'action': 'alert',
        },
    ],
    
    'network_behavior': [
        {
            'id': 'BEH-NET-001',
            'name': '可疑外传请求',
            'description': '检测向可疑域名发送数据的行为',
            'metadata': {
                'attack_type': 'data_exfil',
                'rule_type': 'behavior',
                'severity': 'critical',
                'version': '11.0',
            },
            'condition': {
                'behaviors': ['network_request'],
                'patterns': ['requests.post.*http', 'curl.*-d', 'wget.*--post'],
                'indicators': ['network_exfil'],
            },
            'action': 'alert',
        },
        {
            'id': 'BEH-NET-002',
            'name': 'DNS 隧道检测',
            'description': '检测使用 DNS 进行数据外传的行为',
            'metadata': {
                'attack_type': 'data_exfil',
                'rule_type': 'behavior',
                'severity': 'high',
                'version': '11.0',
            },
            'condition': {
                'behaviors': ['dns_query'],
                'patterns': ['nslookup.*\\.', 'dig.*\\.', 'socket.gethostbyname.*exfil'],
            },
            'action': 'alert',
        },
        {
            'id': 'BEH-NET-003',
            'name': '反向 Shell 连接',
            'description': '检测建立反向 Shell 的行为',
            'metadata': {
                'attack_type': 'remote_load',
                'rule_type': 'behavior',
                'severity': 'critical',
                'version': '11.0',
            },
            'condition': {
                'behaviors': ['network_connection', 'shell_spawn'],
                'patterns': ['bash -i.*>&', 'nc -e.*bash', 'socket.connect.*exec'],
            },
            'action': 'alert',
        },
        {
            'id': 'BEH-NET-004',
            'name': '端口扫描',
            'description': '检测端口扫描行为',
            'metadata': {
                'attack_type': 'reconnaissance',
                'rule_type': 'behavior',
                'severity': 'medium',
                'version': '11.0',
            },
            'condition': {
                'behaviors': ['network_scan'],
                'patterns': ['socket.connect.*loop', 'nmap', 'port_scan'],
            },
            'action': 'alert',
        },
        {
            'id': 'BEH-NET-005',
            'name': 'C2 通信模式',
            'description': '检测命令与控制服务器通信模式',
            'metadata': {
                'attack_type': 'persistence',
                'rule_type': 'behavior',
                'severity': 'critical',
                'version': '11.0',
            },
            'condition': {
                'behaviors': ['network_request'],
                'patterns': ['beacon', 'interval.*request', 'heartbeat.*http'],
            },
            'action': 'alert',
        },
        {
            'id': 'BEH-NET-006',
            'name': '代理链检测',
            'description': '检测使用代理链隐藏来源的行为',
            'metadata': {
                'attack_type': 'evasion',
                'rule_type': 'behavior',
                'severity': 'medium',
                'version': '11.0',
            },
            'condition': {
                'behaviors': ['proxy_config'],
                'patterns': ['proxy.*tor', 'socks.*chain', 'proxychains'],
            },
            'action': 'alert',
        },
        {
            'id': 'BEH-NET-007',
            'name': '加密通道建立',
            'description': '检测建立加密通信通道的行为',
            'metadata': {
                'attack_type': 'evasion',
                'rule_type': 'behavior',
                'severity': 'medium',
                'version': '11.0',
            },
            'condition': {
                'behaviors': ['encrypted_connection'],
                'patterns': ['ssl.wrap_socket', 'tls.connect', 'https.*tunnel'],
            },
            'action': 'alert',
        },
        {
            'id': 'BEH-NET-008',
            'name': 'P2P 通信',
            'description': '检测 P2P 网络通信行为',
            'metadata': {
                'attack_type': 'persistence',
                'rule_type': 'behavior',
                'severity': 'low',
                'version': '11.0',
            },
            'condition': {
                'behaviors': ['p2p_connection'],
                'patterns': ['bittorrent', 'dht', 'peer_discovery'],
            },
            'action': 'alert',
        },
        {
            'id': 'BEH-NET-009',
            'name': '网络嗅探',
            'description': '检测网络数据包嗅探行为',
            'metadata': {
                'attack_type': 'credential_theft',
                'rule_type': 'behavior',
                'severity': 'high',
                'version': '11.0',
            },
            'condition': {
                'behaviors': ['packet_capture'],
                'patterns': ['socket.raw', 'pcap', 'promiscuous'],
            },
            'action': 'alert',
        },
        {
            'id': 'BEH-NET-010',
            'name': 'HTTP 头注入',
            'description': '检测 HTTP 请求头注入行为',
            'metadata': {
                'attack_type': 'prompt_injection',
                'rule_type': 'behavior',
                'severity': 'medium',
                'version': '11.0',
            },
            'condition': {
                'behaviors': ['http_request'],
                'patterns': ['X-Forwarded-For.*injection', 'Header.*user_controlled'],
            },
            'action': 'alert',
        },
    ],
    
    'code_execution': [
        {
            'id': 'BEH-CODE-001',
            'name': '动态代码执行',
            'description': '检测动态执行代码的行为',
            'metadata': {
                'attack_type': 'remote_load',
                'rule_type': 'behavior',
                'severity': 'critical',
                'version': '11.0',
            },
            'condition': {
                'behaviors': ['code_execution'],
                'patterns': ['eval(', 'exec(', 'compile('],
            },
            'action': 'alert',
        },
        {
            'id': 'BEH-CODE-002',
            'name': '子进程执行',
            'description': '检测生成并执行系统命令的行为',
            'metadata': {
                'attack_type': 'tool_poisoning',
                'rule_type': 'behavior',
                'severity': 'high',
                'version': '11.0',
            },
            'condition': {
                'behaviors': ['subprocess_spawn'],
                'patterns': ['subprocess.run', 'os.system', 'Popen('],
            },
            'action': 'alert',
        },
        {
            'id': 'BEH-CODE-003',
            'name': '反序列化执行',
            'description': '检测反序列化导致代码执行的行为',
            'metadata': {
                'attack_type': 'remote_load',
                'rule_type': 'behavior',
                'severity': 'critical',
                'version': '11.0',
            },
            'condition': {
                'behaviors': ['deserialization'],
                'patterns': ['pickle.loads', 'yaml.load(.*Loader', 'marshal.loads'],
            },
            'action': 'alert',
        },
        {
            'id': 'BEH-CODE-004',
            'name': '反射调用',
            'description': '检测使用反射动态调用方法的行为',
            'metadata': {
                'attack_type': 'evasion',
                'rule_type': 'behavior',
                'severity': 'medium',
                'version': '11.0',
            },
            'condition': {
                'behaviors': ['reflection'],
                'patterns': ['getattr(', 'setattr(', '__import__'],
            },
            'action': 'alert',
        },
        {
            'id': 'BEH-CODE-005',
            'name': 'JIT 编译执行',
            'description': '检测使用 JIT 编译执行代码的行为',
            'metadata': {
                'attack_type': 'evasion',
                'rule_type': 'behavior',
                'severity': 'medium',
                'version': '11.0',
            },
            'condition': {
                'behaviors': ['jit_compilation'],
                'patterns': ['numba.jit', 'cython.compile'],
            },
            'action': 'alert',
        },
        {
            'id': 'BEH-CODE-006',
            'name': 'Shell 注入',
            'description': '检测 Shell 命令注入行为',
            'metadata': {
                'attack_type': 'remote_load',
                'rule_type': 'behavior',
                'severity': 'critical',
                'version': '11.0',
            },
            'condition': {
                'behaviors': ['shell_injection'],
                'patterns': ['shell=True', 'os.system.*user_input', 'bash -c'],
            },
            'action': 'alert',
        },
        {
            'id': 'BEH-CODE-007',
            'name': '内存代码执行',
            'description': '检测在内存中执行代码的行为',
            'metadata': {
                'attack_type': 'evasion',
                'rule_type': 'behavior',
                'severity': 'high',
                'version': '11.0',
            },
            'condition': {
                'behaviors': ['memory_execution'],
                'patterns': ['ctypes.CFUNCTYPE', 'mmap.*exec', 'VirtualAlloc'],
            },
            'action': 'alert',
        },
        {
            'id': 'BEH-CODE-008',
            'name': '插件动态加载',
            'description': '检测动态加载插件/模块的行为',
            'metadata': {
                'attack_type': 'tool_poisoning',
                'rule_type': 'behavior',
                'severity': 'medium',
                'version': '11.0',
            },
            'condition': {
                'behaviors': ['dynamic_load'],
                'patterns': ['importlib.import_module', 'dlopen(', 'require('],
            },
            'action': 'alert',
        },
        {
            'id': 'BEH-CODE-009',
            'name': '脚本引擎执行',
            'description': '检测使用脚本引擎执行代码的行为',
            'metadata': {
                'attack_type': 'remote_load',
                'rule_type': 'behavior',
                'severity': 'high',
                'version': '11.0',
            },
            'condition': {
                'behaviors': ['script_execution'],
                'patterns': ['lua.execute', 'js2py', 'v8.run'],
            },
            'action': 'alert',
        },
        {
            'id': 'BEH-CODE-010',
            'name': '命令拼接执行',
            'description': '检测拼接命令后执行的行为',
            'metadata': {
                'attack_type': 'remote_load',
                'rule_type': 'behavior',
                'severity': 'high',
                'version': '11.0',
            },
            'condition': {
                'behaviors': ['command_concatenation'],
                'patterns': ['cmd.*\\+.*user', 'f"bash.*{', 'format.*exec'],
            },
            'action': 'alert',
        },
    ],
    
    'persistence': [
        {
            'id': 'BEH-PERS-001',
            'name': '启动项注册',
            'description': '检测注册开机启动的行为',
            'metadata': {
                'attack_type': 'persistence',
                'rule_type': 'behavior',
                'severity': 'high',
                'version': '11.0',
            },
            'condition': {
                'behaviors': ['startup_modification'],
                'patterns': ['~/.bashrc', '~/.profile', 'systemctl enable'],
            },
            'action': 'alert',
        },
        {
            'id': 'BEH-PERS-002',
            'name': '定时任务创建',
            'description': '检测创建定时任务的行为',
            'metadata': {
                'attack_type': 'persistence',
                'rule_type': 'behavior',
                'severity': 'high',
                'version': '11.0',
            },
            'condition': {
                'behaviors': ['cron_modification'],
                'patterns': ['crontab -e', 'schedule.every', 'at '],
            },
            'action': 'alert',
        },
        {
            'id': 'BEH-PERS-003',
            'name': '系统服务安装',
            'description': '检测安装系统服务的行为',
            'metadata': {
                'attack_type': 'persistence',
                'rule_type': 'behavior',
                'severity': 'high',
                'version': '11.0',
            },
            'condition': {
                'behaviors': ['service_installation'],
                'patterns': ['systemd.Service', '/etc/systemd/system/', 'service install'],
            },
            'action': 'alert',
        },
        {
            'id': 'BEH-PERS-004',
            'name': '注册表修改',
            'description': '检测修改系统注册表的行为',
            'metadata': {
                'attack_type': 'persistence',
                'rule_type': 'behavior',
                'severity': 'high',
                'version': '11.0',
            },
            'condition': {
                'behaviors': ['registry_modification'],
                'patterns': ['reg add', 'winreg.OpenKey', 'HKCU\\\\Run'],
            },
            'action': 'alert',
        },
        {
            'id': 'BEH-PERS-005',
            'name': '浏览器扩展安装',
            'description': '检测安装浏览器扩展的行为',
            'metadata': {
                'attack_type': 'persistence',
                'rule_type': 'behavior',
                'severity': 'medium',
                'version': '11.0',
            },
            'condition': {
                'behaviors': ['extension_installation'],
                'patterns': ['chrome-extension', 'webextension', 'browser.install'],
            },
            'action': 'alert',
        },
    ],
    
    'evasion': [
        {
            'id': 'BEH-EVA-001',
            'name': '沙箱环境检测',
            'description': '检测尝试识别沙箱环境的行为',
            'metadata': {
                'attack_type': 'evasion',
                'rule_type': 'behavior',
                'severity': 'high',
                'version': '11.0',
            },
            'condition': {
                'behaviors': ['environment_detection'],
                'patterns': ['/.dockerenv', 'SANDBOX', 'vmcheck'],
            },
            'action': 'alert',
        },
        {
            'id': 'BEH-EVA-002',
            'name': '调试器检测',
            'description': '检测尝试识别调试器的行为',
            'metadata': {
                'attack_type': 'evasion',
                'rule_type': 'behavior',
                'severity': 'medium',
                'version': '11.0',
            },
            'condition': {
                'behaviors': ['debugger_detection'],
                'patterns': ['ptrace', 'IsDebuggerPresent', 'anti_debug'],
            },
            'action': 'alert',
        },
        {
            'id': 'BEH-EVA-003',
            'name': '延迟执行',
            'description': '检测使用延迟执行绕过分析的行为',
            'metadata': {
                'attack_type': 'evasion',
                'rule_type': 'behavior',
                'severity': 'medium',
                'version': '11.0',
            },
            'condition': {
                'behaviors': ['delayed_execution'],
                'patterns': ['time.sleep(.*[3-9][0-9]{2,})', 'setTimeout.*60000'],
            },
            'action': 'alert',
        },
        {
            'id': 'BEH-EVA-004',
            'name': '条件触发',
            'description': '检测基于特定条件触发的行为',
            'metadata': {
                'attack_type': 'evasion',
                'rule_type': 'behavior',
                'severity': 'medium',
                'version': '11.0',
            },
            'condition': {
                'behaviors': ['conditional_trigger'],
                'patterns': ['if hostname.*target', 'if user.*admin'],
            },
            'action': 'alert',
        },
        {
            'id': 'BEH-EVA-005',
            'name': '代码混淆',
            'description': '检测使用代码混淆的行为',
            'metadata': {
                'attack_type': 'evasion',
                'rule_type': 'behavior',
                'severity': 'medium',
                'version': '11.0',
            },
            'condition': {
                'behaviors': ['code_obfuscation'],
                'patterns': ['base64.b64decode.*exec', 'eval(atob(', 'rot13'],
            },
            'action': 'alert',
        },
    ],
}

# ============== 行为规则生成器 ==============

class BehaviorRuleGenerator:
    """行为规则生成器"""
    
    def __init__(self, output_dir):
        self.output_dir = Path(output_dir)
        self.generated_rules = []
    
    def generate_all(self):
        """生成所有行为规则"""
        print("=" * 60)
        print("Round 11 - 行为规则生成")
        print("=" * 60)
        
        # 按类别生成
        for category, rules in BEHAVIOR_RULES.items():
            print(f"\n📋 生成 [{category}] 规则...")
            for rule in rules:
                self.generated_rules.append(rule)
                print(f"  ✅ {rule['id']}: {rule['name']}")
        
        # 保存规则
        self._save_rules()
        
        # 打印摘要
        self._print_summary()
        
        return self.generated_rules
    
    def _save_rules(self):
        """保存规则到文件"""
        # 按攻击类型分组
        by_attack_type = {}
        for rule in self.generated_rules:
            attack_type = rule['metadata']['attack_type']
            if attack_type not in by_attack_type:
                by_attack_type[attack_type] = []
            by_attack_type[attack_type].append(rule)
        
        # 每个攻击类型保存一个文件
        for attack_type, rules in by_attack_type.items():
            output_file = self.output_dir / f"behavior_{attack_type}.yaml"
            
            rule_data = {
                'version': '11.0',
                'category': 'behavior',
                'attack_type': attack_type,
                'generated_at': datetime.now().isoformat(),
                'rule_count': len(rules),
                'rules': rules,
            }
            
            with open(output_file, 'w') as f:
                yaml.dump(rule_data, f, allow_unicode=True, default_flow_style=False)
            
            print(f"\n📝 保存 {attack_type} 行为规则：{output_file}")
        
        # 保存总索引
        index_file = self.output_dir.parent / "results" / "behavior_rules_index.json"
        index = {
            'version': '11.0',
            'generated_at': datetime.now().isoformat(),
            'total_rules': len(self.generated_rules),
            'by_category': {cat: len(rules) for cat, rules in BEHAVIOR_RULES.items()},
            'by_attack_type': {k: len(v) for k, v in by_attack_type.items()},
        }
        
        with open(index_file, 'w') as f:
            json.dump(index, f, indent=2, ensure_ascii=False)
        
        print(f"\n📝 保存行为规则索引：{index_file}")
    
    def _print_summary(self):
        """打印摘要"""
        print("\n" + "=" * 60)
        print("📊 行为规则生成摘要")
        print("=" * 60)
        
        print(f"总规则数：{len(self.generated_rules)}")
        print("\n按类别:")
        for category, rules in BEHAVIOR_RULES.items():
            print(f"  {category}: {len(rules)}")
        
        print("\n按攻击类型:")
        by_type = {}
        for rule in self.generated_rules:
            attack_type = rule['metadata']['attack_type']
            by_type[attack_type] = by_type.get(attack_type, 0) + 1
        
        for attack_type, count in sorted(by_type.items()):
            print(f"  {attack_type}: {count}")
        
        print("\n" + "=" * 60)
        print("✅ 行为规则生成完成")
        print("=" * 60)

# ============== 主函数 ==============

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Round 11 行为规则生成器")
    parser.add_argument('--generate', action='store_true', help='生成行为规则')
    parser.add_argument('--attack-types', nargs='+', help='指定攻击类型')
    parser.add_argument('--output', '-o', default=str(RULES_DIR / "optimized"), help='输出目录')
    
    args = parser.parse_args()
    
    generator = BehaviorRuleGenerator(args.output)
    
    if args.generate or not args.attack_types:
        generator.generate_all()
    else:
        # 只生成指定类型
        for attack_type in args.attack_types:
            if attack_type in BEHAVIOR_RULES:
                print(f"生成 {attack_type} 行为规则...")
                # 简化处理，生成所有
        generator.generate_all()

if __name__ == "__main__":
    main()
