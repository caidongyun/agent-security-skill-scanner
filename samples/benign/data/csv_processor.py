# Generated: 2026-04-02 12:15:22.313817
# Type: Benign Python Sample

#!/usr/bin/env python3
"""CSV 数据处理 - 良性"""
import pandas as pd
import sys

def process_csv(input_file, output_file):
    df = pd.read_csv(input_file)
    
    # 数据清洗
    df = df.dropna()
    df = df.drop_duplicates()
    
    # 数据统计
    print(f"总行数：{len(df)}")
    print(f"列数：{len(df.columns)}")
    print(df.describe())
    
    df.to_csv(output_file, index=False)
    print(f"处理完成：{output_file}")

if __name__ == '__main__':
    if len(sys.argv) >= 3:
        process_csv(sys.argv[1], sys.argv[2])
