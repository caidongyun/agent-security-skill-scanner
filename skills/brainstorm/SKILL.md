---
name: Brainstorm
version: 1.0.0
category: collaboration
author: ClawHub Community
description: 头脑风暴 Agent - 集体智慧，深度讨论
---

# Brainstorm - 头脑风暴 Agent

组织和管理头脑风暴会议，激发集体智慧，产生创新方案。

## 核心能力

1. **议题设定** - 明确讨论主题和目标
2. **参与者管理** - 邀请相关角色参与
3. **讨论引导** - 引导讨论方向，避免偏离
4. **想法收集** - 记录和整理所有想法
5. **分类整理** - 按主题/优先级分类
6. **方案评估** - 评估每个方案的可行性
7. **决策支持** - 提供决策依据和建议

## 头脑风暴流程

```
1. 议题设定 → 2. 自由发散 → 3. 想法收集 → 4. 分类整理 → 5. 方案评估 → 6. 决策建议
```

## 使用方式

```bash
# 发起头脑风暴
python3 main.py --topic "自动化研发体系架构" --participants 5 --duration 60

# 想法整理
python3 main.py --organize --input ideas.json --output organized_ideas.json

# 方案评估
python3 main.py --evaluate --ideas organized_ideas.json --criteria criteria.json
```

## 输出格式

```json
{
  "topic": "讨论主题",
  "participants": ["角色 1", "角色 2"],
  "ideas": [
    {
      "id": 1,
      "category": "架构",
      "description": "想法描述",
      "pros": ["优点 1", "优点 2"],
      "cons": ["缺点 1"],
      "feasibility": "high|medium|low",
      "priority": "P0|P1|P2",
      "effort": "small|medium|large",
    }
  ],
  "recommendations": ["建议 1", "建议 2"],
}
```

## 适用场景

- 架构设计讨论
- 技术方案选型
- 产品功能规划
- 问题解决方案
- 创新点子挖掘
