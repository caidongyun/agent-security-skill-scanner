# Agent Security Skill Scanner - 快速启动指南

**5 分钟上手** 🚀

---

## ⚡ 一键安装

```bash
cd ~/.openclaw/workspace/agent-security-skill-scanner-master
./install.sh
```

---

## 🔍 第一次扫描

### 扫描 Python 环境

```bash
# 扫描用户 Python 包
./scan.sh ~/.local/lib/python*/site-packages/

# 扫描当前目录
./scan.sh .

# 扫描指定项目
./scan.sh ~/projects/my-project/
```

### 查看结果

```
🔍 开始扫描：/path/to/scan
==========================================
扫描中... [====================] 100%

=== 检测结果 ===
总文件数：1234
可疑文件：3
威胁等级：中等

详情：reports/scan_report.html
```

---

## 🧪 测试检测能力

```bash
# 运行完整测试
./test.sh

# 查看测试报告
cat reports/test/test_report_*.md
```

**预期结果**:
- 恶意样本检出率：100%
- 良性样本误报率：0%

---

## 📖 常用命令

| 命令 | 说明 |
|------|------|
| `./scan.sh /path` | 基础扫描 |
| `./scan.sh /path --report` | 生成 HTML 报告 |
| `./scan.sh /path --quick` | 快速模式 |
| `./scan.sh /path --verbose` | 详细输出 |
| `./test.sh` | 运行测试 |
| `./install.sh` | 重新安装 |

---

## ⚙️ 配置（可选）

```bash
# 编辑配置文件
vim config.yaml

# 关键配置项：
# - ml.enabled: 是否启用 ML 增强（默认 false）
# - output.format: 报告格式（html/json/text）
# - scanner.max_workers: 并发线程数（默认 4）
```

---

## 📊 查看报告

```bash
# 查看最新报告
ls -lt reports/*.html | head -1

# 在浏览器打开
firefox reports/scan_report.html
```

---

## 🆘 常见问题

### Q: 提示找不到 Python 模块？
```bash
# 重新安装依赖
pip3 install -r requirements.txt
```

### Q: 扫描速度慢？
```bash
# 增加并发线程数（编辑 config.yaml）
scanner:
  max_workers: 8
```

### Q: 误报太多？
```bash
# 禁用 ML（如果已启用）
# 编辑 config.yaml: ml.enabled: false
```

---

## 📚 完整文档

- `README.md` - 完整使用文档
- `config.yaml.template` - 配置模板
- `docs/` - 技术文档
- `round*/` - 各轮迭代报告

---

**开始扫描**: `./scan.sh /path/to/scan` 🔍
