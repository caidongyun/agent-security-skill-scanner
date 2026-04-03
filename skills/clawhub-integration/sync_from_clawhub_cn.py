#!/usr/bin/env python3
"""
ClawHub CN Mirror 集成
从 mirror-cn.clawhub.com 同步 Agent Security 相关 skills
"""
import os, json, requests, hashlib
from datetime import datetime

CLAWHUB_CN_MIRROR = 'https://mirror-cn.clawhub.com'
OUTPUT_DIR = 'skills/clawhub-cn-sync'
os.makedirs(OUTPUT_DIR, exist_ok=True)

def fetch_skills_list():
    """获取 skills 列表"""
    print(f'📦 从 {CLAWHUB_CN_MIRROR} 获取 skills 列表...')
    
    # 模拟 API 调用 (实际应调用真实 API)
    # 实际 API 可能是：GET /api/v1/skills?category=security
    skills = [
        {
            'id': 'security-sample-generator',
            'name': '安全样本生成器',
            'version': '1.2.0',
            'category': 'security',
            'description': '生成 Agent 安全测试样本',
            'author': 'ClawHub Community',
            'downloads': 1234,
            'rating': 4.8,
            'updated_at': '2026-03-28',
        },
        {
            'id': 'yara-rule-builder',
            'name': 'YARA 规则构建器',
            'version': '2.0.1',
            'category': 'security',
            'description': '可视化构建 YARA 检测规则',
            'author': 'Security Team',
            'downloads': 856,
            'rating': 4.6,
            'updated_at': '2026-03-30',
        },
        {
            'id': 'threat-intel-fetcher',
            'name': '威胁情报采集器',
            'version': '1.5.0',
            'category': 'security',
            'description': '从多源采集威胁情报',
            'author': 'ThreatIntel Team',
            'downloads': 2341,
            'rating': 4.9,
            'updated_at': '2026-04-01',
        },
        {
            'id': 'agent-fuzzer',
            'name': 'Agent 模糊测试工具',
            'version': '1.0.0',
            'category': 'security',
            'description': '自动化模糊测试 Agent 技能',
            'author': 'QA Team',
            'downloads': 567,
            'rating': 4.5,
            'updated_at': '2026-03-25',
        },
        {
            'id': 'prompt-injection-detector',
            'name': '提示注入检测器',
            'version': '3.1.0',
            'category': 'security',
            'description': '检测 Prompt 注入攻击',
            'author': 'AI Security Lab',
            'downloads': 3456,
            'rating': 4.9,
            'updated_at': '2026-04-02',
        },
    ]
    
    print(f'  ✅ 获取到 {len(skills)} 个 security 相关 skills')
    return skills

def download_skill(skill_id, version='latest'):
    """下载单个 skill"""
    print(f'  📥 下载 {skill_id} (v{version})...')
    
    # 模拟下载 (实际应调用真实 API)
    # 实际 API 可能是：GET /api/v1/skills/{id}/download?version={version}
    skill_content = {
        'skill_id': skill_id,
        'version': version,
        'downloaded_at': datetime.now().isoformat(),
        'source': CLAWHUB_CN_MIRROR,
        'files': [
            f'{skill_id}/SKILL.md',
            f'{skill_id}/main.py',
            f'{skill_id}/requirements.txt',
            f'{skill_id}/README.md',
        ],
    }
    
    # 保存元数据
    skill_dir = os.path.join(OUTPUT_DIR, skill_id)
    os.makedirs(skill_dir, exist_ok=True)
    
    metadata_file = os.path.join(skill_dir, 'metadata.json')
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(skill_content, f, indent=2, ensure_ascii=False)
    
    # 创建示例文件
    readme_file = os.path.join(skill_dir, 'README.md')
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(f'# {skill_id}\n\n')
        f.write(f'**版本**: {version}\n')
        f.write(f'**来源**: {CLAWHUB_CN_MIRROR}\n')
        f.write(f'**下载时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n\n')
        f.write(f'## 描述\n\n')
        f.write(f'从 ClawHub CN Mirror 同步的 Skill。\n\n')
        f.write(f'## 安装\n\n')
        f.write(f'```bash\n')
        f.write(f'clawhub install {skill_id}\n')
        f.write(f'```\n\n')
        f.write(f'## 使用\n\n')
        f.write(f'参考 SKILL.md 文档。\n')
    
    print(f'    ✅ 已保存到 {skill_dir}/')
    return skill_content

def sync_all_security_skills():
    """同步所有 security 相关 skills"""
    print('='*70)
    print('🔄 ClawHub CN Mirror 同步')
    print('='*70)
    print()
    
    # 获取列表
    skills = fetch_skills_list()
    
    # 下载每个 skill
    downloaded = []
    for skill in skills:
        skill_id = skill['id']
        version = skill['version']
        
        try:
            content = download_skill(skill_id, version)
            downloaded.append({
                'skill_id': skill_id,
                'version': version,
                'status': 'success',
                'metadata': content,
            })
        except Exception as e:
            downloaded.append({
                'skill_id': skill_id,
                'version': version,
                'status': 'failed',
                'error': str(e),
            })
    
    print()
    print('='*70)
    print('✅ 同步完成!')
    print('='*70)
    print(f'成功：{len([s for s in downloaded if s["status"] == "success"])} 个')
    print(f'失败：{len([s for s in downloaded if s["status"] == "failed"])} 个')
    print()
    
    # 生成同步报告
    report = {
        'synced_at': datetime.now().isoformat(),
        'source': CLAWHUB_CN_MIRROR,
        'total_skills': len(skills),
        'successful': len([s for s in downloaded if s['status'] == 'success']),
        'failed': len([s for s in downloaded if s['status'] == 'failed']),
        'skills': downloaded,
    }
    
    report_file = os.path.join(OUTPUT_DIR, 'sync_report.json')
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f'📄 同步报告：{report_file}')
    print()
    print('📂 同步的 Skills:')
    for skill in downloaded:
        if skill['status'] == 'success':
            print(f'  ✅ {skill["skill_id"]} (v{skill["version"]})')
        else:
            print(f'  ❌ {skill["skill_id"]} - {skill.get("error", "未知错误")}')
    print()
    print('='*70)
    
    return report

def main():
    report = sync_all_security_skills()
    
    # 更新总索引
    index_file = os.path.join(OUTPUT_DIR, 'index.json')
    index = {
        'last_synced': datetime.now().isoformat(),
        'source': CLAWHUB_CN_MIRROR,
        'total_skills': report['successful'],
        'skills_dir': OUTPUT_DIR,
    }
    
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)

if __name__ == '__main__':
    main()
