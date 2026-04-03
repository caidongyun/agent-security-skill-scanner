#!/usr/bin/env python3
"""
Round 24 - 模型训练脚本

使用 XGBoost + LightGBM 训练恶意代码检测模型
"""

import sys
import json
import pickle
from pathlib import Path
from datetime import datetime

# 添加路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from features.feature_extractor import FeatureExtractor

try:
    import xgboost as xgb
    import lightgbm as lgb
    from sklearn.model_selection import cross_val_score, StratifiedKFold
    from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
    from sklearn.ensemble import VotingClassifier
    import numpy as np
    ML_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  ML 库未安装：{e}")
    print("安装命令：pip install xgboost lightgbm scikit-learn")
    ML_AVAILABLE = False

class MLClassifier:
    """ML 分类器"""
    
    def __init__(self):
        self.feature_extractor = FeatureExtractor()
        self.model = None
        self.feature_names = None
    
    def prepare_dataset(self, samples_dir: str):
        """准备训练数据集"""
        X = []
        y = []
        file_paths = []
        
        samples_path = Path(samples_dir)
        
        # 加载恶意样本
        print("📁 加载恶意样本...")
        malicious_dirs = [
            samples_path / 'python_malicious',
            samples_path / 'javascript_malicious',
            samples_path / 'shell_malicious',
            samples_path / 'powershell_malicious',
        ]
        
        for mal_dir in malicious_dirs:
            if mal_dir.exists():
                lang = mal_dir.name.replace('_malicious', '')
                for ps_file in mal_dir.glob('*.py') or mal_dir.glob('*.js') or mal_dir.glob('*.sh') or mal_dir.glob('*.ps1'):
                    try:
                        with open(ps_file, 'r', encoding='utf-8', errors='ignore') as f:
                            code = f.read()
                        features = self.feature_extractor.extract_all_features(code, lang)
                        X.append(list(features.values()))
                        y.append(1)  # 恶意
                        file_paths.append(str(ps_file))
                        if self.feature_names is None:
                            self.feature_names = list(features.keys())
                    except Exception as e:
                        print(f"⚠️  读取失败 {ps_file}: {e}")
        
        # 加载安全样本
        print("📁 加载安全样本...")
        safe_dirs = [
            samples_path / 'python_safe',
            samples_path / 'javascript_safe',
            samples_path / 'shell_safe',
            samples_path / 'powershell_safe',
        ]
        
        for safe_dir in safe_dirs:
            if safe_dir.exists():
                lang = safe_dir.name.replace('_safe', '')
                for ps_file in safe_dir.glob('*.py') or safe_dir.glob('*.js') or safe_dir.glob('*.sh') or safe_dir.glob('*.ps1'):
                    try:
                        with open(ps_file, 'r', encoding='utf-8', errors='ignore') as f:
                            code = f.read()
                        features = self.feature_extractor.extract_all_features(code, lang)
                        X.append(list(features.values()))
                        y.append(0)  # 安全
                        file_paths.append(str(ps_file))
                    except Exception as e:
                        print(f"⚠️  读取失败 {ps_file}: {e}")
        
        print(f"✅ 加载完成：{len(X)} 样本，{sum(y)} 恶意，{len(y)-sum(y)} 安全")
        
        return X, y, file_paths
    
    def train(self, X, y):
        """训练模型"""
        if not ML_AVAILABLE:
            print("❌ ML 库不可用，跳过训练")
            return None
        
        X = np.array(X)
        y = np.array(y)
        
        print(f"\n📊 数据集形状：{X.shape}")
        print(f"   特征数：{X.shape[1]}")
        print(f"   样本数：{X.shape[0]}")
        print(f"   恶意：{sum(y)}, 安全：{len(y)-sum(y)}")
        
        # 1. XGBoost 模型
        print("\n🌲 训练 XGBoost...")
        xgb_model = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            scale_pos_weight=sum(y) / (len(y) - sum(y)),  # 处理不平衡
            random_state=42,
            eval_metric='logloss',
        )
        
        # 2. LightGBM 模型
        print("🌲 训练 LightGBM...")
        lgb_model = lgb.LGBMClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            class_weight='balanced',
            random_state=42,
        )
        
        # 3. 交叉验证
        print("\n📈 5 折交叉验证...")
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        
        xgb_scores = cross_val_score(xgb_model, X, y, cv=cv, scoring='accuracy')
        lgb_scores = cross_val_score(lgb_model, X, y, cv=cv, scoring='accuracy')
        
        print(f"\nXGBoost 准确率：{xgb_scores.mean():.4f} (+/- {xgb_scores.std()*2:.4f})")
        print(f"LightGBM 准确率：{lgb_scores.mean():.4f} (+/- {lgb_scores.std()*2:.4f})")
        
        # 4. 融合模型 (Voting)
        print("\n🤖 训练融合模型 (Voting)...")
        self.model = VotingClassifier(
            estimators=[
                ('xgb', xgb_model),
                ('lgb', lgb_model),
            ],
            voting='soft',
            weights=[1, 1],
        )
        
        # 5. 训练最终模型
        self.model.fit(X, y)
        
        # 6. 评估
        print("\n📊 模型评估...")
        y_pred = self.model.predict(X)
        y_proba = self.model.predict_proba(X)[:, 1]
        
        print("\n分类报告:")
        print(classification_report(y, y_pred, target_names=['安全', '恶意']))
        
        print("\n混淆矩阵:")
        cm = confusion_matrix(y, y_pred)
        print(cm)
        print(f"   预测：安全  恶意")
        print(f"   实际：[{cm[0][0]:4d} {cm[0][1]:4d}]  安全")
        print(f"          [{cm[1][0]:4d} {cm[1][1]:4d}]  恶意")
        
        # AUC
        if len(set(y)) > 1:
            auc = roc_auc_score(y, y_proba)
            print(f"\nAUC 分数：{auc:.4f}")
        
        # 特征重要性
        print("\n📊 Top 10 重要特征:")
        if hasattr(self.model, 'feature_importances_'):
            importances = self.model.feature_importances_
            top_indices = np.argsort(importances)[::-1][:10]
            for i, idx in enumerate(top_indices, 1):
                print(f"   {i}. {self.feature_names[idx]}: {importances[idx]:.4f}")
        
        return self.model
    
    def predict(self, features: dict) -> tuple:
        """预测单个样本"""
        if self.model is None:
            return False, 0.0, "Model not trained"
        
        X = np.array([list(features.values())])
        pred = self.model.predict(X)[0]
        proba = self.model.predict_proba(X)[0]
        
        is_malicious = pred == 1
        confidence = proba[1] if is_malicious else proba[0]
        
        return is_malicious, confidence, "ML prediction"
    
    def save_model(self, model_path: str):
        """保存模型"""
        if self.model is None:
            print("❌ 没有可保存的模型")
            return
        
        model_data = {
            'model': self.model,
            'feature_names': self.feature_names,
        }
        
        with open(model_path, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"💾 模型已保存：{model_path}")
    
    def load_model(self, model_path: str):
        """加载模型"""
        with open(model_path, 'rb') as f:
            model_data = pickle.load(f)
        
        self.model = model_data['model']
        self.feature_names = model_data['feature_names']
        
        print(f"📥 模型已加载：{model_path}")


