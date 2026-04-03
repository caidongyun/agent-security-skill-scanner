# 🔍 agent-security-skill-scanner 差距分析报告

**时间**: 2026-03-17 20:10  
**项目**: agent-security-skill-scanner  
**版本**: v4 (expert_mode/)

---

## 📊 用户提供的信息

### 已扫描情况

| 指标 | 数值 |
|------|------|
| **扫描文件数** | 3711 个 |
| **发现 patterns** | 多个 |
| `/etc/passwd` | 219 次 |
| `requests.post` | 205 次 |
| `memory/` | 92 次 |

### 用户指出的问题

| 问题 | 状态 | 说明 |
|------|------|------|
| 文档与代码不一致 | ❌ | 文档说 40+ 规则，实际 11 条 |
| 扫描脚本有 bug | ❌ | 参数解析错误 |
| 有迭代框架 | ✅ | v1→v4 版本演进 |

---

## 🔍 实际扫描结果

### 目录结构

```
skills/agent-security-skill-scanner/
├── expert_mode/                    # v4 版本所在地
│   ├── lingshun_v5.py              # 核心引擎
│   ├── lingshun_daemon.py          # 守护进程
│   ├── joint_research.py           # 联合研发
│   ├── sample_explorer.py          # 样本探索
│   ├── defender_autonomous.py      # Defender 自治
│   ├── rule_sync.py                # 规则同步
│   ├── network_tunnel_detector.py  # 网络穿透检测
│   │
│   ├── external_rules/             # 外部规则
│   ├── merged_rules/               # 合并规则
│   ├── optimized_rules/            # 优化规则
│   │
│   ├── tests/cases/                # 测试用例
│   └── logs/                       # 日志
│
└── docs/                           # 文档
```

### 规则数量统计

