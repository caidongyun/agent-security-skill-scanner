#!/usr/bin/env python3
"""
良性样本采集器 - 系统性采集各类良性样本
"""
import os, json, hashlib, subprocess
from datetime import datetime

OUTPUT_BASE = 'samples/benign'

def ensure_dirs():
    """创建目录结构"""
    dirs = [
        'opensource/python', 'opensource/nodejs', 'opensource/go',
        'packages/pypi', 'packages/npm',
        'business/devops', 'business/datascience', 'business/webdev', 'business/cloud',
        'adversarial/rule_based',
    ]
    for d in dirs:
        os.makedirs(os.path.join(OUTPUT_BASE, d), exist_ok=True)
    print('✅ 目录结构创建完成')

def collect_github_samples(limit=100):
    """从 GitHub 采集样本 (模拟)"""
    print(f'📦 采集 GitHub 样本 (目标：{limit} 个)...')
    
    # 模拟采集 (实际应调用 GitHub API)
    samples = []
    
    # Python 示例
    python_scripts = [
        ('data_loader.py', '''#!/usr/bin/env python3
import pandas as pd
data = pd.read_csv('data.csv')
print(f"Loaded {len(data)} rows")
'''),
        ('api_client.py', '''#!/usr/bin/env python3
import requests
response = requests.get('https://api.example.com/data')
print(response.json())
'''),
        ('ml_train.py', '''#!/usr/bin/env python3
from sklearn.ensemble import RandomForestClassifier
model = RandomForestClassifier()
model.fit(X_train, y_train)
print("Training complete")
'''),
    ]
    
    for filename, content in python_scripts[:limit//3]:
        path = os.path.join(OUTPUT_BASE, 'opensource/python', filename)
        with open(path, 'w') as f:
            f.write(f'# Source: GitHub Top Python\n# Collected: {datetime.now()}\n\n{content}')
        samples.append({'file': path, 'type': 'python', 'source': 'github'})
    
    # Node.js 示例
    node_scripts = [
        ('server.js', '''#!/usr/bin/env node
const express = require('express');
const app = express();
app.get('/', (req, res) => res.send('Hello'));
app.listen(3000);
'''),
        ('build.js', '''#!/usr/bin/env node
const { exec } = require('child_process');
exec('npm run build', (err, stdout) => {
    console.log('Build complete');
});
'''),
    ]
    
    for filename, content in node_scripts[:limit//3]:
        path = os.path.join(OUTPUT_BASE, 'opensource/nodejs', filename)
        with open(path, 'w') as f:
            f.write(f'// Source: GitHub Top Node.js\n// Collected: {datetime.now()}\n\n{content}')
        samples.append({'file': path, 'type': 'nodejs', 'source': 'github'})
    
    print(f'  ✅ 采集 {len(samples)} 个 GitHub 样本')
    return samples

def collect_package_samples(source='pypi', limit=100):
    """从包管理器采集样本 (模拟)"""
    print(f'📦 采集 {source.upper()} 样本 (目标：{limit} 个)...')
    
    samples = []
    
    if source == 'pypi':
        packages = [
            ('requests_example.py', '''import requests
response = requests.get('https://httpbin.org/get')
print(response.status_code)
'''),
            ('pandas_example.py', '''import pandas as pd
df = pd.DataFrame({'a': [1,2,3]})
print(df.describe())
'''),
        ]
        subdir = 'pypi'
    else:
        packages = [
            ('express_example.js', '''const express = require('express');
const app = express();
app.listen(3000);
'''),
        ]
        subdir = 'npm'
    
    for filename, content in packages[:limit]:
        path = os.path.join(OUTPUT_BASE, 'packages', subdir, filename)
        with open(path, 'w') as f:
            f.write(f'# Source: {source.upper()}\n# Collected: {datetime.now()}\n\n{content}')
        samples.append({'file': path, 'type': subdir, 'source': source})
    
    print(f'  ✅ 采集 {len(samples)} 个 {source.upper()} 样本')
    return samples

def collect_business_samples():
    """采集业务场景样本"""
    print('📦 采集业务场景样本...')
    
    samples = []
    
    # DevOps
    devops_scripts = [
        ('deploy.sh', '''#!/bin/bash
# 部署脚本
git pull origin main
docker-compose up -d
echo "部署完成"
'''),
        ('backup.sh', '''#!/bin/bash
# 备份脚本
mysqldump -u root mydb > backup.sql
tar -czf backup.tar.gz backup.sql
echo "备份完成"
'''),
    ]
    
    for filename, content in devops_scripts:
        path = os.path.join(OUTPUT_BASE, 'business/devops', filename)
        with open(path, 'w') as f:
            f.write(f'# Business: DevOps\n# Collected: {datetime.now()}\n\n{content}')
        samples.append({'file': path, 'type': 'bash', 'source': 'devops'})
    
    # DataScience
    ds_scripts = [
        ('analysis.py', '''#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt
df = pd.read_csv('data.csv')
df.plot()
plt.savefig('chart.png')
'''),
    ]
    
    for filename, content in ds_scripts:
        path = os.path.join(OUTPUT_BASE, 'business/datascience', filename)
        with open(path, 'w') as f:
            f.write(f'# Business: DataScience\n# Collected: {datetime.now()}\n\n{content}')
        samples.append({'file': path, 'type': 'python', 'source': 'datascience'})
    
    print(f'  ✅ 采集 {len(samples)} 个业务场景样本')
    return samples

def generate_index(samples):
    """生成样本索引"""
    index = {
        'generated_at': datetime.now().isoformat(),
        'total_samples': len(samples),
        'by_type': {},
        'by_source': {},
        'samples': []
    }
    
    for s in samples:
        # 统计
        t = s.get('type', 'unknown')
        src = s.get('source', 'unknown')
        index['by_type'][t] = index['by_type'].get(t, 0) + 1
        index['by_source'][src] = index['by_source'].get(src, 0) + 1
        
        # 计算哈希
        if os.path.exists(s['file']):
            with open(s['file'], 'rb') as f:
                s['sha256'] = hashlib.sha256(f.read()).hexdigest()
        
        index['samples'].append(s)
    
    index_path = os.path.join(OUTPUT_BASE, 'index.json')
    with open(index_path, 'w') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
    
    print(f'✅ 索引生成：{index_path}')
    print(f'   总计：{len(samples)} 个样本')
    print(f'   类型：{index["by_type"]}')
    print(f'   来源：{index["by_source"]}')
    
    return index

def main():
    print('='*60)
    print('🔍 良性样本采集器')
    print('='*60)
    print()
    
    # 创建目录
    ensure_dirs()
    print()
    
    # 采集样本
    all_samples = []
    
    all_samples.extend(collect_github_samples(limit=6))
    all_samples.extend(collect_package_samples('pypi', limit=2))
    all_samples.extend(collect_package_samples('npm', limit=2))
    all_samples.extend(collect_business_samples())
    
    print()
    
    # 生成索引
    generate_index(all_samples)
    
    print()
    print('='*60)
    print('✅ 样本采集完成!')
    print('='*60)

if __name__ == '__main__':
    main()
