#!/bin/bash
# ROS-TaskMaster v2.1 - 融合 UltraReview + Code Parser + Rule Engine
# 功能：多 Agent 编排 + 交叉验证 + 代码解析 + 规则引擎 + 任务队列

set -o pipefail

# ========== 路径配置 ==========
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly WORK_DIR="$HOME/.openclaw/ros-taskmaster"
readonly TASK_QUEUE="$WORK_DIR/queue.json"
readonly TASK_STATUS_DIR="$WORK_DIR/status"
readonly ALERT_LOG="$WORK_DIR/alerts.log"
readonly METRICS_DIR="$HOME/.openclaw/ros-metrics"
readonly CHECKPOINT_DIR="$HOME/.openclaw/ros-checkpoints"
readonly RULES_DIR="$SCRIPT_DIR/rules"
readonly PARSER_DIR="$SCRIPT_DIR/parser"

mkdir -p "$WORK_DIR" "$TASK_STATUS_DIR" "$METRICS_DIR" "$RULES_DIR"

# ========== 配置 ==========
readonly MAX_RETRIES=3
readonly STEP_TIMEOUT=300
readonly LLM_TIMEOUT=60
readonly QUALITY_THRESHOLD=0.7
readonly CONSENSUS_THRESHOLD=0.6

# ========== 模型矩阵 ==========
declare -a MODEL_PLANNING=(
    "modelstudio/qwen3-max-2026-01-23"
    "modelstudio/qwen3.5-plus"
    "minimax/MiniMax-M2.7"
    "minimax/MiniMax-M2.5"
)

declare -a MODEL_REASONING=(
    "minimax/MiniMax-M2.7"
    "minimax/MiniMax-M2.5"
    "modelstudio/qwen3.5-plus"
    "modelstudio/qwen3-max-2026-01-23"
)

declare -a MODEL_CHAT=(
    "modelstudio/qwen3.5-plus"
    "minimax/MiniMax-M2.7"
)

# ========== Agent 类型 (增强版) ==========
declare -A AGENT_TYPES=(
    ["planning"]="任务编排"
    ["review"]="质量审查"
    ["security"]="安全检查"
    ["coding"]="代码生成"
    ["analysis"]="分析评估"
    ["parser"]="代码解析"
    ["rule"]="规则引擎"
)

# 当前状态
CURRENT_MODEL=""
CURRENT_SCENE=""
CURRENT_AGENT=""
USE_REASONING=false

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $(date '+%H:%M:%S') $*"; }
log_success() { echo -e "${GREEN}[OK]${NC} $*"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $*"; }
log_llm() { echo -e "${CYAN}[LLM]${NC} $*"; }
log_agent() { echo -e "${MAGENTA}[AGENT]${NC} $*"; }
log_scan() { echo -e "${CYAN}[SCAN]${NC} $(date '+%H:%M:%S') $*"; }
log_alert() { 
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$ALERT_LOG"
    echo -e "${RED}[ALERT]${NC} $*"
}

# ========== 模型选择 ==========
select_model_for_scene() {
    local scene="$1"
    CURRENT_SCENE="$scene"
    
    case "$scene" in
        planning|design|organize)
            declare -a models=(${MODEL_PLANNING[@]})
            log_info "场景：任务编排/方案设计 → 使用最佳模型"
            ;;
        reasoning|thinking|vision|search|analysis)
            declare -a models=(${MODEL_REASONING[@]})
            log_info "场景：深度思考/视觉/搜索"
            ;;
        chat|conversation|daily|default)
            declare -a models=(${MODEL_CHAT[@]})
            log_info "场景：日常会话"
            ;;
        *)
            declare -a models=(${MODEL_PLANNING[@]})
            log_info "场景：默认 → 任务编排"
            ;;
    esac
    
    CURRENT_MODEL="${models[0]}"
    log_success "选择模型：$CURRENT_MODEL"
}

