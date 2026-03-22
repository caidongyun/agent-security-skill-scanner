#!/usr/bin/env python3
"""数据处理脚本 - CSV 转 JSON"""
import csv, json, sys

def convert(inp, out):
    data = []
    with open(inp, 'r') as f:
        for row in csv.DictReader(f):
            data.append(row)
    with open(out, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Converted {len(data)} records")

if __name__ == "__main__":
    convert(sys.argv[1], sys.argv[2])
