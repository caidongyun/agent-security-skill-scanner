#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
远程分析服务 - 上下文关联分析
集成 LLM 辅助判断，减少误报
"""

import os
import sys
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict


@dataclass
class AnalysisRequest:
    """分析请求"""
    skill_name: str
    file_path: str
    line_number: int
    rule_id: str
    code_snippet: str
    context: Dict
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class AnalysisResult:
    """分析结果"""
    request_id: str
    is_false_positive: bool
    confidence: float
    reasoning: str
    suggestions: List[str]
    auto_whitelist: bool
    analyzed_at: str
    
    def to_dict(self) -> Dict:
        return asdict(self)


class RemoteAnalyzer:
    """远程分析器"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config = self._load_config(config_file)
        self.history_db = Path(self.config.get('history_db', 'data/analysis_history.json'))
        self.history_db.parent.mkdir(parents=True, exist_ok=True)
        self.history = self._load_history()
    
    def _load_config(self, config_file: Optional[str]) -> Dict:
        """加载配置"""
        default_config = {
            'llm_provider': 'bailian',  # bailian/minimax
            'llm_model': 'qwen3.5-plus',
            'context_window': 20,  # 上下文行数
            'confidence_threshold': 0.8,  # 自动加白阈值
            'history_db': 'data/analysis_history.json',
            'cache_enabled': True,
            'cache_ttl_hours': 24
        }
        
        if config_file and os.path.exists(config_file):
            with open(config_file, 'r') as f:
                custom_config = json.load(f)
                default_config.update(custom_config)
        
        return default_config
    
    def _load_history(self) -> Dict:
        """加载分析历史"""
        if self.history_db.exists():
            with open(self.history_db, 'r') as f:
                return json.load(f)
        return {'analyses': {}}
    
    def _save_history(self):
        """保存分析历史"""
        with open(self.history_db, 'w') as f:
            json.dump(self.history, f, indent=2)
    
    def _generate_request_id(self, request: AnalysisRequest) -> str:
        """生成请求 ID（基于内容哈希）"""
        content = json.dumps(request.to_dict(), sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def _extract_context(self, file_path: str, line_number: int, window: int = 20) -> Dict:
        """提取代码上下文"""
        if not os.path.exists(file_path):
            return {'error': 'File not found'}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        start = max(0, line_number - window)
        end = min(len(lines), line_number + window)
        
        return {
            'before': ''.join(lines[start:line_number]),
            'target': lines[line_number] if line_number < len(lines) else '',
            'after': ''.join(lines[line_number+1:end]),
            'function': self._detect_function(lines, line_number),
            'imports': self._extract_imports(lines),
            'callers': []  # 需要静态分析
        }
    
    def _detect_function(self, lines: List[str], line_number: int) -> Optional[str]:
        """检测当前函数名"""
        for i in range(line_number, -1, -1):
            line = lines[i]
            if line.strip().startswith('def '):
                # 提取函数名
                parts = line.split('def ')
                if len(parts) > 1:
                    func_name = parts[1].split('(')[0]
                    return func_name
        return None
    
    def _extract_imports(self, lines: List[str]) -> List[str]:
        """提取导入语句"""
        imports = []
        for line in lines[:50]:  # 只检查前 50 行
            line = line.strip()
            if line.startswith('import ') or line.startswith('from '):
                imports.append(line)
        return imports
    
    def _build_prompt(self, request: AnalysisRequest, context: Dict) -> str:
        """构建 LLM 提示词"""
        prompt = f"""你是一个代码安全分析专家。请分析以下代码是否存在安全风险。

## 代码信息
- 技能名称：{request.skill_name}
- 文件路径：{request.file_path}
- 行号：{request.line_number}
- 检测规则：{request.rule_id}

## 代码片段
```python
{request.code_snippet}
```

## 上下文
```python
{context.get('before', '')}
>>> {context.get('target', '')} <<<
{context.get('after', '')}
```

## 函数信息
- 函数名：{context.get('function', 'unknown')}
- 导入：{', '.join(context.get('imports', []))}

## 分析任务
请判断这是否是误报（即代码实际上是安全的）。

请以以下 JSON 格式返回：
{{
    "is_false_positive": true/false,
    "confidence": 0.0-1.0,
    "reasoning": "详细分析理由",
    "suggestions": ["改进建议 1", "改进建议 2"],
    "auto_whitelist": true/false  # 是否可以自动加入白名单
}}

分析要点:
1. eval/exec 的输入来源是否可信
2. 是否有输入验证
3. 是否在安全上下文中使用
4. 是否有更安全的替代方案
"""
        return prompt
    
    def _call_llm(self, prompt: str) -> Dict:
        """调用 LLM 进行分析"""
        # 这里集成实际的 LLM 调用
        # 目前返回模拟结果用于测试
        
        print(f"[LLM] 调用 {self.config['llm_provider']}/{self.config['llm_model']}...")
        
        # TODO: 实现实际的 LLM 调用
        # 可以使用 sessions_spawn 或直接 API 调用
        
        # 模拟结果
        return {
            'is_false_positive': True,
            'confidence': 0.85,
            'reasoning': '代码用于解析配置文件，输入来源可信，非用户输入',
            'suggestions': ['使用 ast.literal_eval 替代 eval 更安全'],
            'auto_whitelist': True
        }
    
    def analyze(self, request: AnalysisRequest) -> AnalysisResult:
        """执行分析"""
        request_id = self._generate_request_id(request)
        
        # 检查缓存
        if self.config['cache_enabled'] and request_id in self.history['analyses']:
            cached = self.history['analyses'][request_id]
            # 检查缓存是否过期
            cached_at = datetime.fromisoformat(cached['analyzed_at'])
            age_hours = (datetime.now() - cached_at).total_seconds() / 3600
            
            if age_hours < self.config['cache_ttl_hours']:
                print(f"[CACHE] 使用缓存结果：{request_id}")
                return AnalysisResult(**cached)
        
        # 提取上下文
        context = self._extract_context(
            request.file_path,
            request.line_number,
            self.config['context_window']
        )
        
        # 构建提示词
        prompt = self._build_prompt(request, context)
        
        # 调用 LLM
        llm_result = self._call_llm(prompt)
        
        # 创建结果
        result = AnalysisResult(
            request_id=request_id,
            is_false_positive=llm_result.get('is_false_positive', False),
            confidence=llm_result.get('confidence', 0.0),
            reasoning=llm_result.get('reasoning', ''),
            suggestions=llm_result.get('suggestions', []),
            auto_whitelist=llm_result.get('auto_whitelist', False),
            analyzed_at=datetime.now().isoformat()
        )
        
        # 保存到历史
        self.history['analyses'][request_id] = result.to_dict()
        self._save_history()
        
        return result
    
    def analyze_file(self, file_path: str, line_number: int, rule_id: str,
                    code_snippet: str, skill_name: str = "unknown") -> AnalysisResult:
        """便捷方法：分析文件中的某行代码"""
        request = AnalysisRequest(
            skill_name=skill_name,
            file_path=file_path,
            line_number=line_number,
            rule_id=rule_id,
            code_snippet=code_snippet,
            context={}
        )
        
        return self.analyze(request)
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        analyses = self.history.get('analyses', {})
        
        total = len(analyses)
        false_positives = sum(1 for a in analyses.values() if a.get('is_false_positive'))
        auto_whitelisted = sum(1 for a in analyses.values() if a.get('auto_whitelist'))
        
        avg_confidence = 0.0
        if total > 0:
            avg_confidence = sum(a.get('confidence', 0) for a in analyses.values()) / total
        
        return {
            'total_analyses': total,
            'false_positives_detected': false_positives,
            'auto_whitelisted': auto_whitelisted,
            'average_confidence': round(avg_confidence, 3),
            'cache_size': total
        }


class ContextAnalyzer:
    """上下文关联分析器"""
    
    def __init__(self):
        self.trusted_patterns = [
            r'eval\(config\.',  # 配置加载
            r'eval\(settings\.',  # 设置加载
            r'exec\(template\.',  # 模板执行
            r'open\([^)]*\.txt[^\)]*\)',  # 文本文件
        ]
        
        self.suspicious_patterns = [
            r'eval\(input\(',  # 用户输入
            r'eval\(request\.',  # 请求数据
            r'exec\(user\.',  # 用户数据
            r'__import__\(.*input',  # 动态导入用户输入
        ]
    
    def analyze_context(self, code: str, context: Dict) -> Dict:
        """分析代码上下文"""
        import re
        
        result = {
            'trusted_context': False,
            'suspicious_context': False,
            'input_source': 'unknown',
            'risk_indicators': [],
            'safe_indicators': []
        }
        
        # 检查可信模式
        for pattern in self.trusted_patterns:
            if re.search(pattern, code):
                result['trusted_context'] = True
                result['safe_indicators'].append(f'Matches trusted pattern: {pattern}')
        
        # 检查可疑模式
        for pattern in self.suspicious_patterns:
            if re.search(pattern, code):
                result['suspicious_context'] = True
                result['risk_indicators'].append(f'Matches suspicious pattern: {pattern}')
        
        # 分析输入来源
        if 'input(' in code:
            result['input_source'] = 'user_input'
            result['risk_indicators'].append('Direct user input detected')
        elif 'request.' in code:
            result['input_source'] = 'http_request'
            result['risk_indicators'].append('HTTP request data detected')
        elif 'config.' in code or 'settings.' in code:
            result['input_source'] = 'configuration'
            result['safe_indicators'].append('Configuration data source')
        
        return result


def main():
    """CLI 入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='远程分析服务')
    parser.add_argument('--file', '-f', type=str, required=True, help='文件路径')
    parser.add_argument('--line', '-l', type=int, required=True, help='行号')
    parser.add_argument('--rule', '-r', type=str, required=True, help='规则 ID')
    parser.add_argument('--snippet', '-s', type=str, help='代码片段')
    parser.add_argument('--skill', type=str, default='unknown', help='技能名称')
    parser.add_argument('--config', '-c', type=str, help='配置文件')
    parser.add_argument('--stats', action='store_true', help='显示统计')
    
    args = parser.parse_args()
    
    analyzer = RemoteAnalyzer(args.config)
    
    if args.stats:
        stats = analyzer.get_statistics()
        print(json.dumps(stats, indent=2, ensure_ascii=False))
        return
    
    # 读取代码片段
    if not args.snippet:
        with open(args.file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            if args.line < len(lines):
                args.snippet = lines[args.line].strip()
            else:
                print("[ERROR] 行号超出范围")
                sys.exit(1)
    
    # 执行分析
    result = analyzer.analyze_file(
        file_path=args.file,
        line_number=args.line,
        rule_id=args.rule,
        code_snippet=args.snippet,
        skill_name=args.skill
    )
    
    print(f"\n[分析结果]")
    print(f"请求 ID: {result.request_id}")
    print(f"是否误报：{'是' if result.is_false_positive else '否'}")
    print(f"置信度：{result.confidence:.2%}")
    print(f"自动加白：{'是' if result.auto_whitelist else '否'}")
    print(f"\n分析理由:\n{result.reasoning}")
    
    if result.suggestions:
        print(f"\n建议:")
        for i, sug in enumerate(result.suggestions, 1):
            print(f"  {i}. {sug}")
    
    print(f"\n分析时间：{result.analyzed_at}")


if __name__ == "__main__":
    main()
