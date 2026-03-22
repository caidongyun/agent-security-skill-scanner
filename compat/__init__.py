"""
兼容层 - 保证 t14g2-v1 → V3 的 API 兼容性

使用方式:
    from compat.scanner import Scanner
    
    scanner = Scanner()
    result = scanner.scan_file("./target.py")
"""

import asyncio
from pathlib import Path
from typing import Dict, List, Optional

from agents.orchestrator import OrchestratorAgent
from agents.base_agent import Task, Result


class Scanner:
    """兼容 t14g2-v1 的 Scanner API"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.orchestrator = OrchestratorAgent()
        self.config_path = config_path
        self._initialized = False
    
    def _ensure_initialized(self):
        """确保 Orchestrator 已初始化"""
        if not self._initialized:
            # 注册 Detector Agent
            from agents.detector_agent import DetectorAgent
            detector = DetectorAgent()
            self.orchestrator.register_agent(detector, capabilities=["scan", "detect", "analyze"])
            self._initialized = True
    
    def scan_file(self, file_path: str) -> Dict:
        """扫描单个文件 (兼容 t14g2-v1 API)"""
        self._ensure_initialized()
        
        task = Task(
            type="scan",
            parameters={"target": file_path}
        )
        result = asyncio.run(self.orchestrator.execute(task))
        
        if result.success:
            return result.data
        else:
            return {
                'file_path': file_path,
                'is_malicious': False,
                'error': result.error,
            }
    
    def scan_directory(self, dir_path: str) -> Dict:
        """扫描目录 (兼容 t14g2-v1 API)"""
        self._ensure_initialized()
        
        task = Task(
            type="scan",
            parameters={"target": dir_path}
        )
        result = asyncio.run(self.orchestrator.execute(task))
        
        if result.success:
            return result.data
        else:
            return {
                'directory': dir_path,
                'total_files': 0,
                'malicious_count': 0,
                'error': result.error,
            }
    
    def scan_content(self, content: str, file_type: str = "python") -> Dict:
        """扫描内容字符串 (兼容 t14g2-v1 API)"""
        self._ensure_initialized()
        
        task = Task(
            type="detect",
            parameters={
                "content": content,
                "file_type": file_type
            }
        )
        result = asyncio.run(self.orchestrator.execute(task))
        
        if result.success:
            return result.data
        else:
            return {
                'content_length': len(content),
                'is_malicious': False,
                'error': result.error,
            }
    
    def get_statistics(self) -> Dict:
        """获取统计信息 (兼容 t14g2-v1 API)"""
        return {
            'version': '3.0.0',
            'mode': 'multi-agent',
            'orchestrator_status': self.orchestrator.get_status(),
        }


class RuleManager:
    """兼容 t14g2-v1 的规则管理器 API"""
    
    def __init__(self, rules_path: str = "./rules/optimized/"):
        self.rules_path = Path(rules_path)
        self.rules = []
        self._load_rules()
    
    def _load_rules(self):
        """加载规则"""
        import yaml
        
        if not self.rules_path.exists():
            return
        
        for rule_file in self.rules_path.glob("*.yaml"):
            try:
                with open(rule_file, 'r', encoding='utf-8') as f:
                    rules = yaml.safe_load(f)
                    if isinstance(rules, list):
                        self.rules.extend(rules)
                    elif isinstance(rules, dict):
                        self.rules.append(rules)
            except Exception as e:
                print(f"Warning: Failed to load {rule_file}: {e}")
    
    def get_rule_count(self) -> int:
        """获取规则数量"""
        return len(self.rules)
    
    def get_rules_by_tier(self, tier: str) -> List:
        """按层级获取规则"""
        return [r for r in self.rules if r.get('tier') == tier]
    
    def get_rules_by_attack_type(self, attack_type: str) -> List:
        """按攻击类型获取规则"""
        return [r for r in self.rules if r.get('attack_type') == attack_type]


class SampleManager:
    """兼容 t14g2-v1 的样本管理器 API"""
    
    def __init__(self, samples_path: str = "./samples/"):
        self.samples_path = Path(samples_path)
        self.malicious_path = self.samples_path / "malicious"
        self.benign_path = self.samples_path / "benign"
    
    def get_sample_count(self, sample_type: str = "all") -> int:
        """获取样本数量"""
        if sample_type == "malicious":
            return len(list(self.malicious_path.rglob("*"))) if self.malicious_path.exists() else 0
        elif sample_type == "benign":
            return len(list(self.benign_path.rglob("*"))) if self.benign_path.exists() else 0
        else:
            return self.get_sample_count("malicious") + self.get_sample_count("benign")
    
    def get_sample(self, sample_id: str) -> Optional[Path]:
        """获取样本文件路径"""
        # 在恶意样本目录查找
        if self.malicious_path.exists():
            for sample in self.malicious_path.rglob("*"):
                if sample.name == sample_id or sample.stem == sample_id:
                    return sample
        
        # 在良性样本目录查找
        if self.benign_path.exists():
            for sample in self.benign_path.rglob("*"):
                if sample.name == sample_id or sample.stem == sample_id:
                    return sample
        
        return None
