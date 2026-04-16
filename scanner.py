#!/usr/bin/env python3
"""
Security Scanner CLI v6.1.0
统一安全扫描器 - 支持三层架构和 LLM 可选集成

检测流程：
1. PatternEngine (Layer 1) - 快速模式匹配
2. RuleEngine (Layer 2) - 深度规则匹配
3. LLMEngine (Layer 3, 可选) - 语义分析 + 上下文理解
"""

import argparse
import json
import sys
import os
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

# 添加 src 路径
sys.path.insert(0, str(Path(__file__).parent / 'src'))
sys.path.insert(0, str(Path(__file__).parent))

# 导入三层架构引擎
from engines import PatternEngine, RuleEngine, LLMEngine
from whitelist_filter import WhitelistFilter
from config_detector import ConfigFileDetector

# 全局组件
whitelist_filter = WhitelistFilter()
config_detector = ConfigFileDetector()


def create_scanner(args):
    """
    创建扫描器（支持三层架构）
    """
    # Layer 1: Pattern Engine (必选)
    layer1 = PatternEngine()
    
    # Layer 2: Rule Engine (必选)
    rules_file = Path(__file__).parent / 'rules' / 'dist' / 'all_rules.json'
    layer2 = RuleEngine(rules_file=rules_file)
    
    # Layer 3: LLM Engine (可选)
    layer3 = None
    if args.llm:
        print(f"🤖 启用 LLM 深度分析 (模型：{args.llm_model})")
        llm_config = {
            'model': args.llm_model,
            'api_key': args.llm_api_key or os.environ.get('LLM_API_KEY', ''),
            'threshold': args.llm_threshold
        }
        layer3 = LLMEngine(llm_config)
    
    return {
        'layer1': layer1,
        'layer2': layer2,
        'layer3': layer3
    }


def scan_file(file_path: Path, scanner, max_depth: int = -1) -> dict:
    """扫描单个文件（支持三层架构 + 白名单过滤）"""
    try:
        # 检查目录深度
        if max_depth > 0:
            try:
                depth = len(file_path.relative_to(Path(scanner['base_path'])).parts)
                if depth > max_depth:
                    return {'file': str(file_path), 'skipped': 'max_depth'}
            except (ValueError, KeyError):
                pass
        
        # 读取文件内容
        content = file_path.read_text(encoding='utf-8', errors='ignore')
        
        # 配置文件识别 (v6.1.0 新增)
        file_type, config_risk = config_detector.classify_file(str(file_path), content)
        if file_type == 'config':
            if config_risk == 'malicious':
                return {
                    'file': str(file_path),
                    'detected': True,
                    'score': 80,
                    'findings_count': 1,
                    'risk_level': 'HIGH',
                    'matched_rules': ['CONFIG-MALICIOUS'],
                    'whitelist_applied': False,
                    'is_config_file': True
                }
            else:
                return {
                    'file': str(file_path),
                    'detected': False,
                    'score': 0,
                    'findings_count': 0,
                    'risk_level': 'SAFE',
                    'matched_rules': [],
                    'whitelist_applied': False,
                    'is_config_file': True
                }
        
        # 三层架构扫描
        # Layer 1: Pattern Engine
        layer1_result = scanner['layer1'].scan(content, str(file_path))
        
        # Layer 2: Rule Engine
        layer2_result = scanner['layer2'].scan(content, layer1_result)
        
        # Layer 3: LLM Engine (可选)
        layer3_result = None
        if scanner['layer3'] and layer2_result.get('confidence', 1.0) < 0.8:
            layer3_result = scanner['layer3'].scan(content, layer1_result, layer2_result)
        
        # 合并结果
        result = {
            'layer1': layer1_result,
            'layer2': layer2_result,
            'layer3': layer3_result,
            'hit_count': layer2_result.get('hit_count', 0),
            'matches': layer2_result.get('matches', []),
            'score': layer2_result.get('score', 0),
            'risk_level': layer2_result.get('risk_level', 'SAFE')
        }
        
        # 白名单过滤
        if result.get('matches'):
            filtered = whitelist_filter.filter_results(
                result['matches'],
                str(file_path),
                content
            )
            result['matches'] = filtered
            result['hit_count'] = len(filtered)
            result['whitelist_applied'] = True
        
        # 转换为统一格式
        detected = result.get('hit_count', 0) > 0
        
        return {
            'file': str(file_path),
            'detected': detected,
            'score': result.get('score', 0),
            'findings_count': result.get('hit_count', 0),
            'risk_level': result.get('risk_level', 'SAFE'),
            'matched_rules': list(set([m[0] if isinstance(m, tuple) else m.get('rule_id', m.get('pattern', '')) for m in result.get('matches', [])[:5]])),
            'whitelist_applied': result.get('whitelist_applied', False),
            'is_config_file': False,
            'layer1_result': layer1_result,
            'layer2_result': layer2_result,
            'layer3_llm': layer3_result
        }
    except Exception as e:
        return {
            'file': str(file_path),
            'error': str(e),
            'detected': False
        }


