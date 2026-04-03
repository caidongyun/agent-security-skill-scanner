# 良性样本采集器 (Benign Sample Collector)

**目标**: 系统性采集良性样本，建立测试基准

---

## 📋 采集来源

### 1. 开源项目 (GitHub)
- Top 1000 Python 项目
- Top 1000 Node.js 项目
- 提取：scripts/, tools/, examples/ 目录

### 2. 包管理器
- PyPI Top 500 包
- npm Top 500 包
- 提取：示例代码、配置文件

### 3. 业务场景
- DevOps: CI/CD 配置、部署脚本
- DataScience: Jupyter Notebook、数据处理脚本
- WebDev: 后端 API、前端构建脚本
- Cloud: Terraform、K8s 配置

### 4. 对抗样本
- 基于高 FP 规则生成良性变体
- 每个规则 10-20 个变体

---

## 🎯 目标规模

| 类别 | Q2 目标 | Q3 目标 |
|------|---------|---------|
| 开源项目 | 500 | 2,000 |
| 包管理器 | 300 | 1,000 |
| 业务场景 | 150 | 500 |
| 对抗样本 | 50 | 200 |
| **总计** | **1,000** | **3,700** |

---

## 📁 目录结构

```
samples/benign/
├── opensource/          # 开源项目
│   ├── python/
│   ├── nodejs/
│   └── go/
├── packages/            # 包管理器
│   ├── pypi/
│   └── npm/
├── business/            # 业务场景
│   ├── devops/
│   ├── datascience/
│   ├── webdev/
│   └── cloud/
├── adversarial/         # 对抗样本
│   └── rule_based/
└── index.json           # 样本索引
```

---

## 🔧 使用

```bash
# 采集 GitHub 样本
python3 collect_github_samples.py --limit 500

# 采集包管理器样本
python3 collect_packages.py --source pypi --limit 300

# 生成对抗样本
python3 generate_adversarial.py --rules 10

# 生成索引
python3 generate_index.py
```

---

## 📊 质量保证

- 每个样本人工抽检 10%
- 自动去重 (SHA256)
- 元数据完整 (来源、语言、场景)
