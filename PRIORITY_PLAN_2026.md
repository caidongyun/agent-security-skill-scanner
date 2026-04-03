# 样本生成器 v2.0 - 优先级重划 (2026-03-25)

**核心目标**: 做好样本生成器 + 规则积累  
**原则**: 小步快跑，快速迭代，先跑起来再优化

---

## 🎯 核心目标聚焦

### 唯一 KPI
```
✅ 生成 1000+ 高质量样本
✅ 积累 800+ 检测规则
✅ 检测率 ≥95%，误报率 <3%
```

### 砍掉的功能 (暂时不做)
```
❌ 复杂编排系统 (Prefect/Airflow)
❌ Web UI
❌ API 服务
❌ 多 Agent 协作
❌ 高级混淆 (多态/元攻击)
❌ 过长的语言列表 (36 种→8 种)
```

---

## 📋 简化后的优先级

### Phase 1: MVP (本周 - 3 天)

**目标**: 跑通最小闭环

```
Day 1: 基础框架
  □ Makefile 编排 (30 分钟)
  □ 样本生成器 CLI (2h)
  □ 生成 50 个 Python 样本 (1h)

Day 2: 规则生成
  □ YARA 规则生成器 (3h)
  □ 扫描器集成 (2h)
  □ 生成 100+ 规则 (1h)

Day 3: 验证迭代
  □ 检测率验证 (2h)
  □ 质量评估 (2h)
  □ 文档沉淀 (1h)
```

**交付物**:
- ✅ 50 个 Python 样本
- ✅ 100 条 YARA 规则
- ✅ 可运行的 Makefile
- ✅ 检测率报告

---

### Phase 2: 扩展 (下周 - 5 天)

**目标**: 语言 + 场景扩展

```
Day 4-5: 语言扩展
  □ PowerShell 生成器 (4h)
  □ JavaScript 生成器 (4h)
  □ Bash 生成器 (2h)
  □ 生成 200+ 样本 (2h)

Day 6-7: 场景扩展
  □ 供应链攻击场景 (4h)
  □ 云原生场景 (3h)
  □ 生成 150+ 样本 (2h)

Day 8: 规则增强
  □ Sigma 规则 (3h)
  □ ML 特征提取 (3h)
  □ 规则总数 400+ (2h)
```

**交付物**:
- ✅ 400+ 样本 (4 语言)
- ✅ 400+ 规则 (YARA+Sigma)
- ✅ 供应链/云场景覆盖

---

### Phase 3: 增强 (Week 3-4 - 10 天)

**目标**: 质量提升 + 自动化

```
Week 3: 质量提升
  □ LLM 增强生成 (8h)
  □ 混淆增强 (6h)
  □ 样本总数 800+ (4h)

Week 4: 自动化
  □ 简单调度脚本 (4h)
  □ 自动报告生成 (4h)
  □ 规则总数 800+ (8h)
```

**交付物**:
- ✅ 800+ 样本
- ✅ 800+ 规则
- ✅ 自动化流程

---

### Phase 4: 完善 (Week 5-8 - 可选)

**目标**: 按需扩展

```
□ 更多语言 (Go/Swift 等)
□ 高级混淆
□ 完整编排系统
□ Web UI
□ API 服务
```

**原则**: 看需求再决定，不预先开发

---

## 🛠️ 立即开始 - Day 1 任务

### 任务 1: Makefile (30 分钟)

```makefile
# Makefile - 样本生成器编排

.PHONY: all generate scan rules report clean

# 配置
SAMPLES_DIR := output/samples
RULES_DIR := output/rules
REPORTS_DIR := reports

# 生成 Python 样本
generate-python:
	@echo "🔨 生成 Python 样本..."
	python3 -m generators.cli --language python --count 50 --output $(SAMPLES_DIR)/python/
	@echo "✅ Python 样本完成"

# 生成所有样本 (当前仅 Python)
generate: generate-python
	@echo "✅ 所有样本生成完成"

# 扫描样本
scan: generate
	@echo "🔍 扫描样本..."
	python3 multi_language_scanner.py $(SAMPLES_DIR)/ --report --output $(REPORTS_DIR)/
	@echo "✅ 扫描完成"

# 生成规则
rules: generate
	@echo "📝 生成检测规则..."
	python3 -m rules.generator --samples $(SAMPLES_DIR)/ --output $(RULES_DIR)/
	@echo "✅ 规则生成完成"

# 生成报告
report: scan
	@echo "📊 生成报告..."
	python3 -m reports.generator --input $(REPORTS_DIR)/scan_results.json
	@echo "✅ 报告完成"

# 完整流程
all: generate scan rules report
	@echo "🎉 全部完成！"

# 清理
clean:
	@echo "🧹 清理输出目录..."
	rm -rf $(SAMPLES_DIR)/* $(RULES_DIR)/* $(REPORTS_DIR)/*
	@echo "✅ 清理完成"

# 帮助
help:
	@echo "可用命令:"
	@echo "  make generate  - 生成样本"
	@echo "  make scan      - 扫描样本"
	@echo "  make rules     - 生成规则"
	@echo "  make report    - 生成报告"
	@echo "  make all       - 完整流程"
	@echo "  make clean     - 清理"
```

**使用**:
```bash
cd agent-security-skill-scanner-master
make generate    # 生成样本
make all         # 完整流程
make help        # 查看帮助
```

---

### 任务 2: 样本生成器 CLI (2h)

