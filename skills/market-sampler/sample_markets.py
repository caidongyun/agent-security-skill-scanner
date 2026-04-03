#!/usr/bin/env python3
"""
Skill 市场采样器 - 从国内外 Agent/Skill 市场抽样
"""
import os, json
from datetime import datetime

OUTPUT_DIR = 'samples/market'

# 市场配置
MARKETS = {
    'domestic': {
        'coze': {'target': 100, 'url': 'https://www.coze.cn/store/bot'},
        'dify': {'target': 100, 'url': 'https://dify.ai/apps'},
        'bailian': {'target': 50, 'url': 'https://bailian.console.aliyun.com'},
    },
    'international': {
        'gpt_store': {'target': 200, 'url': 'https://openai.com/gpts'},
        'langchain': {'target': 100, 'url': 'https://smith.langchain.com/hub'},
        'autogen': {'target': 100, 'url': 'https://microsoft.github.io/autogen/gallery'},
    },
}

def create_sample_structure():
    """创建样本目录结构"""
    for category, markets in MARKETS.items():
        for market in markets:
            os.makedirs(f'{OUTPUT_DIR}/{category}/{market}', exist_ok=True)
    print('✅ 目录结构创建完成')

def generate_mock_samples(market, count=10):
    """生成模拟样本 (实际应调用 API 或爬虫)"""
    samples = []
    
    for i in range(count):
        sample = {
            'id': f'{market}_{i+1:04d}',
            'name': f'{market.title()} Agent {i+1}',
            'description': f'Auto-generated sample for {market}',
            'category': 'assistant',
            'tools': ['search', 'calculator', 'browser'],
            'created_at': datetime.now().isoformat(),
            'source': market,
        }
        samples.append(sample)
    
    return samples

def sample_market(market_name, config):
    """采样单个市场"""
    print(f'📦 采样 {market_name} (目标：{config["target"]} 个)...')
    
    # 生成样本
    samples = generate_mock_samples(market_name, min(config['target'], 10))
    
    # 保存
    output_file = f'{OUTPUT_DIR}/domestic/{market_name}/samples.json' if market_name in ['coze', 'dify', 'bailian'] else f'{OUTPUT_DIR}/international/{market_name}/samples.json'
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'market': market_name,
            'url': config['url'],
            'sampled_at': datetime.now().isoformat(),
            'target': config['target'],
            'actual': len(samples),
            'samples': samples,
        }, f, indent=2, ensure_ascii=False)
    
    print(f'  ✅ 采样 {len(samples)} 个样本')
    return len(samples)

def main():
    print('='*60)
    print('🌐 Skill 市场采样器')
    print('='*60)
    print()
    
    # 创建目录
    create_sample_structure()
    print()
    
    # 采样所有市场
    total = 0
    
    print('国内市场:')
    for market, config in MARKETS['domestic'].items():
        count = sample_market(market, config)
        total += count
    
    print()
    print('国际市场:')
    for market, config in MARKETS['international'].items():
        count = sample_market(market, config)
        total += count
    
    print()
    print('='*60)
    print(f'✅ 市场采样完成!')
    print('='*60)
    print(f'总样本数：{total}')
    print()
    print('市场分布:')
    for category, markets in MARKETS.items():
        for market in markets:
            print(f'  {category}/{market}: {min(markets[market]["target"], 10)} 个')
    print()
    print(f'样本位置：{OUTPUT_DIR}/')
    print('='*60)

if __name__ == '__main__':
    main()
