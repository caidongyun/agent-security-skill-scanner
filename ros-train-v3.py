#!/usr/bin/env python3
"""
🔄 ROS 训练提升系统 v3.0 - 优化版
=================================
核心改进:
1. 自动样本检查
2. 自动预处理 (提取 payload)
3. 一键扫描
4. 错误处理和重试

使用:
  python3 ros-train-v3.py --attack-type evasion
  python3 ros-train-v3.py --attack-type prompt_injection
  python3 ros-train-v3.py --all  # 处理所有待优化类型
"""

import os
import sys
import json
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

# 配置
BASE_DIR = Path('/home/cdy/Desktop/security-benchmark/samples/from-templates')
OUTPUT_DIR = Path('/home/cdy/.openclaw/workspace/agent-security-skill-scanner-master/training/preprocessed')
SCANNER = Path('/home/cdy/.openclaw/workspace/agent-security-skill-scanner-master/ultimate_scanner_v2.py')
RULES_DIR = Path('/home/cdy/.openclaw/workspace/agent-security-skill-scanner-master/rules/scanner_v3/yara')

# 待优化攻击类型
ATTACK_TYPES = {
    'evasion': {'target': 95.0, 'current': 79.2, 'status': 'done'},
    'prompt_injection': {'target': 95.0, 'current': 79.9, 'status': 'pending'},
    'memory_pollution': {'target': 95.0, 'current': 79.9, 'status': 'pending'},
    'false_prone': {'target': 95.0, 'current': 80.7, 'status': 'pending'},
}

class SamplePreprocessor:
    """样本预处理器"""
    
    def __init__(self, attack_type: str):
        self.attack_type = attack_type
        self.source_dir = BASE_DIR / attack_type
        self.output_dir = OUTPUT_DIR / f"{attack_type}_flat"
        self.sample_count = 0
        
    def check_sample_structure(self) -> str:
        """检查样本结构"""
        print(f"🔍 检查 {self.attack_type} 样本结构...")
        
        if not self.source_dir.exists():
            return "error:directory_not_found"
        
        # 获取第一个样本
        first_samples = list(self.source_dir.glob('MAL-*'))[:5]
        if not first_samples:
            return "error:no_samples_found"
        
        # 检查是目录还是文件
        first = first_samples[0]
        if first.is_dir():
            # 检查目录下是否有 payload 文件
            payload_files = list(first.glob('payload.*'))
            if payload_files:
                print(f"  ✅ 目录结构：{len(first_samples)} 个样本目录")
                print(f"  📁 每个目录包含 payload 文件")
                return "directory_structure"
            else:
                print(f"  ⚠️ 目录下没有找到 payload 文件")
                return "error:no_payload_files"
        else:
            print(f"  ✅ 平坦结构：直接扫描文件")
            return "flat_files"
    
    def extract_payloads(self) -> int:
        """提取 payload 文件"""
        print(f"\n📦 提取 {self.attack_type} payload 文件...")
        
        # 创建输出目录
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 清空旧文件
        for f in self.output_dir.glob('*'):
            f.unlink()
        
        count = 0
        for sample_dir in self.source_dir.glob('MAL-*'):
            if not sample_dir.is_dir():
                continue
            
            sample_id = sample_dir.name
            
            # 查找所有 payload 文件
            for payload_file in sample_dir.glob('payload.*'):
                if payload_file.is_file():
                    ext = payload_file.suffix[1:]  # 去掉 .
                    output_file = self.output_dir / f"{sample_id}.{ext}"
                    shutil.copy2(payload_file, output_file)
                    count += 1
        
        self.sample_count = count
        print(f"  ✅ 提取完成：{count} 个文件")
        return count
    
    def verify_extraction(self) -> bool:
        """验证提取结果"""
        if not self.output_dir.exists():
            print(f"  ❌ 输出目录不存在")
            return False
        
        file_count = len(list(self.output_dir.iterdir()))
        if file_count == 0:
            print(f"  ❌ 输出目录为空")
            return False
        
        print(f"  ✅ 验证通过：{file_count} 个文件")
        return True


class ScannerWrapper:
    """扫描器封装"""
    
    def __init__(self, samples_dir: Path, attack_type: str):
        self.samples_dir = samples_dir
        self.attack_type = attack_type
        
    def scan(self, workers: int = 4, no_ast: bool = True) -> Dict:
        """运行扫描"""
        print(f"\n🔍 扫描 {self.attack_type}...")
        
        cmd = [
            sys.executable, str(SCANNER),
            '--samples', str(self.samples_dir),
            '--rules', str(RULES_DIR),
            '--workers', str(workers),
        ]
        
        if no_ast:
            cmd.append('--no-ast')
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            # 解析输出
            output = result.stdout + result.stderr
            metrics = self._parse_output(output)
            
            return {
                'status': 'success' if result.returncode == 0 else 'failed',
                'returncode': result.returncode,
                'metrics': metrics,
                'output': output[-2000:]  # 最后 2000 字符
            }
            
        except subprocess.TimeoutExpired:
            return {
                'status': 'timeout',
                'returncode': -1,
                'metrics': {},
                'output': '扫描超时 (5 分钟)'
            }
        except Exception as e:
            return {
                'status': 'error',
                'returncode': -1,
                'metrics': {},
                'output': str(e)
            }
    
    def _parse_output(self, output: str) -> Dict:
        """解析扫描输出"""
        metrics = {}
        
        for line in output.split('\n'):
            if '发现' in line and '样本文件' in line:
                try:
                    metrics['total'] = int(line.split('发现')[1].split('个')[0].strip())
                except:
                    pass
            elif '恶意样本' in line:
                try:
                    parts = line.split('：')[1].split('(')
                    metrics['malicious'] = int(parts[0].strip())
                    metrics['detection_rate'] = float(parts[1].replace(')', '').replace('%', '').strip())
                except:
                    pass
        
        return metrics


