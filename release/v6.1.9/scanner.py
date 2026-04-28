#!/usr/bin/env python3
"""
Security Scanner CLI v6.1.9 - 统一架构版

三层检测架构:
1. PatternEngine (Layer 1) - Aho-Corasick 快速预筛选
2. HybridRuleEngine (Layer 2) - AC 自动机 + Regex 精匹配
3. LLMEngine (Layer 3, 可选) - 语义分析

检测流程:
1. Layer 1 快速匹配 → 返回候选攻击类型
2. Layer 2 只匹配候选类型的规则子集 → 大幅减少匹配次数
3. Layer 3 可选 LLM 复核 CRITICAL 级别
"""

import argparse
import json
import sys
import os
import time
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

# 添加 src 路径
sys.path.insert(0, str(Path(__file__).parent / 'src'))
sys.path.insert(0, str(Path(__file__).parent))

# 导入三层架构引擎
from engines import PatternEngine, RuleEngine, LLMEngine
from engines.hybrid_scanner import HybridRuleEngine
from whitelist_filter import WhitelistFilter
from config_detector import ConfigFileDetector

# 全局组件
whitelist_filter = WhitelistFilter()
config_detector = ConfigFileDetector()

# ========== v6.1.9 优化:文件优先级配置 ==========
# 优先级数字越小越优先,timeout 为单文件超时预算 (秒)
FILE_PRIORITY_RULES = {
    # P0 - 必须扫描 (技能定义)
    'skill.md': (0, 10),

    # P1 - 核心工具代码
    '_tools.py': (1, 8),
    'tool_': (1, 8),
    'agent': (1, 8),
    'skill.py': (1, 8),
    'main.py': (1, 8),
    'handler': (1, 8),

    # P2 - 高风险关键词
    'inject': (2, 5),
    'hack': (2, 5),
    'bypass': (2, 5),
    'exploit': (2, 5),
    'subprocess': (2, 5),
    'eval': (2, 5),
    'exec': (2, 5),

    # P3 - 网络/凭据
    'request': (3, 5),
    'http': (3, 5),
    'curl': (3, 5),
    'api_key': (3, 5),
    'token': (3, 5),
    'secret': (3, 5),

    # P4 - 普通代码
    '.py': (4, 3),
    '.js': (4, 3),
    '.sh': (4, 3),
    '.bash': (4, 3),

    # P5 - 配置文件
    '.yaml': (5, 2),
    '.yml': (5, 2),
    '.json': (5, 2),

    # P6 - 文档 (最低优先级,严格熔断)
    'readme': (6, 1),
    'license': (6, 1),
    'changelog': (6, 1),
    'contributing': (6, 1),
    '.md': (6, 1),  # 所有 markdown 文件 1s 熔断
}

def get_file_priority(filepath: Path):
    """获取文件优先级 (priority, timeout)"""
    name_lower = filepath.name.lower()
    suffix = filepath.suffix.lower()

    # 检查精确匹配
    for pattern, (priority, timeout) in FILE_PRIORITY_RULES.items():
        if pattern.startswith('.'):
            # 后缀匹配
            if suffix == pattern:
                return priority, timeout
        elif pattern.endswith('.py') or pattern.endswith('.sh'):
            # 后缀模式
            if name_lower.endswith(pattern):
                return priority, timeout
        elif '*' in pattern:
            # 通配符
            if pattern.replace('*', '') in name_lower:
                return priority, timeout
        else:
            # 关键词/前缀匹配
            if pattern in name_lower or name_lower.startswith(pattern):
                return priority, timeout

    # 默认
    if suffix in {'.py', '.js', '.sh'}:
        return 4, 3
    elif suffix in {'.yaml', '.yml', '.json'}:
        return 5, 2
    else:
        return 6, 1


def create_scanner(args):
    """
    创建扫描器(统一三层架构)
    """
    rules_file = Path(__file__).parent / 'rules' / 'dist' / 'all_rules.json'

    # Layer 1: Pattern Engine (必选)
    print("\n🔧 初始化 Layer 1: PatternEngine...")
    layer1 = PatternEngine()

    # Layer 2: Hybrid Rule Engine (必选) - AC 自动机预筛选 + Regex 精匹配
    print("\n🔧 初始化 Layer 2: HybridRuleEngine...")
    layer2 = HybridRuleEngine(rules_file=rules_file)

    # Layer 3: LLM Engine (可选)
    layer3 = None
    if args.llm:
        print(f"\n🤖 启用 Layer 3: LLMEngine (模型:{args.llm_model})")
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


