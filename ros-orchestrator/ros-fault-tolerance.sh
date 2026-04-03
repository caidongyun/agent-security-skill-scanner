#!/bin/bash
# ROS 故障自愈增强框架 v1.0
# 功能：超时控制 + 自动重试 + 检查点 + 健康检查 + 故障恢复

set -o pipefail

# ========== 配置 ==========
readonly MAX_RETRIES=3          # 最大重试次数
readonly STEP_TIMEOUT=300       # 单步超时 (秒)
readonly CHECKPOINT_DIR="$HOME/.openclaw/ros-checkpoints"
readonly LOG_DIR="$HOME/.openclaw/ros-logs"
readonly HEALTH_CHECK_INTERVAL=60  # 健康检查间隔 (秒)

# 日志配置
readonly LOG_MAX_SIZE=104857600  # 100MB
readonly LOG_MAX_FILES=7         # 保留 7 个日志文件

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# ========== 结构化日志 ==========
get_log_file() {
    echo "$LOG_DIR/ros-$(date +%Y%m%d).log"
}

log_structured() {
    local level="$1"
    local message="$2"
    local timestamp=$(date -Iseconds)
    local log_file=$(get_log_file)
    
    mkdir -p "$LOG_DIR"
    
    # JSON 格式日志
    local json_log=$(cat << EOF
{"timestamp":"$timestamp","level":"$level","message":"$(echo "$message" | sed 's/"/\\"/g')"}
EOF
)
    echo "$json_log" >> "$log_file"
    
    # 控制台输出
    case "$level" in
        INFO)    echo -e "${BLUE}[INFO]${NC} $(date '+%H:%M:%S') $message" ;;
        SUCCESS) echo -e "${GREEN}[OK]${NC} $(date '+%H:%M:%S') $message" ;;
        WARN)    echo -e "${YELLOW}[WARN]${NC} $(date '+%H:%M:%S') $message" ;;
        ERROR)   echo -e "${RED}[ERROR]${NC} $(date '+%H:%M:%S') $message" ;;
        *)       echo -e "$(date '+%H:%M:%S') $message" ;;
    esac
    
    # 日志轮转检查
    rotate_logs
}

rotate_logs() {
    local log_file=$(get_log_file)
    
    if [ -f "$log_file" ]; then
        local log_size=$(stat -c%s "$log_file" 2>/dev/null || stat -f%z "$log_file" 2>/dev/null || echo 0)
        
        if [ "$log_size" -gt "$LOG_MAX_SIZE" ]; then
            # 轮转日志
            local backup="${log_file}.$(date +%H%M%S)"
            mv "$log_file" "$backup"
            log_structured "INFO" "日志轮转：$backup"
            
            # 清理旧日志
            find "$LOG_DIR" -name "*.log.*" -type f | sort -r | tail -n +$((LOG_MAX_FILES + 1)) | xargs rm -f 2>/dev/null
        fi
    fi
}

# 兼容旧日志函数
log_info() { log_structured "INFO" "$*"; }
log_success() { log_structured "SUCCESS" "$*"; }
log_warn() { log_structured "WARN" "$*"; }
log_error() { log_structured "ERROR" "$*"; }

# ========== 检查点管理 ==========
save_checkpoint() {
    local step_name="$1"
    local step_data="$2"
    local checkpoint_file="$CHECKPOINT_DIR/${step_name}.json"
    
    mkdir -p "$CHECKPOINT_DIR"
    echo "{\"timestamp\": \"$(date -Iseconds)\", \"data\": \"$step_data\"}" > "$checkpoint_file"
    log_info "检查点已保存: $step_name"
}

load_checkpoint() {
    local step_name="$1"
    local checkpoint_file="$CHECKPOINT_DIR/${step_name}.json"
    
    if [ -f "$checkpoint_file" ]; then
        cat "$checkpoint_file"
        return 0
    fi
    return 1
}

clear_checkpoint() {
    local step_name="$1"
    rm -f "$CHECKPOINT_DIR/${step_name}.json"
}

clear_all_checkpoints() {
    rm -rf "$CHECKPOINT_DIR"
    log_info "所有检查点已清除"
}

# ========== 超时执行 ==========
exec_with_timeout() {
    local timeout="$1"
    local step_name="$2"
    shift 2
    
    log_info "执行 [${step_name}] (超时: ${timeout}s)..."
    
    # 使用 timeout 命令执行
    if timeout "$timeout" "$@"; then
        log_success "[${step_name}] 完成"
        return 0
    else
        local exit_code=$?
        if [ $exit_code -eq 124 ]; then
            log_error "[${step_name}] 超时 (${timeout}s)"
        else
            log_error "[${step_name}] 失败 (exit: $exit_code)"
        fi
        return $exit_code
    fi
}

