#!/usr/bin/env python3
"""
📚 Security Sample Index Manager - 样本索引管理器
==============================================
功能:
1. 扫描所有样本目录
2. 生成详细索引 (JSON + YAML)
3. 支持快速查询
4. 为训练做准备
"""

import os
import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import yaml

@dataclass
class SampleInfo:
    """单个样本信息"""
    id: str
    file_path: str
    file_name: str
    language: str
    file_size: int
    md5: str
    sha256: str
    attack_type: Optional[str]
    mitre_technique: Optional[str]
    is_malicious: bool
    source_dir: str
    created_at: str
    metadata: Dict

class SampleIndexManager:
    """样本索引管理器"""
    
    def __init__(self, output_dir: str = 'samples-index'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.samples: List[SampleInfo] = []
        
    def detect_language(self, file_path: str) -> str:
        """检测文件语言"""
        path = Path(file_path)
        ext = path.suffix.lower()
        name = path.name.lower()
        
        # 标准扩展名
        lang_map = {
            '.py': 'python',
            '.python': 'python',
            '.js': 'javascript',
            '.javascript': 'javascript',
            '.sh': 'bash',
            '.bash': 'bash',
            '.shell': 'bash',
            '.ps1': 'powershell',
            '.powershell': 'powershell',
            '.bat': 'batch',
            '.cmd': 'batch',
            '.go': 'go',
            '.golang': 'go',
            '.rb': 'ruby',
            '.pl': 'perl',
            '.vbs': 'vbscript',
            '.lua': 'lua',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.json': 'json',
            '.md': 'markdown',
            '.txt': 'text'
        }
        
        # 检查 payload.* 格式
        if name.startswith('payload.'):
            payload_ext = name[8:]  # 去掉 'payload.'
            return lang_map.get(f'.{payload_ext}', 'unknown')
        
        return lang_map.get(ext, 'unknown')
    
    def calculate_hash(self, file_path: str) -> tuple:
        """计算文件哈希"""
        md5_hash = hashlib.md5()
        sha256_hash = hashlib.sha256()
        
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                md5_hash.update(content)
                sha256_hash.update(content)
            return md5_hash.hexdigest(), sha256_hash.hexdigest()
        except:
            return '', ''
    
    def extract_attack_type(self, file_path: str) -> Optional[str]:
        """从路径提取攻击类型"""
        path = Path(file_path)
        
        # 检查目录名
        attack_types = [
            'data_exfiltration', 'supply_chain_attack', 'prompt_injection',
            'resource_exhaustion', 'memory_pollution', 'tool_poisoning',
            'remote_loading', 'credential_theft', 'lateral_movement',
            'model_poisoning', 'normal_script', 'benign'
        ]
        
        for part in path.parts:
            if part in attack_types:
                return part
        
        return None
    
    def scan_directory(self, base_dir: str, verbose: bool = True) -> int:
        """扫描目录并建立索引"""
        base_path = Path(base_dir)
        if not base_path.exists():
            print(f"❌ 目录不存在：{base_dir}")
            return 0
        
        if verbose:
            print(f"🔍 扫描目录：{base_dir}")
        
        count = 0
        extensions = {
            '.py', '.python', '.js', '.javascript', '.sh', '.bash', '.shell',
            '.ps1', '.powershell', '.bat', '.cmd', '.go', '.golang',
            '.rb', '.pl', '.vbs', '.lua'
        }
        
        # 查找所有样本文件
        for ext in extensions:
            for file_path in base_path.rglob(f"*{ext}"):
                try:
                    # 跳过元数据文件
                    if file_path.name in ['metadata.json', 'samples.yaml', 'samples.json']:
                        continue
                    
                    # 提取信息
                    lang = self.detect_language(str(file_path))
                    if lang == 'unknown':
                        continue
                    
                    md5, sha256 = self.calculate_hash(str(file_path))
                    attack_type = self.extract_attack_type(str(file_path))
                    
                    # 创建样本信息
                    sample = SampleInfo(
                        id=sha256[:16] if sha256 else md5[:16],
                        file_path=str(file_path.absolute()),
                        file_name=file_path.name,
                        language=lang,
                        file_size=file_path.stat().st_size,
                        md5=md5,
                        sha256=sha256,
                        attack_type=attack_type,
                        mitre_technique=None,
                        is_malicious=attack_type and attack_type != 'normal_script' and attack_type != 'benign',
                        source_dir=str(base_path),
                        created_at=datetime.now().isoformat(),
                        metadata={
                            'relative_path': str(file_path.relative_to(base_path)),
                            'parent_dir': file_path.parent.name
                        }
                    )
                    
                    self.samples.append(sample)
                    count += 1
                    
                    if verbose and count % 1000 == 0:
                        print(f"  已索引 {count} 个样本...")
                        
                except Exception as e:
                    if verbose:
                        print(f"⚠️  处理失败 {file_path}: {e}")
        
        return count
    
    def generate_index(self, output_file: str = None) -> str:
        """生成索引文件"""
        if not output_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = self.output_dir / f"sample_index_{timestamp}.json"
        else:
            output_file = Path(output_file)
        
        # 统计数据
        stats = {
            'total_samples': len(self.samples),
            'by_language': {},
            'by_attack_type': {},
            'by_source_dir': {},
            'malicious_count': 0,
            'benign_count': 0
        }
        
        for sample in self.samples:
            # 按语言统计
            if sample.language not in stats['by_language']:
                stats['by_language'][sample.language] = 0
            stats['by_language'][sample.language] += 1
            
            # 按攻击类型统计
            attack_type = sample.attack_type or 'unknown'
            if attack_type not in stats['by_attack_type']:
                stats['by_attack_type'][attack_type] = 0
            stats['by_attack_type'][attack_type] += 1
            
            # 按来源统计
            if sample.source_dir not in stats['by_source_dir']:
                stats['by_source_dir'][sample.source_dir] = 0
            stats['by_source_dir'][sample.source_dir] += 1
            
            # 恶意/良性统计
            if sample.is_malicious:
                stats['malicious_count'] += 1
            else:
                stats['benign_count'] += 1
        
        # 生成完整索引
        index_data = {
            'version': '1.0',
            'created_at': datetime.now().isoformat(),
            'statistics': stats,
            'samples': [asdict(s) for s in self.samples]
        }
        
        # 保存 JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, indent=2, ensure_ascii=False)
        
        # 保存 YAML (简化版)
        yaml_file = output_file.with_suffix('.yaml')
        yaml_data = {
            'version': '1.0',
            'created_at': datetime.now().isoformat(),
            'statistics': stats,
            'sample_count': len(self.samples)
        }
        with open(yaml_file, 'w', encoding='utf-8') as f:
            yaml.dump(yaml_data, f, allow_unicode=True, default_flow_style=False)
        
        return str(output_file)
    
    def print_summary(self):
        """打印摘要"""
        print("\n" + "=" * 70)
        print("📚 样本索引摘要")
        print("=" * 70)
        print(f"总样本数：{len(self.samples)}")
        
        # 按语言统计
        by_lang = {}
        for s in self.samples:
            by_lang[s.language] = by_lang.get(s.language, 0) + 1
        
        print("\n按语言:")
        for lang, count in sorted(by_lang.items(), key=lambda x: x[1], reverse=True):
            print(f"  {lang}: {count}")
        
        # 按攻击类型统计
        by_attack = {}
        for s in self.samples:
            attack = s.attack_type or 'unknown'
            by_attack[attack] = by_attack.get(attack, 0) + 1
        
        print("\n按攻击类型 (Top 10):")
        for attack, count in sorted(by_attack.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {attack}: {count}")
        
        # 恶意/良性
        malicious = sum(1 for s in self.samples if s.is_malicious)
        benign = len(self.samples) - malicious
        print(f"\n恶意样本：{malicious} ({malicious/len(self.samples)*100:.1f}%)")
        print(f"良性样本：{benign} ({benign/len(self.samples)*100:.1f}%)")
        
        print("=" * 70)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='📚 样本索引管理器')
    parser.add_argument('--dirs', nargs='+', default=[
        '/home/cdy/Desktop/security-benchmark/samples/from-templates',
        '/home/cdy/Desktop/security-benchmark/github-samples',
        '/home/cdy/.openclaw/workspace/skills/agent-security-benchmark/samples'
    ], help='要扫描的目录列表')
    parser.add_argument('--output', default='samples-index/sample_index.json', help='输出文件')
    parser.add_argument('--verbose', action='store_true', help='详细输出')
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("📚 Security Sample Index Manager - 样本索引系统")
    print("=" * 70)
    print()
    
    manager = SampleIndexManager()
    
    # 扫描所有目录
    total = 0
    for dir_path in args.dirs:
        if Path(dir_path).exists():
            count = manager.scan_directory(dir_path, args.verbose)
            total += count
            if args.verbose:
                print(f"  ✅ {dir_path}: {count} 个样本\n")
        else:
            if args.verbose:
                print(f"  ⚠️  跳过 (不存在): {dir_path}\n")
    
    # 生成索引
    if total > 0:
        output_file = manager.generate_index(args.output)
        manager.print_summary()
        print(f"\n💾 索引已保存：{output_file}")
        print(f"💾 YAML: {Path(output_file).with_suffix('.yaml')}")
    else:
        print("❌ 未找到任何样本")

if __name__ == '__main__':
    main()
