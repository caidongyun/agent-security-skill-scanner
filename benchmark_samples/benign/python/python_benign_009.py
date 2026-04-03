#!/usr/bin/env python3
"""Data processing utility"""
import csv
from typing import List, Dict

def process_csv(filepath: str) -> List[Dict]:
    """Process CSV file"""
    results = []
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            results.append(row)
    return results

def transform_data(data: List[Dict]) -> List[Dict]:
    """Transform data"""
    return [{k.upper(): v for k, v in item.items()} for item in data]
