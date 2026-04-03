#!/usr/bin/env python3
"""
统一规则加载器 v2 - 只导出干净的规则
跳过有问题的 YARA 嵌套规则
"""

import json
import yaml
from pathlib import Path
from typing import List, Dict

class CleanRuleLoader:
    def __init__(self, rules_file=None):
        if rules_file is None:
            self.rules_file = Path(__file__).parent / "unified" / "all_rules_merged.json"
        else:
            self.rules_file = Path(rules_file)
        self.rules = []
        self.load()
    
    def load(self):
        """加载规则"""
        if not self.rules_file.exists():
            print(f"❌ 规则文件不存在: {self.rules_file}")
            return
        
        with open(self.rules_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.rules = data.get('rules', [])
        print(f"✅ 加载 {len(self.rules)} 条规则")
    
    def export_clean_yara(self, output_file):
        """只导出干净的 YARA 规则"""
        yara_content = "// Clean Unified Rules Export\n"
        yara_content += f"// Total: {len(self.rules)} rules\n\n"
        
        count = 0
        for rule in self.rules:
            src = rule.get('_merged_source', '')
            
            # 跳过包含原始 YARA 内容的所有规则 (无法安全解析)
            if '_raw_content' in rule:
                continue
            
            # 其他来源尝试转换
            rule_id = rule.get('id', rule.get('name', 'unknown'))
            safe_name = self._safe_name(rule_id)
            
            category = rule.get('category', 'unknown')
            severity = rule.get('severity', rule.get('level', 'medium'))
            
            # 收集字符串模式
            strings = []
            
            # Gitee 格式: patterns 是 [{match: "...", type: "..."}]
            patterns = rule.get('patterns', rule.get('pattern', []))
            if isinstance(patterns, list):
                for p in patterns:
                    if isinstance(p, dict):
                        m = p.get('match', '')
                        if m and isinstance(m, str) and len(m) < 500:
                            strings.append(m)
                    elif isinstance(p, str) and len(p) < 500:
                        strings.append(p)
            
            # Sigma 格式: detection.logical_expression 或 selection
            detection = rule.get('detection', {})
            if isinstance(detection, dict):
                for key in ['selection', 'condition', 'regex']:
                    val = detection.get(key)
                    if val and isinstance(val, str) and len(val) < 500:
                        strings.append(val)
            
            if not strings:
                continue
            
            # 再次过滤，确保有有效字符串
            valid_strings = []
            for s in strings:
                # 跳过包含非法 YARA 语法字符
                if any(c in s for c in ['=', '{', '}', '(', ')', '\n']):
                    continue
                # 跳过以 \ 开头的 (YARA 字符串标识符)
                if '\\' in s or s.startswith('$') or s.startswith('\\'):
                    continue
                # 跳过包含空格后跟关键字的 (如 "rm -rf" 这种)
                if 'nocase' in s or 'ascii' in s or 'wide' in s:
                    continue
                if not s or len(s) > 200:
                    continue
                valid_strings.append(s)
            
            if not valid_strings:
                continue
            
            try:
                # 构建 YARA 规则
                yara_content += f'rule {safe_name} {{\n'
                yara_content += f'    meta:\n'
                yara_content += f'        id = "{rule_id}"\n'
                yara_content += f'        category = "{category}"\n'
                yara_content += f'        severity = "{severity}"\n'
                yara_content += f'        source = "{src}"\n'
                yara_content += f'    strings:\n'
                
                for i, s in enumerate(strings[:20]):  # 最多20个字符串
                    # 跳过包含非法 YARA 字符的模式
                    if any(c in s for c in ['=', '{', '}', '(', ')', '\n']):
                        continue
                    if s.startswith('$') or s.startswith('\\'):
                        continue
                    escaped = s.replace('\\', '\\\\').replace('"', '\\"')
                    yara_content += f'        $str_{i} = "{escaped}"\n'
                
                yara_content += '    condition:\n'
                yara_content += '        any of them\n'
                yara_content += '}\n\n'
                count += 1
            except:
                pass
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(yara_content)
        
        print(f"✅ 导出 {count} 条干净 YARA 规则到: {output_file}")
        return count
    
    def export_json_rules(self, output_file):
        """导出 JSON 格式规则 (供简单模式匹配用)"""
        json_rules = []
        
        for rule in self.rules:
            patterns = rule.get('patterns', rule.get('pattern', []))
            detection = rule.get('detection', {})
            
            strings = []
            
            # 收集所有字符串模式
            if isinstance(patterns, list):
                for p in patterns:
                    if isinstance(p, dict):
                        m = p.get('match', '')
                        if m and isinstance(m, str):
                            strings.append(m)
                    elif isinstance(p, str):
                        strings.append(p)
            
            if isinstance(detection, dict):
                for key in ['selection', 'condition', 'regex']:
                    val = detection.get(key)
                    if val and isinstance(val, str):
                        strings.append(val)
            
            if strings:
                json_rules.append({
                    'id': rule.get('id', 'unknown'),
                    'name': rule.get('name', rule.get('title', 'unknown')),
                    'category': rule.get('category', 'unknown'),
                    'severity': rule.get('severity', rule.get('level', 'medium')),
                    'patterns': strings[:20],  # 最多20个
                    'source': rule.get('_merged_source', 'unknown')
                })
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'version': '2.0',
                'total': len(json_rules),
                'rules': json_rules
            }, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 导出 {len(json_rules)} 条 JSON 规则到: {output_file}")
        return len(json_rules)
    
    def _safe_name(self, name: str) -> str:
        """生成安全的 YARA 规则名"""
        safe = "".join(c if c.isalnum() or c == '_' else '_' for c in str(name))
        if safe and not safe[0].isalpha():
            safe = 'r_' + safe
        return safe[:64]
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        sources = {}
        categories = {}
        
        for rule in self.rules:
            src = rule.get('_merged_source', 'unknown')
            cat = rule.get('category', 'unknown')
            sources[src] = sources.get(src, 0) + 1
            categories[cat] = categories.get(cat, 0) + 1
        
        return {
            'total': len(self.rules),
            'sources': sources,
            'categories': categories
        }

def main():
    print("=" * 60)
    print("🛡️ 统一规则加载器 v2 - Scanner Master")
    print("=" * 60)
    
    loader = CleanRuleLoader()
    stats = loader.get_stats()
    
    print(f"\n📊 规则统计: {stats['total']} 条")
    print("\n按来源:")
    for src, count in sorted(stats['sources'].items(), key=lambda x: -x[1]):
        print(f"  {src}: {count}")
    
    # 导出干净 YARA 规则
    yara_file = Path(__file__).parent / "unified" / "scanner_rules.yar"
    yara_count = loader.export_clean_yara(yara_file)
    
    # 导出 JSON 规则
    json_file = Path(__file__).parent / "unified" / "scanner_rules.json"
    json_count = loader.export_json_rules(json_file)
    
    # 验证 YARA 编译
    print("\n🔍 验证 YARA 规则...")
    try:
        import yara
        rules = yara.compile(str(yara_file))
        print(f"✅ YARA 规则编译成功: {yara_count} 条")
    except Exception as e:
        print(f"⚠️ YARA 编译警告: {e}")
    
    print("\n✅ 完成!")

if __name__ == '__main__':
    main()
