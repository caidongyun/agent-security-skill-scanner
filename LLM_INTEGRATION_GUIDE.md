# LLM 集成使用文档

**版本**: v6.1.8  
**更新日期**: 2026-04-19

---

## 📋 概述

v6.1.8 已集成 LLM 深度分析引擎，支持：
- ✅ YAML 专用分析 Prompt (Week 1 优化版)
- ✅ 通用代码分析 Prompt
- ✅ 多模型支持 (MiniMax, Qwen, OpenAI)
- ✅ 置信度分级处理
- ✅ MITRE ATLAS + OWASP LLM 映射

---

## 🚀 快速开始

### 1. 配置 API Key

```bash
# 方式 1: 环境变量
export LLM_API_KEY="your-api-key-here"

# 方式 2: 配置文件
echo "LLM_API_KEY=your-api-key-here" >> ~/.openclaw/workspace/agent-security-skill-scanner-master/release/v6.1.8/.env
```

### 2. 启用 LLM 引擎

```bash
# 扫描时启用 LLM
python3 scanner.py /path/to/samples --llm --llm-model minimax

# 或仅对可疑样本启用 (推荐)
python3 scanner.py /path/to/samples --llm --llm-threshold 0.7
```

### 3. Python 代码集成

```python
from src.engines.llm_engine import LLMEngine

# 初始化引擎
llm = LLMEngine(model='minimax')

# 分析 YAML
yaml_content = """
attack_type: resource_exhaustion
resource_attack:
  type: exhaustion
  cpu_hog:
    enabled: true
"""

result = llm.analyze(yaml_content)
print(f"恶意：{result.is_malicious}")
print(f"置信度：{result.confidence}")
print(f"风险等级：{result.risk_level}")
print(f"分析理由：{result.reason}")
```

---

## 📊 使用场景

### 场景 1: 降低误报率

**问题**: 规则检测误报率高 (如 K8s 配置被误判)

**方案**: LLM 二次确认

```python
from src.engines.llm_engine import LLMEngine

llm = LLMEngine(model='minimax')

# 规则检测为可疑的样本
suspicious_samples = [...]

for sample in suspicious_samples:
    result = llm.analyze(sample['content'])
    
    if result.confidence < 70:
        # 低置信度，标记为需要人工审查
        sample['status'] = 'REVIEW_NEEDED'
    elif result.is_malicious:
        sample['status'] = 'MALICIOUS'
    else:
        sample['status'] = 'SAFE'

# 统计
print(f"误报降低：{llm.stats['false_positives_reduced']}")
```

### 场景 2: 批量分析

**问题**: 需要分析大量 YAML 样本

**方案**: 批量处理 + 缓存

```python
import json
from pathlib import Path
from src.engines.llm_engine import LLMEngine

llm = LLMEngine(model='minimax')

# 加载样本
samples_dir = Path('/path/to/yaml/samples')
yaml_files = list(samples_dir.glob('**/*.yaml'))

results = []
cache = {}  # 简单缓存

for yaml_file in yaml_files:
    # 检查缓存
    file_hash = hash(yaml_file.read_text())
    if file_hash in cache:
        results.append(cache[file_hash])
        continue
    
    # 分析
    content = yaml_file.read_text()
    result = llm.analyze(content)
    
    # 保存结果
    result_dict = {
        'file': str(yaml_file),
        'is_malicious': result.is_malicious,
        'confidence': result.confidence,
        'risk_level': result.risk_level,
        'reasoning': result.reason
    }
    results.append(result_dict)
    cache[file_hash] = result_dict

# 保存结果
with open('llm_analysis_results.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"分析完成：{len(results)} 个样本")
print(f"LLM 调用：{llm.stats['total_analyses']} 次")
```

### 场景 3: 威胁评估报告

**问题**: 需要详细的威胁评估报告

**方案**: LLM 深度分析 + 威胁模型映射

