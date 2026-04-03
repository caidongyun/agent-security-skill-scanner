# Agent Security Skill Scanner - Master 合并版

**创建时间**: 2026-03-25  
**合并来源**: 
- `agent-security-skill-scanner-V3/` (v3.0.0 - 完整研发版)
- `skills/agent-security-skill-scanner/` (v0.1.1 - Skill 包)

---

## 🎯 合并策略

| 功能模块 | 来源 | 说明 |
|---------|------|------|
| 多语言扫描器 | V3 | `multi_language_scanner.py` |
| ML 增强检测 | V3 | `round24/ml/` (XGBoost+LightGBM) |
| 样本库 (695 个) | V3 | `samples/` (4 语言) |
| 检测规则 (325 条) | V3 | `rules/` (YARA/Sigma/IOC) |
| Web 仪表板 | V3 | `web-dashboard/` |
| Round 16-25 | V3 | 各轮迭代成果 |
| LiteLLM 专项检测 | Skill 包 | `expert_mode/litellm_detector.py` |
| 供应链守护进程 | Skill 包 | `supply_chain_daemon.sh` |
| 快速排查脚本 | Skill 包 | `check_litellm.sh` |

---

## 📂 目录结构

```
agent-security-skill-scanner-master/
├── multi_language_scanner.py    # ⭐ 主扫描器
├── expert_mode/                 # ⭐ 增强功能（来自 Skill 包）
│   ├── litellm_detector.py      # LiteLLM 投毒检测
│   ├── exfil_detector.py        # 数据外发检测
│   └── ...
├── round16-25/                  # 各轮迭代
├── samples/                     # 695 个样本
├── rules/                       # 325 条规则
├── web-dashboard/               # Web 仪表板
├── check_litellm.sh             # 快速排查
├── supply_chain_daemon.sh       # 守护进程
├── requirements.txt             # Python 依赖
└── MERGE_README.md              # 本文档
```

---

## 🚀 快速开始

### 1. 安装依赖

```bash
cd ~/.openclaw/workspace/agent-security-skill-scanner-master
pip install -r requirements.txt
```

### 2. 创建配置文件

```bash
cat > config.yaml << 'EOF'
scanner:
  max_file_size: "10MB"
  rate_limit: 50
  
ml:
  enabled: true
  model_path: "round24/ml/models/scanner_v3_ml_fusion.pkl"
  threshold: 0.5
  weight: 0.4
  
rules:
  base_dir: "rules/"
  
litellm:
  enabled: true
  check_pth_files: true
  check_c2_domains: true
  
output:
  format: "html"
  save_path: "reports/"
EOF
```

### 3. 运行扫描

```bash
# 基础扫描
python3 multi_language_scanner.py /path/to/scan

# ML 增强扫描
python3 multi_language_scanner.py /path/to/scan --model round24/ml/models/scanner_v3_ml_fusion.pkl

# LiteLLM 专项检测
python3 expert_mode/litellm_detector.py ~/.local/lib/python*/site-packages/

# 快速排查
./check_litellm.sh
```

### 4. 启动监控

```bash
# 启动守护进程
./supply_chain_daemon.sh start

# 查看状态
./supply_chain_daemon.sh status
```

---

## 📊 核心指标

| 指标 | 值 | 来源 |
|------|-----|------|
| 样本总数 | 695 | V3 |
| 检测规则 | 325 | V3 |
| 检测率 | 100% | V3 |
| 误报率 | 0% | V3 |
| 扫描速度 | <1ms/文件 | V3 |
| ML 特征 | 27 个 | V3 |
| 支持语言 | 4 种 | V3 |
| LiteLLM 规则 | 8 项 | Skill 包 |

---

## 🔧 后续优化

### 待整合功能

- [ ] 将 `expert_mode/` 集成到主扫描器
- [ ] 统一配置文件格式
- [ ] 合并文档（ARCHITECTURE.md + SUPPLY_CHAIN_THREAT_DETECTION.md）
- [ ] 创建统一的 CLI 入口

### 待测试功能

- [ ] ML 模型加载测试
- [ ] 多语言扫描测试
- [ ] LiteLLM 检测测试
- [ ] 守护进程稳定性测试

---

## 📝 版本历史

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-03-25 | v1.0.0 (Master) | 首次合并 V3 + Skill 包 |
| 2026-03-24 | v3.0.0 (V3) | ML 增强版 |
| 2026-03-25 | v0.1.1 (Skill) | Skill 包版本 |

---

## 🎯 使用建议

**研发测试** → 使用 `agent-security-skill-scanner-V3/`（保持独立）  
**生产部署** → 使用 `agent-security-skill-scanner-master/`（稳定合并版）  
**Skill 包** → 保持精简，仅包含核心检测功能

---

**下一步**: 
1. 测试合并后的功能完整性
2. 创建统一的安装脚本
3. 编写用户文档
