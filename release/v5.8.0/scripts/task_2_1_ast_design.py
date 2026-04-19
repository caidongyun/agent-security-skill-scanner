#!/usr/bin/env python3
"""
Task 2.1: AST 引擎设计
分析 Bandit 插件，设计 AST 检测方案
"""

import os
import sys
import json
import ast
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('Task2.1')

WORKSPACE_DIR = Path('/home/cdy/.openclaw/workspace/agent-security-skill-scanner-master/release/v5.8.0')
BANDIT_PLUGINS_DIR = Path.home() / '.local/lib/python*/site-packages/bandit/plugins/'
OUTPUT_FILE = WORKSPACE_DIR / 'docs' / 'ast_engine_design.md'

def analyze():
    """分析 Bandit 插件并设计 AST 引擎"""
    logger.info("📐 开始 AST 引擎设计")
    
    # 1. 查找 Bandit 插件目录
    import glob
    bandit_dirs = glob.glob(str(Path.home() / '.local/lib/python*/site-packages/bandit/plugins/'))
    
    if not bandit_dirs:
        logger.error("❌ 未找到 Bandit 插件目录")
        return None
    
    plugins_dir = Path(bandit_dirs[0])
    logger.info(f"  Bandit 插件目录：{plugins_dir}")
    
    # 2. 分析插件文件
    plugin_files = list(plugins_dir.glob('*.py'))
    logger.info(f"  发现 {len(plugin_files)} 个插件文件")
    
    # 3. 提取核心插件信息
    core_plugins = []
    for plugin_file in plugin_files[:10]:  # 分析前 10 个
        try:
            plugin_info = analyze_plugin(plugin_file)
            if plugin_info:
                core_plugins.append(plugin_info)
        except Exception as e:
            logger.warning(f"  跳过 {plugin_file.name}: {str(e)}")
    
    logger.info(f"  分析完成 {len(core_plugins)} 个核心插件")
    
    # 4. 生成设计文档
    design_doc = generate_design_doc(core_plugins)
    
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(design_doc)
    
    logger.info(f"✅ 设计文档已保存：{OUTPUT_FILE}")
    
    return {'output_file': str(OUTPUT_FILE), 'plugins_analyzed': len(core_plugins)}

