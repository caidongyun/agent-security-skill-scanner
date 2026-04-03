# 样本生成器 v2.0 - 完整设计方案

**版本**: v2.0.0  
**创建时间**: 2026-03-25  
**目标**: 构建智能化、多语言、可扩展的恶意样本生成系统

---

## 📋 目录

1. [现状分析](#1-现状分析)
2. [设计目标](#2-设计目标)
3. [系统架构](#3-系统架构)
4. [核心模块设计](#4-核心模块设计)
5. [生成方案详解](#5-生成方案详解)
6. [规则体系设计](#6-规则体系设计)
7. [质量评估体系](#7-质量评估体系)
8. [实施路线图](#8-实施路线图)
9. [附录](#9-附录)

---

## 1. 现状分析

### 1.1 现有生成器清单

| 生成器 | 位置 | 语言 | 状态 |
|--------|------|------|------|
| `sample_generator.py` | `skills/security-sample-generator/` | Python | ✅ 可用 |
| `powershell_sample_generator.py` | `round22/` | PowerShell | ✅ 可用 |
| `variant_generator.py` | `round10/` | Python | ✅ 可用 |
| `rule_generator.py` | `round13/` | - | ✅ 可用 |

### 1.2 现有样本库统计

```
samples/
├── total: 710 个样本
├── python: ~400 个
├── javascript: ~150 个
├── shell: ~100 个
└── powershell: ~60 个
```

### 1.3 现有攻击类型覆盖

| 攻击类型 | 样本数 | 规则数 | 检测率 |
|---------|--------|--------|--------|
| 工具投毒 | 72 | 45 | 100% |
| 远程加载 | 68 | 52 | 100% |
| 数据外传 | 95 | 68 | 100% |
| 提示注入 | 54 | 38 | 100% |
| 资源耗尽 | 61 | 42 | 100% |
| 记忆污染 | 48 | 35 | 100% |
| 持久化 | 76 | 58 | 100% |
| 规避检测 | 63 | 47 | 100% |
| **总计** | **537** | **385** | **100%** |

### 1.4 痛点分析

| 痛点 | 影响 | 优先级 |
|------|------|--------|
| 变体单一 | 多样性不足，检测器易过拟合 | P0 |
| 语言覆盖少 | 仅 4 种语言，无法覆盖真实场景 | P0 |
| 无质量评估 | 无法量化样本价值 | P0 |
| 元数据缺失 | 样本不可追溯，难以分析 | P1 |
| 无对抗生成 | 无法发现检测盲区 | P1 |
| 手动测试 | 效率低，易遗漏 | P1 |
| 场景有限 | 缺少云/容器/AI 等现代场景 | P2 |

---

## 2. 设计目标

### 2.1 核心目标

```
┌─────────────────────────────────────────────────────────┐
│                    样本生成器 v2.0                       │
├─────────────────────────────────────────────────────────┤
│  🎯 多样性：变体数量提升 300%                              │
│  🌍 多语言：支持 8+ 种编程语言                             │
│  🤖 智能化：LLM 辅助生成 + 对抗性生成                       │
│  📊 可量化：完整的质量评估体系                            │
│  🔗 可追溯：完整的元数据和谱系                            │
│  ⚡ 自动化：CI/CD 集成，一键生成测试                       │
│  📈 可扩展：插件化架构，易于新增场景                      │
└─────────────────────────────────────────────────────────┘
```

### 2.2 量化指标

| 指标 | 当前值 | 目标值 | 提升 |
|------|--------|--------|------|
| 样本总数 | 710 | 3000+ | +322% |
| 支持语言 | 4 | 8+ | +100% |
| 攻击场景 | 8 | 15+ | +87% |
| 变体多样性 | 中 | 极高 | +200% |
| 生成速度 | ~1 分钟/个 | ~10 秒/个 | +6x |
| 质量评分 | 无 | 80+/100 | 新增 |
| 元数据完整度 | <20% | 100% | +400% |

---

## 3. 系统架构

### 3.1 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        Sample Generator v2.0                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   CLI 接口    │  │  Web 界面     │  │  API 服务     │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                  │                  │                   │
│         └──────────────────┼──────────────────┘                   │
│                            │                                      │
│                   ┌────────▼────────┐                             │
│                   │  编排引擎        │                             │
│                   │  (Orchestrator) │                             │
│                   └────────┬────────┘                             │
│                            │                                      │
│         ┌──────────────────┼──────────────────┐                   │
│         │                  │                  │                   │
│         ▼                  ▼                  ▼                   │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐             │
│  │ 规则生成器   │   │ 样本生成器   │   │ 评估生成器   │             │
│  │ RuleGen     │   │ SampleGen   │   │ EvalGen     │             │
│  └──────┬──────┘   └──────┬──────┘   └──────┬──────┘             │
│         │                  │                  │                   │
│         └──────────────────┼──────────────────┘                   │
│                            │                                      │
│              ┌─────────────┴─────────────┐                        │
│              │                           │                        │
│              ▼                           ▼                        │
│     ┌─────────────────┐        ┌─────────────────┐                │
│     │   基础生成器     │        │   增强生成器     │                │
│     │  BaseGenerator  │        │ EnhancedGenerator│               │
│     │  - 模板驱动      │        │  - LLM 驱动       │                │
│     │  - 规则变换      │        │  - 对抗生成      │                │
│     │  - 变体生成      │        │  - 语义保持      │                │
│     └─────────────────┘        └─────────────────┘                │
│                            │                                      │
│              ┌─────────────┴─────────────┐                        │
│              │                           │                        │
│              ▼                           ▼                        │
│     ┌─────────────────┐        ┌─────────────────┐                │
│     │   质量评估器     │        │   元数据管理器   │                │
│     │ QualityScorer   │        │ MetadataManager │                │
│     └─────────────────┘        └─────────────────┘                │
│                            │                                      │
│                            ▼                                      │
│                   ┌─────────────────┐                             │
│                   │   输出管理器     │                             │
│                   │ OutputManager   │                             │
│                   └─────────────────┘                             │
│                            │                                      │
│              ┌─────────────┴─────────────┐                        │
│              │                           │                        │
│              ▼                           ▼                        │
│     ┌─────────────────┐        ┌─────────────────┐                │
│     │   samples/      │        │   reports/      │                │
│     │   (样本库)       │        │   (报告库)       │                │
│     └─────────────────┘        └─────────────────┘                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 目录结构

```
sample-generator-v2/
├── README.md                      # 使用文档
├── setup.py                       # 安装脚本
├── requirements.txt               # 依赖清单
├── config.yaml                    # 配置文件
│
├── generators/                    # 生成器核心
│   ├── __init__.py
│   ├── base_generator.py          # 基础生成器（模板驱动）
│   ├── llm_generator.py           # LLM 增强生成器
│   ├── adversarial_generator.py   # 对抗生成器
│   ├── variant_generator.py       # 变体生成器
│   └── cross_language.py          # 跨语言移植
│
├── languages/                     # 语言支持
│   ├── __init__.py
│   ├── python.py                  # Python 生成器
│   ├── javascript.py              # JavaScript 生成器
│   ├── shell.py                   # Shell 生成器
│   ├── powershell.py              # PowerShell 生成器
│   ├── go.py                      # Go 生成器 (新增)
│   ├── rust.py                    # Rust 生成器 (新增)
│   ├── ruby.py                    # Ruby 生成器 (新增)
│   └── php.py                     # PHP 生成器 (新增)
│
├── scenarios/                     # 攻击场景
│   ├── __init__.py
│   ├── tool_poisoning.yaml        # 工具投毒
│   ├── remote_load.yaml           # 远程加载
│   ├── data_exfil.yaml            # 数据外传
│   ├── prompt_injection.yaml      # 提示注入
│   ├── resource_exhaustion.yaml   # 资源耗尽
│   ├── memory_pollution.yaml      # 记忆污染
│   ├── persistence.yaml           # 持久化
│   ├── evasion.yaml               # 规避检测
│   ├── container_escape.yaml      # 容器逃逸 (新增)
│   ├── cloud_credential.yaml      # 云凭据窃取 (新增)
│   ├── cicd_poisoning.yaml        # CI/CD 投毒 (新增)
│   ├── model_poisoning.yaml       # 模型投毒 (新增)
│   └── blockchain_attack.yaml     # 区块链攻击 (新增)
│
├── rules/                         # 规则体系
│   ├── __init__.py
│   ├── rule_templates.yaml        # 规则模板
│   ├── rule_generator.py          # 规则生成器
│   ├── yara_rules.py              # YARA 规则
│   ├── sigma_rules.py             # Sigma 规则
│   └── ioc_rules.py               # IOC 规则
│
├── quality/                       # 质量评估
│   ├── __init__.py
│   ├── scorer.py                  # 质量评分器
│   ├── metrics.py                 # 评估指标
│   └── reporter.py                # 报告生成
│
├── metadata/                      # 元数据管理
│   ├── __init__.py
│   ├── schema.yaml                # 元数据 schema
│   ├── manager.py                 # 元数据管理器
│   └── lineage.py                 # 谱系追踪
│
├── testing/                       # 自动化测试
│   ├── __init__.py
│   ├── test_runner.py             # 测试执行器
│   ├── ci_config.yaml             # CI 配置
│   └── fixtures/                  # 测试夹具
│
├── cli/                           # 命令行接口
│   ├── __init__.py
│   ├── main.py                    # CLI 入口
│   └── commands.py                # 命令定义
│
├── web/                           # Web 界面 (可选)
│   ├── __init__.py
│   ├── app.py                     # Flask 应用
│   ├── templates/                 # HTML 模板
│   └── static/                    # 静态资源
│
├── api/                           # API 服务 (可选)
│   ├── __init__.py
│   ├── server.py                  # API 服务器
│   └── endpoints.py               # API 端点
│
├── utils/                         # 工具函数
│   ├── __init__.py
│   ├── logger.py                  # 日志
│   ├── config.py                  # 配置
│   └── helpers.py                 # 辅助函数
│
└── output/                        # 输出目录 (自动生成)
    ├── samples/                   # 生成的样本
    ├── rules/                     # 生成的规则
    ├── reports/                   # 生成的报告
    └── metadata/                  # 元数据
```

---

## 4. 核心模块设计

### 4.1 基础生成器 (BaseGenerator)

**职责**: 基于模板和规则生成基础样本

```python
# generators/base_generator.py

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class AttackType(Enum):
    TOOL_POISONING = "tool_poisoning"
    REMOTE_LOAD = "remote_load"
    DATA_EXFIL = "data_exfil"
    PROMPT_INJECTION = "prompt_injection"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    MEMORY_POLLUTION = "memory_pollution"
    PERSISTENCE = "persistence"
    EVASION = "evasion"
    CONTAINER_ESCAPE = "container_escape"
    CLOUD_CREDENTIAL = "cloud_credential"
    CICD_POISONING = "cicd_poisoning"
    MODEL_POISONING = "model_poisoning"

@dataclass
class SampleConfig:
    """样本配置"""
    attack_type: AttackType
    language: str
    complexity: str  # "low", "medium", "high"
    obfuscation_level: int  # 0-5
    variant_count: int
    seed: Optional[int] = None

@dataclass
class GeneratedSample:
    """生成的样本"""
    code: str
    attack_type: AttackType
    language: str
    metadata: Dict
    quality_score: Optional[float] = None

class BaseGenerator(ABC):
    """基础生成器 - 模板驱动"""
    
    def __init__(self, config: SampleConfig):
        self.config = config
        self.templates = self._load_templates()
        self.rules = self._load_rules()
    
    @abstractmethod
    def _load_templates(self) -> Dict:
        """加载模板"""
        pass
    
    @abstractmethod
    def _load_rules(self) -> Dict:
        """加载规则"""
        pass
    
    def generate(self) -> List[GeneratedSample]:
        """生成样本"""
        samples = []
        for i in range(self.config.variant_count):
            # 1. 选择模板
            template = self._select_template()
            
            # 2. 应用变换
            code = self._apply_transformations(template)
            
            # 3. 应用混淆
            if self.config.obfuscation_level > 0:
                code = self._apply_obfuscation(code)
            
            # 4. 生成元数据
            metadata = self._generate_metadata(i)
            
            # 5. 创建样本
            sample = GeneratedSample(
                code=code,
                attack_type=self.config.attack_type,
                language=self.config.language,
                metadata=metadata
            )
            samples.append(sample)
        
        return samples
    
    def _select_template(self) -> Dict:
        """根据攻击类型选择模板"""
        templates = self.templates.get(self.config.attack_type.value, [])
        # 根据复杂度筛选
        templates = [t for t in templates if t['complexity'] == self.config.complexity]
        return random.choice(templates) if templates else self._get_default_template()
    
    def _apply_transformations(self, template: Dict) -> str:
        """应用代码变换"""
        code = template['code']
        
        # 变量重命名
        code = self._rename_variables(code)
        
        # 结构调整
        code = self._restructure(code)
        
        # 注释添加/移除
        code = self._modify_comments(code)
        
        return code
    
    def _apply_obfuscation(self, code: str, level: int = None) -> str:
        """应用混淆"""
        if level is None:
            level = self.config.obfuscation_level
        
        techniques = [
            self._string_encoding,      # 字符串编码
            self._control_flow_flatten, # 控制流扁平
            self._dead_code_insert,     # 死代码插入
            self._function_inline,      # 函数内联
            self._identifier_obfuscate, # 标识符混淆
        ]
        
        for i in range(level):
            if i < len(techniques):
                code = techniques[i](code)
        
        return code
    
    def _generate_metadata(self, variant_index: int) -> Dict:
        """生成元数据"""
        return {
            'generator': 'BaseGenerator',
            'version': '2.0.0',
            'generation_date': datetime.now().isoformat(),
            'attack_type': self.config.attack_type.value,
            'language': self.config.language,
            'complexity': self.config.complexity,
            'obfuscation_level': self.config.obfuscation_level,
            'variant_index': variant_index,
            'seed': self.config.seed,
        }
```

---

### 4.2 LLM 增强生成器 (LLMGenerator)

**职责**: 使用大语言模型生成语义保持的变体

```python
# generators/llm_generator.py

import openai  # 或本地 LLM 客户端
from typing import List, Dict
from .base_generator import BaseGenerator, GeneratedSample, SampleConfig

class LLMGenerator(BaseGenerator):
    """LLM 增强生成器 - 语义保持变换"""
    
    def __init__(self, config: SampleConfig, llm_config: Dict):
        super().__init__(config)
        self.llm_config = llm_config
        self.client = self._init_llm_client()
    
    def _init_llm_client(self):
        """初始化 LLM 客户端"""
        # 支持多种 LLM
        provider = self.llm_config.get('provider', 'openai')
        if provider == 'openai':
            return openai.OpenAI(api_key=self.llm_config['api_key'])
        elif provider == 'qwen':
            # 阿里云 Qwen
            return QwenClient(api_key=self.llm_config['api_key'])
        elif provider == 'local':
            # 本地部署的模型
            return LocalLLMClient(url=self.llm_config['url'])
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")
    
    def generate_with_llm(self, seed_sample: GeneratedSample) -> List[GeneratedSample]:
        """使用 LLM 生成变体"""
        variants = []
        
        for i in range(self.config.variant_count):
            # 构建提示词
            prompt = self._build_prompt(seed_sample.code, i)
            
            # 调用 LLM
            response = self.client.generate(
                prompt=prompt,
                max_tokens=2000,
                temperature=0.7 + (i * 0.05),  # 逐步增加随机性
            )
            
            # 解析响应
            variant_code = self._parse_response(response)
            
            # 验证语义保持
            if self._verify_semantic_equivalence(seed_sample.code, variant_code):
                metadata = seed_sample.metadata.copy()
                metadata['generator'] = 'LLMGenerator'
                metadata['variant_method'] = 'semantic_transformation'
                metadata['llm_model'] = self.llm_config['model']
                
                variant = GeneratedSample(
                    code=variant_code,
                    attack_type=seed_sample.attack_type,
                    language=seed_sample.language,
                    metadata=metadata
                )
                variants.append(variant)
        
        return variants
    
    def _build_prompt(self, code: str, variant_index: int) -> str:
        """构建 LLM 提示词"""
        transformation_types = [
            "变量重命名（保持语义）",
            "函数重构（拆分/合并）",
            "控制流重组（if/else ↔ ternary）",
            "数据结构变换（list ↔ dict）",
            "异常处理重写",
            "导入语句重组",
            "字符串操作变换",
            "循环结构变换（for ↔ while）",
        ]
        
        transformation = transformation_types[variant_index % len(transformation_types)]
        
        prompt = f"""你是一个安全研究专家。请对以下恶意代码样本进行{transformation}，生成一个功能等价但结构不同的变体。

要求：
1. 保持原有的恶意行为不变
2. 改变代码结构和表达方式
3. 使用不同的变量名和函数名
4. 可以调整代码顺序但不改变逻辑
5. 输出纯代码，不要解释

原始代码：
```{self.config.language}
{code}
```

生成的变体代码：
"""
        return prompt
    
    def _verify_semantic_equivalence(self, original: str, variant: str) -> bool:
        """验证语义等价性（简化版）"""
        # TODO: 实现更复杂的语义分析
        # 当前仅检查基本特征
        original_features = self._extract_features(original)
        variant_features = self._extract_features(variant)
        
        # 检查关键特征是否保留
        key_behaviors = ['dangerous_api', 'network_call', 'file_operation']
        for behavior in key_behaviors:
            if original_features.get(behavior) != variant_features.get(behavior):
                return False
        
        return True
    
    def _extract_features(self, code: str) -> Dict:
        """提取代码特征"""
        features = {
            'dangerous_api': self._count_dangerous_api(code),
            'network_call': 'socket' in code or 'urllib' in code or 'requests' in code,
            'file_operation': 'open(' in code or 'write(' in code,
        }
        return features
```

---

### 4.3 对抗生成器 (AdversarialGenerator)

**职责**: 与检测器对抗，生成高难度样本

```python
# generators/adversarial_generator.py

from typing import List, Tuple
from .base_generator import BaseGenerator, GeneratedSample, SampleConfig

class AdversarialGenerator(BaseGenerator):
    """对抗生成器 - 生成器 vs 检测器"""
    
    def __init__(self, config: SampleConfig, detector_interface):
        super().__init__(config)
        self.detector = detector_interface
        self.generation_history = []
    
    def generate_adversarial(self, seed_sample: GeneratedSample, 
                            max_rounds: int = 10) -> Tuple[GeneratedSample, int]:
        """
        生成能绕过检测的样本
        
        返回：(成功样本，尝试轮数)
        """
        current_sample = seed_sample
        
        for round_num in range(max_rounds):
            # 1. 尝试检测
            detection_result = self.detector.detect(current_sample.code)
            
            if not detection_result['is_malicious']:
                # 成功绕过！
                current_sample.metadata['bypass_rounds'] = round_num + 1
                current_sample.metadata['detection_score'] = detection_result.get('score', 0)
                return current_sample, round_num + 1
            
            # 2. 分析检测结果
            weak_points = self._analyze_detection(detection_result)
            
            # 3. 针对性变换
            current_sample = self._apply_targeted_transformation(
                current_sample, 
                weak_points
            )
            
            # 4. 记录历史
            self.generation_history.append({
                'round': round_num,
                'detected': True,
                'score': detection_result.get('score', 0),
            })
        
        # 达到最大轮数仍未成功
        return current_sample, max_rounds
    
    def _analyze_detection(self, detection_result: Dict) -> List[str]:
        """分析检测结果，找出被检出的原因"""
        weak_points = []
        
        if detection_result.get('rule_matches'):
            for match in detection_result['rule_matches']:
                weak_points.append(f"rule:{match['rule_id']}")
        
        if detection_result.get('ml_score', 0) > 0.5:
            weak_points.append("ml_model")
        
        if detection_result.get('feature_flags', {}).get('base64_string'):
            weak_points.append("feature:base64")
        
        return weak_points
    
    def _apply_targeted_transformation(self, sample: GeneratedSample, 
                                       weak_points: List[str]) -> GeneratedSample:
        """针对弱点应用变换"""
        code = sample.code
        
        for weak_point in weak_points:
            if weak_point.startswith("rule:"):
                rule_id = weak_point.split(":")[1]
                code = self._evade_rule(code, rule_id)
            elif weak_point == "ml_model":
                code = self._evade_ml(code)
            elif weak_point.startswith("feature:"):
                feature = weak_point.split(":")[1]
                code = self._evade_feature(code, feature)
        
        # 更新元数据
        sample.code = code
        sample.metadata['transformations_applied'] = weak_points
        return sample
    
    def _evade_rule(self, code: str, rule_id: str) -> str:
        """绕过特定规则"""
        # 根据规则 ID 选择规避策略
        evasion_strategies = {
            'YARA_001': self._split_string,
            'YARA_002': self._encode_payload,
            'SIGMA_001': self._change_api_sequence,
            # ... 更多策略
        }
        
        strategy = evasion_strategies.get(rule_id, self._generic_evasion)
        return strategy(code)
    
    def _evade_ml(self, code: str) -> str:
        """绕过 ML 模型"""
        # 调整特征分布
        code = self._add_benign_patterns(code)
        code = self._normalize_complexity(code)
        return code
    
    def _evade_feature(self, code: str, feature: str) -> str:
        """绕过特定特征检测"""
        if feature == 'base64':
            return self._replace_base64(code)
        elif feature == 'entropy':
            return self._normalize_entropy(code)
        else:
            return code
```

---

### 4.4 跨语言移植器 (CrossLanguageTranspiler)

**职责**: 将攻击逻辑从一种语言移植到另一种语言

```python
# generators/cross_language.py

from typing import Dict, List
from .base_generator import GeneratedSample, AttackType

class CrossLanguageTranspiler:
    """跨语言移植器"""
    
    def __init__(self):
        self.language_pairs = self._load_transpilation_rules()
    
    def transpile(self, source: GeneratedSample, 
                  target_language: str) -> List[GeneratedSample]:
        """
        将样本移植到目标语言
        
        例如：Python 数据外传 → PowerShell 数据外传
        """
        if source.language == target_language:
            return [source]
        
        # 获取移植规则
        rules = self._get_transpilation_rules(source.language, target_language)
        
        variants = []
        for rule in rules:
            transpiled_code = self._apply_transpilation(source.code, rule)
            
            metadata = source.metadata.copy()
            metadata['original_language'] = source.language
            metadata['transpiled_to'] = target_language
            metadata['transpilation_rule'] = rule['id']
            
            variant = GeneratedSample(
                code=transpiled_code,
                attack_type=source.attack_type,
                language=target_language,
                metadata=metadata
            )
            variants.append(variant)
        
        return variants
    
    def _load_transpilation_rules(self) -> Dict:
        """加载跨语言移植规则"""
        return {
            ('python', 'powershell'): [
                {
                    'id': 'py2ps_001',
                    'name': 'HTTP 请求移植',
                    'patterns': {
                        'requests.get': 'Invoke-WebRequest',
                        'urllib.request': 'Invoke-RestMethod',
                    }
                },
                {
                    'id': 'py2ps_002',
                    'name': '文件操作移植',
                    'patterns': {
                        'open(...).write': 'Set-Content',
                        'os.remove': 'Remove-Item',
                    }
                },
            ],
            ('python', 'javascript'): [
                {
                    'id': 'py2js_001',
                    'name': '网络请求移植',
                    'patterns': {
                        'requests.post': 'fetch(..., {method: "POST"})',
                        'socket.connect': 'net.connect',
                    }
                },
            ],
            # ... 更多语言对
        }
    
    def _get_transpilation_rules(self, source_lang: str, 
                                  target_lang: str) -> List[Dict]:
        """获取特定语言对的移植规则"""
        key = (source_lang, target_lang)
        return self.language_pairs.get(key, [])
    
    def _apply_transpilation(self, code: str, rule: Dict) -> str:
        """应用移植规则"""
        result = code
        for src_pattern, tgt_pattern in rule['patterns'].items():
            result = result.replace(src_pattern, tgt_pattern)
        return result
```

---

## 5. 生成方案详解

### 5.1 方案 A: 模板驱动生成（基础）

**适用场景**: 快速生成大量基础样本

**流程**:
```
1. 选择攻击场景模板
   ↓
2. 填充具体参数（URL、文件名、API 等）
   ↓
3. 应用基础变换（变量重命名、结构调整）
   ↓
4. 应用混淆（可选）
   ↓
5. 生成元数据
   ↓
6. 输出样本
```

**优点**:
- ✅ 速度快（~1 秒/样本）
- ✅ 可控性强
- ✅ 易于理解

**缺点**:
- ❌ 变体有限
- ❌ 容易被规则检测

**代码示例**:
```python
from generators.base_generator import BaseGenerator, SampleConfig, AttackType

config = SampleConfig(
    attack_type=AttackType.DATA_EXFIL,
    language='python',
    complexity='medium',
    obfuscation_level=2,
    variant_count=10,
)

generator = BaseGenerator(config)
samples = generator.generate()

for i, sample in enumerate(samples):
    with open(f'samples/generated/exfil_{i:03d}.py', 'w') as f:
        f.write(sample.code)
```

---

### 5.2 方案 B: LLM 增强生成（推荐）

**适用场景**: 生成高质量、多样化的变体

**流程**:
```
1. 准备种子样本
   ↓
2. 选择变换类型（变量重命名/函数重构/控制流重组等）
   ↓
3. 构建 LLM 提示词
   ↓
4. 调用 LLM 生成变体
   ↓
5. 验证语义保持
   ↓
6. 质量评分
   ↓
7. 输出合格样本
```

**优点**:
- ✅ 变体多样性极高
- ✅ 代码自然度高
- ✅ 难以被规则检测

**缺点**:
- ❌ 速度较慢（~10 秒/样本）
- ❌ 依赖 LLM 质量
- ❌ 成本较高

**配置示例**:
```yaml
# config.yaml
llm:
  provider: "qwen"  # openai / qwen / local
  model: "qwen-plus"
  api_key: "${QWEN_API_KEY}"
  temperature: 0.7
  max_tokens: 2000
  
generation:
  transformations:
    - variable_rename
    - function_refactor
    - control_flow_restructure
    - data_structure_transform
  validation:
    semantic_check: true
    quality_threshold: 70
```

---

### 5.3 方案 C: 对抗生成（高级）

**适用场景**: 发现检测盲区，提升检测器鲁棒性

**流程**:
```
1. 准备种子样本 + 检测器
   ↓
2. 第一轮：生成初始变体
   ↓
3. 检测器尝试检测
   ↓
4. 分析检出原因
   ↓
5. 针对性变换（规避检出的特征）
   ↓
6. 重复步骤 3-5，直到绕过或达到最大轮数
   ↓
7. 保存成功绕过的样本到"高难度库"
```

**优点**:
- ✅ 自动生成高难度样本
- ✅ 发现检测盲区
- ✅ 推动检测器进化

**缺点**:
- ❌ 实现复杂
- ❌ 需要检测器接口
- ❌ 计算资源消耗大

**架构示意**:
```
┌─────────────┐      样本       ┌─────────────┐
│  Generator  │ ──────────────→ │  Detector   │
│             │                 │             │
│             │ ←── 检出结果 ─── │             │
│             │                 │             │
│   变换代码   │                 │   分析弱点   │
└─────────────┘                 └─────────────┘
```

---

### 5.4 方案 D: 跨语言移植（扩展）

**适用场景**: 快速扩展语言覆盖

**流程**:
```
1. 准备源语言样本（如 Python）
   ↓
2. 解析攻击逻辑（AST 分析）
   ↓
3. 映射到目标语言 API（如 PowerShell）
   ↓
4. 生成目标语言代码
   ↓
5. 验证功能等价性
   ↓
6. 输出多语言样本
```

**支持的语言对**:
```
Python ←→ PowerShell
Python ←→ JavaScript
Python ←→ Go
Python ←→