class TrainingOrchestrator:
    """训练编排器"""
    
    def __init__(self):
        self.results = []
        
    def run_single(self, attack_type: str) -> Dict:
        """运行单个攻击类型的训练"""
        print(f"\n{'='*70}")
        print(f"🎯 攻击类型：{attack_type}")
        print(f"{'='*70}")
        
        # 步骤 1: 检查样本结构
        preprocessor = SamplePreprocessor(attack_type)
        structure = preprocessor.check_sample_structure()
        
        if structure == "error:directory_not_found":
            print(f"  ❌ 目录不存在：{preprocessor.source_dir}")
            return {'status': 'error', 'reason': 'directory_not_found'}
        
        if structure == "error:no_samples_found":
            print(f"  ❌ 没有找到样本")
            return {'status': 'error', 'reason': 'no_samples'}
        
        # 步骤 2: 预处理 (如果是目录结构)
        if structure == "directory_structure":
            preprocessor.extract_payloads()
            if not preprocessor.verify_extraction():
                return {'status': 'error', 'reason': 'extraction_failed'}
            samples_dir = preprocessor.output_dir
        else:
            samples_dir = preprocessor.source_dir
        
        # 步骤 3: 扫描
        scanner = ScannerWrapper(samples_dir, attack_type)
        scan_result = scanner.scan()
        
        if scan_result['status'] != 'success':
            print(f"  ❌ 扫描失败：{scan_result['output']}")
            return {'status': 'error', 'reason': 'scan_failed'}
        
        # 步骤 4: 输出结果
        metrics = scan_result['metrics']
        print(f"\n📊 扫描结果:")
        print(f"  总样本：{metrics.get('total', 'N/A')}")
        print(f"  恶意检出：{metrics.get('malicious', 'N/A')}")
        print(f"  检测率：{metrics.get('detection_rate', 'N/A')}%")
        
        # 步骤 5: 判断是否达标
        target = ATTACK_TYPES.get(attack_type, {}).get('target', 95.0)
        rate = metrics.get('detection_rate', 0)
        
        if rate >= target:
            print(f"  ✅ 达标 (≥{target}%)")
            status = 'passed'
        else:
            print(f"  ⚠️  未达标 (目标≥{target}%, 实际{rate}%)")
            status = 'needs_optimization'
        
        return {
            'status': status,
            'attack_type': attack_type,
            'metrics': metrics,
            'target': target,
            'preprocessed': structure == "directory_structure",
            'sample_count': preprocessor.sample_count
        }
    
    def run_all(self) -> List[Dict]:
        """运行所有待优化类型"""
        results = []
        
        for attack_type, info in ATTACK_TYPES.items():
            if info.get('status') == 'done':
                print(f"\n⏭️  跳过 {attack_type} (已完成)")
                continue
            
            result = self.run_single(attack_type)
            results.append(result)
            
            # 保存中间结果
            self._save_results(results)
        
        return results
    
    def _save_results(self, results: List[Dict]):
        """保存结果"""
        output_file = OUTPUT_DIR / f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'results': results,
                'summary': {
                    'total': len(results),
                    'passed': sum(1 for r in results if r.get('status') == 'passed'),
                    'needs_optimization': sum(1 for r in results if r.get('status') == 'needs_optimization')
                }
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 结果已保存：{output_file}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='🔄 ROS 训练提升系统 v3.0')
    parser.add_argument('--attack-type', '-a', help='攻击类型')
    parser.add_argument('--all', action='store_true', help='处理所有待优化类型')
    parser.add_argument('--check-only', action='store_true', help='仅检查样本结构')
    
    args = parser.parse_args()
    
    print("="*70)
    print("🔄 ROS 训练提升系统 v3.0 - 优化版")
    print("="*70)
    
    orchestrator = TrainingOrchestrator()
    
    if args.all:
        results = orchestrator.run_all()
    elif args.attack_type:
        result = orchestrator.run_single(args.attack_type)
        results = [result]
    else:
        print("请使用 --attack-type 或 --all 参数")
        return
    
    # 最终总结
    print(f"\n{'='*70}")
    print("📊 训练总结")
    print(f"{'='*70}")
    
    passed = sum(1 for r in results if r.get('status') == 'passed')
    total = len(results)
    
    print(f"已完成：{total} 个攻击类型")
    print(f"已达标：{passed} 个")
    print(f"需优化：{total - passed} 个")


if __name__ == '__main__':
    main()
