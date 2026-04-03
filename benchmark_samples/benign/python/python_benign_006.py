#!/usr/bin/env python3
"""Benign utility functions"""
import os
import json

def read_config(path):
    """Read configuration file"""
    with open(path, 'r') as f:
        return json.load(f)

def calculate_sum(numbers):
    """Calculate sum of numbers"""
    return sum(numbers)

if __name__ == "__main__":
    print(calculate_sum([1, 2, 3, 4, 5]))
