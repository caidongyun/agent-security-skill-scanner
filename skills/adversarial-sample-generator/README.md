# 对抗样本生成器 (Adversarial Sample Generator)

**目标**: 生成容易导致误报的良性样本，促进扫描器优化

---

## 📋 功能

1. **基于规则推导** - 分析 YARA 规则，生成匹配规则但实际良性的代码
2. **常见业务场景** - 生成运维/开发/数据科学等场景的良性脚本
3. **持续迭代** - 根据误报结果自动生成新的对抗样本

---

## 🎯 生成的误报类型

### 1. 运维脚本 (高 FP)
- curl/wget 下载文件
- 系统配置修改
- 日志清理
- 备份脚本

### 2. 开发工具 (高 FP)
- Python eval/exec 使用
- 动态导入
- 代码生成
- 测试框架

### 3. 数据科学 (高 FP)
- subprocess 调用
- 内存密集型操作
- 网络请求
- 文件处理

### 4. 云服务 (高 FP)
- AWS/GCP/Azure CLI
- K8s 操作
- Docker 命令
- CI/CD 脚本

---

## 🚀 使用

```bash
# 生成对抗样本
python3 generate_adversarial_samples.py --output samples/adversarial/

# 测试扫描器
python3 scanner-master/ros-scanner-v2.py samples/adversarial/

# 分析误报
python3 analyze_false_positives.py
```

---

## 📊 预期效果

- **误报样本**: 1,000+ 个
- **覆盖场景**: 20+ 业务场景
- **促进优化**: FP 降低 50%+

---

**生成时间**: 2026-04-02
