#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MITRE ATT&CK Rules Fetcher - 从 MITRE ATT&CK 获取规则
https://attack.mitre.org/
"""

import os
import json
import requests
import logging
from typing import List, Dict
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

class MITREFetcher:
    """MITRE ATT&CK 规则获取器"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.enterprise_url = "https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json"
        self.output_dir = Path(self.config.get('output_dir', 'external_rules/mitre'))
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def fetch_all(self) -> Dict:
        """获取所有 MITRE ATT&CK 数据"""
        logger.info("开始获取 MITRE ATT&CK 数据...")
        
        try:
            response = requests.get(self.enterprise_url, timeout=60)
            response.raise_for_status()
            
            data = response.json()
            
            # 解析数据
            parsed = self._parse_data(data)
            
            # 保存
            self._save_data(parsed)
            
            logger.info(f"MITRE ATT&CK 数据获取完成")
            return parsed
        
        except Exception as e:
            logger.error(f"获取 MITRE ATT&CK 失败：{e}")
            return {}
    
    def _parse_data(self, data: Dict) -> Dict:
        """解析 MITRE ATT&CK 数据"""
        parsed = {
            'source': 'MITRE ATT&CK',
            'retrieved_at': datetime.now().isoformat(),
            'version': data.get('spec_version', 'unknown'),
            'techniques': [],
            'tactics': [],
            'software': [],
            'groups': [],
        }
        
        for obj in data.get('objects', []):
            obj_type = obj.get('type')
            
            if obj_type == 'attack-pattern':
                parsed['techniques'].append(self._parse_technique(obj))
            elif obj_type == 'x-mitre-tactic':
                parsed['tactics'].append(self._parse_tactic(obj))
            elif obj_type == 'malware' or obj_type == 'tool':
                parsed['software'].append(self._parse_software(obj))
            elif obj_type == 'intrusion-set':
                parsed['groups'].append(self._parse_group(obj))
        
        return parsed
    
    def _parse_technique(self, obj: Dict) -> Dict:
        """解析技术"""
        return {
            'id': obj.get('external_references', [{}])[0].get('external_id', 'unknown'),
            'name': obj.get('name', 'unknown'),
            'description': obj.get('description', ''),
            'kill_chain': obj.get('kill_chain_phases', []),
            'platforms': obj.get('x_mitre_platforms', []),
            'permissions': obj.get('x_mitre_permissions_required', []),
            'data_sources': obj.get('x_mitre_data_sources', []),
            'detection': obj.get('x_mitre_detection', ''),
            'mitigated_by': obj.get('x_mitre_mitigation', []),
        }
    
    def _parse_tactic(self, obj: Dict) -> Dict:
        """解析战术"""
        return {
            'id': obj.get('external_references', [{}])[0].get('external_id', 'unknown'),
            'name': obj.get('name', 'unknown'),
            'description': obj.get('description', ''),
            'short_name': obj.get('x_mitre_shortname', ''),
        }
    
    def _parse_software(self, obj: Dict) -> Dict:
        """解析软件"""
        return {
            'id': obj.get('name', 'unknown'),
            'type': obj.get('type', 'unknown'),
            'description': obj.get('description', ''),
            'aliases': obj.get('aliases', []),
        }
    
    def _parse_group(self, obj: Dict) -> Dict:
        """解析组织"""
        return {
            'id': obj.get('name', 'unknown'),
            'description': obj.get('description', ''),
            'aliases': obj.get('aliases', []),
        }
    
    def _save_data(self, data: Dict):
        """保存数据"""
        output_file = self.output_dir / f"mitre_attack_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"数据保存到：{output_file}")
    
    def generate_sigma_rules(self, techniques: List[Dict]) -> str:
        """生成 Sigma 规则"""
        sigma_rules = []
        
        for tech in techniques[:20]:  # 限制前 20 个
            sigma = self._tech_to_sigma(tech)
            if sigma:
                sigma_rules.append(sigma)
        
        return "\n---\n".join(sigma_rules)
    
    def _tech_to_sigma(self, tech: Dict) -> str:
        """单个技术转 Sigma"""
        tech_id = tech.get('id', 'UNKNOWN')
        tech_name = tech.get('name', 'Unknown Technique')
        
        sigma = f"""title: MITRE ATT&CK {tech_name}
id: {self._generate_uuid()}
status: stable
description: {tech.get('description', '')[:200]}
author: MITRE ATT&CK + Lingshun V5
date: {datetime.now().strftime('%Y/%m/%d')}
references:
    - https://attack.mitre.org/techniques/{tech_id.replace('.', '/')}
tags:
    - attack.{tech_id.lower()}
logsource:
    category: process_creation
    product: linux
detection:
    selection:
        # TODO: 根据具体技术添加检测条件
    condition: selection
falsepositives:
    - 需要根据具体环境评估
level: medium
"""
        return sigma
    
    def _generate_uuid(self) -> str:
        """生成 UUID"""
        import uuid
        return str(uuid.uuid4())


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    config = {
        'output_dir': 'external_rules/mitre'
    }
    
    fetcher = MITREFetcher(config)
    data = fetcher.fetch_all()
    
    # 生成 Sigma 规则
    if data.get('techniques'):
        sigma_rules = fetcher.generate_sigma_rules(data['techniques'])
        
        sigma_file = Path(config['output_dir']) / 'mitre_sigma.yml'
        with open(sigma_file, 'w', encoding='utf-8') as f:
            f.write(sigma_rules)
    
    print(f"✅ MITRE ATT&CK 数据获取完成")
    print(f"✅ 技术数：{len(data.get('techniques', []))}")
    print(f"✅ Sigma 规则保存：{config['output_dir']}/mitre_sigma.yml")
