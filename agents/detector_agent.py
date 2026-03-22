"""
Detector Agent - 安全检测 Agent
整合 t14g2-v1 的检测引擎
"""

from pathlib import Path
from typing import Dict, List, Optional
import asyncio

from .base_agent import BaseAgent, Task, Result


class DetectorAgent(BaseAgent):
    """检测 Agent"""
    
    def __init__(self, config: Optional[Dict] = None):
        super().__init__("detector", config)
        self.supported_types = ["scan", "detect", "analyze"]
        self.rules_loaded = 0
        self.samples_indexed = 0
        self._load_rules()
    
    def _load_rules(self):
        """加载检测规则 (从 t14g2-v1)"""
        # TODO: 集成 t14g2-v1 的规则加载逻辑
        self.rules_loaded = 350  #  placeholder
        self._log("INFO", f"Loaded {self.rules_loaded} rules")
    
    async def execute(self, task: Task) -> Result:
        """执行检测任务"""
        self.current_task = task
        self.update_status("busy")
        
        try:
            task_type = task.type
            parameters = task.parameters
            
            if task_type == "scan":
                target = parameters.get("target", "")
                result_data = await self._scan_target(target)
            elif task_type == "detect":
                content = parameters.get("content", "")
                result_data = await self._detect_content(content)
            elif task_type == "analyze":
                file_path = parameters.get("file_path", "")
                result_data = await self._analyze_file(file_path)
            else:
                raise ValueError(f"Unknown task type: {task_type}")
            
            self.completed_tasks += 1
            
            return Result(
                task_id=task.id,
                agent_id=self.agent_id,
                success=True,
                data=result_data,
                metrics={
                    'scan_duration_ms': result_data.get('duration_ms', 0),
                    'files_scanned': result_data.get('files_scanned', 0),
                }
            )
        
        except Exception as e:
            self.failed_tasks += 1
            self._log("ERROR", f"Detection failed: {e}")
            
            return Result(
                task_id=task.id,
                agent_id=self.agent_id,
                success=False,
                error=str(e),
            )
        
        finally:
            self.current_task = None
            self.update_status("idle")
    
    async def _scan_target(self, target: str) -> Dict:
        """扫描目标 (文件/目录)"""
        self._log("INFO", f"Scanning target: {target}")
        
        start_time = asyncio.get_event_loop().time()
        
        path = Path(target)
        if not path.exists():
            raise FileNotFoundError(f"Target not found: {target}")
        
        if path.is_file():
            result = await self._scan_file(path)
        elif path.is_dir():
            result = await self._scan_directory(path)
        else:
            raise ValueError(f"Invalid target type: {target}")
        
        duration_ms = (asyncio.get_event_loop().time() - start_time) * 1000
        result['duration_ms'] = duration_ms
        
        return result
    
    async def _scan_file(self, file_path: Path) -> Dict:
        """扫描单个文件"""
        self._log("DEBUG", f"Scanning file: {file_path}")
        
        # TODO: 集成 t14g2-v1 的检测逻辑
        # 这里是 placeholder
        result = {
            'file_path': str(file_path),
            'is_malicious': False,
            'confidence': 0.0,
            'matched_rules': [],
            'severity': 'none',
            'files_scanned': 1,
        }
        
        return result
    
    async def _scan_directory(self, dir_path: Path) -> Dict:
        """扫描目录"""
        self._log("INFO", f"Scanning directory: {dir_path}")
        
        files = list(dir_path.rglob("*"))
        files = [f for f in files if f.is_file()]
        
        results = []
        for file in files:
            try:
                result = await self._scan_file(file)
                results.append(result)
            except Exception as e:
                self._log("ERROR", f"Failed to scan {file}: {e}")
        
        # 汇总结果
        malicious_files = [r for r in results if r.get('is_malicious')]
        
        return {
            'directory': str(dir_path),
            'total_files': len(files),
            'files_scanned': len(results),
            'malicious_count': len(malicious_files),
            'malicious_files': malicious_files,
            'duration_ms': 0,  # 会在上层设置
        }
    
    async def _detect_content(self, content: str) -> Dict:
        """检测内容字符串"""
        self._log("DEBUG", "Detecting content")
        
        # TODO: 集成 t14g2-v1 的内容检测逻辑
        result = {
            'content_length': len(content),
            'is_malicious': False,
            'confidence': 0.0,
            'matched_rules': [],
        }
        
        return result
    
    async def _analyze_file(self, file_path: str) -> Dict:
        """深度分析文件"""
        self._log("DEBUG", f"Analyzing file: {file_path}")
        
        # TODO: 集成 AST/语义/控制流分析
        result = {
            'file_path': file_path,
            'ast_analysis': {},
            'semantic_analysis': {},
            'cfg_analysis': {},
        }
        
        return result
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        base_stats = super().get_stats()
        base_stats.update({
            'rules_loaded': self.rules_loaded,
            'samples_indexed': self.samples_indexed,
        })
        return base_stats