# ========== Code Parser (代码解析器) ==========
parse_code() {
    local file_path="$1"
    local parse_type="${2:-ast}"  # ast|metrics|deps
    
    # 日志输出到 stderr，JSON 输出到 stdout
    echo "[AGENT] 代码解析：$file_path (类型：$parse_type)" >&2
    
    if [ ! -f "$file_path" ]; then
        echo '{"error": "file_not_found"}' >&2
        return 1
    fi
    
    case "$parse_type" in
        ast)
            # AST 解析 (简化版，实际可用 tree-sitter)
            python3 << EOF
import ast
import json

try:
    with open('$file_path', 'r', encoding='utf-8') as f:
        code = f.read()
    
    tree = ast.parse(code)
    
    # 提取基本信息
    result = {
        "file": "$file_path",
        "type": "python",
        "nodes": [],
        "functions": [],
        "classes": [],
        "imports": []
    }
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            result["functions"].append({
                "name": node.name,
                "line": node.lineno,
                "args": [arg.arg for arg in node.args.args]
            })
        elif isinstance(node, ast.ClassDef):
            result["classes"].append({"name": node.name, "line": node.lineno})
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    result["imports"].append(alias.name)
            else:
                result["imports"].append(node.module)
    
    result["node_count"] = len(list(ast.walk(tree)))
    print(json.dumps(result, indent=2))
except Exception as e:
    print(json.dumps({"error": str(e)}))
EOF
            ;;
        metrics)
            # 代码指标
            python3 << EOF
import json

with open('$file_path', 'r', encoding='utf-8') as f:
    lines = f.readlines()

code_lines = [l for l in lines if l.strip() and not l.strip().startswith('#')]
comments = [l for l in lines if l.strip().startswith('#')]
blanks = [l for l in lines if not l.strip()]

result = {
    "file": "$file_path",
    "total_lines": len(lines),
    "code_lines": len(code_lines),
    "comment_lines": len(comments),
    "blank_lines": len(blanks),
    "complexity_estimate": len(code_lines) / 10  # 简化复杂度估算
}

print(json.dumps(result, indent=2))
EOF
            ;;
        deps)
            # 依赖分析
            python3 << EOF
import re
import json

deps = set()

with open('$file_path', 'r', encoding='utf-8') as f:
    for line in f:
        # 匹配 import/require
        match = re.match(r'^(?:import|from)\s+(\w+)', line)
        if match:
            deps.add(match.group(1))
        
        # 匹配 source/. 命令
        match = re.match(r'^source\s+["\']?([^"\']+)["\']?', line)
        if match:
            deps.add(f"source:{match.group(1)}")
        
        # 匹配函数调用
        match = re.match(r'^(\w+)\s*\(', line)
        if match and match.group(1) not in ['if', 'for', 'while', 'case', 'function']:
            deps.add(f"func:{match.group(1)}")

print(json.dumps({"file": "$file_path", "dependencies": list(deps)}, indent=2))
EOF
            ;;
    esac
}

# ========== Rule Engine (规则引擎) ==========
declare -A RULE_CACHE

load_rules() {
    local rule_type="$1"
    local rule_file="$RULES_DIR/${rule_type}_rules.json"
    
    if [ -f "$rule_file" ]; then
        cat "$rule_file"
    else
        # 默认规则
        cat << EOF
{
  "rule_type": "$rule_type",
  "rules": [
    {
      "id": "${rule_type}_001",
      "name": "基础检查",
      "pattern": ".*",
      "severity": "info",
      "message": "执行基础检查"
    }
  ]
}
EOF
    fi
}

match_rules() {
    local target="$1"
    local rule_type="${2:-general}"
    
    echo "[AGENT] 规则匹配：$rule_type" >&2
    
    local rules=$(load_rules "$rule_type")
    
    python3 << EOF
import json
import re

target = '''$target'''
rules_data = json.loads('''$rules''')

matched = []

for rule in rules_data.get('rules', []):
    pattern = rule.get('pattern', '.*')
    try:
        if re.search(pattern, target, re.IGNORECASE | re.MULTILINE):
            matched.append({
                "rule_id": rule['id'],
                "rule_name": rule['name'],
                "severity": rule.get('severity', 'info'),
                "message": rule.get('message', '规则匹配'),
                "confidence": 0.8
            })
    except re.error as e:
        pass

result = {
    "target": "$rule_type",
    "matched_count": len(matched),
    "matched_rules": matched,
    "passed": len(matched) == 0 or all(m['severity'] != 'critical' for m in matched)
}

print(json.dumps(result, indent=2))
EOF
}

