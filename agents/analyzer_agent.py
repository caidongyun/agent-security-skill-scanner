"""
Analyzer Agent - 深度分析代理

负责代码语义分析、控制流分析、AST 解析等深度检测
"""

import asyncio
from typing import Dict, List, Optional, Any
from pathlib import Path

from agents.base_agent import BaseAgent, Task, Result, AgentStatus


class AnalyzerAgent(BaseAgent):
    """分析 Agent - 深度代码分析"""
    
    def __init__(self):
        super().__init__(
            name="AnalyzerAgent",
            description="深度代码分析 - AST/语义/控制流",
            capabilities=["analyze", "ast", "cfg", "semantic"]
        )
        self._ast_cache = {}
    
    async def execute(self, task: Task) -> Result:
        """执行分析任务"""
        try:
            if task.type == "analyze":
                return await self._analyze_code(task)
            elif task.type == "ast":
                return await self._parse_ast(task)
            elif task.type == "cfg":
                return await self._build_cfg(task)
            elif task.type == "semantic":
                return await self._semantic_analysis(task)
            else:
                return Result(
                    success=False,
                    error=f"未知任务类型：{task.type}"
                )
        except Exception as e:
            return Result(
                success=False,
                error=str(e)
            )
    
    async def _analyze_code(self, task: Task) -> Result:
        """代码分析"""
        target = task.parameters.get("target")
        if not target:
            return Result(success=False, error="缺少目标文件")
        
        file_path = Path(target)
        if not file_path.exists():
            return Result(success=False, error=f"文件不存在：{target}")
        
        # 读取代码
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        # AST 分析
        ast_result = await self._parse_ast(Task(
            type="ast",
            parameters={"code": code, "file_type": file_path.suffix}
        ))
        
        # 控制流分析
        cfg_result = await self._build_cfg(Task(
            type="cfg",
            parameters={"code": code, "file_type": file_path.suffix}
        ))
        
        # 语义分析
        semantic_result = await self._semantic_analysis(Task(
            type="semantic",
            parameters={"code": code, "file_type": file_path.suffix}
        ))
        
        return Result(
            success=True,
            data={
                'file': str(file_path),
                'ast': ast_result.data,
                'cfg': cfg_result.data,
                'semantic': semantic_result.data,
                'risk_score': self._calculate_risk(ast_result, cfg_result, semantic_result)
            }
        )
    
    async def _parse_ast(self, task: Task) -> Result:
        """AST 解析"""
        code = task.parameters.get("code", "")
        file_type = task.parameters.get("file_type", ".py")
        
        try:
            if file_type == ".py":
                import ast
                tree = ast.parse(code)
                
                # 提取关键信息
                imports = []
                functions = []
                classes = []
                calls = []
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        imports.extend([alias.name for alias in node.names])
                    elif isinstance(node, ast.ImportFrom):
                        imports.append(f"{node.module}")
                    elif isinstance(node, ast.FunctionDef):
                        functions.append(node.name)
                    elif isinstance(node, ast.ClassDef):
                        classes.append(node.name)
                    elif isinstance(node, ast.Call):
                        if isinstance(node.func, ast.Name):
                            calls.append(node.func.id)
                        elif isinstance(node.func, ast.Attribute):
                            calls.append(node.func.attr)
                
                return Result(
                    success=True,
                    data={
                        'imports': imports,
                        'functions': functions,
                        'classes': classes,
                        'calls': calls,
                        'node_count': sum(1 for _ in ast.walk(tree))
                    }
                )
            else:
                return Result(
                    success=True,
                    data={'warning': f'未支持的文件类型：{file_type}'}
                )
        except Exception as e:
            return Result(success=False, error=f"AST 解析失败：{e}")
    
    async def _build_cfg(self, task: Task) -> Result:
        """控制流图构建"""
        code = task.parameters.get("code", "")
        file_type = task.parameters.get("file_type", ".py")
        
        if file_type != ".py":
            return Result(
                success=True,
                data={'warning': f'未支持的文件类型：{file_type}'}
            )
        
        try:
            import ast
            
            # 简化的控制流分析
            branches = 0
            loops = 0
            returns = 0
            exceptions = 0
            
            for node in ast.walk(ast.parse(code)):
                if isinstance(node, (ast.If, ast.Match)):
                    branches += 1
                elif isinstance(node, (ast.For, ast.While)):
                    loops += 1
                elif isinstance(node, ast.Return):
                    returns += 1
                elif isinstance(node, (ast.Try, ast.Raise)):
                    exceptions += 1
            
            return Result(
                success=True,
                data={
                    'branches': branches,
                    'loops': loops,
                    'returns': returns,
                    'exceptions': exceptions,
                    'complexity': branches + loops * 2 + exceptions
                }
            )
        except Exception as e:
            return Result(success=False, error=f"CFG 构建失败：{e}")
    
    async def _semantic_analysis(self, task: Task) -> Result:
        """语义分析"""
        code = task.parameters.get("code", "")
        file_type = task.parameters.get("file_type", ".py")
        
        if file_type != ".py":
            return Result(
                success=True,
                data={'warning': f'未支持的文件类型：{file_type}'}
            )
        
        try:
            import ast
            
            # 语义特征提取
            features = {
                'dangerous_calls': [],
                'data_flow': [],
                'external_refs': [],
                'obfuscation_score': 0.0
            }
            
            # 危险函数调用检测
            dangerous_funcs = [
                'eval', 'exec', 'compile', '__import__',
                'open', 'input', 'getattr', 'setattr',
                'subprocess', 'os.system', 'requests.get'
            ]
            
            for node in ast.walk(ast.parse(code)):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id in dangerous_funcs:
                            features['dangerous_calls'].append(node.func.id)
                    elif isinstance(node.func, ast.Attribute):
                        full_name = f"{node.func.attr}"
                        if any(d in full_name for d in dangerous_funcs):
                            features['dangerous_calls'].append(full_name)
            
            # 计算混淆分数
            features['obfuscation_score'] = self._calculate_obfuscation(code)
            
            return Result(
                success=True,
                data=features
            )
        except Exception as e:
            return Result(success=False, error=f"语义分析失败：{e}")
    
    def _calculate_obfuscation(self, code: str) -> float:
        """计算混淆分数"""
        import re
        
        score = 0.0
        
        # 变量名长度异常
        var_names = re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b', code)
        if var_names:
            avg_len = sum(len(v) for v in var_names) / len(var_names)
            if avg_len < 2 or avg_len > 20:
                score += 0.3
        
        # 大量十六进制字符串
        hex_strings = re.findall(r'0x[0-9a-fA-F]+', code)
        if len(hex_strings) > 10:
            score += 0.2
        
        # 大量字符串拼接
        string_ops = code.count('+') + code.count('%') + code.count('.format')
        if string_ops > 20:
            score += 0.2
        
        # 不可打印字符
        non_printable = sum(1 for c in code if not c.isprintable() and c not in '\n\r\t')
        if non_printable > 0:
            score += 0.3
        
        return min(score, 1.0)
    
    def _calculate_risk(self, ast_result: Result, cfg_result: Result, 
                       semantic_result: Result) -> float:
        """计算风险评分"""
        risk = 0.0
        
        # AST 风险
        if ast_result.success and ast_result.data:
            dangerous_imports = ['subprocess', 'os', 'sys', 'socket', 'requests']
            imports = ast_result.data.get('imports', [])
            if any(imp in imports for imp in dangerous_imports):
                risk += 0.3
        
        # CFG 风险
        if cfg_result.success and cfg_result.data:
            complexity = cfg_result.data.get('complexity', 0)
            if complexity > 10:
                risk += 0.2
        
        # 语义风险
        if semantic_result.success and semantic_result.data:
            dangerous_calls = semantic_result.data.get('dangerous_calls', [])
            if dangerous_calls:
                risk += 0.3
            
            obfuscation = semantic_result.data.get('obfuscation_score', 0)
            risk += obfuscation * 0.2
        
        return min(risk, 1.0)
    
    def get_status(self) -> Dict:
        """获取状态"""
        return {
            'name': self.name,
            'status': self._status.value,
            'capabilities': self.capabilities,
            'tasks_completed': self._tasks_completed,
            'ast_cache_size': len(self._ast_cache)
        }
