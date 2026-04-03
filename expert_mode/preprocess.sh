#!/bin/bash
#
# Agent Security Skill Scanner - 预处理脚本
# 功能：状态文件锁保护 + 大文件预处理
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# ============ 状态文件锁保护 ============
setup_state_locks() {
    log_info "设置状态文件锁保护..."
    
    local state_files=(
        ".lingshun_daemon_state.json"
        ".lingshun_optimizer_state.json"
        ".joint_research_state.json"
        ".lingshun_state.json"
    )
    
    for state_file in "${state_files[@]}"; do
        if [[ -f "$state_file" ]]; then
            # 创建锁文件（如果不存在）
            lock_file="${state_file}.lock"
            if [[ ! -f "$lock_file" ]]; then
                touch "$lock_file"
                log_success "创建锁文件：$lock_file"
            fi
            
            # 设置权限
            chmod 644 "$state_file"
            chmod 644 "$lock_file"
        fi
    done
    
    log_success "状态文件锁保护完成"
}

# ============ 大文件预处理 ============
preprocess_large_files() {
    log_info "预处理大文件..."
    
    # 定义大文件
    local large_files=(
        "kb_index.json"
        "knowledge_base.json"
    )
    
    local backup_dir="file_backups"
    mkdir -p "$backup_dir"
    
    for file in "${large_files[@]}"; do
        if [[ -f "$file" ]]; then
            local size=$(du -h "$file" | cut -f1)
            log_info "处理文件：$file ($size)"
            
            # 备份
            local timestamp=$(date +%Y%m%d_%H%M%S)
            local backup_name="${file%.json}_${timestamp}.json"
            cp "$file" "$backup_dir/$backup_name"
            log_success "备份：$backup_dir/$backup_name"
            
            # 压缩（如果 >10MB）
            local size_bytes=$(stat -c%s "$file" 2>/dev/null || stat -f%z "$file")
            if [[ $size_bytes -gt 10485760 ]]; then
                log_info "压缩文件（>10MB）..."
                gzip -k "$file"
                log_success "压缩完成：${file}.gz"
            fi
        else
            log_warn "文件不存在：$file"
        fi
    done
    
    # 清理旧备份（保留最近 5 个）
    log_info "清理旧备份..."
    for pattern in "kb_index_*.json" "knowledge_base_*.json"; do
        local count=$(ls -1 "$backup_dir"/$pattern 2>/dev/null | wc -l)
        if [[ $count -gt 5 ]]; then
            ls -1t "$backup_dir"/$pattern | tail -n +6 | xargs rm -f
            log_success "清理旧备份：$pattern"
        fi
    done
    
    log_success "大文件预处理完成"
}

# ============ 分片处理 ============
create_shards() {
    log_info "创建文件分片..."
    
    local shards_dir="shards"
    mkdir -p "$shards_dir"
    
    # 为 kb_index.json 创建分片（按 attack_type）
    if [[ -f "kb_index.json" ]]; then
        python3 -c "
import json
from pathlib import Path

with open('kb_index.json', 'r') as f:
    data = json.load(f)

if isinstance(data, list):
    shards = {}
    for item in data:
        key = item.get('attack_type', 'unknown')
        if key not in shards:
            shards[key] = []
        shards[key].append(item)
    
    for key, items in shards.items():
        shard_path = Path('shards') / f'kb_index_{key}.json'
        with open(shard_path, 'w') as f:
            json.dump(items, f, ensure_ascii=False, indent=2)
        print(f'创建分片：{shard_path} ({len(items)} 条)')
else:
    print('kb_index.json 不是列表格式，跳过分片')
"
        log_success "分片创建完成"
    else
        log_warn "kb_index.json 不存在，跳过分片"
    fi
}

# ============ 状态验证 ============
validate_states() {
    log_info "验证状态文件..."
    
    local state_files=(
        ".lingshun_daemon_state.json"
        ".lingshun_optimizer_state.json"
        ".joint_research_state.json"
    )
    
    local all_valid=true
    
    for state_file in "${state_files[@]}"; do
        if [[ -f "$state_file" ]]; then
            # 检查 JSON 有效性
            if python3 -c "import json; json.load(open('$state_file'))" 2>/dev/null; then
                log_success "有效：$state_file"
            else
                log_error "无效 JSON: $state_file"
                all_valid=false
            fi
            
            # 检查锁文件
            lock_file="${state_file}.lock"
            if [[ -f "$lock_file" ]]; then
                log_success "锁文件存在：$lock_file"
            else
                log_warn "锁文件缺失：$lock_file"
            fi
        else
            log_warn "状态文件不存在：$state_file"
        fi
    done
    
    if $all_valid; then
        log_success "所有状态文件验证通过"
    else
        log_error "部分状态文件验证失败"
        return 1
    fi
}

# ============ 主函数 ============
show_usage() {
    cat << EOF
用法：$0 <命令>

命令:
  setup       设置状态文件锁保护
  preprocess  预处理大文件（备份 + 压缩）
  shard       创建文件分片
  validate    验证状态文件
  all         执行全部预处理（推荐）
  status      显示当前状态

示例:
  $0 all      # 执行完整预处理流程
  $0 status   # 查看当前文件状态

EOF
}

show_status() {
    echo ""
    echo "=== 状态文件 ==="
    for f in .lingshun_*.json .joint_*.json; do
        if [[ -f "$f" ]]; then
            local size=$(du -h "$f" | cut -f1)
            local lock_status="🔓"
            [[ -f "${f}.lock" ]] && lock_status="🔒"
            echo "  $lock_status $f ($size)"
        fi
    done
    
    echo ""
    echo "=== 大文件 ==="
    for f in kb_index.json knowledge_base.json; do
        if [[ -f "$f" ]]; then
            local size=$(du -h "$f" | cut -f1)
            local compressed="❌"
            [[ -f "${f}.gz" ]] && compressed="✅"
            echo "  压缩：$compressed  $f ($size)"
        fi
    done
    
    echo ""
    echo "=== 备份目录 ==="
    if [[ -d "file_backups" ]]; then
        local count=$(ls -1 file_backups/*.json 2>/dev/null | wc -l)
        local size=$(du -sh file_backups 2>/dev/null | cut -f1)
        echo "  备份数量：$count"
        echo "  备份大小：$size"
    else
        echo "  无备份目录"
    fi
    
    echo ""
    echo "=== 分片目录 ==="
    if [[ -d "shards" ]]; then
        local count=$(find shards -name "*.json" | wc -l)
        local size=$(du -sh shards 2>/dev/null | cut -f1)
        echo "  分片数量：$count"
        echo "  分片大小：$size"
    else
        echo "  无分片目录"
    fi
    
    echo ""
}

main() {
    case "${1:-}" in
        setup)
            setup_state_locks
            ;;
        preprocess)
            preprocess_large_files
            ;;
        shard)
            create_shards
            ;;
        validate)
            validate_states
            ;;
        all)
            log_info "=== 开始完整预处理流程 ==="
            echo ""
            setup_state_locks
            echo ""
            preprocess_large_files
            echo ""
            create_shards
            echo ""
            validate_states
            echo ""
            log_success "=== 预处理完成 ==="
            show_status
            ;;
        status)
            show_status
            ;;
        *)
            show_usage
            ;;
    esac
}

main "$@"