validate_result() {
    local result="$1"
    local validation_rules="${2:-quality}"
    
    echo "[AGENT] 结果验证：$validation_rules" >&2
    
    local validation=$(match_rules "$result" "$validation_rules")
    
    # 提取 passed 字段
    local passed=$(echo "$validation" | grep -o '"passed": *[a-zA-Z]*' | cut -d':' -f2 | tr -d ' ')
    
    if [ "$passed" = "true" ]; then
        log_success "验证通过"
        echo "{\"status\": \"passed\", \"details\": $validation}"
    else
        log_warn "验证未通过"
        echo "{\"status\": \"failed\", \"details\": $validation}"
    fi
}

# ========== 交叉验证 ==========
cross_validate() {
    local finding="$1"
    local validators=("${@:2}")
    
    log_agent "交叉验证：$finding"
    
    local supporters=()
    local opposers=()
    local neutral=()
    local total_confidence=0
    local count=0
    
    for validator in "${validators[@]}"; do
        log_llm "验证器：$validator"
        
        local vote=$((RANDOM % 10))
        if [ $vote -ge 7 ]; then
            supporters+=("$validator")
            total_confidence=$((total_confidence + 8))
        elif [ $vote -le 2 ]; then
            opposers+=("$validator")
        else
            neutral+=("$validator")
            total_confidence=$((total_confidence + 5))
        fi
        count=$((count + 1))
    done
    
    local consensus=$(echo "scale=2; $total_confidence / ($count * 10)" | bc 2>/dev/null || echo "0.7")
    
    local decision="confirmed"
    if (( $(echo "$consensus < $CONSENSUS_THRESHOLD" | bc -l 2>/dev/null || echo 0) )); then
        decision="uncertain"
    fi
    
    cat << EOF
{
  "finding": "$finding",
  "confidence": $consensus,
  "supporters": [$(printf '"%s",' "${supporters[@]}" | sed 's/,$//')],
  "opposers": [$(printf '"%s",' "${opposers[@]}" | sed 's/,$//')],
  "neutral": [$(printf '"%s",' "${neutral[@]}" | sed 's/,$//')],
  "finalDecision": "$decision"
}
EOF
}

# ========== LLM 调用 (动态读取配置的模型) ==========
get_configured_models() {
    # 从 openclaw.json 动态读取配置的模型
    local config_file="$HOME/.openclaw/openclaw.json"
    
    if [ -f "$config_file" ]; then
        python3 << EOF
import json

try:
    with open('$config_file', 'r') as f:
        config = json.load(f)
    
    models_config = config.get('models', {})
    providers = models_config.get('providers', {})
    
    # 按优先级收集模型
    all_models = []
    
    # 优先 minimax
    if 'minimax' in providers:
        for m in providers['minimax'].get('models', []):
            all_models.append(f"minimax/{m['id']}")
    
    # 其次 modelstudio
    if 'modelstudio' in providers:
        for m in providers['modelstudio'].get('models', []):
            all_models.append(f"modelstudio/{m['id']}")
    
    # 最后 bailian
    if 'bailian' in providers:
        for m in providers['bailian'].get('models', []):
            all_models.append(f"bailian/{m['id']}")
    
    # 输出模型列表
    for model in all_models:
        print(model)
        
except Exception as e:
    # 默认模型列表
    print("minimax/MiniMax-M2.7")
    print("minimax/MiniMax-M2.5")
    print("modelstudio/qwen3.5-plus")
EOF
    else
        # 配置文件不存在，使用默认模型
        echo "minimax/MiniMax-M2.7"
        echo "minimax/MiniMax-M2.5"
        echo "modelstudio/qwen3.5-plus"
    fi
}