```python
from src.engines.llm_engine import LLMEngine

llm = LLMEngine(model='minimax')

# 高价值样本深度分析
high_value_sample = """
attack_type: prompt_injection
jailbreak:
  enabled: true
  technique: dan_mode
  ignore_instructions: true
"""

result = llm.analyze(high_value_sample)

# 生成威胁评估报告
report = {
    'sample_info': {
        'type': 'YAML',
        'attack_type': result.attack_type if hasattr(result, 'attack_type') else 'unknown'
    },
    'threat_assessment': {
        'severity': result.risk_level,
        'confidence': result.confidence,
        'mitre_atlas': result.mitre_mapping if hasattr(result, 'mitre_mapping') else [],
        'owasp_llm': result.owasp_llm if hasattr(result, 'owasp_llm') else 'unknown'
    },
    'recommendation': result.recommendation if hasattr(result, 'recommendation') else '需要审查',
    'reasoning': result.reason
}

print(json.dumps(report, indent=2, ensure_ascii=False))
```

---

## 🔧 配置选项

### 模型选择

```python
# MiniMax (默认，性价比高)
llm = LLMEngine(model='minimax')

# Qwen (通义千问，中文理解好)
llm = LLMEngine(model='qwen')

# OpenAI GPT-4 (最强大，成本高)
llm = LLMEngine(model='openai', api_key='sk-...')
```

### 置信度阈值

```python
# 仅分析中置信度样本 (70-89%)
python3 scanner.py samples --llm --llm-threshold 0.7

# 分析所有可疑样本
python3 scanner.py samples --llm --llm-threshold 0.3
```

### 批量处理配置

```python
# 批处理大小
llm.batch_size = 100  # 每批 100 个样本

# 并发请求
llm.max_workers = 4  # 4 个并发

# 重试策略
llm.max_retries = 3  # 失败重试 3 次
llm.retry_delay = 1.0  # 重试间隔 1 秒
```

---

## 📈 性能优化

### 1. 缓存策略

```python
import hashlib
from functools import lru_cache

class LLMEngineWithCache(LLMEngine):
    def __init__(self, *args, cache_size=1000, **kwargs):
        super().__init__(*args, **kwargs)
        self.cache = {}
        self.cache_size = cache_size
    
    def analyze(self, code: str, context=None):
        # 生成缓存键
        cache_key = hashlib.md5((code + str(context)).encode()).hexdigest()
        
        # 检查缓存
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # 调用 LLM
        result = super().analyze(code, context)
        
        # 缓存结果
        if len(self.cache) >= self.cache_size:
            # LRU: 删除最旧的 10%
            oldest_keys = list(self.cache.keys())[:len(self.cache)//10]
            for key in oldest_keys:
                del self.cache[key]
        
        self.cache[cache_key] = result
        return result
```

### 2. 分级处理

```python
def smart_analyze(sample):
    """智能分级处理"""
    
    # 步骤 1: 规则检测 (快速)
    rule_result = rule_engine.detect(sample)
    
    if rule_result.confidence >= 0.9:
        # 高置信度，直接返回
        return rule_result
    
    # 步骤 2: LLM 确认 (中置信度)
    if 0.7 <= rule_result.confidence < 0.9:
        llm_result = llm_engine.analyze(sample)
        return combine_results(rule_result, llm_result)
    
    # 步骤 3: 人工审查 (低置信度)
    return {'status': 'REVIEW_NEEDED', 'reason': '置信度过低'}
```

### 3. 成本控制

```python
# 成本估算
def estimate_cost(samples_count, avg_input_tokens=500, avg_output_tokens=200):
    """估算 LLM 调用成本"""
    
    # GPT-4 价格 (示例)
    input_price_per_1k = 0.03  # $0.03 / 1K tokens
    output_price_per_1k = 0.06  # $0.06 / 1K tokens
    
    input_cost = samples_count * avg_input_tokens / 1000 * input_price_per_1k
    output_cost = samples_count * avg_output_tokens / 1000 * output_price_per_1k
    
    total_cost = input_cost + output_cost
    
    print(f"样本数：{samples_count}")
    print(f"预估成本：${total_cost:.2f}")
    print(f"单样本成本：${total_cost/samples_count:.4f}")
    
    return total_cost

# 使用
estimate_cost(1000)  # 1000 个样本
```