def scan_file_with_timeout(file_path: Path, scanner, max_depth: int = -1, timeout_per_file: float = 3.0) -> dict:
    """扫描单个文件 (带超时控制 - 记录但不跳过)"""
    start_time = time.time()
    timed_out = False

    try:
        # 读取文件
        content = file_path.read_text(encoding='utf-8', errors='ignore')

        # 检查读取是否超时
        if time.time() - start_time > timeout_per_file:
            timed_out = True  # 记录超时,但继续扫描

        # 执行扫描
        result = scan_file(file_path, scanner, max_depth)
        result['priority'], result['timeout_budget'] = get_file_priority(file_path)
        result['scan_time'] = time.time() - start_time
        result['timed_out'] = timed_out
        return result

    except Exception as e:
        elapsed = time.time() - start_time
        return {
            'file': str(file_path),
            'error': str(e),
            'priority': get_file_priority(file_path)[0],
            'timeout_budget': timeout_per_file,
            'scan_time': elapsed,
            'timed_out': elapsed > timeout_per_file,
            'detected': False
        }


def scan_file(file_path: Path, scanner, max_depth: int = -1) -> dict:
    """扫描单个文件(支持三层架构 + 白名单过滤)"""
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
        # Layer 1: Pattern Engine (快速预筛选)
        layer1_result = scanner['layer1'].scan(content, str(file_path))

        # Layer 2: HybridRuleEngine (AC 自动机 + Regex 精匹配)
        # HybridRuleEngine 内部会自动使用 AC 自动机预筛选
        layer2_result = scanner['layer2'].scan(content)

        # Layer 3: LLM Engine (可选) - 只复核 CRITICAL 级别
        layer3_result = None
        if scanner['layer3'] and layer2_result.get('hit_count', 0) > 0:
            if layer2_result.get('risk_level') == 'CRITICAL':
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
    """扫描目录 (v6.1.9 优化:优先级 + 记录超时)"""
    print(f"\n📂 扫描目标:{target_path}")

    # 收集文件
    files_to_scan = []
    for ext in args.extensions.split(','):
        files_to_scan.extend(list(target_path.rglob(f'*{ext.strip()}')))

    # 去重
    files_to_scan = list(set(files_to_scan))

    # v6.1.9 优化:按优先级排序
    files_with_priority = [(f, *get_file_priority(f)) for f in files_to_scan]
    files_with_priority.sort(key=lambda x: x[1])  # 优先级数字小的在前

    print(f"✅ 找到 {len(files_with_priority)} 个文件 (已按优先级排序)")

    # 应用文件数限制
    if args.max_files > 0 and len(files_with_priority) > args.max_files:
        print(f"⚠️  文件数超过 {args.max_files},只扫描前 {args.max_files} 个")
        files_with_priority = files_with_priority[:args.max_files]

    # 并发扫描 (不熔断,全部执行完)
    results = []
    timeout_count = 0

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = []
        for filepath, priority, timeout in files_with_priority:
            future = executor.submit(scan_file_with_timeout, filepath, scanner, args.max_depth, timeout)
            futures.append((future, filepath, priority, timeout))

        for future, filepath, priority, timeout in tqdm(futures, total=len(futures), desc="扫描进度"):
            result = future.result()
            results.append(result)

            # 统计超时
            if result.get('timed_out'):
                timeout_count += 1

    # 超时率警告
    if timeout_count > 0:
        timeout_rate = timeout_count / len(results) * 100
        print(f"\n⚠️  超时文件:{timeout_count}/{len(results)} ({timeout_rate:.1f}%)")
        if timeout_rate > 20:
            print(f"💡 建议:超时率较高,可调整 --max-files 或增加超时阈值")

    return results


