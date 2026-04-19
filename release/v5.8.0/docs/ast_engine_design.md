# AST 引擎设计文档

**生成时间**: 2026-04-13T22:53:58.281581
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

### weak_cryptographic_key
- **文件**: weak_cryptographic_key.py
- **大小**: 5.4 KB
- **AST Visitors**: 无
- **检测内容**: 未分类

### pytorch_load
- **文件**: pytorch_load.py
- **大小**: 2.6 KB
- **AST Visitors**: 无
- **检测内容**: exec/eval

### trojansource
- **文件**: trojansource.py
- **大小**: 2.4 KB
- **AST Visitors**: 无
- **检测内容**: 未分类

### huggingface_unsafe_download
- **文件**: huggingface_unsafe_download.py
- **大小**: 5.8 KB
- **AST Visitors**: 无
- **检测内容**: 未分类

### mako_templates
- **文件**: mako_templates.py
- **大小**: 2.5 KB
- **AST Visitors**: 无
- **检测内容**: 未分类

### general_bad_file_permissions
- **文件**: general_bad_file_permissions.py
- **大小**: 3.3 KB
- **AST Visitors**: 无
- **检测内容**: exec/eval

### markupsafe_markup_xss
- **文件**: markupsafe_markup_xss.py
- **大小**: 3.6 KB
- **AST Visitors**: 无
- **检测内容**: 未分类

### try_except_pass
- **文件**: try_except_pass.py
- **大小**: 2.8 KB
- **AST Visitors**: 无
- **检测内容**: 未分类

### general_hardcoded_password
- **文件**: general_hardcoded_password.py
- **大小**: 8.6 KB
- **AST Visitors**: 无
- **检测内容**: hardcoded secrets

### hashlib_insecure_functions
- **文件**: hashlib_insecure_functions.py
- **大小**: 4.2 KB
- **AST Visitors**: 无
- **检测内容**: 未分类


---

**状态**: 设计完成
**下一步**: 实现 ASTEngine
