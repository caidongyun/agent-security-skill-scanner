#!/usr/bin/env python3
"""
样本生成器 CLI - 批量生成多语言测试样本

使用方法:
    python3 scripts/sample_generator.py --languages python,javascript,go --attack-types all --count 10
"""

import asyncio
import argparse
import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.sample_generator_agent import SampleGeneratorAgent
from agents.base_agent import Task


async def main():
    parser = argparse.ArgumentParser(description='多语言样本生成器')
    
    parser.add_argument('--languages', '-l', type=str, default='all',
                       help='语言列表 (逗号分隔): python,javascript,go,rust,shell 或 all')
    parser.add_argument('--attack-types', '-a', type=str, default='all',
                       help='攻击类型列表 (逗号分隔) 或 all')
    parser.add_argument('--count', '-c', type=int, default=5,
                       help='每种组合生成的样本数量')
    parser.add_argument('--output', '-o', type=str, default=None,
                       help='输出目录')
    parser.add_argument('--coverage', action='store_true',
                       help='生成规则覆盖样本')
    parser.add_argument('--stats', action='store_true',
                       help='显示生成统计')
    
    args = parser.parse_args()
    
    # 创建生成器
    generator = SampleGeneratorAgent()
    
    if args.stats:
        # 显示统计
        result = await generator.execute(Task(type="stats"))
        print("\n📊 样本生成统计")
        print("=" * 50)
        print(f"总生成数：{result.data['total_generated']}")
        print(f"按语言:")
        for lang, count in result.data['by_language'].items():
            print(f"  {lang}: {count}")
        print(f"按攻击类型:")
        for attack, count in result.data['by_attack_type'].items():
            print(f"  {attack}: {count}")
        print(f"最后生成：{result.data['last_generated']}")
        return
    
    # 解析语言列表
    if args.languages == 'all':
        languages = generator.languages
    else:
        languages = [l.strip() for l in args.languages.split(',')]
    
    # 解析攻击类型列表
    if args.attack_types == 'all':
        attack_types = generator.attack_types
    else:
        attack_types = [a.strip() for a in args.attack_types.split(',')]
    
    print(f"\n🚀 开始生成样本")
    print("=" * 50)
    print(f"语言：{languages}")
    print(f"攻击类型：{attack_types}")
    print(f"每种组合数量：{args.count}")
    
    if args.coverage:
        # 生成规则覆盖样本
        print("\n📋 生成规则覆盖样本...")
        # TODO: 从规则文件加载规则
        result = await generator.execute(Task(
            type="generate_batch",
            parameters={
                "languages": languages,
                "attack_types": attack_types,
                "count": args.count,
                "output_dir": args.output
            }
        ))
    else:
        # 批量生成
        result = await generator.execute(Task(
            type="generate_batch",
            parameters={
                "languages": languages,
                "attack_types": attack_types,
                "count": args.count,
                "output_dir": args.output
            }
        ))
    
    if result.success:
        print(f"\n✅ 生成完成!")
        print(f"总样本数：{result.data['total_generated']}")
        print(f"\n按语言分布:")
        for lang, count in result.data['by_language'].items():
            print(f"  {lang}: {count}")
        print(f"\n按攻击类型分布:")
        for attack, count in result.data['by_attack_type'].items():
            print(f"  {attack}: {count}")
        print(f"\n样本位置：{generator.samples_path}")
    else:
        print(f"\n❌ 生成失败：{result.error}")


if __name__ == '__main__':
    asyncio.run(main())
