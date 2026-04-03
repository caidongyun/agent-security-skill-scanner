# 🤖 扫描器自治研发系统

**项目**: agent-security-skill-scanner-master  
**版本**: v1.0  
**创建时间**: 2026-04-03  
**状态**: ✅ 生产就绪

---

## 📖 简介

**扫描器自治研发系统** 是专门为 `agent-security-skill-scanner-master` 项目设计的自动规则研发系统，能够：

- 🔍 **自动分析** - 找出漏报样本
- 🛠️ **自动增强** - 针对性生成规则
- ✅ **自动验证** - 10+10 样本测试
- 📤 **自动发布** - 质量达标自动提交
- 🔄 **循环迭代** - 持续优化改进

---

## 🚀 快速开始

### 方式 1: 单次运行

```bash
cd ~/.openclaw/workspace/agent-security-skill-scanner-master
python3 auto_rd_scanner.py
```

### 方式 2: 守护进程 (推荐)

```bash
# 安装
cd ~/.openclaw/workspace/agent-security-skill-scanner-master
sudo ./install_auto_rd.sh

# 查看状态
sudo systemctl status scanner_auto_rd
```

---

## 📊 测试结果

### 首次运行结果

```
[08:53:13] Step 0: 检查扫描器状态
[08:53:13] ✅ 规则文件：544 条
[08:53:14] ✅ 扫描器正常
[08:53:14] Step 1: 分析漏报样本
[08:53:18] 发现 0 个漏报样本
[08:53:18] Step 2: 增强规则
[08:53:18] ✅ 无需增强规则
[08:53:18] Step 3: 验证测试
[08:53:23] 测试结果:
  - 恶意样本：10/10 (100.0%)
  - 良性样本：10/10 (0.0% 误报)
[08:53:23] ✅ 质量门禁通过 (DR≥95%, FP<5%)
[08:53:23] Step 4: 发布
[08:53:46] ✅ 已提交到 git
```

### 质量指标

| 指标 | 结果 | 目标 | 状态 |
|------|------|------|------|
| **检测率** | 100.0% | ≥95% | ✅ 超额完成 |
| **误报率** | 0.0% | ≤5% | ✅ 零误报 |
| **规则数** | 544 条 | - | ✅ 充足 |

---

## 📁 文件结构

```
agent-security-skill-scanner-master/
├── auto_rd_scanner.py          # 自治研发脚本 ⭐
├── auto_rd_scanner.service     # systemd 服务 ⭐
├── install_auto_rd.sh          # 安装脚本 ⭐
├── logs/
│   └── auto_rd.log             # 运行日志
├── rules/
│   └── scanner_v3/yara/
│       └── scanner_rules.yar   # 规则文件
└── reports/
    └── ultimate_v2_*.json      # 扫描报告
```

---

## ⚙️ 配置参数

编辑 `auto_rd_scanner.py`:

```python
class ScannerAutoRD:
    def __init__(self):
        self.scanner_dir = Path.home() / ".openclaw/workspace/agent-security-skill-scanner-master"
        self.sample_gen_dir = Path.home() / ".openclaw/workspace/skills/security-sample-generator"
        self.benchmark_dir = Path.home() / "Desktop/security-benchmark"
        
        # 配置参数
        self.config = {
            'min_dr': 95.0,    # 最低检测率
            'max_fp': 5.0,     # 最高误报率
            'test_mal': 10,    # 恶意样本测试数
            'test_ben': 10     # 良性样本测试数
        }
```

---

## 🔄 运行流程

