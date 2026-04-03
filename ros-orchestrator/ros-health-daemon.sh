#!/bin/bash
# ROS 健康检查守护进程
# 功能：定时健康检查 + 自动恢复 + 告警通知

set -o pipefail

# ========== 配置 ==========
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly LOG_DIR="$HOME/.openclaw/ros-logs"
readonly CHECKPOINT_DIR="$HOME/.openclaw/ros-checkpoints"
readonly HEALTH_LOG="$LOG_DIR/health-check.log"
readonly PID_FILE="$HOME/.openclaw/ros-health.pid"
readonly CHECK_INTERVAL=60  # 检查间隔 (秒)

# 阈值配置
readonly DISK_THRESHOLD=90      # 磁盘使用率阈值 (%)
readonly MEMORY_THRESHOLD=90    # 内存使用率阈值 (%)
readonly LOG_MAX_AGE=7          # 日志保留天数
readonly LOG_MAX_SIZE_MB=1000   # 日志目录最大大小 (MB)

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_health() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    mkdir -p "$LOG_DIR"
    echo "[$timestamp] [$level] $message" >> "$HEALTH_LOG"
    
    case "$level" in
        INFO)    echo -e "${BLUE}[HEALTH]${NC} $message" ;;
        SUCCESS) echo -e "${GREEN}[OK]${NC} $message" ;;
        WARN)    echo -e "${YELLOW}[WARN]${NC} $message" ;;
        ERROR)   echo -e "${RED}[ERROR]${NC} $message" ;;
    esac
}

# ========== 健康检查项 ==========
check_disk() {
    log_health "INFO" "检查磁盘空间..."
    
    local disk_usage=$(df -h "$HOME" | awk 'NR==2 {print $5}' | sed 's/%//')
    
    if [ "$disk_usage" -gt "$DISK_THRESHOLD" ]; then
        log_health "ERROR" "磁盘使用率：${disk_usage}% (阈值：${DISK_THRESHOLD}%)"
        
        # 自动清理
        cleanup_old_logs
        cleanup_checkpoints
        
        # 重新检查
        disk_usage=$(df -h "$HOME" | awk 'NR==2 {print $5}' | sed 's/%//')
        if [ "$disk_usage" -gt "$DISK_THRESHOLD" ]; then
            send_alert "磁盘空间不足：${disk_usage}%"
            return 1
        fi
    fi
    
    log_health "SUCCESS" "磁盘使用率：${disk_usage}%"
    return 0
}

check_memory() {
    log_health "INFO" "检查内存..."
    
    local mem_info=$(free -m | awk 'NR==2 {printf "%.0f", $3*100/$2}')
    
    if [ "$mem_info" -gt "$MEMORY_THRESHOLD" ]; then
        log_health "ERROR" "内存使用率：${mem_info}% (阈值：${MEMORY_THRESHOLD}%)"
        send_alert "内存不足：${mem_info}%"
        return 1
    fi
    
    log_health "SUCCESS" "内存使用率：${mem_info}%"
    return 0
}

check_logs() {
    log_health "INFO" "检查日志文件..."
    
    if [ -d "$LOG_DIR" ]; then
        local log_size=$(du -sm "$LOG_DIR" 2>/dev/null | awk '{print $1}')
        
        if [ "$log_size" -gt "$LOG_MAX_SIZE_MB" ]; then
            log_health "WARN" "日志目录大小：${log_size}MB (阈值：${LOG_MAX_SIZE_MB}MB)"
            cleanup_old_logs
        else
            log_health "SUCCESS" "日志目录大小：${log_size}MB"
        fi
    fi
    
    return 0
}

check_checkpoints() {
    log_health "INFO" "检查检查点..."
    
    if [ -d "$CHECKPOINT_DIR" ]; then
        local checkpoint_count=$(ls -1 "$CHECKPOINT_DIR" 2>/dev/null | wc -l)
        
        if [ "$checkpoint_count" -gt 100 ]; then
            log_health "WARN" "检查点数量：$checkpoint_count，清理旧检查点"
            cleanup_old_checkpoints
        else
            log_health "SUCCESS" "检查点数量：$checkpoint_count"
        fi
    fi
    
    return 0
}

check_processes() {
    log_health "INFO" "检查 ROS 进程..."
    
    # 检查是否有僵尸进程
    local zombie_count=$(ps aux | awk '$8 ~ /Z/ {print}' | wc -l)
    
    if [ "$zombie_count" -gt 0 ]; then
        log_health "WARN" "发现 $zombie_count 个僵尸进程"
    else
        log_health "SUCCESS" "无僵尸进程"
    fi
    
    return 0
}

# ========== 清理函数 ==========
cleanup_old_logs() {
    log_health "INFO" "清理 ${LOG_MAX_AGE} 天前的日志..."
    
    find "$LOG_DIR" -name "*.log" -type f -mtime +$LOG_MAX_AGE -delete 2>/dev/null
    find "$LOG_DIR" -name "*.log.*" -type f -mtime +$LOG_MAX_AGE -delete 2>/dev/null
    
    log_health "SUCCESS" "日志清理完成"
}

