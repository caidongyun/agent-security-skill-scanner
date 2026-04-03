# Generated: 2026-04-02 11:55:15.209383
# Type: Benign Python Sample

#!/usr/bin/env python3
"""ML 训练管道 - 良性"""
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

df = pd.read_csv('data.csv')
X = df.drop('target', axis=1)
y = df['target']
X_train, X_test = train_test_split(X, y)
model = RandomForestClassifier()
model.fit(X_train, y_train)
print(f"训练完成，准确率：{model.score(X_test, y_test):.2f}")