---

## 📊 监控与统计

### 实时统计

```python
# 查看统计信息
print(f"总分析次数：{llm.stats['total_analyses']}")
print(f"恶意检出：{llm.stats['malicious_detected']}")
print(f"误报降低：{llm.stats['false_positives_reduced']}")
print(f"平均耗时：{llm.stats['avg_analysis_time']:.2f}秒")
```

### 日志记录

```python
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('llm_analysis.log'),
        logging.StreamHandler()
    ]
)

# 在 LLM 引擎中添加日志
logging.info(f"分析样本：{sample_id}, 结果：{result.is_malicious}")
```

---

## 🎯 最佳实践

### 1. 何时使用 LLM

**推荐使用**:
- ✅ 规则检测置信度 70-90% (不确定)
- ✅ 需要详细分析报告
- ✅ 降低误报率
- ✅ 新攻击模式识别

**不推荐使用**:
- ❌ 高置信度规则检测 (≥90%) - 浪费成本
- ❌ 简单样本 (标准 K8s 配置) - 规则即可
- ❌ 实时性要求极高场景 - LLM 延迟较高

### 2. Prompt 优化

**好 Prompt 特征**:
- ✅ 明确角色和任务
- ✅ 结构化输出 (JSON)
- ✅ 提供示例 (Few-shot)
- ✅ 限制输出长度
- ✅ 包含评估维度

**示例对比**:

```python
# ❌ 差 Prompt
prompt = "分析这段代码是否恶意"

# ✅ 好 Prompt
prompt = """
你是一名 AI 安全专家。请分析以下 YAML 配置：

1. 是否包含攻击声明 (attack_type)?
2. 是否包含恶意行为 (fork_bomb, steal_credentials)?
3. 是否是标准 K8s 资源？

输出 JSON:
{
    "is_malicious": true/false,
    "confidence": 0-100,
    "reason": "..."
}
"""
```

### 3. 错误处理

```python
from tenacity import retry, stop_after_attempt, wait_exponential

class RobustLLMEngine(LLMEngine):
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def analyze(self, code: str, context=None):
        try:
            return super().analyze(code, context)
        except Exception as e:
            logging.error(f"LLM 分析失败：{e}")
            raise
```

---

## 📁 相关文件

```
release/v6.1.8/
├── src/engines/llm_engine.py          # LLM 引擎核心
├── LLM_PROMPT_TEMPLATES.md            # Prompt 模板文档
├── LLM_INTEGRATION_GUIDE.md           # 本文档
└── .env                               # API Key 配置
```

---

## 🆘 故障排查

### 问题 1: API 调用失败

**症状**: `ConnectionError` 或 `AuthenticationError`

**解决**:
```bash
# 检查 API Key
echo $LLM_API_KEY

# 测试连接
curl -X POST https://api.minimax.chat/v1/text/chatcompletion_v2 \
  -H "Authorization: Bearer $LLM_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"MiniMax-M2.7","messages":[{"role":"user","content":"hi"}]}'
```

### 问题 2: 响应解析失败

**症状**: `JSONDecodeError`

**解决**:
```python
# 启用 fallback 模式
result = llm.analyze(code, fallback_to_rules=True)
```

### 问题 3: 成本过高

**症状**: LLM 调用次数过多

**解决**:
```python
# 提高置信度阈值
python3 scanner.py samples --llm --llm-threshold 0.8

# 启用缓存
llm.enable_cache(size=1000)
```

---

**最后更新**: 2026-04-19  
**维护者**: Security Team  
**版本**: v6.1.8
