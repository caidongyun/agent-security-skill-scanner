#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LOLBAS Rules Fetcher - 从 LOLBAS 项目获取规则
https://lolbas-project.github.io/
"""

import os
import json
import requests
import logging
from typing import List, Dict
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

class LOLBASFetcher:
    """LOLBAS 规则获取器"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.base_url = "https://raw.githubusercontent.com/LOLBAS-Project/LOLBAS/master/"
        self.output_dir = Path(self.config.get('output_dir', 'external_rules/lolbas'))
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def fetch_all(self) -> List[Dict]:
        """获取所有 LOLBAS 条目"""
        logger.info("开始获取 LOLBAS 规则...")
        
        rules = []
        
        # 获取 binaries 列表
        binaries = self._fetch_category("binaries/")
        rules.extend(binaries)
        
        # 获取 scripts 列表
        scripts = self._fetch_category("scripts/")
        rules.extend(scripts)
        
        # 获取 libraries 列表
        libraries = self._fetch_category("libraries/")
        rules.extend(libraries)
        
        # 保存规则
        self._save_rules(rules)
        
        logger.info(f"LOLBAS 规则获取完成：{len(rules)} 条")
        return rules
    
    def _fetch_category(self, category: str) -> List[Dict]:
        """获取指定类别的规则"""
        rules = []
        
        try:
            # 获取索引文件
            index_url = f"{self.base_url}{category}index.json"
            response = requests.get(index_url, timeout=30)
            response.raise_for_status()
            
            index_data = response.json()
            
            # 获取每个条目的详细信息
            for item in index_data:
                rule = self._fetch_item(category, item.get('name'))
                if rule:
                    rules.append(rule)
        
        except Exception as e:
            logger.error(f"获取 {category} 失败：{e}")
        
        return rules
    
    def _fetch_item(self, category: str, name: str) -> Dict:
        """获取单个条目"""
        try:
            url = f"{self.base_url}{category}{name}.md"
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # 解析 Markdown 内容
            content = response.text
            rule = self._parse_markdown(content, name, category)
            
            return rule
        
        except Exception as e:
            logger.error(f"获取 {name} 失败：{e}")
            return None
    
    def _parse_markdown(self, content: str, name: str, category: str) -> Dict:
        """解析 Markdown 内容"""
        rule = {
            'source': 'LOLBAS',
            'name': name,
            'category': category.rstrip('/'),
            'commands': [],
            'detection': [],
            'mitre_attack': [],
            'retrieved_at': datetime.now().isoformat(),
        }
        
        # 提取命令
        import re
        command_pattern = r'```(?:powershell|cmd|powershell\n|cmd\n)?(.*?)```'
        commands = re.findall(command_pattern, content, re.DOTALL)
        rule['commands'] = [cmd.strip() for cmd in commands if cmd.strip()]
        
        # 提取 MITRE ATT&CK 技术 ID
        mitre_pattern = r'(T\d{4}\.\d{3}|T\d{4})'
        mitre_ids = re.findall(mitre_pattern, content)
        rule['mitre_attack'] = list(set(mitre_ids))
        
        # 提取检测规则
        if 'detection:' in content.lower():
            rule['detection'] = self._extract_detection(content)
        
        return rule
    
    def _extract_detection(self, content: str) -> List[str]:
        """提取检测规则"""
        detections = []
        # 简化实现，实际需更复杂的解析
        return detections
    
    def _save_rules(self, rules: List[Dict]):
        """保存规则"""
        output_file = self.output_dir / f"lolbas_rules_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'source': 'LOLBAS',
                'retrieved_at': datetime.now().isoformat(),
                'total_count': len(rules),
                'rules': rules
            }, f, indent=2, ensure_ascii=False)
        
        logger.info(f"规则保存到：{output_file}")
    
    def convert_to_yara(self, rules: List[Dict]) -> str:
        """转换为 YARA 规则"""
        yara_rules = []
        
        for i, rule in enumerate(rules):
            yara = self._rule_to_yara(rule, i)
            if yara:
                yara_rules.append(yara)
        
        return "\n\n".join(yara_rules)
    
    def _rule_to_yara(self, rule: Dict, index: int) -> str:
        """单个规则转 YARA"""
        name = rule.get('name', f'LOLBAS_{index}')
        commands = rule.get('commands', [])
        
        if not commands:
            return None
        
        yara = f"""rule LOLBAS_{name.replace(' ', '_')}_{index} {{
    meta:
        source = "LOLBAS"
        name = "{name}"
        category = "{rule.get('category', 'unknown')}"
        mitre_attack = {json.dumps(rule.get('mitre_attack', []))}
    
    strings:
"""
        
        # 添加命令特征
        for i, cmd in enumerate(commands[:5]):  # 限制前 5 个命令
            cmd_escaped = cmd.replace('"', '\\"').replace('\\', '\\\\')
            yara += f'        $cmd{i} = "{cmd_escaped}" ascii\n'
        
        yara += """
    condition:
        any of them
}"""
        
        return yara


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    config = {
        'output_dir': 'external_rules/lolbas'
    }
    
    fetcher = LOLBASFetcher(config)
    rules = fetcher.fetch_all()
    
    # 转换为 YARA
    yara_rules = fetcher.convert_to_yara(rules)
    
    # 保存 YARA 规则
    yara_file = Path(config['output_dir']) / 'lolbas.yara'
    with open(yara_file, 'w', encoding='utf-8') as f:
        f.write(yara_rules)
    
    print(f"✅ LOLBAS 规则获取完成：{len(rules)} 条")
    print(f"✅ YARA 规则保存：{yara_file}")
