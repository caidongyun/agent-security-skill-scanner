# Phase 3 执行计划 - 进阶语言扩展

**目标**: 4 种进阶语言 (Go/PHP/Rust/Ruby)  
**时间**: 3 天 (Day 1-3)  
**质量门禁**: 每轮验证，检测率≥95%

---

## 📋 总体架构

```
Phase 3 (3 天)
├── Day 1: Go + PHP (2 语言)
│   ├── 上午：Go 生成器 + 50 样本
│   ├── 下午：PHP 生成器 + 50 样本
│   └── 晚上：质量验证 + 反思
├── Day 2: Rust + Ruby (2 语言)
│   ├── 上午：Rust 生成器 + 40 样本
│   ├── 下午：Ruby 生成器 + 40 样本
│   └── 晚上：质量验证 + 反思
└── Day 3: 全量验证 + 优化
    ├── 上午：全量扫描验证
    ├── 下午：规则优化 + 补全
    └── 晚上：Phase 3 总结 + Phase 4 计划
```

---

## 🎯 质量保障体系

### 三级质量门禁

```
每轮生成 → Gate 1 → Gate 2 → Gate 3 → 下一轮
           ↓        ↓        ↓
        样本检查  规则检查  扫描验证
```

#### Gate 1: 样本质量检查 (≥80 分)
- [x] 文件大小 (100-5000 行)
- [x] 结构完整性 (import/def/if)
- [x] 恶意模式 (≥2 indicators)
- [x] 安全性 (无危险命令)

#### Gate 2: 规则质量检查 (≥90 分)
- [x] 段落完整 (meta/strings/condition)
- [x] 字符串数量 (2-20 条)
- [x] YARA 语法有效
- [x] 元数据完整

#### Gate 3: 扫描验证 (≥95% 检测率)
- [x] 恶意样本检测率 ≥95%
- [x] 白样本误报率 <3%
- [x] 扫描速度 <10ms/样本

---

## 📅 Day 1: Go + PHP

### 上午 (9:00-12:00) - Go 生成器

| 任务 | 时间 | 输出 | 质量检查 |
|------|------|------|---------|
| Go 生成器设计 | 9:00-9:30 | `go_generator.py` | 代码审查 |
| Go 模板创建 (8 个) | 9:30-10:30 | `templates/go/` | 人工审核 |
| 生成 50 个样本 | 10:30-11:00 | `output/samples/go/` | Gate 1 |
| 生成 YARA 规则 | 11:00-11:30 | `output/rules/go_*.yar` | Gate 2 |
| 扫描验证 | 11:30-12:00 | `reports/scan_go.md` | Gate 3 |

**Go 攻击场景**:
1. C2 服务器 (跨平台)
2. 加密货币挖矿
3. DDoS 攻击
4. Rootkit
5. 数据外传
6. 横向移动
7. 持久化
8. 反调试

### 下午 (14:00-18:00) - PHP 生成器

| 任务 | 时间 | 输出 | 质量检查 |
|------|------|------|---------|
| PHP 生成器设计 | 14:00-14:30 | `php_generator.py` | 代码审查 |
| PHP 模板创建 (8 个) | 14:30-15:30 | `templates/php/` | 人工审核 |
| 生成 50 个样本 | 15:30-16:00 | `output/samples/php/` | Gate 1 |
| 生成 YARA 规则 | 16:00-16:30 | `output/rules/php_*.yar` | Gate 2 |
| 扫描验证 | 16:30-17:00 | `reports/scan_php.md` | Gate 3 |
| 反思改进 | 17:00-18:00 | `reports/day1_reflection.md` | - |

**PHP 攻击场景**:
1. WebShell (文件上传)
2. SQL 注入
3. 命令注入
4. 文件包含 (LFI/RFI)
5. XSS 生成器
6. 后门账户
7. 数据库窃取
8. 服务器侦察

### 晚上 (19:00-20:00) - Day 1 反思

```python
# 反思检查清单
reflection_checklist = {
    'go_samples': {
        'count': 50,
        'quality_pass_rate': '≥80%',
        'detection_rate': '≥95%',
        'false_positive_rate': '<3%'
    },
    'php_samples': {
        'count': 50,
        'quality_pass_rate': '≥80%',
        'detection_rate': '≥95%',
        'false_positive_rate': '<3%'
    },
    'issues_found': [],
    'improvements': []
}
```

---

## 📅 Day 2: Rust + Ruby

### 上午 (9:00-12:00) - Rust 生成器

