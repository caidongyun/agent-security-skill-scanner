#!/usr/bin/env python3
"""
Phase 1 样本测试 - 用真实 OpenClaw skills 验证
"""

import os
import sys
import json
import yaml
import re
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('Phase1SampleTest')

WORKSPACE_DIR = Path('/home/cdy/.openclaw/workspace/agent-security-skill-scanner-master/release/v5.8.0')
PATTERNS_FILE = WORKSPACE_DIR / 'rules' / 'v580_patterns_semgrep.yaml'
SKILLS_DIR = Path('/home/cdy/.openclaw/workspace/skills')
OUTPUT_FILE = WORKSPACE_DIR / 'reports' / 'phase1_sample_test.json'

def test():
    """用真实样本测试 Phase 1"""
    logger.info("🧪 Phase 1 真实样本测试")
    
    # 1. 加载 Patterns
    with open(PATTERNS_FILE, 'r', encoding='utf-8') as f:
        patterns_data = yaml.safe_load(f)
    
    patterns = patterns_data.get('patterns', [])
    logger.info(f"  加载 {len(patterns)} 个 Patterns")
    
    # 2. 编译正则
    compiled_patterns = []
    for p in patterns:
        try:
            compiled_patterns.append({
                'id': p['id'],
                'pattern': re.compile(p['pattern']),
                'severity': p['severity']
            })
        except Exception as e:
            logger.warning(f"  Pattern {p['id']} 编译失败：{str(e)}")
    
    logger.info(f"  成功编译 {len(compiled_patterns)} 个 Patterns")
    
    # 3. 扫描样本 (抽样 100 个 skills)
    import random
    skill_files = list(SKILLS_DIR.glob('**/*.py'))[:100]
    logger.info(f"  扫描 {len(skill_files)} 个样本文件")
    
    # 4. 执行扫描
    scan_results = []
    total_hits = 0
    files_with_hits = 0
    
    for skill_file in skill_files:
        try:
            with open(skill_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            hits = []
            for cp in compiled_patterns:
                if cp['pattern'].search(content):
                    hits.append({
                        'pattern_id': cp['id'],
                        'severity': cp['severity']
                    })
            
            if hits:
                files_with_hits += 1
                total_hits += len(hits)
                scan_results.append({
                    'file': str(skill_file.relative_to(SKILLS_DIR)),
                    'hits': hits,
                    'hit_count': len(hits)
                })
        except Exception as e:
            pass
    
    # 5. 统计结果
    detection_rate = files_with_hits / len(skill_files) * 100 if skill_files else 0
    avg_hits_per_file = total_hits / files_with_hits if files_with_hits else 0
    
    # 6. 保存报告
    report = {
        'test_time': datetime.now().isoformat(),
        'total_patterns': len(compiled_patterns),
        'total_samples': len(skill_files),
        'files_with_hits': files_with_hits,
        'total_hits': total_hits,
        'detection_rate': f"{detection_rate:.2f}%",
        'avg_hits_per_file': f"{avg_hits_per_file:.2f}",
        'sample_results': scan_results[:20]  # 只显示前 20 个
    }
    
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    logger.info(f"✅ 测试完成")
    logger.info(f"  扫描样本：{len(skill_files)} 个")
    logger.info(f"  检出文件：{files_with_hits} 个 ({detection_rate:.2f}%)")
    logger.info(f"  总命中数：{total_hits}")
    logger.info(f"  平均每文件：{avg_hits_per_file:.2f} 个命中")
    logger.info(f"  报告保存至：{OUTPUT_FILE}")
    
    return report

if __name__ == '__main__':
    result = test()
    print(json.dumps(result, indent=2, ensure_ascii=False)[:2000])
