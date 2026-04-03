#!/bin/bash
# 供应链安全定时扫描守护进程
# 用法：./supply_chain_daemon.sh [start|stop|status|run]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$SCRIPT_DIR/logs"
PID_FILE="$SCRIPT_DIR/daemon.pid"
LOG_FILE="$LOG_DIR/supply_chain_scan.log"
INTEL_DIR="$SCRIPT_DIR/intel"

# 创建日志目录
mkdir -p "$LOG_DIR"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

check_intel() {
    log "=== 更新威胁情报 ==="
    
    # 检查是否需要更新 (6 小时间隔)
    INTEL_FILE="$INTEL_DIR/ioc.json"
    if [ -f "$INTEL_FILE" ]; then
        LAST_UPDATE=$(stat -c %Y "$INTEL_FILE" 2>/dev/null || stat -f %m "$INTEL_FILE" 2>/dev/null)
        NOW=$(date +%s)
        HOURS=$(( (NOW - LAST_UPDATE) / 3600 ))
        
        if [ "$HOURS" -lt 6 ]; then
            log "情报库更新于 ${HOURS} 小时前，跳过"
            return 0
        fi
    fi
    
    # 更新情报
    cd "$SCRIPT_DIR"
    python3 expert_mode/intel_fetcher.py >> "$LOG_FILE" 2>&1
    
    if [ $? -eq 0 ]; then
        log "✅ 威胁情报更新完成"
    else
        log "❌ 威胁情报更新失败"
    fi
}

run_scan() {
    log "=== 开始供应链安全扫描 ==="
    
    # 1. 更新情报
    check_intel
    
    # 2. Scanner v3 基础扫描
    log "[1/3] Scanner v3 基础扫描..."
    cd "$SCRIPT_DIR"
    python3 cli.py scan ~/.openclaw/workspace/ >> "$LOG_FILE" 2>&1
    
    # 3. LiteLLM 专项检测
    log "[2/3] LiteLLM 供应链检测..."
    python3 expert_mode/litellm_detector.py ~/.local/lib/python*/site-packages/ >> "$LOG_FILE" 2>&1
    
    # 4. 异常外发检测
    log "[3/3] 异常外发数据检测..."
    python3 expert_mode/exfil_detector.py ~/.openclaw/workspace/ >> "$LOG_FILE" 2>&1
    
    # 5. 检查高风险
    if grep -q "CRITICAL\|HIGH" "$LOG_FILE"; then
        log "🚨 发现高风险！发送告警..."
        # TODO: 集成告警通知
        # python3 expert_mode/alert_sender.py --severity HIGH
    fi
    
    log "=== 扫描完成 ==="
}

daemon_loop() {
    log "守护进程启动 (PID: $$)"
    echo $$ > "$PID_FILE"
    
    while true; do
        run_scan
        
        # 每 6 小时执行一次
        log "等待 6 小时后再次扫描..."
        sleep 21600  # 6 * 60 * 60 = 21600 秒
    done
}

start_daemon() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "守护进程已在运行 (PID: $PID)"
            return 1
        fi
    fi
    
    echo "启动守护进程..."
    nohup bash "$0" run > /dev/null 2>&1 &
    echo "守护进程已启动 (PID: $!)"
}

stop_daemon() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            kill "$PID"
            rm "$PID_FILE"
            echo "守护进程已停止 (PID: $PID)"
            return 0
        fi
    fi
    
    echo "守护进程未运行"
    return 1
}

show_status() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "守护进程运行中 (PID: $PID)"
            
            # 显示最近日志
            echo ""
            echo "最近日志:"
            tail -20 "$LOG_FILE"
            return 0
        fi
    fi
    
    echo "守护进程未运行"
    return 1
}

# 主入口
case "${1:-run}" in
    start)
        start_daemon
        ;;
    stop)
        stop_daemon
        ;;
    status)
        show_status
        ;;
    run)
        daemon_loop
        ;;
    scan)
        run_scan
        ;;
    intel)
        check_intel
        ;;
    *)
        echo "用法：$0 {start|stop|status|run|scan|intel}"
        echo ""
        echo "命令:"
        echo "  start   启动守护进程"
        echo "  stop    停止守护进程"
        echo "  status  查看状态"
        echo "  run     前台运行 (调试用)"
        echo "  scan    执行一次扫描"
        echo "  intel   更新威胁情报"
        exit 1
        ;;
esac