| 任务 | 时间 | 输出 | 质量检查 |
|------|------|------|---------|
| Rust 生成器设计 | 9:00-9:30 | `rust_generator.py` | 代码审查 |
| Rust 模板创建 (6 个) | 9:30-10:30 | `templates/rust/` | 人工审核 |
| 生成 40 个样本 | 10:30-11:00 | `output/samples/rust/` | Gate 1 |
| 生成 YARA 规则 | 11:00-11:30 | `output/rules/rust_*.yar` | Gate 2 |
| 扫描验证 | 11:30-12:00 | `reports/scan_rust.md` | Gate 3 |

**Rust 攻击场景**:
1. 高级持久化 (系统服务)
2. 内存操作 (凭证窃取)
3. 跨平台 C2
4. Rootkit
5. 反分析/反调试
6. 数据加密勒索

### 下午 (14:00-18:00) - Ruby 生成器

| 任务 | 时间 | 输出 | 质量检查 |
|------|------|------|---------|
| Ruby 生成器设计 | 14:00-14:30 | `ruby_generator.py` | 代码审查 |
| Ruby 模板创建 (6 个) | 14:30-15:30 | `templates/ruby/` | 人工审核 |
| 生成 40 个样本 | 15:30-16:00 | `output/samples/ruby/` | Gate 1 |
| 生成 YARA 规则 | 16:00-16:30 | `output/rules/ruby_*.yar` | Gate 2 |
| 扫描验证 | 16:30-17:00 | `reports/scan_ruby.md` | Gate 3 |
| 反思改进 | 17:00-18:00 | `reports/day2_reflection.md` | - |

**Ruby 攻击场景**:
1. Metasploit 风格 payload
2. Rails 漏洞利用
3. 系统命令执行
4. 网络扫描
5. 数据外传
6. 持久化

### 晚上 (19:00-20:00) - Day 2 反思

```python
# 反思检查清单
reflection_checklist = {
    'rust_samples': {
        'count': 40,
        'quality_pass_rate': '≥80%',
        'detection_rate': '≥95%',
        'false_positive_rate': '<3%'
    },
    'ruby_samples': {
        'count': 40,
        'quality_pass_rate': '≥80%',
        'detection_rate': '≥95%',
        'false_positive_rate': '<3%'
    },
    'issues_found': [],
    'improvements': []
}
```

---

## 📅 Day 3: 全量验证 + 优化

### 上午 (9:00-12:00) - 全量扫描验证

| 任务 | 时间 | 输出 | 目标 |
|------|------|------|------|
| Python 样本扫描 | 9:00-9:15 | `reports/final_python.md` | ≥95% |
| PowerShell 样本扫描 | 9:15-9:30 | `reports/final_powershell.md` | ≥95% |
| JavaScript 样本扫描 | 9:30-9:45 | `reports/final_javascript.md` | ≥95% |
| Bash 样本扫描 | 9:45-10:00 | `reports/final_bash.md` | ≥95% |
| Go 样本扫描 | 10:00-10:15 | `reports/final_go.md` | ≥95% |
| PHP 样本扫描 | 10:15-10:30 | `reports/final_php.md` | ≥95% |
| Rust 样本扫描 | 10:30-10:45 | `reports/final_rust.md` | ≥95% |
| Ruby 样本扫描 | 10:45-11:00 | `reports/final_ruby.md` | ≥95% |
| 误报率测试 | 11:00-11:30 | `reports/final_fp_test.md` | <3% |
| 性能测试 | 11:30-12:00 | `reports/performance.md` | <10ms |

### 下午 (14:00-18:00) - 规则优化 + 补全

| 任务 | 时间 | 输出 | 目标 |
|------|------|------|------|
| 低检测率规则优化 | 14:00-15:00 | `rules/optimized/` | +5% 检测率 |
| 高误报规则调整 | 15:00-16:00 | `rules/optimized/` | -2% 误报率 |
| 缺失规则补全 | 16:00-17:00 | `rules/extra/` | 100% 覆盖 |
| 规则合并去重 | 17:00-17:30 | `rules/all_rules.yar` | -20% 规则数 |
| 规则索引生成 | 17:30-18:00 | `rules/index.json` | 快速检索 |

### 晚上 (19:00-20:00) - Phase 3 总结