def analyze_plugin(plugin_file: Path) -> dict:
    """分析单个插件"""
    with open(plugin_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取关键信息
    info = {
        'name': plugin_file.stem,
        'file': str(plugin_file.name),
        'size_kb': len(content) / 1024,
        'has_test': False,
        'ast_visitors': [],
        'checks': []
    }
    
    # 查找 AST visitor 方法
    if 'visit_' in content:
        import re
        visitors = re.findall(r'def (visit_\w+)', content)
        info['ast_visitors'] = list(set(visitors))
    
    # 查找检测内容
    if 'exec' in content.lower():
        info['checks'].append('exec/eval')
    if 'shell' in content.lower() or 'subprocess' in content.lower():
        info['checks'].append('shell injection')
    if 'password' in content.lower() or 'secret' in content.lower():
        info['checks'].append('hardcoded secrets')
    if 'sql' in content.lower():
        info['checks'].append('SQL injection')
    
    return info

def generate_design_doc(plugins: list) -> str:
    """生成 AST 引擎设计文档"""
    doc = f"""# AST 引擎设计文档

**生成时间**: {datetime.now().isoformat()}
**分析来源**: Bandit 插件

---

## 1. 核心检测能力

基于 Bandit 插件分析，AST 引擎需要支持以下检测：

### 1.1 代码执行检测
- `exec()` 调用检测
- `eval()` 调用检测
- `compile()` 调用检测

### 1.2 Shell 注入检测
- `os.system()` 调用
- `subprocess.call/run/Popen` 调用
- 参数包含用户输入

### 1.3 硬编码凭据检测
- 密码字符串
- API Key
- Token

### 1.4 SQL 注入检测
- 字符串拼接 SQL
- 格式化 SQL

---

## 2. AST 节点类型

### 2.1 Call 节点 (函数调用)
```python
class CallVisitor(ast.NodeVisitor):
    def visit_Call(self, node):
        # 检测 exec/eval/compile
        if isinstance(node.func, ast.Name):
            if node.func.id in ['exec', 'eval', 'compile']:
                self.report_issue(node, 'DANGEROUS_CALL')
        
        # 检测 os.system/subprocess
        elif isinstance(node.func, ast.Attribute):
            if node.func.attr in ['system', 'call', 'run', 'Popen']:
                self.report_issue(node, 'SHELL_INJECTION')
```

### 2.2 Import 节点 (导入)
```python
class ImportVisitor(ast.NodeVisitor):
    def visit_Import(self, node):
        for alias in node.names:
            if alias.name in ['os', 'sys', 'subprocess', 'socket']:
                self.report_issue(node, 'DANGEROUS_IMPORT')
```

### 2.3 Assign 节点 (赋值)
```python
class AssignVisitor(ast.NodeVisitor):
    def visit_Assign(self, node):
        # 检测硬编码密码
        if isinstance(node.value, ast.Constant):
            if isinstance(node.value.value, str):
                if 'password' in str(node.targets[0]).lower():
                    self.report_issue(node, 'HARDCODED_PASSWORD')
```

---

## 3. AST 引擎架构

```
┌─────────────────────────────────────┐
│  ASTEngine                          │
│  - load_rules()                     │
│  - scan(file_path, content)         │
│  - parse_ast(content)               │
│  - walk_tree(tree)                  │
│  - check_call(node)                 │
│  - check_import(node)               │
│  - check_assign(node)               │
└─────────────────────────────────────┘
         ↓
┌─────────────────────────────────────┐
│  AST Visitors                       │
│  - CallVisitor                      │
│  - ImportVisitor                    │
│  - AssignVisitor                    │
│  - AttributeVisitor                 │
└─────────────────────────────────────┘
         ↓
┌─────────────────────────────────────┐
│  Rule Matching                      │
│  - 50-100 条 AST 规则                 │
│  - 仅用于可疑文件 (Pattern 命中 2+)  │
└─────────────────────────────────────┘
```

---

## 4. 触发条件

AST 引擎仅在以下条件满足时触发：

```python
def should_use_ast(pattern_hits: int, regex_hits: int) -> bool:
    # Pattern 命中 ≥2 条
    if pattern_hits >= 2:
        return True
    
    # 正则规则命中 ≥3 条
    if regex_hits >= 3:
        return True
    
    return False
```

---

## 5. 性能目标

| 指标 | 目标 |
|------|------|
| AST 解析时间 | <1ms/file |
| 规则匹配时间 | <5ms/file |
| 仅用于可疑文件 | <5% 总文件 |
| 总体性能影响 | <10% |

---

## 6. 实施计划

### Phase 2.1: 设计 (当前)
- [x] 分析 Bandit 插件
- [x] 生成设计文档
- [ ] 确定核心检测规则

### Phase 2.2: 实现
- [ ] 创建 ASTEngine 类
- [ ] 实现 CallVisitor
- [ ] 实现 ImportVisitor
- [ ] 实现 AssignVisitor
- [ ] 实现 50-100 条 AST 规则

### Phase 2.3: 集成
- [ ] 集成到 RuleEngine
- [ ] 实现触发逻辑
- [ ] 性能优化

---

## 7. 分析的 Bandit 插件

"""
    
    for plugin in plugins:
        doc += f"""### {plugin['name']}
- **文件**: {plugin['file']}
- **大小**: {plugin['size_kb']:.1f} KB
- **AST Visitors**: {', '.join(plugin['ast_visitors']) or '无'}
- **检测内容**: {', '.join(plugin['checks']) or '未分类'}

"""
    
    doc += """
---

**状态**: 设计完成
**下一步**: 实现 ASTEngine
"""
    
    return doc

if __name__ == '__main__':
    result = analyze()
    print(json.dumps(result, indent=2) if result else "分析失败")
