# 全量编程语言扩展计划

**版本**: v2.0  
**创建时间**: 2026-03-25  
**目标**: 覆盖多平台热点编程语言

---

## 📊 2026 语言热度调研

### TIOBE 排行榜 (2026-03)

| 排名 | 语言 | 份额 | 趋势 |
|------|------|------|------|
| 1 | Python | 28.5% | ↑ |
| 2 | C | 12.3% | ↓ |
| 3 | C++ | 11.8% | → |
| 4 | Java | 10.2% | ↓ |
| 5 | C# | 7.5% | ↑ |
| 6 | JavaScript | 6.8% | → |
| 7 | Go | 4.2% | ↑↑ |
| 8 | Rust | 3.5% | ↑↑ |
| 9 | PHP | 2.8% | ↓ |
| 10 | Swift | 2.5% | ↑ |

### GitHub Octoverse (2025)

| 排名 | 语言 | 开发者使用率 |
|------|------|-------------|
| 1 | JavaScript | 68% |
| 2 | Python | 55% |
| 3 | TypeScript | 42% |
| 4 | Java | 38% |
| 5 | PHP | 25% |
| 6 | C# | 24% |
| 7 | Ruby | 18% |
| 8 | Go | 17% |
| 9 | Rust | 12% |
| 10 | Swift | 10% |

### 安全领域常用语言

| 语言 | 恶意代码占比 | 攻击场景 | 优先级 |
|------|-------------|---------|--------|
| Python | 35% | 通用攻击、AI 攻击 | P0 |
| PowerShell | 18% | Windows 渗透、凭据窃取 | P0 |
| JavaScript | 15% | Web 攻击、供应链投毒 | P0 |
| Bash/Shell | 12% | Linux 渗透、C2 脚本 | P0 |
| Go | 8% | 跨平台恶意软件、C2 | P1 |
| PHP | 5% | WebShell、后门 | P1 |
| Ruby | 3% | 漏洞利用脚本 | P2 |
| Rust | 2% | 高级持久化、免杀 | P1 |
| Swift | 1% | macOS 恶意软件 | P2 |
| BAT/VBS | 1% | Windows 传统攻击 | P2 |

---

## 🎯 扩展目标

### Phase 2 (本周) - 4 种核心语言

| 语言 | 样本数 | 规则数 | 攻击场景 | 优先级 |
|------|--------|--------|---------|--------|
| Python | 100 | 25 | 通用攻击 | ✅ 已完成 |
| PowerShell | 100 | 20 | Windows 渗透 | P0 |
| JavaScript | 100 | 20 | Web/供应链 | P0 |
| Bash | 100 | 15 | Linux 渗透 | P0 |

**小计**: 400 样本 + 80 规则

---

### Phase 3 (下周) - 4 种进阶语言

| 语言 | 样本数 | 规则数 | 攻击场景 | 优先级 |
|------|--------|--------|---------|--------|
| Go | 80 | 15 | 跨平台 C2 | P1 |
| PHP | 80 | 15 | WebShell | P1 |
| Rust | 60 | 12 | 高级持久化 | P1 |
| Ruby | 60 | 10 | 漏洞利用 | P2 |

**小计**: 280 样本 + 52 规则

---

### Phase 4 (后续) - 6 种扩展语言

| 语言 | 样本数 | 规则数 | 攻击场景 | 优先级 |
|------|--------|--------|---------|--------|
| Swift | 50 | 10 | macOS 恶意软件 | P2 |
| TypeScript | 50 | 10 | Node.js 攻击 | P2 |
| BAT (Batch) | 50 | 8 | Windows 传统 | P2 |
| VBS (VBScript) | 50 | 8 | Windows 脚本 | P2 |
| Perl | 40 | 6 | 传统脚本 | P3 |
| AppleScript | 30 | 5 | macOS 自动化 | P3 |

**小计**: 270 样本 + 47 规则

---

## 📈 总计目标

| 阶段 | 语言数 | 样本数 | 规则数 | 周期 |
|------|--------|--------|--------|------|
| Phase 2 | 4 | 400 | 80 | 1 周 |
| Phase 3 | 4 | 280 | 52 | 1 周 |
| Phase 4 | 6 | 270 | 47 | 1 周 |
| **总计** | **14** | **950** | **179** | **3 周** |

---

## 🏗️ 架构设计

### 统一生成器架构

```
generators/
├── base_generator.py       # 基础类 (语言无关)
├── python_generator.py     # Python 生成器 ✅
├── powershell_generator.py # PowerShell 生成器
├── javascript_generator.py # JavaScript 生成器
├── bash_generator.py       # Bash 生成器
├── go_generator.py         # Go 生成器
├── php_generator.py        # PHP 生成器
├── rust_generator.py       # Rust 生成器
└── ruby_generator.py       # Ruby 生成器
```

### 统一模板结构

```
templates/
├── python/
│   ├── data_exfil.template
│   ├── code_exec.template
│   └── ...
├── powershell/
│   ├── credential_theft.template
│   ├── persistence.template
│   └── ...
├── javascript/
│   ├── supply_chain.template
│   ├── web_attack.template
│   └── ...
└── ...
```

### 统一 CLI 接口

```bash
# 单语言生成
python3 -m generators.cli --language python --count 100
python3 -m generators.cli --language powershell --count 100
python3 -m generators.cli --language javascript --count 100

# 全量生成
python3 -m generators.cli --all-languages --count 100

# 指定语言列表
python3 -m generators.cli --languages python,powershell,go --count 100
```

---

## 🔧 实施计划

### Week 1: Phase 2 (4 种核心语言)

