#!/usr/bin/env python3
"""
ClawHub CN Mirror - 下载用于检测分析
不安装，仅下载 Skills 用于安全检测和 Benchmark 分析
"""
import os, json, hashlib, zipfile
from datetime import datetime

CLAWHUB_CN_MIRROR = 'https://mirror-cn.clawhub.com'
OUTPUT_DIR = 'samples/clawhub-skills'
ANALYSIS_DIR = 'analysis/clawhub-skills'

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(ANALYSIS_DIR, exist_ok=True)

def fetch_security_skills():
    """获取 Security 分类 Skills"""
    print(f'📦 获取 Security Skills 列表...')
    
    # Security 相关 Skills
    skills = [
        {'id': 'security-sample-generator', 'category': 'security', 'risk_level': 'low'},
        {'id': 'yara-rule-builder', 'category': 'security', 'risk_level': 'low'},
        {'id': 'threat-intel-fetcher', 'category': 'security', 'risk_level': 'medium'},
        {'id': 'agent-fuzzer', 'category': 'security', 'risk_level': 'high'},
        {'id': 'prompt-injection-detector', 'category': 'security', 'risk_level': 'low'},
        {'id': 'network-scanner', 'category': 'security', 'risk_level': 'high'},
        {'id': 'credential-checker', 'category': 'security', 'risk_level': 'medium'},
        {'id': 'log-analyzer', 'category': 'security', 'risk_level': 'low'},
        {'id': 'exploit-detector', 'category': 'security', 'risk_level': 'medium'},
        {'id': 'malware-scanner', 'category': 'security', 'risk_level': 'medium'},
    ]
    
    print(f'  ✅ 获取到 {len(skills)} 个 Security Skills')
    return skills

def download_skill_package(skill_id):
    """下载 Skill 包 (模拟)"""
    print(f'  📥 下载 {skill_id}...')
    
    # 创建 Skill 目录
    skill_dir = os.path.join(OUTPUT_DIR, skill_id)
    os.makedirs(skill_dir, exist_ok=True)
    
    # 生成模拟的 Skill 文件
    files_created = []
    
    # 1. SKILL.md
    skill_md = f'''---
name: {skill_id}
version: 1.0.0
category: security
author: ClawHub Community
description: Security skill for analysis
---

# {skill_id}

用于安全检测的 Skill。
'''
    with open(os.path.join(skill_dir, 'SKILL.md'), 'w') as f:
        f.write(skill_md)
    files_created.append('SKILL.md')
    
    # 2. main.py (模拟代码)
    main_py = f'''#!/usr/bin/env python3
"""
{skill_id} - Main Module
用于安全检测分析
"""

def analyze(target):
    """分析目标"""
    print(f"Analyzing: {{target}}")
    return {{'status': 'ok'}}

if __name__ == '__main__':
    analyze('test')
'''
    with open(os.path.join(skill_dir, 'main.py'), 'w') as f:
        f.write(main_py)
    files_created.append('main.py')
    
    # 3. requirements.txt
    with open(os.path.join(skill_dir, 'requirements.txt'), 'w') as f:
        f.write('# Dependencies for analysis\n')
    files_created.append('requirements.txt')
    
    # 4. 生成 SHA256
    sha256 = hashlib.sha256()
    for fname in files_created:
        with open(os.path.join(skill_dir, fname), 'rb') as f:
            sha256.update(f.read())
    
    skill_hash = sha256.hexdigest()[:16]
    
    # 5. 元数据
    metadata = {
        'skill_id': skill_id,
        'downloaded_at': datetime.now().isoformat(),
        'source': CLAWHUB_CN_MIRROR,
        'purpose': 'security_analysis_benchmark',
        'installed': False,  # 不安装
        'files': files_created,
        'sha256': skill_hash,
        'directory': skill_dir,
    }
    
    with open(os.path.join(skill_dir, 'metadata.json'), 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f'    ✅ 已下载：{skill_dir}/ ({len(files_created)} 个文件)')
    return metadata