def scan_directory(target_path: Path, scanner, args) -> list:
    """扫描目录"""
    print(f"\n📂 扫描目标：{target_path}")
    
    # 收集文件
    files_to_scan = []
    for ext in args.extensions.split(','):
        files_to_scan.extend(list(target_path.rglob(f'*{ext.strip()}')))
    
    # 去重
    files_to_scan = list(set(files_to_scan))
    
    # 应用文件数限制
    if args.max_files > 0 and len(files_to_scan) > args.max_files:
        print(f"⚠️  文件数超过 {args.max_files}，只扫描前 {args.max_files} 个")
        files_to_scan = files_to_scan[:args.max_files]
    
    print(f"✅ 找到 {len(files_to_scan)} 个文件")
    
    # 并发扫描
    results = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = [executor.submit(scan_file, f, scanner, args.max_depth) for f in files_to_scan]
        for future in tqdm(as_completed(futures), total=len(futures), desc="扫描进度"):
            results.append(future.result())
    
    return results


def generate_report(results, args):
    """生成扫描报告"""
    # 统计
    total = len(results)
    detected = sum(1 for r in results if r.get('detected'))
    safe = total - detected
    
    # 风险分布
    risk_dist = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0, 'SAFE': 0}
    for r in results:
        risk_level = r.get('risk_level', 'SAFE')
        if risk_level in risk_dist:
            risk_dist[risk_level] += 1
    
    # LLM 统计
    llm_stats = None
    if args.llm:
        llm_count = sum(1 for r in results if r.get('layer3_llm'))
        llm_stats = {
            'analyzed': llm_count,
            'model': args.llm_model
        }
    
    # 生成报告
    report = {
        'summary': {
            'total_files': total,
            'detected': detected,
            'safe': safe,
            'detection_rate': detected / total * 100 if total > 0 else 0,
            'scan_time': datetime.now().isoformat()
        },
        'config': {
            'version': '6.1.0',
            'rules_count': 609,
            'extensions': args.extensions,
            'max_files': args.max_files,
            'llm_enabled': args.llm,
            'llm_model': args.llm_model if args.llm else None
        },
        'risk_distribution': risk_dist,
        'llm_stats': llm_stats,
        'results': results
    }
    
    return report


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Security Scanner CLI v6.1.0 - 支持三层架构和 LLM 可选集成')
    
    # 基本参数
    parser.add_argument('target', type=str, help='扫描目标 (文件或目录)')
    parser.add_argument('--extensions', type=str, default='.py,.js,.sh,.ps1,.yaml,.json',
                        help='文件扩展名 (默认：.py,.js,.sh,.ps1,.yaml,.json)')
    parser.add_argument('--max-files', type=int, default=1000,
                        help='最大文件数 (默认：1000)')
    parser.add_argument('--max-depth', type=int, default=10,
                        help='最大目录深度 (默认：10)')
    parser.add_argument('--workers', type=int, default=4,
                        help='并发 workers (默认：4)')
    
    # LLM 可选参数
    llm_group = parser.add_argument_group('LLM 选项 (可选)')
    llm_group.add_argument('--llm', action='store_true',
                          help='启用 LLM 深度分析 (仅对可疑样本)')
    llm_group.add_argument('--llm-model', type=str, default='minimax',
                          choices=['minimax', 'qwen', 'openai'],
                          help='LLM 模型选择 (默认：minimax)')
    llm_group.add_argument('--llm-threshold', type=float, default=0.5,
                          help='LLM 分析阈值 (confidence < 阈值时启用，默认：0.5)')
    llm_group.add_argument('--llm-api-key', type=str, default='',
                          help='LLM API Key (默认：从 LLM_API_KEY 环境变量读取)')
    
    # 输出参数
    parser.add_argument('--output', type=str, default='text',
                        choices=['text', 'json'],
                        help='输出格式 (默认：text)')
    parser.add_argument('--output-file', type=str, default='scan_report.json',
                        help='输出文件路径 (默认：scan_report.json)')
    
    args = parser.parse_args()
    
    # 打印版本信息
    print("=" * 60)
    print("🛡️  Security Scanner CLI v6.1.0")
    print("=" * 60)
    print(f"⏰ 开始时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 创建扫描器 (三层架构)
    scanner = create_scanner(args)
    scanner['base_path'] = args.target
    
    # 扫描
    target_path = Path(args.target)
    results = scan_directory(target_path, scanner, args)
    
    # 生成报告
    report = generate_report(results, args)
    
    # 输出
    if args.output == 'json':
        with open(args.output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"\n📂 报告已保存：{args.output_file}")
    else:
        print("\n" + "=" * 60)
        print("📊 扫描总结")
        print("=" * 60)
        print(f"⏱️  总耗时：N/A")
        print(f"📁 文件数：{report['summary']['total_files']}")
        print(f"✅ 检出：{report['summary']['detected']}")
        print(f"❌ 漏检：{report['summary']['safe']}")
        print(f"📈 检测率：{report['summary']['detection_rate']:.2f}%")
        print(f"\n🚨 风险分布:")
        for level, count in report['risk_distribution'].items():
            if count > 0:
                print(f"   {level}: {count} 个")
        if report['llm_stats']:
            print(f"\n🤖 LLM 分析:")
            print(f"   分析样本：{report['llm_stats']['analyzed']} 个")
            print(f"   模型：{report['llm_stats']['model']}")
        print("=" * 60)
        print("\n✅ 扫描完成！")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
