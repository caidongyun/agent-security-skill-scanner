# Skill 市场采样器 (Market Sampler)

**目标**: 从国内外 Agent/Skill 市场抽样，用于生产验证

---

## 🌐 采样来源

### 国内市场
| 平台 | 类型 | 目标样本 |
|------|------|----------|
| Coze (扣子) | Bot 商店 | 100 |
| Dify | 应用市场 | 100 |
| 百炼 | 技能市场 | 100 |
| 通义灵码 | 插件 | 50 |
| 文心一言 | 插件 | 50 |

### 国外市场
| 平台 | 类型 | 目标样本 |
|------|------|----------|
| GPT Store | Apps | 200 |
| LangChain Hub | Tools | 100 |
| AutoGen Gallery | Agents | 100 |
| Zapier | Actions | 100 |
| Hugging Face | Spaces | 200 |

---

## 📁 目录结构

```
samples/market/
├── domestic/          # 国内市场
│   ├── coze/
│   ├── dify/
│   └── bailian/
├── international/     # 国际市场
│   ├── gpt_store/
│   ├── langchain/
│   └── autogen/
└── index.json         # 样本索引
```

---

## 🔧 使用

```bash
# 采样 Coze
python3 sample_coze.py --limit 100

# 采样 GPT Store
python3 sample_gpt_store.py --limit 200

# 生成索引
python3 generate_index.py
```

---

## 📊 质量保证

- 去重 (SHA256)
- 分类标注 (类型、功能、风险等级)
- 元数据完整 (来源 URL、采集时间)