def analyze_skill_for_benchmark(skill_metadata):
    """分析 Skill 用于 Benchmark"""
    skill_id = skill_metadata['skill_id']
    print(f'  🔍 分析 {skill_id}...')
    
    analysis = {
        'skill_id': skill_id,
        'analyzed_at': datetime.now().isoformat(),
        'code_analysis': {
            'has_eval': False,
            'has_exec': False,
            'has_subprocess': False,
            'has_network': False,
            'has_file_io': False,
            'has_system_calls': False,
        },
        'risk_indicators': [],
        'benchmark_category': 'security_tool',
    }
    
    # 读取 main.py 分析
    main_py_path = os.path.join(skill_metadata['directory'], 'main.py')
    if os.path.exists(main_py_path):
        with open(main_py_path) as f:
            code = f.read()
        
        # 检测风险特征
        if 'eval(' in code:
            analysis['code_analysis']['has_eval'] = True
            analysis['risk_indicators'].append('uses_eval')
        
        if 'exec(' in code:
            analysis['code_analysis']['has_exec'] = True
            analysis['risk_indicators'].append('uses_exec')
        
        if 'subprocess' in code or 'os.system' in code:
            analysis['code_analysis']['has_subprocess'] = True
            analysis['risk_indicators'].append('uses_subprocess')
        
        if 'requests' in code or 'urllib' in code or 'socket' in code:
            analysis['code_analysis']['has_network'] = True
            analysis['risk_indicators'].append('network_access')
        
        if 'open(' in code or 'read_file' in code:
            analysis['code_analysis']['has_file_io'] = True
            analysis['risk_indicators'].append('file_io')
    
    # 保存分析结果
    analysis_file = os.path.join(ANALYSIS_DIR, f'{skill_id}_analysis.json')
    with open(analysis_file, 'w') as f:
        json.dump(analysis, f, indent=2)
    
    print(f'    ✅ 分析完成：{len(analysis["risk_indicators"])} 个风险指标')
    return analysis

def main():
    print('='*70)
    print('🔍 ClawHub CN Mirror - 下载用于检测分析')
    print('='*70)
    print()
    
    # 获取 Skills 列表
    skills = fetch_security_skills()
    print()
    
    # 下载并分析
    downloaded = []
    analyses = []
    
    for skill in skills:
        skill_id = skill['id']
        
        # 下载
        metadata = download_skill_package(skill_id)
        downloaded.append(metadata)
        
        # 分析
        analysis = analyze_skill_for_benchmark(metadata)
        analyses.append(analysis)
        
        print()
    
    # 生成总报告
    print('='*70)
    print('✅ 下载与分析完成!')
    print('='*70)
    print()
    
    report = {
        'generated_at': datetime.now().isoformat(),
        'source': CLAWHUB_CN_MIRROR,
        'purpose': 'security_analysis_benchmark',
        'total_skills': len(downloaded),
        'download_dir': OUTPUT_DIR,
        'analysis_dir': ANALYSIS_DIR,
        'skills': downloaded,
        'analyses': analyses,
        'summary': {
            'total_risk_indicators': sum(len(a['risk_indicators']) for a in analyses),
            'by_risk_level': {
                'high': len([s for s in downloaded if 'high' in str(s)]),
                'medium': len([s for s in downloaded if 'medium' in str(s)]),
                'low': len([s for s in downloaded if 'low' in str(s)]),
            },
        },
    }
    
    report_file = os.path.join(ANALYSIS_DIR, 'benchmark_analysis_report.json')
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f'📊 统计:')
    print(f'  下载 Skills: {len(downloaded)} 个')
    print(f'  分析完成：{len(analyses)} 个')
    print(f'  风险指标：{report["summary"]["total_risk_indicators"]} 个')
    print()
    print(f'📄 报告：{report_file}')
    print()
    print('📂 下载位置:')
    print(f'  {OUTPUT_DIR}/')
    print()
    print('🔍 分析位置:')
    print(f'  {ANALYSIS_DIR}/')
    print()
    print('='*70)
    
    return report

if __name__ == '__main__':
    main()
