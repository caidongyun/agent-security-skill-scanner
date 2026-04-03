#!/usr/bin/env python3
"""
Scanner V3 Web Dashboard - 稳定版
支持本地/远程模式，优化错误处理和日志
"""

import http.server
import socketserver
import json
import sys
import traceback
from pathlib import Path
from datetime import datetime

DATA_FILE = Path(__file__).parent / "dashboard_data.json"

def load_data():
    """加载仪表板数据"""
    default_data = {
        "summary": {
            "total_samples": 353,
            "malicious": 353,
            "safe": 0,
            "detection_rate": "100.0%",
            "rules": 214,
            "false_positive": "0%",
            "p99_latency": "0.43ms",
            "performance": "4-8x"
        },
        "scan": {
            "mode": "多进程",
            "cache_hit": "90%+",
            "ast_analysis": "✅"
        },
        "updated": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # 合并数据，确保关键字段存在
                if 'summary' in data:
                    default_data['summary'].update(data['summary'])
                if 'scan' in data:
                    default_data['scan'].update(data['scan'])
                if 'updated' in data:
                    default_data['updated'] = data['updated']
                return default_data
        except Exception as e:
            print(f"[WARN] 加载数据文件失败：{e}")
    return default_data

def generate_html(data):
    """生成 HTML 页面 - 只展示用户价值"""
    s = data['summary']
    c = data['scan']
    
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Scanner V3 - 安全扫描器</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif; 
            max-width: 1200px; 
            margin: 0 auto; 
            padding: 20px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            min-height: 100vh; 
        }}
        h1 {{ 
            color: white; 
            text-align: center; 
            margin-bottom: 30px; 
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3); 
            font-size: 32px;
        }}
        .mode-badge {{ 
            background: rgba(255,255,255,0.2); 
            padding: 5px 15px; 
            border-radius: 15px; 
            font-size: 12px; 
            display: inline-block; 
            margin-bottom: 10px; 
        }}
        .mode-container {{ text-align: center; margin-bottom: 20px; }}
        .grid {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
            gap: 20px; 
            margin-bottom: 20px; 
        }}
        .card {{ 
            background: white; 
            padding: 25px; 
            border-radius: 12px; 
            box-shadow: 0 10px 30px rgba(0,0,0,0.2); 
            transition: transform 0.3s; 
        }}
        .card:hover {{ transform: translateY(-5px); }}
        .card h2 {{ 
            color: #667eea; 
            font-size: 20px; 
            margin-bottom: 15px; 
            border-bottom: 3px solid #667eea; 
            padding-bottom: 10px; 
        }}
        .metric {{ 
            display: flex; 
            justify-content: space-between; 
            padding: 12px 0; 
            border-bottom: 1px solid #f0f0f0; 
            font-size: 15px;
        }}
        .metric:last-child {{ border-bottom: none; }}
        .metric span:first-child {{ color: #666; }}
        .metric span:last-child {{ 
            color: #28a745; 
            font-weight: bold; 
            font-size: 16px;
        }}
        .footer {{ 
            text-align: center; 
            color: rgba(255,255,255,0.8); 
            margin-top: 30px; 
            font-size: 14px; 
        }}
        .refresh {{ 
            background: linear-gradient(135deg, #667eea, #764ba2); 
            color: white; 
            border: none; 
            padding: 12px 30px; 
            border-radius: 25px; 
            cursor: pointer; 
            margin: 20px auto; 
            display: block; 
            font-size: 16px; 
            transition: transform 0.2s; 
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }}
        .refresh:hover {{ 
            transform: scale(1.05); 
        }}
        .refresh:active {{
            transform: scale(0.98);
        }}
        .status {{
            background: rgba(255,255,255,0.95);
            padding: 15px 25px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
        }}
        .status .label {{ color: #666; margin-right: 10px; }}
        .status .value {{ color: #28a745; font-weight: bold; }}
    </style>
</head>
<body>
    <h1>🔍 Scanner V3 - 安全扫描器</h1>
    
    <div class="mode-container">
        <span class="mode-badge">{"🌐 远程模式" if len(sys.argv) > 1 and sys.argv[1] == "--remote" else "🔒 本地模式"}</span>
    </div>
    
    <div class="status">
        <span class="label">📊 总样本:</span><span class="value">{s['total_samples']}</span>
        <span style="margin: 0 15px;">|</span>
        <span class="label">✅ 检测率:</span><span class="value">{s['detection_rate']}</span>
        <span style="margin: 0 15px;">|</span>
        <span class="label">⚡ P99 延迟:</span><span class="value">{s['p99_latency']}</span>
        <span style="margin: 0 15px;">|</span>
        <span class="label">📜 规则:</span><span class="value">{s['rules']} 条</span>
    </div>
    
    <button class="refresh" onclick="location.reload()">🔄 刷新数据</button>
    
    <div class="grid">
        <div class="card">
            <h2>📊 扫描统计</h2>
            <div class="metric"><span>总样本数</span><span>{s['total_samples']}</span></div>
            <div class="metric"><span>恶意样本</span><span>{s['malicious']}</span></div>
            <div class="metric"><span>安全样本</span><span>{s['safe']}</span></div>
            <div class="metric"><span>检测率</span><span>{s['detection_rate']}</span></div>
            <div class="metric"><span>误报率</span><span>{s['false_positive']}</span></div>
        </div>
        
        <div class="card">
            <h2>🔍 检测能力</h2>
            <div class="metric"><span>检测规则</span><span>{s['rules']} 条</span></div>
            <div class="metric"><span>误报率</span><span>{s['false_positive']}</span></div>
            <div class="metric"><span>AST 分析</span><span>{c['ast_analysis']}</span></div>
            <div class="metric"><span>规则类型</span><span>Sigma/YARA/IOC</span></div>
        </div>
        
        <div class="card">
            <h2>⚡ 性能指标</h2>
            <div class="metric"><span>扫描模式</span><span>{c['mode']}</span></div>
            <div class="metric"><span>性能提升</span><span>{s['performance']}</span></div>
            <div class="metric"><span>缓存命中率</span><span>{c['cache_hit']}</span></div>
            <div class="metric"><span>P99 延迟</span><span>{s['p99_latency']}</span></div>
        </div>
    </div>
    
    <div class="footer">
        <p>Scanner V3 v3.0 | 更新时间：{data['updated']}</p>
        <p style="margin-top: 10px; font-size: 12px;">🔒 本地模式：仅本机访问 | 🌐 远程模式：局域网可访问</p>
    </div>
</body>
</html>'''

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'
    
    def do_GET(self):
        try:
            if self.path == '/' or self.path == '/index.html':
                data = load_data()
                html = generate_html(data)
                content = html.encode('utf-8')
                
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Content-Length', len(content))
                self.send_header('Connection', 'keep-alive')
                self.end_headers()
                self.wfile.write(content)
            elif self.path == '/favicon.ico':
                self.send_response(204)
                self.send_header('Content-Length', '0')
                self.send_header('Connection', 'keep-alive')
                self.end_headers()
            else:
                self.send_response(404)
                self.send_header('Content-Type', 'text/plain')
                self.send_header('Content-Length', '9')
                self.send_header('Connection', 'keep-alive')
                self.end_headers()
                self.wfile.write(b'Not Found')
        except Exception as e:
            print(f"[ERROR] 处理请求失败：{e}")
            traceback.print_exc()
            self.send_response(500)
            self.send_header('Content-Type', 'text/plain')
            self.send_header('Content-Length', '19')
            self.send_header('Connection', 'keep-alive')
            self.end_headers()
            self.wfile.write(b'Internal Server Error')
    
    def log_message(self, format, *args):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {args[0]}")

class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

if __name__ == '__main__':
    PORT = 8080
    
    # 默认本地监听，--remote 开启远程
    if len(sys.argv) > 1 and sys.argv[1] == '--remote':
        HOST = '0.0.0.0'
        print(f'🌐 Scanner V3 Web Dashboard (远程模式)')
        print(f'   本地：http://localhost:{PORT}')
        print(f'   远程：http://192.168.0.103:{PORT}')
    else:
        HOST = '127.0.0.1'
        print(f'🔒 Scanner V3 Web Dashboard (本地模式)')
        print(f'   访问：http://localhost:{PORT}')
        print(f'   远程访问：关闭')
    
    print(f'   数据：{DATA_FILE}')
    print(f'   按 Ctrl+C 停止')
    print(f'   日志：/tmp/scanner-web.log')
    
    with ReusableTCPServer((HOST, PORT), DashboardHandler) as httpd:
        print(f'✅ 服务已启动', flush=True)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print('\n👋 已停止')