#### Day 1-2: PowerShell
- [ ] 创建 PowerShell 生成器
- [ ] 编写 10 个模板 (Windows 场景)
- [ ] 生成 100 个样本
- [ ] 生成 20 条 YARA 规则
- [ ] 扫描验证

**攻击场景**:
- 凭据窃取 (Mimikatz 集成)
- 持久化 (注册表/任务计划)
- 横向移动 (WMI/PSRemoting)
- 防御规避 (AMSI 绕过)
- 数据外传

#### Day 3-4: JavaScript
- [ ] 创建 JavaScript 生成器
- [ ] 编写 10 个模板 (Web/供应链)
- [ ] 生成 100 个样本
- [ ] 生成 20 条 YARA 规则
- [ ] 扫描验证

**攻击场景**:
- 供应链投毒 (npm 包)
- Web 后门
- 浏览器攻击
- Node.js 恶意模块
- 数据窃取

#### Day 5: Bash
- [ ] 创建 Bash 生成器
- [ ] 编写 8 个模板 (Linux 场景)
- [ ] 生成 100 个样本
- [ ] 生成 15 条 YARA 规则
- [ ] 扫描验证

**攻击场景**:
- Linux 持久化 (cron/systemd)
- 网络侦察
- C2 通信
- 数据打包外传
- 横向移动 (SSH)

#### Day 6-7: 整合与测试
- [ ] 统一 CLI 接口
- [ ] 批量生成测试
- [ ] 质量门禁验证
- [ ] 文档完善

---

### Week 2: Phase 3 (4 种进阶语言)

#### Day 1-3: Go
- [ ] 创建 Go 生成器
- [ ] 编写 8 个模板
- [ ] 生成 80 个样本
- [ ] 生成 15 条规则

**特点**: 跨平台编译、静态链接、免杀

#### Day 4-5: PHP
- [ ] 创建 PHP 生成器
- [ ] 编写 8 个模板
- [ ] 生成 80 个样本
- [ ] 生成 15 条规则

**特点**: WebShell、服务器后门

#### Day 6-7: Rust
- [ ] 创建 Rust 生成器
- [ ] 编写 6 个模板
- [ ] 生成 60 个样本
- [ ] 生成 12 条规则

**特点**: 内存安全、高性能、免杀

---

### Week 3: Phase 4 (6 种扩展语言)

#### Day 1-2: Swift + TypeScript
- Swift: macOS 专用
- TypeScript: Node.js 类型安全攻击

#### Day 3-4: BAT + VBS
- 传统 Windows 脚本
- 企业环境常见

#### Day 5-6: Perl + AppleScript
- Perl: 传统脚本
- AppleScript: macOS 自动化

#### Day 7: 总结与文档
- 全量测试
- 性能优化
- 文档完善

---

## 📊 预期成果

### 样本库规模

| 语言 | 样本数 | 攻击类型 | 变体数 |
|------|--------|---------|--------|
| Python | 100 | 10 | 10/类型 |
| PowerShell | 100 | 8 | 12/类型 |
| JavaScript | 100 | 8 | 12/类型 |
| Bash | 100 | 6 | 16/类型 |
| Go | 80 | 5 | 16/类型 |
| PHP | 80 | 5 | 16/类型 |
| Rust | 60 | 4 | 15/类型 |
| Ruby | 60 | 4 | 15/类型 |
| Swift | 50 | 4 | 12/类型 |
| TypeScript | 50 | 4 | 12/类型 |
| BAT | 50 | 4 | 12/类型 |
| VBS | 50 | 4 | 12/类型 |
| Perl | 40 | 3 | 13/类型 |
| AppleScript | 30 | 3 | 10/类型 |
| **总计** | **950** | **72** | **~13/类型** |

### 规则库规模

| 规则类型 | 数量 | 覆盖语言 |
|---------|------|---------|
| 通用检测 | 20 | 全部 |
| 语言特定 | 100 | 各语言 |
| 攻击类型 | 50 | 跨语言 |
| 行为检测 | 9 | 高级 |
| **总计** | **179** | **14 语言** |

---

## 🎯 质量目标

| 指标 | Phase 2 | Phase 3 | Phase 4 | 最终目标 |
|------|---------|---------|---------|---------|
| 检测率 | ≥95% | ≥96% | ≥97% | ≥98% |
| 误报率 | <5% | <4% | <3% | <2% |
| 样本质量 | ≥80 | ≥82 | ≥85 | ≥88 |
| 规则质量 | ≥85 | ≥88 | ≥90 | ≥92 |

---

## 🚀 立即开始

### 下一步行动

**从 PowerShell 开始** (Windows 环境最常用攻击语言)

```bash
# 1. 创建 PowerShell 生成器
mkdir -p generators templates/powershell

# 2. 编写模板 (10 个)
# - credential_theft
# - persistence
# - lateral_movement
# - defense_evasion
# - data_exfil

# 3. 生成样本
python3 -m generators.cli --language powershell --count 100

# 4. 生成规则
python3 rules/generator.py --samples output/samples/powershell --output output/rules

# 5. 扫描验证
python3 scanner/integration_scanner.py --rules output/rules --samples output/samples/powershell
```

---

## 📚 参考资料

- MITRE ATT&CK: https://attack.mitre.org/
- OWASP Top 10: https://owasp.org/www-project-top-ten/
- GitHub Security Lab: https://securitylab.github.com/
- VirusShare: https://virusshare.com/
- MalwareBazaar: https://bazaar.abuse.ch/

---

**全量语言覆盖，打造最全面的安全样本库！** 🎯
