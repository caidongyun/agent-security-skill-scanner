# Lean Harness 整合计划

**来源**: https://clawhub.ai/aznikline/lean-claude-code-harness  
**整合时间**: 2026-04-02  
**目标**: 构建简洁、可审计的自动化研发体系

---

## 📐 核心设计原则

### 原则 1: 冻结运行时边界

**当前状态**: ✅ 80% 符合

**已有**:
- `ros-health-daemon` - 主守护进程
- `orchestrator.py` - 主编排器

**待改进**:
```python
# 入口层应该只负责:
# 1. 解析命令
# 2. 加载配置
# 3. 连接服务
# 4. 输出结果

# 不应该:
# - 包含业务逻辑
# - 混合配置加载和执行逻辑
```

**行动项**:
- [ ] 重构 `orchestrator.py` 入口层
- [ ] 分离配置加载和业务逻辑
- [ ] 添加入口层文档

---

### 原则 2: 配置优先级明确

**当前状态**: ❌ 0% (需要实现)

**目标架构**:
```
配置优先级 (从低到高):
1. defaults        - 默认配置 (代码中)
2. user config     - 用户配置 (~/.config/auto-rd/)
3. project config  - 项目配置 (项目根目录)
4. local config    - 本地配置 (.local/)
5. env overrides   - 环境变量覆盖
```

**实现计划**:
```python
# config/loader.py
class ConfigLoader:
    def load(self):
        config = {}
        
        # 1. 默认配置
        config.update(self.load_defaults())
        
        # 2. 用户配置
        config.update(self.load_user_config())
        
        # 3. 项目配置
        config.update(self.load_project_config())
        
        # 4. 本地配置
        config.update(self.load_local_config())
        
        # 5. 环境变量覆盖
        config.update(self.load_env_overrides())
        
        return config
        
    def trace_value(self, key):
        """追踪配置值来源"""
        # 返回配置值的来源路径
        pass
```

**行动项**:
- [ ] 创建 `config/loader.py`
- [ ] 实现配置加载器
- [ ] 添加配置追踪功能
- [ ] 编写配置文档

---

### 原则 3: 执行前权限检查

**当前状态**: ❌ 0% (需要实现)

**权限模型**:
```
权限级别:
- read_only    - 只读操作 (默认)
- write        - 写操作 (需要授权)
- shell        - Shell 执行 (需要授权)
- admin        - 管理员权限 (稀有)

执行流程:
1. 接收任务
2. 检查权限级别
3. 验证当前模式
4. 执行或拒绝
```

**实现计划**:
```python
# permissions/gatekeeper.py
class PermissionGatekeeper:
    MODES = {
        'default': ['read_only'],
        'plan': ['read_only'],
        'execute': ['read_only', 'write'],
        'admin': ['read_only', 'write', 'shell', 'admin'],
    }
    
    def check_permission(self, tool, required_permission):
        """检查权限"""
        current_mode = self.get_current_mode()
        allowed = self.MODES[current_mode]
        
        if required_permission not in allowed:
            raise PermissionError(
                f"工具 {tool} 需要权限 {required_permission}, "
                f"当前模式 {current_mode} 只允许 {allowed}"
            )
            
        return True
```

**行动项**:
- [ ] 创建 `permissions/` 目录
- [ ] 实现权限检查器
- [ ] 定义工具权限标签
- [ ] 集成到主编排器

---

### 原则 4: 小型工具集

**当前状态**: ✅ 90% 符合

**默认工具集**:
```
核心工具 (已有):
- list_files      ✅
- read_file       ✅
- scan            ✅ (ros-scanner-v2)
- generate_sample ✅ (security-sample-generator)
- build_rule      ✅ (yara-rule-builder)
- run_test        ✅ (ros_test.py)
- generate_report ✅ (progress_reporter)
- release         ✅ (prepare_release.py)

不添加的工具:
- 复杂 UI 工具
- 远程调用工具
- 遥测工具
```

**行动项**:
- [ ] 文档化现有工具集
- [ ] 添加工具注册表
- [ ] 定义工具添加标准

---

### 原则 5: 技能文件化

**当前状态**: ✅ 100% 符合

**已有**:
- `skills/*/SKILL.md` - 技能定义文件
- 自动发现机制

**行动项**:
- [ ] 添加技能元数据验证
- [ ] 技能索引生成

---

### 原则 6: 会话持久化

**当前状态**: ✅ 60% (部分实现)

**已有**:
- `logs/` - 日志目录
- `reports/` - 报告目录
- `progress_reporter.py` - 进度汇报

**待改进**:
```python
# 每次运行应该保存:
{
  "session_id": "uuid",
  "timestamp": "ISO8601",
  "prompt": "用户输入",
  "tool_steps": [
    {"tool": "scan", "args": {...}, "result": {...}},
    ...
  ],
  "final_response": {...}
}
```

**行动项**:
- [ ] 创建 `sessions/` 目录
- [ ] 实现会话记录器
- [ ] 添加会话查询功能

---

### 原则 7: 查询循环可见

**当前状态**: ✅ 70%

**已有循环**:
```
接收任务 → 分析 → 执行 → 验证 → 汇报
```

**待改进**:
- [ ] 添加循环流程图
- [ ] 实现循环追踪
- [ ] 添加调试模式

---

## 📋 快速审计清单

根据 Lean Harness 的 6 个审计问题:

| 问题 | 当前答案 | 目标 |
|------|----------|------|
| 配置优先级能否无需读 3 个文件就解释清楚？ | ❌ 否 | ✅ 是 |
| 工具执行前是否检查权限？ | ❌ 否 | ✅ 是 |
| 能否在一个屏幕内列出所有内置工具？ | ✅ 是 | ✅ 是 |
| 技能是否从可见文件发现？ | ✅ 是 | ✅ 是 |
| 每次运行是否保存记录？ | 🟡 部分 | ✅ 是 |
| 能否从记忆中追踪查询循环？ | 🟡 部分 | ✅ 是 |

**当前评分**: 3/6 ✅ (50%)  
**目标评分**: 6/6 ✅ (100%)

---

## 🚀 实施优先级

### P0 (本周)
1. ✅ 技能文件化 (已有)
2. ⏳ 配置加载器实现
3. ⏳ 会话持久化增强

### P1 (下周)
4. ⏳ 权限检查器实现
5. ⏳ 入口层重构
6. ⏳ 查询循环追踪

### P2 (下下周)
7. ⏳ 工具注册表
8. ⏳ 循环流程图
9. ⏳ 完整文档

---

## 📊 整合进度

```
Lean Harness 整合进度

原则 1: 冻结边界     [████████░░] 80%
原则 2: 配置明确     [░░░░░░░░░░] 0%
原则 3: 权限检查     [░░░░░░░░░░] 0%
原则 4: 小型工具集   [█████████░] 90%
原则 5: 技能文件化   [██████████] 100%
原则 6: 会话持久化   [██████░░░░] 60%
原则 7: 循环可见     [███████░░░] 70%

整体进度：[█████░░░░░] 50%
```

---

**下一步**: 实施 P0 优先级任务 (配置加载器 + 会话持久化)