def generate_report(results, args):
    """生成扫描报告 (v6.1.9 优化:超时统计)"""
    # 统计
    total = len(results)
    detected = sum(1 for r in results if r.get('detected'))
    safe = total - detected

    # 超时统计
    timeout_files = [r for r in results if r.get('timed_out')]
    timeout_count = len(timeout_files)
    timeout_rate = timeout_count / total * 100 if total > 0 else 0

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

    # 超时建议
    timeout_recommendation = None
    if timeout_rate > 20:
        timeout_recommendation = {
            'issue': f'超时率过高 ({timeout_rate:.1f}%)',
            'suggestion': '建议增加超时阈值或减少扫描文件数',
            'config': {
                'current_timeout': '动态 (1-10s)',
                'recommendation': '可考虑增加 P4/P5/P6 文件超时预算'
            }
        }

    # 生成报告
    report = {
        'summary': {
            'total_files': total,
            'detected': detected,
            'safe': safe,
            'detection_rate': detected / total * 100 if total > 0 else 0,
            'scan_time': datetime.now().isoformat(),
            'timeout_count': timeout_count,
            'timeout_rate': timeout_rate
        },
        'config': {
            'version': '6.1.9-optimized',
            'rules_count': 627,
            'extensions': args.extensions,
            'max_files': args.max_files,
            'llm_enabled': args.llm,
            'llm_model': args.llm_model if args.llm else None,
            'priority_scan': True,
            'timeout_tracking': True
        },
        'risk_distribution': risk_dist,
        'llm_stats': llm_stats,
        'timeout_analysis': {
            'count': timeout_count,
            'rate': timeout_rate,
            'recommendation': timeout_recommendation,
            'files': [{'file': r['file'], 'priority': r.get('priority'), 'timeout_budget': r.get('timeout_budget'), 'scan_time': r.get('scan_time')} for r in timeout_files[:100]]  # 前 100 个超时文件
        },
        'results': results
    }

    return report


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Security Scanner CLI v6.1.9 - 统一三层架构 (AC 自动机 + Pattern + Rule + LLM)')

    # 基本参数
    parser.add_argument('target', type=str, help='扫描目标 (文件或目录)')
    parser.add_argument('--extensions', type=str, default='.py,.js,.sh,.ps1,.yaml,.json',
                        help='文件扩展名 (默认:.py,.js,.sh,.ps1,.yaml,.json)')
    parser.add_argument('--max-files', type=int, default=200000,
                        help='最大文件数 (默认:200000)')
    parser.add_argument('--max-depth', type=int, default=20,
                        help='最大目录深度 (默认:20)')
    parser.add_argument('--workers', type=int, default=8,
                        help='并发 workers (默认:8，稳定模式)')

    # LLM 可选参数
    llm_group = parser.add_argument_group('LLM 选项 (可选)')
    llm_group.add_argument('--llm', action='store_true',
                          help='启用 LLM 深度分析 (仅对 CRITICAL 级别)')
    llm_group.add_argument('--llm-model', type=str, default='qwen',
                          choices=['minimax', 'qwen', 'openai'],
                          help='LLM 模型选择 (默认:qwen)')
    llm_group.add_argument('--llm-threshold', type=float, default=0.5,
                          help='LLM 分析阈值 (默认:0.5)')
    llm_group.add_argument('--llm-api-key', type=str, default='',
                          help='LLM API Key (默认：从 LLM_API_KEY 环境变量读取)')

    # 输出参数
    parser.add_argument('--output', type=str, default='text',
                        choices=['text', 'json'],
                        help='输出格式 (默认:text)')
    parser.add_argument('--output-file', type=str, default='scan_report.json',
                        help='输出文件路径 (默认:scan_report.json)')

    args = parser.parse_args()

    # 打印版本信息
    print("=" * 60)
    print("🛡️  Security Scanner CLI v6.1.9 - 统一架构版")
    print("=" * 60)
    print(f"⏰ 开始时间:{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📊 架构:Layer1(Pattern) → Layer2(Hybrid AC+Regex) → Layer3(LLM 可选)")
    print(f"👷 Workers:{args.workers} | 📁 Max Files:{args.max_files} | 🔍 Max Depth:{args.max_depth}")

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
        print(f"\n📂 报告已保存:{args.output_file}")
    else:
        print("\n" + "=" * 60)
        print("📊 扫描总结")
        print("=" * 60)
        print(f"⏱️  总耗时:N/A")
        print(f"📁 文件数:{report['summary']['total_files']}")
        print(f"✅ 检出:{report['summary']['detected']}")
        print(f"❌ 漏检:{report['summary']['safe']}")
        print(f"📈 检测率:{report['summary']['detection_rate']:.2f}%")
        print(f"\n🚨 风险分布:")
        for level, count in report['risk_distribution'].items():
            if count > 0:
                print(f"   {level}: {count} 个")
        if report['llm_stats']:
            print(f"\n🤖 LLM 分析:")
            print(f"   分析样本:{report['llm_stats']['analyzed']} 个")
            print(f"   模型:{report['llm_stats']['model']}")
        print("=" * 60)
        print("\n✅ 扫描完成!")

    return 0


if __name__ == '__main__':
    sys.exit(main())
