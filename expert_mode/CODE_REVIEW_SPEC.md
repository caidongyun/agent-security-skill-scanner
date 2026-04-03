# 🔍 Code Review & 单元测试规范

## 一、Code Review 角色

### 1.1 审查维度

| 维度 | 检查项 | 权重 |
|------|--------|------|
| **功能正确性** | 逻辑正确、边界处理、错误处理 | 30% |
| **代码质量** | 可读性、命名规范、复杂度 | 20% |
| **安全性** | 注入风险、权限检查、敏感数据 | 25% |
| **性能** | 时间复杂度、资源泄漏、缓存 | 15% |
| **测试覆盖** | 单元测试、边界测试 | 10% |

### 1.2 审查清单

```markdown
## Code Review 清单

### 功能正确性
- [ ] 逻辑正确，符合需求
- [ ] 边界条件处理完整
- [ ] 错误处理恰当
- [ ] 无硬编码

### 代码质量
- [ ] 命名清晰 (变量/函数/类)
- [ ] 函数单一职责
- [ ] 复杂度 < 10
- [ ] 无重复代码

### 安全性
- [ ] 无 SQL/命令注入
- [ ] 权限检查正确
- [ ] 敏感数据不泄露
- [ ] 输入验证

### 性能
- [ ] 无内存泄漏
- [ ] 循环优化
- [ ] 缓存合理

### 测试
- [ ] 单元测试覆盖
- [ ] 边界测试
- [ ] 集成测试
```

---

## 二、单元测试规范

### 2.1 测试金字塔

```
        /\
       /  \
      / E2E \        E2E (端到端) - 少量
     /--------\
    /  Integration \  集成测试 - 中量
   /----------------\
  /    Unit Tests    \  单元测试 - 大量
 /--------------------\
```

### 2.2 AAA 模式

```python
def test_example():
    # Arrange (准备)
    input_data = "malicious_code"
    detector = SecurityDetector()
    
    # Act (执行)
    result = detector.detect(input_data)
    
    # Assert (断言)
    assert result["detected"] == True
    assert result["risk_level"] == "HIGH"
```

### 2.3 测试命名规范

```python
def test_<规则ID>_<场景>_<预期>():
    """
    格式: test_{rule_id}_{scenario}_{expectation}
    
    示例:
    - test_TP_RUNTIME_001_base64_decode_should_detect
    - test_TP_RUNTIME_002_eval_execute_should_block
    """
```

### 2.4 测试覆盖要求

| 规则类型 | 最小用例数 | 场景 |
|----------|------------|------|
| Positive | 3 | 正常检测 |
| Negative | 2 | 正常放行 |
| Boundary | 2 | 边界情况 |
| Performance | 1 | 性能要求 |

---

## 三、TDD 工作流

```
1. 编写失败测试
   ↓
2. 运行测试 (必须失败)
   ↓
3. 编写最小代码通过测试
   ↓
4. 重构代码
   ↓
5. 测试全部通过
   ↓
6. 提交 + Code Review
```

---

## 四、自动化工具

### 4.1 Linting

```bash
# Python
pip install pylint flake8 black mypy

pylint your_code.py
flake8 your_code.py
black --check your_code.py
mypy your_code.py
```

### 4.2 测试覆盖

```bash
# 安装 coverage
pip install coverage

# 运行测试并生成报告
coverage run -m pytest tests/
coverage report
coverage html
```

### 4.3 CI/CD 集成

```yaml
# .github/workflows/test.yml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      
      - name: Run linting
        run: |
          pylint **/*.py
          flake8 **/*.py
      
      - name: Run tests
        run: |
          pytest tests/ --cov=src --cov-report=xml
      
      - name: Code coverage
        uses: codecov/codecov-action@v2
```

---

## 五、规则测试模板

### 5.1 完整示例

```python
"""
Tool Poisoning 规则单元测试
============================
规则: TP-RUNTIME-001 - Base64 解码检测
模式: base64\\s+-d, b64decode, atob\\s*\\(
"""

import pytest
import re
from pathlib import Path
import json


class TestToolPoisoningBase64:
    """TP-RUNTIME-001: Base64 解码检测"""
    
    @pytest.fixture
    def rule(self):
        """加载规则"""
        rule_file = Path("rules/runtime/tool_poisoning/TP-RUNTIME-001.json")
        with open(rule_file) as f:
            return json.load(f)
    
    @pytest.fixture
    def detector(self):
        """创建检测器"""
        # 模拟检测器
        class Detector:
            def __init__(self, rules):
                self.rules = rules
            
            def detect(self, input_text):
                for pattern in self.rules.get("patterns", []):
                    if re.search(pattern, input_text, re.IGNORECASE):
                        return {
                            "detected": True,
                            "risk_level": self.rules.get("severity", "HIGH"),
                            "matched": pattern
                        }
                return {"detected": False}
        
        return Detector
    
    # ===== Positive Cases (必须检测到) =====
    
    def test_base64_flag_d(self, rule, detector):
        """检测 base64 -d 命令"""
        result = detector.detect("echo test | base64 -d")
        assert result["detected"] == True
    
    def test_base64_flag_D(self, rule, detector):
        """检测 base64 -D 命令"""
        result = detector.detect("base64 -D file.txt")
        assert result["detected"] == True
    
    def test_b64decode_function(self, rule, detector):
        """检测 b64decode 函数"""
        result = detector.detect("import base64; data = base64.b64decode(encoded)")
        assert result["detected"] == True
    
    def test_atob_function(self, rule, detector):
        """检测 atob 函数"""
        result = detector.detect("decoded = atob(encoded)")
        assert result["detected"] == True
    
    # ===== Negative Cases (必须不检测) =====
    
    def test_b64encode_safe(self, rule, detector):
        """base64 编码是安全的"""
        result = detector.detect("encoded = base64.b64encode(data)")
        assert result["detected"] == False
    
    # ===== Boundary Cases (边界) =====
    
    def test_base64_in_string(self, rule, detector):
        """字符串中的 base64"""
        result = detector.detect("print('base64 is useful')")
        assert result["detected"] == False


# ===== 测试运行器 =====

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
```

---

## 六、Code Review Agent 提示词

```python
CODE_REVIEW_PROMPT = """
你是一个高级 Code Review Agent。请审查以下代码:

## 审查标准
1. 功能正确性 (30%)
2. 代码质量 (20%)
3. 安全性 (25%)
4. 性能 (15%)
5. 测试覆盖 (10%)

## 审查要求
- 指出具体问题
- 给出修复建议
- 评估风险等级

## 输出格式
```json
{
  "issues": [
    {
      "line": 10,
      "severity": "HIGH",
      "category": "SECURITY",
      "description": "...",
      "suggestion": "..."
    }
  ],
  "summary": "总体评价",
  "approved": true/false
}
```
"""
```

---

## 七、Superpowers 参考

类似 superpowers 的 AI 开发工具:

| 工具 | 功能 |
|------|------|
| **Cursor** | AI 配对编程 |
| **GitHub Copilot** | 代码补全 |
| **CodeScene** | 代码分析 |
| **SonarQube** | 静态分析 |
| **Snyk** | 安全扫描 |

---

## 八、快速开始

```bash
# 1. 安装工具
pip install pytest pylint coverage black

# 2. 运行单元测试
pytest tests/unit/ -v

# 3. 代码审查
pylint your_module.py

# 4. 格式化
black your_module.py

# 5. 覆盖率
coverage run -m pytest tests/
coverage report
```

---

**总结**: Code Review + 单元测试 = 更高质量的规则！