```python
#!/usr/bin/env python3
# generators/cli.py

import argparse
from pathlib import Path
from generators.base_generator import BaseGenerator
from scenarios.traditional import TraditionalScenarios

def generate_samples(language: str, count: int, output_dir: str):
    """生成样本"""
    print(f"🔨 生成 {count} 个 {language} 样本...")
    
    # 创建输出目录
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 初始化生成器
    generator = BaseGenerator(language=language)
    
    # 生成样本
    samples = []
    for i in range(count):
        sample = generator.generate(
            attack_type='data_exfil',
            variation=i
        )
        
        # 保存样本
        filename = f"{language}_malicious_{i:03d}.py"
        filepath = output_path / filename
        filepath.write_text(sample.code)
        samples.append(filepath)
        
        if (i + 1) % 10 == 0:
            print(f"  已生成 {i+1}/{count} 个样本")
    
    print(f"✅ 生成 {len(samples)} 个样本 → {output_dir}/")
    return samples

def main():
    parser = argparse.ArgumentParser(description='恶意样本生成器')
    parser.add_argument('--language', '-l', default='python',
                       choices=['python', 'powershell', 'javascript', 'bash'],
                       help='目标语言')
    parser.add_argument('--count', '-c', type=int, default=50,
                       help='生成数量')
    parser.add_argument('--output', '-o', default='output/samples',
                       help='输出目录')
    
    args = parser.parse_args()
    generate_samples(args.language, args.count, args.output)

if __name__ == '__main__':
    main()
```

---

### 任务 3: 基础生成器 (2h)

```python
#!/usr/bin/env python3
# generators/base_generator.py

from pathlib import Path
import random

class BaseGenerator:
    """基础样本生成器"""
    
    def __init__(self, language: str = 'python'):
        self.language = language
        self.templates = self._load_templates()
    
    def _load_templates(self):
        """加载模板"""
        templates_dir = Path(__file__).parent / 'templates' / self.language
        templates = {}
        
        if templates_dir.exists():
            for f in templates_dir.glob('*.template'):
                name = f.stem
                templates[name] = f.read_text()
        
        return templates
    
    def generate(self, attack_type: str, variation: int = 0):
        """生成单个样本"""
        # 选择模板
        template_key = f"{attack_type}_v{variation % 3}"
        template = self.templates.get(template_key)
        
        if not template:
            template = self.templates.get(attack_type)
        
        if not template:
            # 回退到默认模板
            template = self._default_template(attack_type)
        
        # 应用变体
        code = self._apply_variation(template, variation)
        
        # 应用混淆
        code = self._apply_obfuscation(code, level=1)
        
        return MaliciousSample(
            language=self.language,
            attack_type=attack_type,
            code=code,
            metadata={
                'variation': variation,
                'template': template_key,
            }
        )
    
    def _apply_variation(self, template: str, variation: int):
        """应用变体"""
        # 变量名随机化
        var_names = ['data', 'payload', 'buffer', 'content', 'result']
        random.seed(variation)
        
        for i, name in enumerate(var_names):
            template = template.replace(f'var_{i}', name)
        
        return template
    
    def _apply_obfuscation(self, code: str, level: int):
        """应用混淆"""
        if level == 0:
            return code
        
        # Level 1: 基础混淆
        # - 插入注释
        # - 变量重命名
        # - 字符串拆分
        
        import base64
        
        # 简单示例：Base64 编码字符串
        lines = code.split('\n')
        for i, line in enumerate(lines):
            if 'sensitive_string' in line:
                encoded = base64.b64encode(
                    line.encode()
                ).decode()
                lines[i] = f"# Encoded: {encoded}"
        
        return '\n'.join(lines)
    
    def _default_template(self, attack_type: str):
        """默认模板"""
        return f"""
# {attack_type} sample
# Generated by Sample Generator v2.0

import os
import sys

def main():
    # TODO: Implement {attack_type} logic
    print("Sample executed")

if __name__ == '__main__':
    main()
"""

class MaliciousSample:
    """恶意样本表示"""
    
    def __init__(self, language, attack_type, code, metadata=None):
        self.language = language
        self.attack_type = attack_type
        self.code = code
        self.metadata = metadata or {}
    
    def save(self, filepath):
        """保存到文件"""
        Path(filepath).write_text(self.code)
    
    def __repr__(self):
        return f"MaliciousSample({self.language}, {self.attack_type})"
```

---

## 📊 成功指标

### Phase 1 (本周)
| 指标 | 目标 | 实际 |
|------|------|------|
| 样本数 | 50 | - |
| 规则数 | 100 | - |
| 检测率 | ≥90% | - |
| 运行时间 | <5 分钟 | - |

### Phase 2 (下周)
| 指标 | 目标 | 实际 |
|------|------|------|
| 样本数 | 400 | - |
| 规则数 | 400 | - |
| 检测率 | ≥95% | - |
| 语言数 | 4 | - |

### Phase 3 (Week 3-4)
| 指标 | 目标 | 实际 |
|------|------|------|
| 样本数 | 800 | - |
| 规则数 | 800 | - |
| 检测率 | ≥98% | - |
| 自动化 | 是 | - |

---

## 🚀 立即开始

```bash
cd agent-security-skill-scanner-master

# 1. 创建 Makefile (复制上面的代码)
cat > Makefile << 'EOF'
# Makefile 内容
EOF

# 2. 测试
make generate

# 3. 查看结果
ls -la output/samples/
```

---

**准备好了吗？现在开始 Day 1 第一个任务？** 🛠️
