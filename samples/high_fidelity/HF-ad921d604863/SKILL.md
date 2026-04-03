# unknown

**样本 ID**: HF-ad921d604863  
**攻击类型**: 伪装/远程执行  
**严重程度**: 高  
**来源**: Koi ClawHavoc report  
**生成时间**: 2026-03-24T09:24:43.350004

## 描述
伪装更新器/安装器

## 攻击链
Prerequisites→外链安装脚本→payload

## 缓解措施
立即下架/阻断IOC/轮换凭据

## 元数据
```json
{
  "﻿skill_name": "amir",
  "source": "Koi ClawHavoc report",
  "author": "未确认",
  "published_date": "2026-02-01",
  "description": "伪装更新器/安装器",
  "evidence": "Koi 将其归入 Auto-Updaters 恶意/可疑技能清单",
  "attack_chain": "Prerequisites→外链安装脚本→payload",
  "risk_category": "伪装/远程执行",
  "impact_scope": "主机+凭据",
  "confidence": "4",
  "severity": "高",
  "mitigation": "立即下架/阻断IOC/轮换凭据"
}
```
