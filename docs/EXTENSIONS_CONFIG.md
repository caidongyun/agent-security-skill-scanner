# 扫描器扩展名配置

## 支持的扩展名

v6.1.9+ 支持以下文件扩展名：

### 脚本语言
- `.py`, `.python` - Python
- `.js`, `.javascript`, `.jsx` - JavaScript/React
- `.ts`, `.tsx` - TypeScript
- `.sh`, `.bash` - Shell/Bash
- `.ps1` - PowerShell
- `.rb` - Ruby
- `.php` - PHP
- `.pl`, `.pm` - Perl

### 编译语言
- `.c`, `.cpp`, `.cc` - C/C++
- `.h`, `.hpp` - C/C++ 头文件
- `.java` - Java
- `.go` - Go
- `.rs` - Rust
- `.swift` - Swift
- `.kt` - Kotlin

### 配置文件
- `.yaml`, `.yml` - YAML
- `.json` - JSON
- `.toml` - TOML
- `.ini`, `.cfg`, `.conf` - INI 配置
- `.xml` - XML

### 其他
- `.md` - Markdown
- `.txt` - 文本文件
- `.html`, `.htm` - HTML
- `.css`, `.scss`, `.less` - 样式表

## 配置方式

### 命令行参数
```bash
# 使用默认扩展名
python3 scanner.py /path/to/scan

# 自定义扩展名
python3 scanner.py /path/to/scan --extensions ".py,.js,.yaml,.json,.python,.bash"
```

### 默认配置
```python
# scanner.py line ~421
parser.add_argument('--extensions', type=str, 
    default='.py,.python,.js,.javascript,.jsx,.ts,.tsx,.sh,.bash,.ps1,.yaml,.yml,.json,.go,.rb,.php,.java,.c,.cpp,.h,.hpp',
    help='文件扩展名 (默认:20+ 种)')
```

## 性能建议

1. **只扫描必要扩展名** - 扩展名越多，扫描越慢
2. **使用 --max-files 限制** - 避免扫描过多文件
3. **使用 --workers 并发** - 推荐 8-16 workers

## Benchmark 样本兼容性

Benchmark 样本使用非标准扩展名：
- `.python` (不是 `.py`)
- `.javascript` (不是 `.js`)
- `.bash` (不是 `.sh`)
- `.go`, `.rb`, `.php` 等

v6.1.9+ 已完全兼容这些扩展名。

---

*最后更新：2026-04-21 (v6.1.9)*