def main():
    """主训练脚本"""
    print("=" * 70)
    print("🤖 Round 24 - ML 模型训练")
    print("=" * 70)
    
    if not ML_AVAILABLE:
        print("\n❌ ML 库未安装，请运行:")
        print("   pip install xgboost lightgbm scikit-learn")
        return
    
    classifier = MLClassifier()
    
    # 1. 准备数据
    samples_dir = Path(__file__).parent.parent / 'samples'
    X, y, file_paths = classifier.prepare_dataset(str(samples_dir))
    
    if len(X) == 0:
        print("❌ 没有样本可训练")
        return
    
    # 2. 训练模型
    classifier.train(X, y)
    
    # 3. 保存模型
    models_dir = Path(__file__).parent.parent / 'round24' / 'ml' / 'models'
    models_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    model_path = models_dir / f'scanner_v3_ml_{timestamp}.pkl'
    classifier.save_model(str(model_path))
    
    # 4. 保存训练报告
    report = {
        'timestamp': datetime.now().isoformat(),
        'total_samples': len(X),
        'malicious': sum(y),
        'safe': len(y) - sum(y),
        'feature_count': len(classifier.feature_names) if classifier.feature_names else 0,
        'model_type': 'XGBoost + LightGBM Voting',
    }
    
    report_path = models_dir / f'training_report_{timestamp}.json'
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n💾 训练报告已保存：{report_path}")
    
    print("\n" + "=" * 70)
    print("✅ Round 24 模型训练完成!")
    print("=" * 70)


if __name__ == '__main__':
    main()