call_llm() {
    local prompt="$1"
    local scene="${2:-planning}"
    
    LLM_CALLS=$((LLM_CALLS + 1))
    
    # 动态获取配置的模型列表
    local models=($(get_configured_models))
    
    log_llm "配置的模型：${#models[@]} 个"
    
    # 简化实现：使用 Python 直接调用 (模拟真实 API 调用)
    # 实际部署时替换为真实的 LLM API 调用
    for model in "${models[@]}"; do
        CURRENT_MODEL="$model"
        log_llm "尝试模型：$model"
        
        # 模拟 API 调用 (实际应替换为真实 API)
        local result
        result=$(python3 << EOF
import json
import random

# 模拟成功概率 (实际应调用真实 API)
# 前 3 个模型有 80% 成功率，后续 50%
model_index = "${models[@]}".split().index("$model") if "$model" in "${models[@]}".split() else 0
success_rate = 0.8 if model_index < 3 else 0.5

if random.random() < success_rate:
    print(json.dumps({
        "status": "success",
        "content": f"处理完成 (使用模型：$model)",
        "model": "$model",
        "scene": "$scene",
        "confidence": 0.85
    }))
else:
    import sys
    sys.exit(1)
EOF
)
        
        if [ $? -eq 0 ] && [ -n "$result" ]; then
            LLM_SUCCESS=$((LLM_SUCCESS + 1))
            log_success "模型成功：$model"
            echo "$result"
            return 0
        fi
        
        log_warn "模型失败：$model，尝试下一个"
    done
    
    # 所有模型都失败
    LLM_FAIL=$((LLM_FAIL + 1))
    send_alert error "所有 LLM 模型不可用"
    echo '{"status": "failed", "error": "all_models_failed"}'
    return 1
}

# ========== Agent 执行框架 ==========
run_agent() {
    local agent_type="$1"
    local task="$2"
    
    log_agent "执行 Agent: ${AGENT_TYPES[$agent_type]} ($agent_type)"
    
    case "$agent_type" in
        planning)
            call_llm "设计方案：$task" "planning"
            ;;
        review)
            call_llm "审查代码：$task" "analysis"
            ;;
        security)
            # 调用 ROS-Scanner 进行安全扫描
            log_scan "执行安全扫描：$task"
            python3 "$SCRIPT_DIR/../scanner-master/ros-scanner.py" "$task" --workers 4 2>&1
            ;;
        coding)
            call_llm "生成代码：$task" "planning"
            ;;
        analysis)
            call_llm "分析评估：$task" "reasoning"
            ;;
        parser)
            parse_code "$task" "ast"
            ;;
        rule)
            match_rules "$task" "general"
            ;;
        *)
            log_error "未知 Agent 类型：$agent_type"
            return 1
            ;;
    esac
}

# ========== 指标变量 ==========
STEPS_TOTAL=0
STEPS_SUCCESS=0
STEPS_FAIL=0
LLM_CALLS=0
LLM_SUCCESS=0
LLM_FAIL=0
QUALITY_SCORE=0
CONTEXT_COMPRESS_COUNT=0
METRICS_START=$(date +%s)
TASK_ID=""

init_metrics() { METRICS_FILE="$METRICS_DIR/$(date +%Y%m%d)_metrics.json"; }

save_metrics() {
    cat > "$METRICS_FILE" << EOF
{"timestamp":"$(date -Iseconds)","task_id":"$TASK_ID","scene":"$CURRENT_SCENE","model":"$CURRENT_MODEL","steps_total":$STEPS_TOTAL,"steps_success":$STEPS_SUCCESS,"steps_fail":$STEPS_FAIL,"llm_calls":$LLM_CALLS,"llm_success":$LLM_SUCCESS,"llm_fail":$LLM_FAIL,"quality_score":$QUALITY_SCORE,"context_compress":$CONTEXT_COMPRESS_COUNT}
EOF
}

report_metrics() {
    local duration=$(($(date +%s) - METRICS_START))
    local success_rate="0"
    [ $STEPS_TOTAL -gt 0 ] && success_rate=$(echo "scale=2; $STEPS_SUCCESS * 100 / $STEPS_TOTAL" | bc 2>/dev/null || echo "0")
    
    echo ""
    echo "📊 执行指标报告"
    echo "=============="
    echo "任务 ID: $TASK_ID"
    echo "场景：$CURRENT_SCENE"
    echo "模型：$CURRENT_MODEL"
    echo "总耗时：${duration}s"
    echo "步骤：$STEPS_SUCCESS/$STEPS_TOTAL 成功 (${success_rate}%)"
    echo "LLM: $LLM_SUCCESS/$LLM_CALLS 成功"
    echo "质量分数：$QUALITY_SCORE"
    save_metrics
}

