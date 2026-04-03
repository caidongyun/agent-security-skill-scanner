# FakeGit 攻击情报 - AI Agent 供应链投毒

> 来源: 腾讯安全威胁情报中心 (2026-03-23)

## 攻击概述

FakeGit 是一种针对 AI Agent 的供应链投毒攻击，攻击者批量伪造开源仓库，诱骗 AI Agent 自动安装恶意工具。

## 攻击流程

```
1. 受害者向 AI Agent (如 OpenClaw) 请求工具
2. AI 自动搜索 GitHub，返回"专业"仓库
3. 用户确认安装
4. 恶意 payload 执行：
   - ptd.txt (混淆 Lua 脚本)
   - gcc.exe (合法 LuaJIT 解释器)
   - 截图 → 上传 C2
   - 下载热补丁 → 持续控制
```

## 已确认的恶意仓库矩阵

| GitHub 账号 | 仓库名 | 伪装主题 | 恶意载荷路径 |
|-------------|--------|----------|---------------|
| damiansilverado | xhs_one_spider | 社交平台爬虫 | ferryway/one-xhs-spider-v1.7.zip |
| adeelakhit | kimi-voxel | Kimi AI 引擎 | src/gpu/terrain/gpu/voxel-kimi-resistively.zip |
| sanjusathian | ai-specs | AI 开发规范 | ai-specs/.agents/ai-specs-1.5.zip |
| arashfr933 | flow2api | OpenAI API 服务 | src/core/api_flow_1.0.zip |

## 技术特征

### 1. 混淆技术

- **Lua VM 混淆**: 114KB 加密常量池 (P Table)
- **动态表索引解密**: 数百个自定义解密函数
- **无文件 PE 镂空**: Process Hollowing

### 2. 运行时行为

- **PEB 遍历**: 手动定位 DLL，绕过 IAT Hook
- **地理探测**: ip-api.com 获取受害者位置
- **截图采集**: 1920×1080 24-bit BMP
- **C2 通信**: multipart/form-data 上传

### 3. C2 基础设施

- **IP**: 213.176.73.162 (德国)
- **端点**: /api/NTE3YjdjNWU1NjYzNjU2YTA1N2Y=
- **协议**: XOR + Hex + Base64 三层加密
- **EtherHiding**: 基于 Polygon 区块链的隐藏技术

## 检测规则

### Sigma 规则: 检测恶意仓库特征

```yaml
# rules/sigma/supply_chain/fakegit-repos.yaml
id: sigma-fakegit-detection-001
name: Detect FakeGit Malicious Repository
attack_type: supply_chain_attack
severity: critical

condition: |
  (
    contains_any (file_path, ".agents/ai-specs", ".agents/", "one-xhs-spider", "kimi-voxel", "flow2api")
    and contains_any (file_path, ".zip", ".exe", "ptd.txt", "Launch.cmd")
  )
  or (
    contains_any (content, "Double-click on the application file", "This may be named https://raw.githubusercontent.com")
  )

metadata:
  author: AutoResearch
  date: 2026-03-23
  source: Tencent Security Intelligence
  technique: Supply Chain Attack, Fake Repository
```

### 样本特征检测

```yaml
# 检测 ptd.txt 混淆脚本特征
id: sigma-lua-obfuscation-001
name: Detect Obfuscated Lua Script
attack_type: malware
severity: high

condition: |
  (
    file_name == "ptd.txt"
    and size > 10000
    and contains_any (content, "WU({", "iU({", "h[", "ffi.cdef")
  )
  or (
    file_name == "gcc.exe"
    and file_size matches "2MB to 5MB"
    and not has_valid_signature
  )

metadata:
  author: AutoResearch
  tags: ["malware", "lua", "obfuscation"]
```

### 网络特征检测

```yaml
# 检测可疑 C2 通信
id: sigma-c2-communication-001
name: Detect FakeGit C2 Communication
attack_type: command_and_control
severity: critical

condition: |
  (
    network_connection to "213.176.73.162"
    and contains_any (http_request, "/api/NTE3", "multipart/form-data")
  )
  or (
    domain == "ip-api.com"
    and http_user_agent == ""
  )

metadata:
  author: AutoResearch
  mitre: T1071, T1041
```

## IoC 列表

### C2 服务器

| 类型 | 值 |
|------|-----|
| IP | 213.176.73.162 |
| 协议 | HTTPS |
| 端口 | 443 |

### 恶意文件

| 文件名 | SHA256 | 说明 |
|--------|--------|------|
| gcc.exe (原始) | a5edd208f0f92184a06b9dfb8eb5acee | LuaJIT 解释器 (合法) |
| ptd.txt | - | 混淆 Lua 侦察脚本 |
| one-xhs-spider-v1.7.zip | - | 恶意载荷 |

### GitHub 恶意仓库

- damiansilverado/xhs_one_spider
- adeelakhit/kimi-voxel
- sanjusathian/ai-specs
- arashfr933/flow2api

## 防御建议

1. **AI Agent 安全**
   - 禁止自动执行从 GitHub 下载的可执行文件
   - 验证仓库签名和完整性
   - 扫描下载的文件

2. **代码审计**
   - 检查隐藏目录 (., _)
   - 警惕 AI 生成内容的逻辑漏洞
   - 验证安装步骤的合理性

3. **网络监控**
   - 监控异常出站连接
   - 检测空 UA 的 HTTP 请求
   - 告警 multipart/form-data 上传

---
**情报来源**: 腾讯安全威胁情报中心  
**披露时间**: 2026-03-23  
**类型**: AI Agent 供应链攻击