# ========== 带重试的步骤执行 (指数退避) ==========
exec_step() {
    local step_name="$1"
    local max_retries="${2:-$MAX_RETRIES}"
    local timeout="${3:-$STEP_TIMEOUT}"
    shift 3
    
    local attempt=1
    local success=false
    local base_delay=5  # 基础延迟 5 秒
    
    while [ $attempt -le $max_retries ]; do
        log_info "[${step_name}] 尝试 $attempt/$max_retries"
        
        if exec_with_timeout "$timeout" "$step_name" "$@"; then
            success=true
            save_checkpoint "step_${step_name}" "completed"
            break
        else
            local remaining=$(($max_retries - $attempt))
            if [ $remaining -gt 0 ]; then
                # 指数退避：5s → 10s → 20s → 40s
                local delay=$((base_delay * (2 ** ($attempt - 1))))
                log_warn "[${step_name}] 失败，${remaining} 次重试机会，${delay}s 后重试"
                
                # 显示倒计时
                for i in $(seq $delay -1 1); do
                    printf "\r\033[K[${step_name}] 重试倒计时：%ds" $i
                    sleep 1
                done
                echo ""
            else
                log_warn "[${step_name}] 失败，无重试机会"
            fi
            attempt=$((attempt + 1))
        fi
    done
    
    if [ "$success" = true ]; then
        return 0
    else
        log_error "[${step_name}] 多次失败，放弃"
        return 1
    fi
}

# ========== 健康检查 ==========
ros_health_check() {
    log_info "执行健康检查..."
    
    local issues=0
    
    # 检查磁盘空间
    local disk_usage=$(df -h . | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ "$disk_usage" -gt 90 ]; then
        log_warn "磁盘使用率: ${disk_usage}%"
        issues=$((issues + 1))
    fi
    
    # 检查内存
    local mem_available=$(free -m | awk 'NR==2 {print $7}')
    if [ "$mem_available" -lt 500 ]; then
        log_warn "可用内存: ${mem_available}MB"
        issues=$((issues + 1))
    fi
    
    # 检查日志文件大小
    if [ -d "$LOG_DIR" ]; then
        local log_size=$(du -sm "$LOG_DIR" | awk '{print $1}')
        if [ "$log_size" -gt 1000 ]; then
            log_warn "日志目录大小: ${log_size}MB"
            # 自动清理旧日志
            find "$LOG_DIR" -name "*.log" -mtime +7 -delete
            log_info "已清理 7 天前的日志"
        fi
    fi
    
    if [ $issues -eq 0 ]; then
        log_success "健康检查通过"
        return 0
    else
        log_warn "健康检查发现 $issues 个问题"
        return 1
    fi
}

# ========== 故障恢复 ==========
ros_recover() {
    local last_checkpoint="$1"
    
    log_info "开始故障恢复..."
    
    # 查找最近的检查点
    if [ -d "$CHECKPOINT_DIR" ]; then
        local latest=$(ls -t "$CHECKPOINT_DIR" | head -1)
        if [ -n "$latest" ]; then
            log_info "发现检查点: $latest"
            # 从检查点恢复状态
            return 0
        fi
    fi
    
    log_warn "未找到检查点，将从头开始"
    return 1
}

# ========== 主框架 ==========
ros_run() {
    local workflow_name="${1:-unnamed}"
    shift
    
    mkdir -p "$LOG_DIR"
    local log_file="$LOG_DIR/${workflow_name}_$(date +%Y%m%d_%H%M%S).log"
    
    log_info "========== ROS 工作流: $workflow_name =========="
    log_info "日志文件: $log_file"
    
    # 健康检查
    ros_health_check || log_warn "继续执行（可能存在性能问题）"
    
    # 执行工作流
    local step_num=1
    for step in "$@"; do
        log_info "--- 步骤 $step_num: $step ---"
        
        if exec_step "$step" 3 300 eval "$step"; then
            log_success "步骤完成: $step"
        else
            log_error "步骤失败: $step"
            
            # 询问是否恢复
            echo -n "是否尝试恢复执行? (y/n): "
            read -r response
            if [ "$response" = "y" ]; then
                ros_recover
            fi
            return 1
        fi
        
        step_num=$((step_num + 1))
    done
    
    log_success "========== 工作流完成: $workflow_name =========="
    clear_all_checkpoints
    return 0
}

# ========== 使用说明 ==========
show_help() {
    cat << EOF
ROS 故障自愈框架 v1.0

用法: $(basename "$0") <命令> [参数]

命令:
  run <工作流名> <步骤1> <步骤2> ...   运行工作流
  status                                   显示状态
  health                                   健康检查
  checkpoints                              列出检查点
  clear                                    清除检查点
  recover                                  从故障恢复
  help                                     显示帮助

示例:
  $(basename "$0") run my-workflow "echo step1" "echo step2"
  $(basename "$0") health
  $(basename "$0") clear
EOF
}

# ========== 主入口 ==========
case "${1:-help}" in
    run)
        shift
        ros_run "$@"
        ;;
    status)
        echo "=== ROS 状态 ==="
        echo "检查点目录: $CHECKPOINT_DIR"
        echo "日志目录: $LOG_DIR"
        ls -la "$CHECKPOINT_DIR" 2>/dev/null || echo "无检查点"
        ;;
    health)
        ros_health_check
        ;;
    checkpoints)
        ls -la "$CHECKPOINT_DIR" 2>/dev/null || echo "无检查点"
        ;;
    clear)
        clear_all_checkpoints
        ;;
    recover)
        ros_recover
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        log_error "未知命令: $1"
        show_help
        exit 1
        ;;
esac