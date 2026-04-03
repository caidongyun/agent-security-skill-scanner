# Sample Generator v2.0
"""恶意样本生成器"""

__version__ = "2.0.0"
__author__ = "Security Team"

from .base_generator import BaseGenerator, MaliciousSample
from .cli import generate_samples, main

__all__ = [
    'BaseGenerator',
    'MaliciousSample',
    'generate_samples',
    'main',
]