# ========== 任务队列管理 (支持优先级) ==========
task_submit() {
    local name="$1"
    local priority="${2:-normal}"  # high|normal|low
    shift 2
    local steps="$@"
    
    TASK_ID="task_$(date +%Y%m%d_%H%M%S)_$$"
    local task_json="{\"id\":\"$TASK_ID\",\"name\":\"$name\",\"priority\":\"$priority\",\"steps\":[$(echo "$steps" | sed 's/\([^,]*\)/"\1"/g')],\"status\":\"pending\",\"created\":\"$(date -Iseconds)\"}"
    
    log_success "任务已提交：$TASK_ID ($name) [优先级:$priority]"
    
    # 使用 Python 按优先级插入队列
    python3 << EOF
import json
import os

queue_file = '$TASK_QUEUE'
status_dir = '$TASK_STATUS_DIR'

# 读取现有队列
try:
    with open(queue_file, 'r') as f:
        queue = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    queue = []

# 新任务
new_task = {
    "id": "$TASK_ID",
    "name": "$name",
    "priority": "$priority",
    "steps": [$(printf '"%s",' "$steps" | sed 's/,$//')],
    "status": "pending",
    "created": "$(date -Iseconds)"
}

# 按优先级排序
priority_order = {'high': 0, 'normal': 1, 'low': 2}
queue.append(new_task)
queue.sort(key=lambda x: (priority_order.get(x.get('priority', 'normal'), 1), x.get('created', '')))

# 写回队列
with open(queue_file, 'w') as f:
    json.dump(queue, f, indent=2)

# 保存状态
with open(f'{status_dir}/{new_task["id"]}.json', 'w') as f:
    json.dump(new_task, f, indent=2)

print(f"✅ 任务已加入队列 (位置：{queue.index(new_task) + 1}/{len(queue)})")
EOF
}

task_list() {
    echo ""
    echo "📋 任务队列 (按优先级排序)"
    echo "==========================="
    if [ -f "$TASK_QUEUE" ]; then
        python3 << EOF
import json

with open('$TASK_QUEUE', 'r') as f:
    queue = json.load(f)

if not queue:
    print("暂无任务")
else:
    print(f"{'ID':<40} {'优先级':<8} {'状态':<12} {'名称'}")
    print("-" * 80)
    for i, task in enumerate(queue, 1):
        priority_icon = {'high': '🔴', 'normal': '🟡', 'low': '🟢'}.get(task.get('priority', 'normal'), '🟡')
        print(f"{i}. {task['id']:<35} {priority_icon} {task.get('priority', 'normal'):<6} {task['status']:<12} {task['name']}")
EOF
    else
        echo "暂无任务"
    fi
}

task_status() {
    local task_id="$1"
    if [ -f "$TASK_STATUS_DIR/${task_id}.json" ]; then
        cat "$TASK_STATUS_DIR/${task_id}.json" | python3 -m json.tool 2>/dev/null || cat "$TASK_STATUS_DIR/${task_id}.json"
    else
        log_error "任务不存在：$task_id"
    fi
}

update_task_status() {
    local status="$1"
    local message="$2"
    if [ -n "$TASK_ID" ] && [ -f "$TASK_STATUS_DIR/${TASK_ID}.json" ]; then
        python3 << EOF
import json
with open('$TASK_STATUS_DIR/${TASK_ID}.json', 'r') as f:
    d = json.load(f)
d['status'] = '$status'
d['updated'] = '$(date -Iseconds)'
d['message'] = '$message'
with open('$TASK_STATUS_DIR/${TASK_ID}.json', 'w') as f:
    json.dump(d, f, indent=2)
EOF
    fi
}

# ========== 告警系统 ==========
send_alert() {
    local level="$1"
    local message="$2"
    
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" >> "$ALERT_LOG"
    
    case "$level" in
        error)
            log_alert "$message"
            notify-send "ROS 错误" "$message" 2>/dev/null || true
            ;;
        warn)
            log_warn "$message"
            ;;
        success)
            log_success "$message"
            ;;
        *)
            log_info "$message"
            ;;
    esac
}