```
┌─────────────────────────────────────────┐
│  自治研发开始                            │
└────────────┬────────────────────────────┘
             ↓
┌─────────────────────────────────────────┐
│  Step 0: 检查扫描器状态                 │
│    - 规则文件存在性                     │
│    - 扫描器可用性                       │
└────────────┬────────────────────────────┘
             ↓
┌─────────────────────────────────────────┐
│  Step 1: 分析漏报样本 (20 个)             │
│    - 找出检测失败的样本                 │
│    - 分析攻击类型分布                   │
└────────────┬────────────────────────────┘
             ↓
┌─────────────────────────────────────────┐
│  Step 2: 增强规则                       │
│    - 生成针对性样本                     │
│    - 重新生成规则                       │
│    - 部署到扫描器                       │
└────────────┬────────────────────────────┘
             ↓
┌─────────────────────────────────────────┐
│  Step 3: 验证测试                       │
│    - 10 个恶意样本测试                   │
│    - 10 个良性样本测试                   │
│    - 计算检测率/误报率                  │
└────────────┬────────────────────────────┘
             ↓
┌─────────────────────────────────────────┐
│  Step 4: 质量门禁                       │
│    - DR≥95% 且 FP≤5% ?                  │
│    - YES → 自动提交 git                 │
│    - NO  → 跳过发布                     │
└────────────┬────────────────────────────┘
             ↓
┌─────────────────────────────────────────┐
│  完成                                    │
└─────────────────────────────────────────┘
```

---

## 📈 监控与日志

### 日志文件

```bash
# 查看最新日志
tail -f ~/.openclaw/workspace/agent-security-skill-scanner-master/logs/auto_rd.log
```

### 系统服务状态

```bash
# 查看服务状态
sudo systemctl status scanner_auto_rd

# 查看实时日志
sudo journalctl -u scanner_auto_rd -f
```

### 扫描报告

```bash
# 查看最新扫描报告
ls -lt ~/.openclaw/workspace/agent-security-skill-scanner-master/reports/ultimate_v2_*.json | head -1 | awk '{print $NF}' | xargs cat
```

---

## 🔧 故障排查

### 问题 1: 扫描器异常

**症状**: `❌ 扫描器状态异常`

**解决**:
```bash
# 恢复规则文件
cd ~/.openclaw/workspace/agent-security-skill-scanner-master/rules/scanner_v3/yara
rm -f *.yar *.yaml
cp ~/.openclaw/workspace/skills/security-sample-generator/rules/sigma_converted.yar scanner_rules.yar
chmod 444 scanner_rules.yar
```

### 问题 2: 检测率不达标

**症状**: `⚠️ 质量门禁未达标`

**解决**:
```bash
# 手动运行分析
python3 auto_rd_scanner.py

# 查看漏报样本
cat logs/auto_rd.log | grep "FN:"
```

### 问题 3: 服务无法启动

**症状**: `systemctl start` 失败

**解决**:
```bash
# 查看错误日志
sudo journalctl -u scanner_auto_rd -n 50

# 重新安装服务
sudo ./install_auto_rd.sh
```

---

## 📊 性能指标

### 典型运行时间

| 步骤 | 耗时 |
|------|------|
| 状态检查 | ~1 秒 |
| 分析漏报 (20 样本) | ~5 秒 |
| 增强规则 | ~2 秒 |
| 验证测试 (20 样本) | ~10 秒 |
| 发布提交 | ~20 秒 |
| **总计** | **~38 秒** |

### 资源使用

| 资源 | 使用量 |
|------|--------|
| CPU | <20% (运行时) |
| 内存 | <300MB |
| 磁盘 | <5MB/次 (日志) |

---

## 🎓 最佳实践

1. **定期运行**: 建议每小时或每天运行一次
2. **监控日志**: 定期检查日志，确保正常运行
3. **质量优先**: 不要为了数量降低质量门禁
4. **备份规则**: 定期备份规则文件
5. **版本控制**: 每次发布自动提交 git

---

## 📞 支持

- **文档**: 查看本文件
- **日志**: `logs/auto_rd.log`
- **相关项目**: 
  - security-sample-generator (规则生成)
  - security-benchmark (测试样本)

---

## 📄 许可证

MIT License