```markdown
# Phase 3 总结报告

## 成果
- 新增语言：4 种 (Go/PHP/Rust/Ruby)
- 新增样本：180 个
- 新增规则：40 条
- 总样本：380 个 (累计)
- 总规则：80 条 (累计)

## 质量指标
- 平均检测率：≥95%
- 平均误报率：<3%
- 平均扫描速度：<10ms

## 问题与改进
- 发现的问题
- 解决方案
- 经验教训

## Phase 4 计划
- 目标语言：6 种
- 样本目标：270 个
- 规则目标：47 条
```

---

## 🔧 自动化脚本

### 1. 质量门禁脚本

```bash
#!/bin/bash
# quality_gate.sh

LANGUAGE=$1
COUNT=${2:-50}

echo "=== 质量门禁：$LANGUAGE ==="

# Gate 1: 样本生成 + 检查
echo "[Gate 1] 生成样本..."
python3 -m generators.cli --language $LANGUAGE --count $COUNT

echo "[Gate 1] 质量检查..."
python3 quality_gate/gatekeeper.py \
    --samples output/samples/$LANGUAGE \
    --output reports/quality_$LANGUAGE.json

# Gate 2: 规则生成 + 检查
echo "[Gate 2] 生成规则..."
python3 rules/generator.py --samples output/samples/$LANGUAGE --output output/rules

echo "[Gate 2] 规则检查..."
python3 quality_gate/gatekeeper.py \
    --rules output/rules \
    --output reports/quality_rules_$LANGUAGE.json

# Gate 3: 扫描验证
echo "[Gate 3] 扫描验证..."
python3 scanner/integration_scanner.py \
    --rules output/rules \
    --samples output/samples/$LANGUAGE \
    --output reports/scan_$LANGUAGE

echo "[Gate 3] 验证结果..."
python3 -c "
import json
with open('reports/scan_{}.json'.format('$LANGUAGE')) as f:
    data = json.load(f)
    rate = data['detection_rate']
    if rate >= 95:
        print('✅ 检测率：{}%'.format(rate))
    else:
        print('❌ 检测率：{}% < 95%'.format(rate))
"
```

### 2. 反思报告脚本

```bash
#!/bin/bash
# generate_reflection.sh

DATE=$1
DAY=$2

cat > reports/day${DAY}_reflection.md << EOF
# Day $DAY 反思报告

**日期**: $DATE
**语言**: $LANGUAGE

## 完成情况
- [ ] 生成器实现
- [ ] 样本生成
- [ ] 规则生成
- [ ] 质量验证

## 质量指标
| 指标 | 目标 | 实际 | 状态 |
|------|------|------|------|
| 样本数 | 50 | - | - |
| 检测率 | ≥95% | - | - |
| 误报率 | <3% | - | - |

## 遇到的问题
1. ...

## 解决方案
1. ...

## 改进建议
1. ...

## 下一步
1. ...
EOF
```

### 3. 全量验证脚本

```bash
#!/bin/bash
# full_validation.sh

echo "=== 全量验证 Phase 3 ==="

LANGUAGES="python powershell javascript bash go php rust ruby"

for lang in $LANGUAGES; do
    echo ""
    echo "=== 验证：$lang ==="
    
    python3 scanner/integration_scanner.py \
        --rules output/rules \
        --samples output/samples/$lang \
        --output reports/final_$lang
    
    # 提取检测率
    python3 -c "
import json
with open('reports/final_{}.json'.format('$lang')) as f:
    data = json.load(f)
    print('检测率：{}%'.format(data['detection_rate']))
"
done

echo ""
echo "=== 误报率测试 ==="
python3 scanner/integration_scanner.py \
    --rules output/rules \
    --samples samples/white \
    --output reports/final_fp_test
```

---

## 📊 质量追踪表

### 每日追踪

| Day | 语言 | 样本数 | 检测率 | 误报率 | 状态 |
|-----|------|--------|--------|--------|------|
| 1 | Go | 50 | - | - | ⏳ |
| 1 | PHP | 50 | - | - | ⏳ |
| 2 | Rust | 40 | - | - | ⏳ |
| 2 | Ruby | 40 | - | - | ⏳ |

### 累计追踪

| 阶段 | 语言数 | 样本数 | 规则数 | 检测率 | 误报率 | 状态 |
|------|--------|--------|--------|--------|--------|------|
| Phase 1 | 1 | 50 | 10 | 100% | 0% | ✅ |
| Phase 2 | 4 | 200 | 40 | - | - | ✅ |
| Phase 3 | 4 | 180 | 40 | ≥95% | <3% | ⏳ |
| **累计** | **9** | **430** | **90** | **≥95%** | **