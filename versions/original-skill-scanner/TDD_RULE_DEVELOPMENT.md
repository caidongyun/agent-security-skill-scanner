# 🔬 Skill Scanner - TDD 逐规则研发框架

## 一、架构设计

### 1.1 目录结构 (按 TDD 方式重组织)

```
expert_mode/
├── rules/                          # 规则目录 (按攻击类型分类)
│   ├── tool_poisoning/
│   │   ├── yara/                  # YARA 规则
│   │   │   ├── TP-YARA-001.yar
│   │   │   └── TP-YARA-002.yar
│   │   ├── runtime/               # Runtime 检测规则
│   │   │   ├── TP-RUNTIME-001.json
│   │   │   └── TP-RUNTIME-002.json
│   │   ├── sigma/                 # Sigma 规则
│   │   ├── ioc/                   # IOC 规则
│   │   └── dlp/                   # DLP 规则
│   ├── remote_load/
│   │   ├── yara/
│   │   ├── runtime/
│   │   └── ...
│   └── ...
│
├── tests/                          # 测试目录 (按攻击类型分类)
│   ├── unit/                       # 单元测试
│   │   ├── test_tool_poisoning.py
│   │   ├── test_remote_load.py
│   │   └── ...
│   ├── integration/                # 集成测试
│   └── cases/                      # 测试用例数据
│       ├── tool_poisoning.json
│       └── ...
│
├── src/                            # 源代码
│   ├── detector.py                 # 检测器核心
│   ├── rules/                      # 规则加载器
│   │   ├── yara_loader.py
│   │   ├── runtime_loader.py
│   │   └── ...
│   └── utils/
│
└── tdd_runner.py                   # TDD 运行器
```

---

## 二、TDD 工作流

### 2.1 逐规则研发流程

```bash
# 1. 选择一个规则进行开发
python3 tdd_runner.py --rule TP-RUNTIME-001

# 2. 查看规则规格
# TP-RUNTIME-001: 检测 base64 解码命令

# 3. 运行单元测试
python3 -m pytest tests/unit/test_tool_poisoning.py::test_TP_RUNTIME_001 -v

# 4. 查看结果
# ❌ FAIL: Expected detection but got None

# 5. 修复规则
# 修改 patterns: ["base64\\s+-d", "b64decode"]

# 6. 再次测试
# ✅ PASS

# 7. 提交规则
python3 tdd_runner.py --commit TP-RUNTIME-001
```

### 2.2 批量 TDD 模式

```bash
# 对整个攻击类型进行 TDD
python3 tdd_runner.py --attack-type tool_poisoning

# 输出:
# === Tool Poisoning TDD ===
# Testing TP-RUNTIME-001... ✅ PASS
# Testing TP-RUNTIME-002... ❌ FAIL (fixing...)
# Testing TP-RUNTIME-002... ✅ PASS
# ...
# Summary: 10/12 passed
```

---

## 三、单元测试设计

### 3.1 规则测试模板

```python
# tests/unit/test_tool_poisoning.py
import pytest
from src.detector import SecurityDetector

class TestToolPoisoning:
    """Tool Poisoning 规则单元测试"""
    
    @pytest.fixture
    def detector(self):
        return SecurityDetector(rules_type="runtime")
    
    # ===== TP-RUNTIME-001: base64 解码 =====
    def test_TP_RUNTIME_001_base64_d(self, detector):
        """检测 base64 -d 命令"""
        result = detector.detect("echo 'test' | base64 -d")
        assert result["detected"] == True
        assert "TP-RUNTIME-001" in result["matched_rules"]
    
    def test_TP_RUNTIME_001_b64decode(self, detector):
        """检测 b64decode 函数"""
        result = detector.detect("import base64; base64.b64decode(data)")
        assert result["detected"] == True
    
    # ===== TP-RUNTIME-002: eval/exec =====
    def test_TP_RUNTIME_002_eval(self, detector):
        """检测 eval 调用"""
        result = detector.detect("eval('os.system(\"ls\")')")
        assert result["detected"] == True
        assert result["risk_level"] == "CRITICAL"
    
    def test_TP_RUNTIME_002_exec(self, detector):
        """检测 exec 调用"""
        result = detector.detect("exec('malicious code')")
        assert result["detected"] == True
    
    # ... 更多测试
```

### 3.2 运行单元测试

```bash
# 运行所有单元测试
python3 -m pytest tests/unit/ -v

# 运行单个攻击类型
python3 -m pytest tests/unit/test_tool_poisoning.py -v

# 运行单个规则测试
python3 -m pytest tests/unit/test_tool_poisoning.py::TestToolPoisoning::test_TP_RUNTIME_001_base64_d -v

# 生成覆盖率报告
python3 -m pytest tests/unit/ --cov=src --cov-report=html
```

---

## 四、规则规格定义

### 4.1 规则元数据格式

```json
{
  "id": "TP-RUNTIME-001",
  "name": "Base64 解码检测",
  "category": "tool_poisoning",
  "type": "runtime",
  "severity": "high",
  "description": "检测 base64 解码命令和函数调用",
  "patterns": [
    "base64\\s+-d",
    "base64\\s+-D",
    "b64decode",
    "atob\\s*\\("
  ],
  "test_cases": {
    "positive": [
      "echo test | base64 -d",
      "base64.b64decode(data)",
      "atob(encoded)"
    ],
    "negative": [
      "base64.b64encode(data)",
      "base64_decode_file(input)"  # 误报示例
    ]
  },
  "risk_score": 85,
  "enabled": true
}
```

---

## 五、进度追踪

### 5.1 规则覆盖矩阵

| 攻击类型 | 规则类型 | 规则数 | 通过 | 失败 | 覆盖率 |
|----------|----------|--------|------|------|--------|
| tool_poisoning | runtime | 10 | 8 | 2 | 80% |
| tool_poisoning | yara | 5 | 5 | 0 | 100% |
| remote_load | runtime | 8 | - | - | 0% |
| ... | ... | ... | ... | ... | ... |

### 5.2 TDD 报告

```bash
$ python3 tdd_runner.py --report

=== TDD 进度报告 ===
生成时间: 2026-03-17 23:30

| 攻击类型   | 总规则 | 通过 | 失败 | 阻塞 |
|------------|--------|------|------|------|
| tool_poisoning | 15 | 12 | 3 | 0 |
| remote_load | 12 | 0 | 0 | 12 |
| data_exfil | 10 | 0 | 0 | 10 |
| prompt_injection | 8 | 0 | 0 | 8 |
| resource_exhaustion | 6 | 0 | 0 | 6 |
| memory_pollution | 5 | 0 | 0 | 5 |
| supply_chain | 4 | 0 | 0 | 4 |

总计: 60 规则 | 12 通过 | 3 失败 | 45 阻塞
检测率: 20% | 目标: 95%
```

---

## 六、快速开始

```bash
cd expert_mode

# 1. 查看可用规则
python3 tdd_runner.py --list

# 2. 运行单个规则 TDD
python3 tdd_runner.py --rule TP-RUNTIME-001

# 3. 运行攻击类型 TDD
python3 tdd_runner.py --attack-type tool_poisoning

# 4. 运行所有单元测试
python3 -m pytest tests/unit/ -v

# 5. 生成报告
python3 tdd_runner.py --report
```

---

## 七、优势对比

| 方式 | 优点 | 缺点 |
|------|------|------|
| **TDD 逐规则** | 精细控制、易定位问题、保证质量 | 需要更多测试代码 |
| 全量测试 | 一次运行全部 | 问题难以定位、不知道哪个规则失败 |

**结论**: TDD 更加适合规则研发！