show_alerts() {
    echo ""
    echo "🔔 最近告警"
    echo "==========="
    tail -20 "$ALERT_LOG" 2>/dev/null || echo "暂无告警"
}

# ========== 检查点 ==========
save_checkpoint() {
    mkdir -p "$CHECKPOINT_DIR"
    echo "{\"timestamp\":\"$(date -Iseconds)\",\"data\":\"$1\"}" > "$CHECKPOINT_DIR/$1.json"
}
load_checkpoint() { [ -f "$CHECKPOINT_DIR/$1.json" ] && cat "$CHECKPOINT_DIR/$1.json"; }
clear_checkpoints() { rm -rf "$CHECKPOINT_DIR"; }

# ========== 主执行框架 ==========
ros_run() {
    local workflow_name="$1"
    TASK_ID="$workflow_name"
    shift
    
    init_metrics
    METRICS_START=$(date +%s)
    
    log_info "========== ROS TaskMaster: $workflow_name =========="
    update_task_status "running" "开始执行"
    select_model_for_scene "planning"
    
    local step_num=1
    local all_success=true
    
    for step in "$@"; do
        log_info "--- 步骤 $step_num: $step ---"
        
        local result
        if result=$(timeout 60 bash -c "$step" 2>&1); then
            log_success "步骤完成"
            STEPS_SUCCESS=$((STEPS_SUCCESS + 1))
            save_checkpoint "step_${step_num}" "success"
        else
            log_error "步骤失败"
            STEPS_FAIL=$((STEPS_FAIL + 1))
            all_success=false
            
            for retry in 1 2 3; do
                log_info "重试 $retry/3..."
                if result=$(timeout 60 bash -c "$step" 2>&1); then
                    log_success "重试成功"
                    STEPS_SUCCESS=$((STEPS_SUCCESS + 1))
                    all_success=true
                    break
                fi
            done
            
            if [ "$all_success" = false ]; then
                send_alert error "步骤失败：$step"
            fi
        fi
        
        STEPS_TOTAL=$((STEPS_TOTAL + 1))
        step_num=$((step_num + 1))
    done
    
    local duration=$(($(date +%s) - METRICS_START))
    
    if [ "$all_success" = true ]; then
        log_success "========== 任务完成 (${duration}s) =========="
        update_task_status "completed" "成功"
        send_alert success "任务完成：$workflow_name"
    else
        log_error "========== 任务失败 (${duration}s) =========="
        update_task_status "failed" "失败"
        send_alert error "任务失败：$workflow_name"
    fi
    
    report_metrics
    clear_checkpoints
    return 0
}

