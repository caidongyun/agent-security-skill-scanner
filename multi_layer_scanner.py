#!/usr/bin/env python3
"""
多层扫描器 - 对齐历史系统设计
集成 AST/意图/控制流/语义/行为/ML 分析
"""

import subprocess
import json
from pathlib import Path
from datetime import datetime

class MultiLayerScanner:
    """多层检测架构"""
    
    def __init__(self):
        self.scanner_dir = Path.home() / ".openclaw/workspace/agent-security-skill-scanner-master"
        self.benchmark_dir = Path.home() / "Desktop/security-benchmark"
        
        # 多层检测架构
        self.layers = {
            'layer1_yara': {'enabled': True, 'name': 'YARA 规则'},
            'layer2_intent': {'enabled': True, 'name': '意图识别'},
            'layer3_ast': {'enabled': True, 'name': 'AST 分析'},
            'layer4_cfg': {'enabled': True, 'name': '控制流'},
            'layer5_semantic': {'enabled': True, 'name': '语义分析'},
            'layer6_behavior': {'enabled': True, 'name': '行为分析'},
            'layer7_ml': {'enabled': True, 'name': 'ML 分类'},
            'layer8_llm': {'enabled': False, 'name': 'LLM 分析'},
        }
        
        # 检测器路径 (实际位置)
        self.detectors = {
            'ast': self.scanner_dir / "expert_mode/round16/ast_analyzer.py",
            'intent': None,  # 待创建
            'cfg': None,  # 待创建
            'semantic': None,  # 待创建
            'behavior': Path.home() / ".openclaw/workspace/agent-security-skill-scanner-gitee/dynamic_detector.py",
            'ml': self.scanner_dir / "round24/integration/ml_classifier.py",
        }
    
    def check_detector_status(self):
        """检查各层检测器状态"""
        print("=" * 60)
        print("🔍 多层检测器状态检查")
        print("=" * 60)
        
        for layer_id, layer_info in self.layers.items():
            status = "✅" if layer_info['enabled'] else "❌"
            print(f"{status} {layer_info['name']:12} ({layer_id})")
        
        print("\n检测器文件:")
        for name, path in self.detectors.items():
            exists = "✅" if path.exists() else "❌"
            print(f"  {exists} {name:12} {path.name}")
        
        print("=" * 60)
    
    def run_layer1_yara(self, sample_path):
        """Layer 1: YARA 规则扫描"""
        print(f"\n🔍 Layer 1: YARA 规则扫描")
        result = subprocess.run(
            [str(self.scanner_dir / "scan.sh"), str(sample_path)],
            capture_output=True, text=True, timeout=30
        )
        return {
            'layer': 'yara',
            'detected': "恶意样本" in result.stdout,
            'output': result.stdout[:500]
        }
    
    def run_layer2_intent(self, sample_path):
        """Layer 2: 意图识别"""
        print(f"\n🔍 Layer 2: 意图识别")
        if not self.detectors['intent'].exists():
            print("  ⚠️  检测器不存在")
            return {'layer': 'intent', 'detected': False, 'reason': 'missing'}
        
        try:
            result = subprocess.run(
                [str(self.detectors['intent']), str(sample_path)],
                capture_output=True, text=True, timeout=30
            )
            return {
                'layer': 'intent',
                'detected': "malicious" in result.stdout.lower() or "恶意" in result.stdout,
                'output': result.stdout[:500]
            }
        except Exception as e:
            return {'layer': 'intent', 'detected': False, 'error': str(e)}
    
    def run_layer3_ast(self, sample_path):
        """Layer 3: AST 分析"""
        print(f"\n🔍 Layer 3: AST 分析")
        if not self.detectors['ast'].exists():
            print("  ⚠️  检测器不存在")
            return {'layer': 'ast', 'detected': False, 'reason': 'missing'}
        
        try:
            result = subprocess.run(
                [str(self.detectors['ast']), str(sample_path)],
                capture_output=True, text=True, timeout=30
            )
            return {
                'layer': 'ast',
                'detected': result.returncode == 0 and "obfuscation" in result.stdout.lower(),
                'output': result.stdout[:500]
            }
        except Exception as e:
            return {'layer': 'ast', 'detected': False, 'error': str(e)}
    
    def run_all_layers(self, sample_path):
        """运行所有层"""
        results = []
        
        # Layer 1: YARA
        results.append(self.run_layer1_yara(sample_path))
        
        # Layer 2: Intent
        results.append(self.run_layer2_intent(sample_path))
        
        # Layer 3: AST
        results.append(self.run_layer3_ast(sample_path))
        
        # 综合判断
        detected_count = sum(1 for r in results if r.get('detected'))
        total_layers = len([r for r in results if r.get('layer')])
        
        print(f"\n{'='*60}")
        print(f"📊 综合判断：{detected_count}/{total_layers} 层检出")
        print(f"{'='*60}")
        
        return {
            'sample': str(sample_path),
            'results': results,
            'detected_count': detected_count,
            'total_layers': total_layers,
            'is_malicious': detected_count >= 2  # 至少 2 层检出才判定为恶意
        }
    
    def test_sample(self, sample_path):
        """测试单个样本"""
        print(f"\n{'='*60}")
        print(f"🧪 测试样本：{sample_path.name}")
        print(f"{'='*60}")
        
        result = self.run_all_layers(sample_path)
        
        if result['is_malicious']:
            print(f"✅ 判定：恶意")
        else:
            print(f"✅ 判定：良性")
        
        return result

def main():
    scanner = MultiLayerScanner()
    
    # 检查检测器状态
    scanner.check_detector_status()
    
    # 测试样本
    benchmark_dir = Path.home() / "Desktop/security-benchmark"
    test_samples = list(benchmark_dir.glob("samples/from-templates/**/MAL-*.json"))[:3]
    
    for sample in test_samples:
        scanner.test_sample(sample.parent)
        print("\n\n")

if __name__ == '__main__':
    main()
