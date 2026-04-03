#!/usr/bin/env python3
"""
样本生成器 CLI - Sample Generator v2.0

使用示例:
    python3 -m generators.cli --language python --count 50
    python3 -m generators.cli -l python -c 50 -o output/samples
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime
from typing import List

from .base_generator import BaseGenerator, MaliciousSample


def generate_samples(
    language: str,
    count: int,
    output_dir: str,
    attack_types: List[str] = None,
    obfuscation_level: int = 1
) -> List[MaliciousSample]:
    """
    生成样本
    
    Args:
        language: 目标语言
        count: 生成数量
        output_dir: 输出目录
        attack_types: 攻击类型列表 (默认轮询所有类型)
        obfuscation_level: 混淆等级 (0-5)
    
    Returns:
        生成的样本列表
    """
    print(f"🔨 开始生成 {count} 个 {language} 样本...")
    print(f"📂 输出目录：{output_dir}")
    print(f"🎭 混淆等级：{obfuscation_level}")
    print()
    
    # 创建输出目录
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 初始化生成器
    generator = get_generator(language)
    
    # 攻击类型
    if attack_types is None:
        attack_types = generator.ATTACK_TYPES
    
    # 生成样本
    samples = []
    start_time = datetime.now()
    
    for i in range(count):
        # 轮询攻击类型
        attack_type = attack_types[i % len(attack_types)]
        
        # 生成样本
        sample = generator.generate(
            attack_type=attack_type,
            variation=i,
            obfuscation_level=obfuscation_level
        )
        
        # 保存样本
        ext_map = {
            'python': 'py',
            'powershell': 'ps1',
            'javascript': 'js',
            'bash': 'sh',
        }
        ext = ext_map.get(language, 'txt')
        filename = f"{language}_{attack_type}_{i:03d}.{ext}"
        filepath = output_path / filename
        
        sample.save(filepath)
        samples.append(sample)
        
        # 进度显示
        if (i + 1) % 10 == 0 or (i + 1) == count:
            elapsed = (datetime.now() - start_time).total_seconds()
            print(f"  ✓ 已生成 {i+1}/{count} 个样本 ({elapsed:.1f}s)")
    
    # 汇总
    elapsed = (datetime.now() - start_time).total_seconds()
    print()
    print(f"✅ 生成完成!")
    print(f"   样本数：{len(samples)}")
    print(f"   耗时：{elapsed:.1f}s")
    print(f"   速度：{len(samples)/max(elapsed, 0.1):.1f} 样本/秒")
    print(f"   位置：{output_path.absolute()}")
    
    return samples


def main():
    """CLI 入口"""
    parser = argparse.ArgumentParser(
        description='恶意样本生成器 v2.0',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  %(prog)s --language python --count 50
  %(prog)s -l powershell -c 30 -o output/samples
  %(prog)s --language javascript --attack-types data_exfil,code_execution
        '''
    )
    
    parser.add_argument(
        '--language', '-l',
        type=str,
        default='python',
        choices=['python', 'powershell', 'javascript', 'bash'],
        help='目标语言 (默认：python)'
    )
    
    parser.add_argument(
        '--count', '-c',
        type=int,
        default=50,
        help='生成数量 (默认：50)'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='output/samples',
        help='输出目录 (默认：output/samples)'
    )
    
    parser.add_argument(
        '--attack-types', '-t',
        type=str,
        default=None,
        help='攻击类型，逗号分隔 (默认：所有类型)'
    )
    
    parser.add_argument(
        '--obfuscation',
        type=int,
        default=1,
        choices=[0, 1, 2, 3, 4, 5],
        help='混淆等级 0-5 (默认：1)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='详细输出'
    )
    
    args = parser.parse_args()
    
    # 解析攻击类型
    attack_types = None
    if args.attack_types:
        attack_types = [t.strip() for t in args.attack_types.split(',')]
    
    # 生成样本
    try:
        samples = generate_samples(
            language=args.language,
            count=args.count,
            output_dir=args.output,
            attack_types=attack_types,
            obfuscation_level=args.obfuscation
        )
        
        # 返回码
        sys.exit(0 if len(samples) > 0 else 1)
        
    except KeyboardInterrupt:
        print("\n⚠️  用户中断")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ 错误：{e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
if __name__ == '__main__':
    main()
     attack_types = [t.strip() for t in args.attack_types.split(',')]
    
    # 生成样本
    try:
        samples = generate_samples(
            language=args.language,
            count=args.count,
            output_dir=args.output,
            attack_types=attack_types,
            obfuscation_level=args.obfuscation
        )
        
        # 返回码
        sys.exit(0 if len(samples) > 0 else 1)
        
    except KeyboardInterrupt:
        print("\n⚠️  用户中断")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ 错误：{e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