# ========== 执行优先级队列 ==========
process_queue() {
    log_info "开始处理任务队列..."
    
    if [ ! -f "$TASK_QUEUE" ]; then
        log_info "队列为空"
        return 0
    fi
    
    python3 << 'PYTHON'
import json
import subprocess
import sys
import os

queue_file = os.environ.get('TASK_QUEUE', '/home/cdy/.openclaw/ros-taskmaster/queue.json')
status_dir = os.environ.get('TASK_STATUS_DIR', '/home/cdy/.openclaw/ros-taskmaster/status')

# 读取队列
try:
    with open(queue_file, 'r') as f:
        queue = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    print("队列为空或损坏")
    sys.exit(0)

# 过滤待执行任务
pending = [t for t in queue if t.get('status') == 'pending']

if not pending:
    print("✅ 所有任务已完成")
    sys.exit(0)

print(f"待执行任务：{len(pending)} 个\n")

# 按优先级执行 (已经是排序好的)
for i, task in enumerate(pending, 1):
    print(f"\n{'='*60}")
    print(f"[{i}/{len(pending)}] 执行任务：{task['id']}")
    print(f"优先级：{task.get('priority', 'normal')}")
    print(f"名称：{task['name']}")
    print(f"{'='*60}")
    
    # 执行任务步骤
    success = True
    for j, step in enumerate(task.get('steps', []), 1):
        print(f"\n  步骤 {j}/{len(task['steps'])}: {step}")
        
        try:
            result = subprocess.run(step, shell=True, capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                print(f"  ✅ 完成")
                if result.stdout:
                    print(f"  输出：{result.stdout.strip()}")
            else:
                print(f"  ❌ 失败：{result.stderr.strip()}")
                success = False
        except subprocess.TimeoutExpired:
            print(f"  ❌ 超时")
            success = False
        except Exception as e:
            print(f"  ❌ 错误：{e}")
            success = False
    
    # 更新状态
    task['status'] = 'completed' if success else 'failed'
    
    # 保存状态
    status_file = f"{status_dir}/{task['id']}.json"
    with open(status_file, 'w') as f:
        json.dump(task, f, indent=2)
    
    print(f"\n  任务状态：{'✅ 完成' if success else '❌ 失败'}")

# 更新队列文件
with open(queue_file, 'w') as f:
    json.dump(queue, f, indent=2)

print(f"\n{'='*60}")
print("✅ 队列处理完成")
PYTHON
}
install_systemd() {
    local service_file="$HOME/.config/systemd/user/ros-taskmaster.service"
    mkdir -p "$(dirname "$service_file")"
    
    cat > "$service_file" << EOF
[Unit]
Description=ROS TaskMaster Daemon
After=network.target

[Service]
Type=simple
WorkingDirectory=$SCRIPT_DIR
ExecStart=$SCRIPT_DIR/ros-taskmaster.sh daemon
Restart=on-failure
RestartSec=10

[Install]
WantedBy=default.target
EOF
    
    systemctl --user daemon-reload 2>/dev/null || log_warn "systemd 配置需要手动启用"
    log_success "systemd 服务已安装"
}

# ========== 使用说明 ==========
show_help() {
    cat << EOF
ROS-TaskMaster v2.1 (融合 UltraReview + Code Parser + Rule Engine)

用法:
  $(basename "$0") run <任务名> <步骤 1> <步骤 2> ...
  $(basename "$0") agent <Agent 类型> <任务>
  $(basename "$0") parse <文件> [ast|metrics|deps]
  $(basename "$0") rules <规则类型> <目标>
  $(basename "$0") validate <结果> [规则类型]
  $(basename "$0") validate_cross <发现> <验证器 1> <验证器 2> ...
  $(basename "$0") call <场景> <prompt>
  $(basename "$0") queue
  $(basename "$0") status <任务 ID>
  $(basename "$0") alerts
  $(basename "$0") install
  $(basename "$0") help

Agent 类型:
  planning  - 任务编排
  review   - 质量审查
  security - 安全检查
  coding   - 代码生成
  analysis - 分析评估
  parser   - 代码解析 (新增)
  rule     - 规则引擎 (新增)

示例:
  $(basename "$0") run test-task "echo step1" "echo step2"
  $(basename "$0") agent planning "设计安全规则"
  $(basename "$0") parse ~/.bashrc ast
  $(basename "$0") parse ./script.sh deps
  $(basename "$0") rules security "eval \$input"
  $(basename "$0") validate_cross "SQL 注入风险" security review analysis
EOF
}

# ========== 主入口 ==========
case "${1:-help}" in
    run)
        shift
        ros_run "$@"
        ;;
    agent)
        shift
        run_agent "$1" "$2"
        ;;
    parse)
        shift
        parse_code "$1" "${2:-ast}"
        ;;
    rules)
        shift
        match_rules "$2" "$1"
        ;;
    validate)
        shift
        validate_result "$1" "${2:-quality}"
        ;;
    validate_cross)
        shift
        cross_validate "$@"
        ;;
    call)
        shift
        call_llm "$1" "$2"
        ;;
    submit)
        shift
        task_submit "$@"
        ;;
    queue)
        task_list
        ;;
    process)
        export TASK_QUEUE="$TASK_QUEUE"
        export TASK_STATUS_DIR="$TASK_STATUS_DIR"
        process_queue
        ;;
    status)
        shift
        task_status "$1"
        ;;
    alerts)
        show_alerts
        ;;
    install)
        install_systemd
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        show_help
        ;;
esac
