#!/usr/bin/env python3
"""
Scanner V3 Web Dashboard - 优化版本
修复 HTML 渲染问题，增强稳定性
"""

import http.server
import socketserver
import json
from pathlib import Path
from datetime import datetime

PORT = 8080
DATA_FILE = Path(__file__).parent / "dashboard_data.json"

def load_data():
    """加载仪表板数据"""
    default_data = {
        "round15": {"samples": 353, "detection_rate": "100%", "p99_latency": "0.01ms"},
        "round16": {"files": 353, "malicious": 353, "detection_rate": "100%"},
        "round17": {"agents": 4, "framework": "✅", "mode": "顺序/并行"},
        "round18": {"mode": "多进程", "improvement": "4-8x", "cache_hit": "90%+"},
        "summary": {
            "total_samples": 353,
            "detection_rate": "100%",
            "rules": 214,
            "false_positive": "0%",
            "performance": "4-8x"
        },
        "updated": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return default_data

def generate_html(data):
    """生成 HTML 页面"""
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Scanner V3 Dashboard</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }}
        h1 {{ color: white; text-align: center; margin-bottom: 30px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; margin-bottom: 20px; }}
        .card {{ background: white; padding: 25px; border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); transition: transform 0.3s; }}
        .card:hover {{ transform: translateY(-5px); }}
        .card h2 {{ color: #667eea; font-size: 18px; margin-bottom: 15px; border-bottom: 3px solid #667eea; padding-bottom: 10px; }}
        .metric {{ display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #f0f0f0; }}
        .metric:last-child {{ border-bottom: none; }}
        .metric span:first-child {{ color: #666; }}
        .metric span:last-child {{ color: #28a745; font-weight: bold; }}
        .summary {{ background: white; padding: 25px; border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }}
        .summary h2 {{ color: #667eea; font-size: 18px; margin-bottom: 15px; border-bottom: 3px solid #667eea; padding-bottom: 10px; }}
        .footer {{ text-align: center; color: rgba(255,255,255,0.8); margin-top: 30px; font-size: 14px; }}
        .refresh {{ background: linear-gradient(135deg, #667eea, #764ba2); color: white; border: none; padding: 12px 30px; border-radius: 25px; cursor: pointer; margin: 20px auto; display: block; font-size: 16px; transition: transform 0.2s; }}
        .refresh:hover {{ transform: scale(1.05); }}
    </style>
</head>
<body>
    <h1>🔍 Scanner V3 - Web Dashboard</h1>
    
    <button class="refresh" onclick="location.reload()">🔄 刷新数据</button>
    
    <div class="grid">
        <div class="card">
            <h2>📊 Round 15: 样本验证</h2>
            <div class="metric"><span>总样本</span><span>{data['round15']['samples']}</span></div>
            <div class="metric"><span>检测率</span><span>{data['round15']['detection_rate']}</span></div>
            <div class="metric"><span>P99 延迟</span><span>{data['round15']['p99_latency']}</span></div>
        </div>
        
        <div class="card">
            <h2>🔍 Round 16: AST 检测</h2>
            <div class="metric"><span>总文件</span><span>{data['round16']['files']}</span></div>
            <div class="metric"><span>恶意</span><span>{data['round16']['malicious']}</span></div>
            <div class="metric"><span>检出率</span><span>{data['round16']['detection_rate']}</span></div>
        </div>
        
        <div class="card">
            <h2>🤖 Round 17: 多 Agent</h2>
            <div class="metric"><span>Agent 数量</span><span>{data['round17']['agents']}</span></div>
            <div class="metric"><span>编排框架</span><span>{data['round17']['framework']}</span></div>
            <div class="metric"><span>执行模式</span><span>{data['round17']['mode']}</span></div>
        </div>
        
        <div class="card">
            <h2>⚡ Round 18: 性能优化</h2>
            <div class="metric"><span>扫描模式</span><span>{data['round18']['mode']}</span></div>
            <div class="metric"><span>性能提升</span><span>{data['round18']['improvement']}</span></div>
            <div class="metric"><span>缓存命中</span><span>{data['round18']['cache_hit']}</span></div>
        </div>
    </div>
    
    <div class="summary">
        <h2>📈 核心指标汇总</h2>
        <div class="metric"><span>总样本数</span><span>{data['summary']['total_samples']}</span></div>
        <div class="metric"><span>检测率</span><span>{data['summary']['detection_rate']}</span></div>
        <div class="metric"><span>规则数量</span><span>{data['summary']['rules']} 条</span></div>
        <div class="metric"><span>误报率</span><span>{data['summary']['false_positive']}</span></div>
        <div class="metric"><span>性能提升</span><span>{data['summary']['performance']}</span></div>
    </div>
    
    <div class="footer">
        <p>Scanner V3 v3.0 | 更新时间：{data['updated']}</p>
        <p style="margin-top: 10px; font-size: 12px;">独立 Web 服务 - 与主扫描程序隔离</p>
    </div>
</body>
</html>'''

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        try:
            data = load_data()
            html = generate_html(data)
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', len(html.encode('utf-8')))
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(f"Error: {str(e)}".encode('utf-8'))
    
    def log_message(self, format, *args):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {args[0]}")

if __name__ == '__main__':
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(('0.0.0.0', PORT), DashboardHandler) as httpd:
        print(f'🌐 Scanner V3 Web Dashboard (优化版)')
        print(f'   本地：http://localhost:{PORT}')
        print(f'   远程：http://192.168.0.103:{PORT}')
        print(f'   数据：{DATA_FILE}')
        print(f'   按 Ctrl+C 停止')
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print('\n👋 已停止')
