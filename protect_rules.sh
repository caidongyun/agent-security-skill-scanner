#!/bin/bash
# ==============================================================================
# 🛡️ 规则目录保护脚本
# 监控规则目录变化，阻止未经授权的修改
# ==============================================================================

set -e

RULES_DIR="/home/cdy/.openclaw/workspace/agent-security-skill-scanner-master/rules/scanner_v3/yara"
BACKUP_DIR="/home/cdy/.openclaw/workspace/agent-security-skill-scanner-master/rules/backup"
CHANGELOG="/home/cdy/.openclaw/workspace/agent-security-skill-scanner-master/rules/CHANGELOG.md"
LOCK_FILE="/tmp/rules_dir.lock"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# 检查是否有冲突进程
check_conflicting_processes() {
    log "🔍 检查冲突进程..."
    
    CONFLICT_PIDS=$(ps aux | grep -E "enhanced_orchestrator|progress_reporter|hros_auto_start" | grep -v grep | awk '{print $2}' || true)
    
    if [ -n "$CONFLICT_PIDS" ]; then
        log "${YELLOW}⚠️  发现冲突进程:${NC}"
        echo "$CONFLICT_PIDS" | while read pid; do
            log "  PID $pid: $(ps -p $pid -o comm=)"
        done
        
        read -p "是否停止这些进程？(y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "$CONFLICT_PIDS" | while read pid; do
                kill -9 $pid 2>/dev/null || true
                log "✅ 已停止进程 $pid"
            done
        fi
    else
        log "✅ 无冲突进程"
    fi
}

# 清理规则目录
clean_rules_dir() {
    log "🧹 清理规则目录..."
    
    # 备份当前规则
    if [ -f "$RULES_DIR/scanner_rules.yar" ]; then
        TIMESTAMP=$(date +%Y%m%d_%H%M%S)
        cp "$RULES_DIR/scanner_rules.yar" "$BACKUP_DIR/scanner_rules.yar.backup_$TIMESTAMP"
        log "✅ 已备份规则到 backup_$TIMESTAMP"
    fi
    
    # 删除所有文件
    rm -rf "$RULES_DIR"/*
    
    # 恢复标准规则
    cp "/home/cdy/.openclaw/workspace/skills/security-sample-generator/rules/sigma_converted.yar" "$RULES_DIR/scanner_rules.yar"
    chmod 444 "$RULES_DIR/scanner_rules.yar"
    
    log "✅ 规则目录已清理并锁定"
}

# 锁定规则目录
lock_rules_dir() {
    log "🔒 锁定规则目录..."
    chmod 444 "$RULES_DIR/scanner_rules.yar"
    log "✅ 规则目录已锁定 (只读)"
}

# 解锁规则目录
unlock_rules_dir() {
    log "🔓 解锁规则目录..."
    chmod 644 "$RULES_DIR/scanner_rules.yar"
    log "✅ 规则目录已解锁 (可写)"
}

# 记录变更
log_change() {
    local reason="$1"
    local rule_count=$(grep -c "^rule " "$RULES_DIR/scanner_rules.yar" 2>/dev/null || echo "0")
    
    if [ ! -f "$CHANGELOG" ]; then
        echo "# 规则目录变更日志" > "$CHANGELOG"
        echo "" >> "$CHANGELOG"
    fi
    
    echo "## $(date '+%Y-%m-%d %H:%M')" >> "$CHANGELOG"
    echo "" >> "$CHANGELOG"
    echo "| 时间 | 操作 | 操作人 | 原因 | 规则数 |" >> "$CHANGELOG"
    echo "|------|------|--------|------|--------|" >> "$CHANGELOG"
    echo "| $(date '+%H:%M') | 更新 | $(whoami) | $reason | $rule_count 条 |" >> "$CHANGELOG"
    echo "" >> "$CHANGELOG"
    
    log "✅ 变更已记录到 CHANGELOG.md"
}

# 验证规则
validate_rules() {
    log "🔍 验证规则..."
    
    if python3 -c "import yara; yara.compile('$RULES_DIR/scanner_rules.yar')" 2>/dev/null; then
        log "✅ 规则验证通过"
        return 0
    else
        log "${RED}❌ 规则验证失败${NC}"
        return 1
    fi
}

# 显示状态
show_status() {
    log "📊 规则目录状态:"
    echo ""
    echo "目录：$RULES_DIR"
    echo "权限：$(ls -la "$RULES_DIR/scanner_rules.yar" 2>/dev/null | awk '{print $1}' || echo 'N/A')"
    echo "规则数：$(grep -c "^rule " "$RULES_DIR/scanner_rules.yar" 2>/dev/null || echo 'N/A')"
    echo "最后修改：$(stat -c %y "$RULES_DIR/scanner_rules.yar" 2>/dev/null || echo 'N/A')"
    echo ""
    echo "备份目录：$BACKUP_DIR"
    echo "备份数量：$(ls -1 "$BACKUP_DIR"/*.backup_* 2>/dev/null | wc -l)"
    echo ""
    echo "变更日志：$CHANGELOG"
    echo "最后更新：$(tail -1 "$CHANGELOG" 2>/dev/null | cut -d'|' -f2 || echo 'N/A')"
}

# 主菜单
show_menu() {
    echo ""
    echo -e "${GREEN}==============================================================================${NC}"
    echo -e "${GREEN}       🛡️  规则目录保护系统${NC}"
    echo -e "${GREEN}==============================================================================${NC}"
    echo ""
    echo "1. 检查冲突进程"
    echo "2. 清理规则目录"
    echo "3. 解锁规则目录"
    echo "4. 锁定规则目录"
    echo "5. 验证规则"
    echo "6. 记录变更"
    echo "7. 显示状态"
    echo "8. 退出"
    echo ""
    echo -e "${YELLOW}==============================================================================${NC}"
}

# 主循环
main() {
    # 创建备份目录
    mkdir -p "$BACKUP_DIR"
    
    while true; do
        show_menu
        read -p "请选择操作 [1-8]: " choice
        
        case $choice in
            1)
                check_conflicting_processes
                ;;
            2)
                clean_rules_dir
                ;;
            3)
                unlock_rules_dir
                ;;
            4)
                lock_rules_dir
                ;;
            5)
                validate_rules
                ;;
            6)
                read -p "变更原因： " reason
                log_change "$reason"
                ;;
            7)
                show_status
                ;;
            8)
                log "👋 再见!"
                exit 0
                ;;
            *)
                log "${RED}无效选择${NC}"
                ;;
        esac
        
        echo ""
        read -p "按回车键继续..."
    done
}

# 命令行参数处理
case "${1:-}" in
    --check)
        check_conflicting_processes
        ;;
    --clean)
        clean_rules_dir
        ;;
    --lock)
        lock_rules_dir
        ;;
    --unlock)
        unlock_rules_dir
        ;;
    --validate)
        validate_rules
        ;;
    --status)
        show_status
        ;;
    --log)
        log_change "${2:-手动更新}"
        ;;
    --help)
        echo "用法：$0 [选项]"
        echo ""
        echo "选项:"
        echo "  --check     检查冲突进程"
        echo "  --clean     清理规则目录"
        echo "  --lock      锁定规则目录"
        echo "  --unlock    解锁规则目录"
        echo "  --validate  验证规则"
        echo "  --status    显示状态"
        echo "  --log [原因] 记录变更"
        echo "  --help      显示帮助"
        echo "  (无参数)    交互模式"
        ;;
    *)
        main
        ;;
esac
