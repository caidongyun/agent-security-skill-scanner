"""
Agent Security Multi-Agent System
"""

from .base_agent import BaseAgent, Task, Result
from .orchestrator import OrchestratorAgent
from .detector_agent import DetectorAgent

__version__ = "2.0.0"
__all__ = [
    "BaseAgent",
    "Task",
    "Result",
    "OrchestratorAgent",
    "DetectorAgent",
]
