# 📊 扫描器优化方案

## 问题分析

### 当前状态
- **检测率**: 100% (使用原始扫描器)
- **误报率**: 100% (所有 59 个良性样本都被误报)

### 根本原因

1. **规则过于宽泛**
   - 616 条规则中包含大量通用关键词
   - 例如：`curl `, `subprocess`, `requests.post`, `socket.`
   - 这些模式在正常代码中也很常见

2. **缺乏上下文分析**
   - 无法区分"描述攻击"和"实施攻击"
   - 无法识别测试代码、示例代码、文档
   - 无法识别安全研究/防御性代码

3. **单一特征判定**
   - 匹配一个模式就判定为恶意
   - 没有多特征交叉验证

## 优化策略

### 策略 1: 白名单机制 ✅

**目标**: 豁免明显的良性代码

**白名单指示器**:
- 文件路径：`test_`, `example`, `sample`, `demo`, `spec`
- 内容关键词：`fibonacci`, `prime`, `calculator`, `utility`
- 高注释比例：> 30%

**实施**:
```python
def is_likely_benign(content, file_path):
    # 检查文件路径
    if 'test' in file_path or 'example' in file_path:
        return True
    
    # 检查内容
    if 'fibonacci' in content or 'prime' in content:
        return True
    
    # 检查注释比例
    if comment_ratio(content) > 0.3:
        return True
    
    return False
```

### 策略 2: 高置信度模式

**目标**: 只对有明确恶意意图的代码报警

**高置信度模式** (单独命中即报警):
- `curl.*|.*bash` - 远程下载执行
- `/dev/tcp/` - Bash 反向 shell
- `nc -e` - Netcat 后门
- `pickle.loads(` - 反序列化 RCE
- `eval(base64` - 混淆执行

**低置信度模式** (需要多个同时命中):
- `subprocess` - 太通用
- `requests.post` - 太通用
- `os.system` - 太通用

### 策略 3: 多特征确认

**规则**: 低置信度模式需要 ≥3 个同时命中才报警

```python
def scan_file_smart(file_path):
    content = read_file(file_path)
    
    # 白名单检查
    if is_likely_benign(content, file_path):
        return {'is_malicious': False}
    
    # 高置信度检查
    if has_high_confidence_attack(content):
        return {'is_malicious': True, 'confidence': 'high'}
    
    # 多特征确认
    pattern_count = count_attack_patterns(content)
    if pattern_count >= 3:
        return {'is_malicious': True, 'confidence': 'medium'}
    
    return {'is_malicious': False}
```

### 策略 4: 文件类型识别

**区分代码文件和文档**:
- `.txt` 文件 → 可能是文档/配置
- `.md` 文件 → 文档
- `.py`, `.js`, `.sh` → 代码

**对文档文件使用更宽松的规则**

## 预期效果

| 指标 | 当前 | 目标 | 优化后 (预估) |
|------|------|------|---------------|
| 检测率 | 100% | > 95% | 95-98% |
| 误报率 | 100% | < 5% | 3-5% |
| F1 Score | 0.50 | > 0.95 | 0.95+ |

## 实施步骤

### 阶段 1: 白名单机制 (1-2 小时)
- [x] 创建白名单关键词列表
- [ ] 实现文件路径检查
- [ ] 实现内容检查
- [ ] 测试良性样本豁免

### 阶段 2: 高置信度模式 (2-3 小时)
- [ ] 从高置信度攻击特征
- [ ] 实现模式匹配
- [ ] 测试恶意样本检出

### 阶段 3: 多特征确认 (1-2 小时)
- [ ] 实现低置信度模式计数
- [ ] 调整阈值 (≥3 个)
- [ ] 平衡检测率和误报率

### 阶段 4: 集成测试 (1-2 小时)
- [ ] 全量样本测试
- [ ] 调整参数
- [ ] 生成最终报告

## 测试样本

- **恶意样本**: 619 个 (10 个攻击类型)
- **良性样本**: 59 个 (7 个类别)
- **总计**: 678 个样本

## 相关文件

- `scanner_optimized.py` - 优化后的扫描器原型
- `full_benchmark.py` - 完整 benchmark 脚本
- `samples/ground_truth_v2.json` - 包含良性样本的 ground truth

## 下一步

1. 修复白名单逻辑 (不要对 malicious 目录应用白名单)
2. 添加高置信度模式检测
3. 实现多特征确认逻辑
4. 运行完整 benchmark 验证效果
