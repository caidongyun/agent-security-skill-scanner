"""
检测器模块
"""

from .malware import MalwareDetector
from .metadata import MetadataDetector

__all__ = ['MalwareDetector', 'MetadataDetector']
