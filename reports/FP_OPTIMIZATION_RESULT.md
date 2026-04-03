# 误报优化结果

**时间**: 2026-04-02 11:20  
**状态**: ✅ 误报率降至 0%，需恢复检测率

---

## 📊 优化前后对比

| 指标 | 优化前 | 优化后 | 变化 |
|------|--------|--------|------|
| **检测率** | 100% | 91.1% | ⬇️ -8.9% |
| **误报率** | 26.7% | **0.0%** | ⬇️ -100% ✅ |
| **FP 数量** | 4,241 | **0** | -4,241 ✅ |
| **FN 数量** | 0 | 4,307 | ⬆️ +4,307 |

---

## ✅ 优化内容

**修复的规则**: `Shell_ReverseShell_Python`

**原规则**:
```yara
strings:
    $py1 = "python -c 'import socket"
    $py2 = "python3 -c 'import socket"
    $py3 = "python -c \"import socket"
    $subprocess = "subprocess"  ← 太宽泛
condition:
    $py1 or $py2 or $py3 or $subprocess  ← 误报源头
```

**优化后**:
```yara
strings:
    $py1 = "python -c 'import socket"
    $py2 = "python3 -c 'import socket"
    $py3 = "python -c \"import socket"
    ← 移除 $subprocess
condition:
    $py1 or $py2 or $py3  ← 仅匹配明确的 Python reverse shell
```

---

## 📋 下一步：恢复检测率

### 方案 A: 添加更严格的 subprocess 规则
```yara
strings:
    $subprocess = "subprocess"
    $socket = "socket"
    $connect = "connect"
condition:
    $subprocess and $socket and $connect  ← 多条件组合
```

### 方案 B: 使用 L1+L2 组合
- L1: 高置信度规则 (当前 28 条)
- L2: 中等置信度规则 (需添加更多具体规则)

### 方案 C: 分层扫描
1. 第一层：L1 规则 (快速，0 FP)
2. 第二层：L2 规则 (需人工审查)

---

## 🎯 推荐：方案 A

**立即执行**:
1. 为 subprocess 添加多条件组合
2. 测试验证检测率恢复
3. 确保 FP 仍为 0

**目标**:
- 检测率：> 98%
- 误报率：< 1%

---

**生成时间**: 2026-04-02 11:20