cleanup_checkpoints() {
    log_health "INFO" "清理旧检查点..."
    cleanup_old_checkpoints
}

cleanup_old_checkpoints() {
    if [ -d "$CHECKPOINT_DIR" ]; then
        # 保留最近 50 个检查点
        ls -t "$CHECKPOINT_DIR" 2>/dev/null | tail -n +51 | xargs rm -f 2>/dev/null
        log_health "SUCCESS" "检查点清理完成"
    fi
}

# ========== 告警通知 ==========
send_alert() {
    local message="$1"
    
    log_health "ERROR" "告警：$message"
    
    # 桌面通知
    notify-send "ROS 健康告警" "$message" 2>/dev/null || true
    
    # 可以扩展为飞书/钉钉/邮件通知
    # curl -X POST "webhook_url" -d "{\"text\": \"$message\"}"
}

# ========== 主健康检查 ==========
run_health_check() {
    log_health "INFO" "========== 开始健康检查 =========="
    
    local issues=0
    
    check_disk || issues=$((issues + 1))
    check_memory || issues=$((issues + 1))
    check_logs || issues=$((issues + 1))
    check_checkpoints || issues=$((issues + 1))
    check_processes || issues=$((issues + 1))
    
    log_health "INFO" "========== 健康检查完成 =========="
    
    if [ $issues -eq 0 ]; then
        log_health "SUCCESS" "✅ 所有检查项通过"
        return 0
    else
        log_health "WARN" "⚠️  发现 $issues 个问题"
        return 1
    fi
}

# ========== 守护进程模式 ==========
run_daemon() {
    log_health "INFO" "启动健康检查守护进程 (间隔：${CHECK_INTERVAL}s)"
    
    # 保存 PID
    echo $$ > "$PID_FILE"
    
    trap cleanup_daemon EXIT INT TERM
    
    while true; do
        run_health_check
        
        # 休眠
        sleep "$CHECK_INTERVAL"
    done
}

cleanup_daemon() {
    log_health "INFO" "停止守护进程..."
    rm -f "$PID_FILE"
}

# ========== 状态查询 ==========
show_status() {
    echo "=== ROS 健康检查状态 ==="
    echo ""
    
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            echo "守护进程：✅ 运行中 (PID: $pid)"
        else
            echo "守护进程：❌ 已停止 (PID 文件存在但进程不存在)"
            rm -f "$PID_FILE"
        fi
    else
        echo "守护进程：❌ 未运行"
    fi
    
    echo ""
    echo "检查间隔：${CHECK_INTERVAL}s"
    echo "磁盘阈值：${DISK_THRESHOLD}%"
    echo "内存阈值：${MEMORY_THRESHOLD}%"
    echo "日志保留：${LOG_MAX_AGE}天"
    echo ""
    
    if [ -f "$HEALTH_LOG" ]; then
        echo "最近检查记录:"
        tail -10 "$HEALTH_LOG" | while read line; do
            echo "  $line"
        done
    fi
}

# ========== 使用说明 ==========
show_help() {
    cat << EOF
ROS 健康检查守护进程

用法: $(basename "$0") <命令>

命令:
  start       启动守护进程
  stop        停止守护进程
  restart     重启守护进程
  status      显示状态
  check       执行一次健康检查
  logs [行数] 查看健康检查日志
  help        显示帮助

示例:
  $(basename "$0") start
  $(basename "$0") status
  $(basename "$0") check
  $(basename "$0") logs 20
  $(basename "$0") stop
EOF
}

# ========== 主入口 ==========
case "${1:-help}" in
    start)
        if [ -f "$PID_FILE" ]; then
            pid=$(cat "$PID_FILE")
            if ps -p "$pid" > /dev/null 2>&1; then
                echo "守护进程已在运行 (PID: $pid)"
                exit 0
            fi
        fi
        
        # 后台启动
        nohup "$0" daemon > /dev/null 2>&1 &
        echo "✅ 守护进程已启动"
        sleep 1
        show_status
        ;;
    daemon)
        run_daemon
        ;;
    stop)
        if [ -f "$PID_FILE" ]; then
            pid=$(cat "$PID_FILE")
            if ps -p "$pid" > /dev/null 2>&1; then
                kill "$pid"
                rm -f "$PID_FILE"
                echo "✅ 守护进程已停止"
            else
                rm -f "$PID_FILE"
                echo "✅ 守护进程已停止 (PID 文件已清理)"
            fi
        else
            echo "守护进程未运行"
        fi
        ;;
    restart)
        "$0" stop
        sleep 1
        "$0" start
        ;;
    status)
        show_status
        ;;
    check)
        run_health_check
        ;;
    logs)
        lines="${1:-20}"
        if [ -f "$HEALTH_LOG" ]; then
            tail -n "$lines" "$HEALTH_LOG"
        else
            echo "日志文件不存在"
        fi
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        show_help
        exit 1
        ;;
esac
