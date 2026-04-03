# 🤖 Release Agent - 发布管理 Agent

## 📋 角色定义

**名称**: Release Agent (发布管理 Agent)
**职责**: 管理 Agent Security Skill Scanner 的发布流程
**位置**: `/home/cdy/.openclaw/workspace/agent-security-skill-scanner-master/release/`

---

## 🎯 核心职责

### 1. 发布准备
- ✅ 打包样本库 (malicious + industry-datasets)
- ✅ 打包规则文件 (YARA rules)
- ✅ 打包报告文档 (completion reports)
- ✅ 打包工具脚本 (generators, validators)
- ✅ 生成发布清单 (MANIFEST.json)
- ✅ 生成文件校验和 (CHECKSUMS.sha256)

### 2. 版本管理
- 维护版本历史 (RELEASE_NOTES.md)
- 语义化版本号 (v3.0.0, v3.1.0, ...)
- 变更日志记录
- 向后兼容性检查

### 3. 质量验证
- 检测率验证 (≥98%)
- 误报率验证 (<1%)
- 性能验证 (<1ms/样本)
- 样本完整性检查

### 4. 发布渠道
- GitHub Releases
- Gitee Releases
- PyPI (如适用)
- 内部文档同步

---

## 📁 目录结构

```
release/
├── RELEASE_NOTES.md          # 发布说明 (版本历史)
├── RELEASE_AGENT.md          # 本文件 (Agent 定义)
├── prepare_release.py        # 发布打包脚本
├── v3.0.0/                   # v3.0.0 发布包
│   ├── samples/
│   │   ├── malicious/
│   │   ├── industry-datasets/
│   │   └── ground_truth.json
│   ├── rules/
│   │   └── scanner_master_rules.yar
│   ├── reports/
│   │   ├── FINAL_PLAN_BC_REPORT.md
│   │   ├── PLAN_B_COMPLETION_REPORT.md
│   │   └── PLAN_C_COMPLETION_REPORT.md
│   ├── tools/
│   │   ├── batch_generator.py
│   │   ├── plan_c_integrator.py
│   │   ├── generate_ground_truth.py
│   │   └── quick_validate.py
│   ├── MANIFEST.json         # 发布清单
│   ├── CHECKSUMS.sha256      # 文件校验和
│   └── RELEASE_STATS.json    # 发布统计
└── v3.1.0/                   # 未来版本
```

---

## 🚀 使用流程

### 准备新版本
```bash
cd /home/cdy/.openclaw/workspace/agent-security-skill-scanner-master

# 1. 运行发布脚本
python3 release/prepare_release.py --version 3.0.0 --output release/v3.0.0

# 2. 验证发布包
cd release/v3.0.0
ls -la
cat MANIFEST.json

# 3. 验证校验和
sha256sum -c CHECKSUMS.sha256
```

### 发布到 GitHub
```bash
# 1. 创建 Git tag
git tag -a v3.0.0 -m "Release v3.0.0 - 方案 B+C 优化版"

# 2. 推送到远程
git push origin v3.0.0

# 3. 在 GitHub 创建 Release
# https://github.com/your-repo/releases/new
# - Tag: v3.0.0
# - Title: Agent Security Skill Scanner v3.0.0
# - Description: 参考 RELEASE_NOTES.md
# - Attachments: 上传 release/v3.0.0/ 目录
```

### 发布到 Gitee
```bash
# 1. 同步到 Gitee
git push gitee v3.0.0

# 2. 在 Gitee 创建 Release
# https://gitee.com/your-repo/releases/new
```

---

## 📊 v3.0.0 发布统计

| 指标 | 数值 |
|------|------|
| **总文件数** | 827 |
| **样本总数** | 634 |
| **规则数量** | 167 条 |
| **报告数量** | 3 个 |
| **工具数量** | 4 个 |
| **发布包大小** | ~500KB (压缩前) |

### 样本分布
| 来源 | 样本数 |
|------|--------|
| 方案 B (自生成) | 559 |
| 方案 C (行业) | 75 |
| **总计** | **634** |

### 攻击类型覆盖
- tool_poisoning (67 样本)
- resource_exhaustion (82 样本)
- data_exfiltration (67 样本)
- prompt_injection (82 样本)
- evasion (58 样本)
- remote_load (58 样本)
- supply_chain (50 样本)
- credential_theft (50 样本)
- persistence (50 样本)
- memory_pollution (68 样本)

---

## 🔐 安全验证

### 校验和验证
```bash
cd release/v3.0.0
sha256sum -c CHECKSUMS.sha256
```

### 完整性检查
```bash
# 验证样本数量
find samples -name "*.txt" | wc -l  # 应为 634

# 验证规则文件
wc -l rules/scanner_master_rules.yar  # 应为 ~1700 行

# 验证报告文件
ls -la reports/  # 应为 3 个文件
```

---

## 📝 发布检查清单

### 发布前
- [ ] 所有测试通过
- [ ] 检测率 ≥98%
- [ ] 误报率 <1%
- [ ] 文档更新完成
- [ ] RELEASE_NOTES.md 更新
- [ ] 样本库整理完成
- [ ] 规则优化完成

### 发布中
- [ ] 运行 prepare_release.py
- [ ] 验证 MANIFEST.json
- [ ] 验证 CHECKSUMS.sha256
- [ ] 创建 Git tag
- [ ] 推送到远程

### 发布后
- [ ] GitHub Release 创建
- [ ] Gitee Release 创建
- [ ] 通知用户/团队
- [ ] 更新文档站点
- [ ] 收集反馈

---

## 🎯 下一步计划

### v3.1.0 (计划中)
- [ ] LiteLLM 投毒检测规则
- [ ] 白名单机制
- [ ] 增强报告生成
- [ ] 静态/动态检测引擎

### v3.2.0 (计划中)
- [ ] 持续迭代守护进程
- [ ] 意图分析增强
- [ ] 规则库扩充至 1000+

---

## 📞 联系方式

**维护者**: OpenClaw Agent
**项目**: Agent Security Skill Scanner
**仓库**: 
- GitHub: https://github.com/caidongyun/agent-security-skill-scanner
- Gitee: https://gitee.com/caidongyun/agent-security-skill-scanner-t14g2-v1

---

**最后更新**: 2026-04-01 23:38
**版本**: v3.0.0