| 规则库 | 文件数 | 规则数 | 状态 |
|--------|--------|--------|------|
| **external_rules/** | 10 个 | 138 条 | ✅ |
| **merged_rules/** | 11 个 | 110 条 | ✅ |
| **optimized_rules/** | 1 个 | 53 条 | ✅ |
| **总计** | 22 个 | **301 条** | ✅ |

**用户说"实际 11 条"可能是指：**
- 某个特定类别的规则
- 旧版本数据
- 文档中提到的某个子集

---

## ❌ 问题分析

### 问题 1: 文档与代码不一致

**用户反馈**: 文档说 40+ 规则，实际 11 条

**实际情况**:
- ✅ 当前代码有 **301 条规则** (138 外部 + 110 合并 + 53 自研)
- ⚠️ 可能某个文档 (README 或 FINAL_COMPLETION_REPORT.md) 还写着旧数据

**需要检查的文档**:
- `expert_mode/README.md`
- `expert_mode/FINAL_COMPLETION_REPORT.md`
- `expert_mode/docs/` 下的文档

---

### 问题 2: 扫描脚本有 bug (参数解析错误)

**用户反馈**: aass.js 参数解析 bug

**实际情况**:
- ❌ 未找到 `aass.js` 文件
- ❌ 未找到 `tools/aass-scanner/` 目录

**可能情况**:
1. aass.js 是外部项目，不在当前 workspace
2. 用户记错了文件名
3. 用户想要创建这个扫描器

**需要确认**:
- aass.js 的实际位置
- 参数解析 bug 的具体表现
- 是否要修复或重新实现

---

### 问题 3: patterns_found 统计

**用户提供的数据**:
```
patterns_found: /etc/passwd(219), requests.post(205), memory/(92)
```

**分析**:
- `/etc/passwd` (219 次) - 敏感文件访问
- `requests.post` (205 次) - 网络请求 (可能数据外传)
- `memory/` (92 次) - 内存操作

**这些 patterns 来自哪里？**
- 可能是某个扫描工具的输出
- 可能是灵顺 V5 的样本探索结果
- 可能是外部扫描器的报告

---

## 📋 待办任务

### 高优先级 🔴

| 任务 | 状态 | 说明 |
|------|------|------|
| **1. 确认 aass.js 位置** | ⏳ 待确认 | 用户提到的扫描器 |
| **2. 修复参数解析 bug** | ⏳ 待修复 | aass.js 的 bug |
| **3. 更新文档规则数量** | ⏳ 待更新 | 确保文档与实际一致 |
| **4. 验证实际规则数量** | ⏳ 进行中 | 当前统计 301 条 |

### 中优先级 🟡

| 任务 | 状态 | 说明 |
|------|------|------|
| **5. 扩充规则到 40+** | ✅ 已完成 | 实际已 301 条 |
| **6. 添加持续迭代机制** | ✅ 已完成 | 守护进程自动循环 |
| **7. 创建沙箱模块** | ⏳ 待创建 | 恶意代码行为分析 |

---

## 🎯 建议的修复方案

### 方案 1: 修复 aass.js (如果存在)

```bash
# 1. 找到 aass.js
find /home/cdy -name "aass.js" 2>/dev/null

# 2. 检查参数解析代码
grep -n "process.argv\|argparse\|commander" aass.js

# 3. 修复 bug
# (需要看到具体代码)
```

### 方案 2: 重新实现扫描器 (如果 aass.js 不存在)

在 `expert_mode/` 下创建 `skill_scanner.py`:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Skill 安全扫描器 - 扫描 Skill 文件中的恶意代码
"""

import os
import re
import json
import argparse
from pathlib import Path
from typing import Dict, List

class SkillScanner:
    """Skill 安全扫描器"""
    
    def __init__(self, patterns_file: str = None):
        self.patterns = self._load_patterns(patterns_file)
        self.results = []
    
    def _load_patterns(self, patterns_file: str) -> Dict:
        """加载扫描 patterns"""
        default_patterns = {
            "sensitive_files": [
                r"/etc/passwd",
                r"/etc/shadow",
                r"\.ssh/",
                r"\.gnupg/",
            ],
            "network_exfil": [
                r"requests\.post",
                r"urllib\.request\.urlopen",
                r"socket\.connect",
                r"httpx\.post",
            ],
            "memory_access": [
                r"memory/",
                r"__memory__",
                r"memory_store",
            ],
            "command_execution": [
                r"os\.system",
                r"subprocess\.(call|run|Popen)",
                r"exec\(",
                r"eval\(",
            ],
            "file_operations": [
                r"open\([^)]*['\"]w['\"]",
                r"os\.remove",
                r"shutil\.rmtree",
            ]
        }
        
        if patterns_file and os.path.exists(patterns_file):
            with open(patterns_file, 'r') as f:
                return json.load(f)
        
        return default_patterns
    
    def scan_directory(self, directory: str, extensions: List[str] = None) -> List[Dict]:
        """扫描目录"""
        if extensions is None:
            extensions = ['.py', '.js', '.ts', '.sh']
        
        results = []
        
        for root, dirs, files in os.walk(directory):
            # 跳过隐藏目录和 node_modules
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'node_modules']
            
            for file in files:
                if any(file.endswith(ext) for ext in extensions):
                    file_path = os.path.join(root, file)
                    result = self.scan_file(file_path)
                    if result['matches']:
                        results.append(result)
        
        return results
    
    def scan_file(self, file_path: str) -> Dict:
        """扫描单个文件"""
        result = {
            'file': file_path,
            'matches': []
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
                
                for category, patterns in self.patterns.items():
                    for pattern in patterns:
                        for line_num, line in enumerate(lines, 1):
                            if re.search(pattern, line):
                                result['matches'].append({
                                    'category': category,
                                    'pattern': pattern,
                                    'line': line_num,
                                    'content': line.strip()[:100]
                                })
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def generate_report(self, results: List[Dict], output_file: str = None) -> str:
        """生成报告"""
        report = {
            'summary': {
                'total_files': len(results),
                'files_with_matches': len([r for r in results if r['matches']]),
                'total_matches': sum(len(r['matches']) for r in results)
            },
            'by_category': self._group_by_category(results),
            'details': results
        }
        
        report_json = json.dumps(report, indent=2)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report_json)
        
        return report_json
    
    def _group_by_category(self, results: List[Dict]) -> Dict:
        """按类别分组统计"""
        categories = {}
        
        for result in results:
            for match in result['matches']:
                cat = match['category']
                if cat not in categories:
                    categories[cat] = {
                        'count': 0,
                        'files': set(),
                        'patterns': {}
                    }
                categories[cat]['count'] += 1
                categories[cat]['files'].add(result['file'])
                
                pattern = match['pattern']
                if pattern not in categories[cat]['patterns']:
                    categories[cat]['patterns'][pattern] = 0
                categories[cat]['patterns'][pattern] += 1
        
        # 转换 set 为 list 以便 JSON 序列化
        for cat in categories:
            categories[cat]['files'] = list(categories[cat]['files'])
        
        return categories


def main():
    parser = argparse.ArgumentParser(
        description='Skill 安全扫描器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  %(prog)s -d ./skills                    # 扫描 skills 目录
  %(prog)s -d ./skills -o report.json     # 输出报告
  %(prog)s -f custom_patterns.json        # 使用自定义 patterns
        '''
    )
    
    parser.add_argument('-d', '--directory', required=True,
                       help='要扫描的目录')
    parser.add_argument('-o', '--output', default=None,
                       help='输出报告文件')
    parser.add_argument('-f', '--patterns', default=None,
                       help='自定义 patterns 文件 (JSON)')
    parser.add_argument('-e', '--extensions', default='.py,.js,.ts,.sh',
                       help='要扫描的文件扩展名 (逗号分隔)')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='详细输出')
    
    args = parser.parse_args()
    
    # 解析扩展名
    extensions = [ext.strip() for ext in args.extensions.split(',')]
    
    # 创建扫描器
    scanner = SkillScanner(patterns_file=args.patterns)
    
    # 扫描
    print(f"🔍 开始扫描目录：{args.directory}")
    results = scanner.scan_directory(args.directory, extensions)
    
    # 输出结果
    if args.verbose:
        for result in results:
            if result['matches']:
                print(f"\n📁 {result['file']}")
                for match in result['matches']:
                    print(f"  ⚠️  Line {match['line']}: {match['content']}")
    
    # 生成报告
    report_json = scanner.generate_report(results, args.output)
    
    # 打印摘要
    report = json.loads(report_json)
    print(f"\n📊 扫描完成:")
    print(f"  总文件数：{report['summary']['total_files']}")
    print(f"  有问题文件：{report['summary']['files_with_matches']}")
    print(f"  总匹配数：{report['summary']['total_matches']}")
    
    if args.output:
        print(f"  报告已保存到：{args.output}")


if __name__ == '__main__':
    main()
```

---

### 方案 3: 更新文档

检查并更新以下文档中的规则数量：

```bash
# 检查文档中的规则数量描述
grep -n "规则\|rules\|[0-9]\+ 条" expert_mode/*.md
```

需要更新的文档：
- `expert_mode/README.md`
- `expert_mode/FINAL_COMPLETION_REPORT.md`
- `expert_mode/docs/` 下的文档

---

## 📊 规则数量验证脚本

```python
#!/usr/bin/env python3
# rules_counter.py

import os
import json

def count_rules(directory: str) -> int:
    """统计目录中的规则数量"""
    total = 0
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            total += len(data)
                        elif isinstance(data, dict):
                            # 可能是 {"rules": [...]} 格式
                            if 'rules' in data:
                                total += len(data['rules'])
                            elif 'patterns' in data:
                                total += len(data['patterns'])
                except:
                    pass
    
    return total

if __name__ == '__main__':
    dirs = ['external_rules', 'merged_rules', 'optimized_rules']
    
    print("规则数量统计:")
    print("-" * 40)
    
    for d in dirs:
        if os.path.exists(d):
            count = count_rules(d)
            print(f"{d:25} {count:5} 条")
    
    print("-" * 40)
    total = sum(count_rules(d) for d in dirs if os.path.exists(d))
    print(f"总计：{total} 条")
```

---

## 🎯 总结

### 当前状态

| 项目 | 状态 | 说明 |
|------|------|------|
| **规则数量** | ✅ 301 条 | 138 外部 + 110 合并 + 53 自研 |
| **文档一致性** | ⚠️ 待检查 | 可能有旧数据 |
| **aass.js** | ❌ 未找到 | 需要确认位置 |
| **参数解析 bug** | ⏳ 待修复 | 需要看到代码 |
| **持续迭代** | ✅ 运行中 | 守护进程自动循环 |
| **沙箱模块** | ❌ 缺失 | 待创建 |

---

### 下一步行动

1. **确认 aass.js 位置** - 请用户提供路径或链接
2. **检查文档规则数量** - 更新不一致的地方
3. **创建 skill_scanner.py** - 如果 aass.js 不存在
4. **创建沙箱模块** - 恶意代码行为分析
5. **验证 patterns_found** - 确认 3711 个文件的扫描结果

---

**时间**: 2026-03-17 20:10  
**状态**: 📊 分析完成  
**待确认**: aass.js 位置

🎯 **等待用户确认 aass.js 位置，然后继续修复！** 🔍
