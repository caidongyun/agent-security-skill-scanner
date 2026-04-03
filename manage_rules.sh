#!/bin/bash
##############################################
# 规则版本管理系统 v1.0
# Rules Version Management System
#
# 功能:
# 1. 创建规则版本目录 (rules/v1.0/, v1.1/, etc.)
# 2. 备份和恢复规则
# 3. 版本比较
# 4. CHANGELOG 管理
##############################################

set -e

# 配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RULES_DIR="${SCRIPT_DIR}/rules"
VERSIONS_DIR="${RULES_DIR}/versions"
CHANGELOG_FILE="${RULES_DIR}/CHANGELOG.md"

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

##############################################
# 1. 创建新版本
##############################################

create_version() {
    local version="$1"
    local description="$2"
    
    if [ -z "$version" ]; then
        log_error "请提供版本号 (例如：v1.0, v1.1)"
        echo "用法：$0 version <version> [description]"
        exit 1
    fi
    
    # 验证版本号格式
    if ! [[ "$version" =~ ^v[0-9]+\.[0-9]+(\.[0-9]+)?$ ]]; then
        log_error "版本号格式不正确，应为：v1.0, v1.1, v2.0.1 等"
        exit 1
    fi
    
    local version_dir="${VERSIONS_DIR}/${version}"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    # 检查版本是否已存在
    if [ -d "$version_dir" ]; then
        log_error "版本已存在：$version"
        log_info "现有版本目录：$version_dir"
        echo "如需覆盖，请先删除：rm -rf $version_dir"
        exit 1
    fi
    
    log_info "创建版本：$version"
    
    # 创建版本目录
    mkdir -p "$version_dir"
    
    # 复制当前规则
    log_info "复制规则文件..."
    cp -r "$RULES_DIR"/*.yaml "$version_dir/" 2>/dev/null || true
    cp -r "$RULES_DIR"/*.json "$version_dir/" 2>/dev/null || true
    cp -r "$RULES_DIR"/*.yar "$version_dir/" 2>/dev/null || true
    
    # 复制 sigma 和 yara 目录
    [ -d "$RULES_DIR/sigma" ] && cp -r "$RULES_DIR/sigma" "$version_dir/"
    [ -d "$RULES_DIR/yara" ] && cp -r "$RULES_DIR/yara" "$version_dir/"
    
    # 创建版本元数据
    cat > "${version_dir}/VERSION_INFO.json" << EOF
{
  "version": "$version",
  "created_at": "$timestamp",
  "description": "$description",
  "rule_count": $(find "$version_dir" -type f \( -name "*.yaml" -o -name "*.json" -o -name "*.yar" \) | wc -l),
  "files": [
$(find "$version_dir" -type f \( -name "*.yaml" -o -name "*.json" -o -name "*.yar" \) -exec basename {} \; | sort | sed 's/^/    "/;s/$/",/' | sed '$ s/,$//')
  ]
}
EOF
    
    # 更新 CHANGELOG
    update_changelog "$version" "$description"
    
    log_success "版本 $version 创建成功!"
    log_info "版本目录：$version_dir"
    log_info "规则数量：$(find "$version_dir" -type f \( -name "*.yaml" -o -name "*.json" -o -name "*.yar" \) | wc -l)"
}

##############################################
# 2. 更新 CHANGELOG
##############################################

update_changelog() {
    local version="$1"
    local description="$2"
    local timestamp=$(date '+%Y-%m-%d')
    
    # 如果 CHANGELOG 不存在，创建它
    if [ ! -f "$CHANGELOG_FILE" ]; then
        cat > "$CHANGELOG_FILE" << EOF
# 规则变更日志 (CHANGELOG)

本文档记录规则系统的所有重要变更。

## 格式说明

- **Added**: 新增功能
- **Changed**: 变更现有功能
- **Deprecated**: 即将移除的功能
- **Removed**: 已移除的功能
- **Fixed**: 修复的问题
- **Security**: 安全相关的修复

---

EOF
    fi
    
    # 读取当前 CHANGELOG 内容（跳过开头部分）
    local temp_file=$(mktemp)
    
    cat > "$temp_file" << EOF
# 规则变更日志 (CHANGELOG)

本文档记录规则系统的所有重要变更。

## 格式说明

- **Added**: 新增功能
- **Changed**: 变更现有功能
- **Deprecated**: 即将移除的功能
- **Removed**: 已移除的功能
- **Fixed**: 修复的问题
- **Security**: 安全相关的修复

---

## [$version] - $timestamp

### Description
$description

### Changes
- 规则版本化保存
- 性能优化
- 质量门禁集成

EOF
    
    # 添加旧内容（跳过前面的标题部分）
    if [ -f "$CHANGELOG_FILE" ]; then
        tail -n +16 "$CHANGELOG_FILE" >> "$temp_file" 2>/dev/null || true
    fi
    
    mv "$temp_file" "$CHANGELOG_FILE"
    
    log_success "CHANGELOG 已更新"
}

##############################################
# 3. 列出版本
##############################################

list_versions() {
    log_info "可用版本列表:"
    echo ""
    
    if [ ! -d "$VERSIONS_DIR" ]; then
        log_warning "暂无版本目录"
        return
    fi
    
    # 获取所有版本目录并排序
    local versions=($(ls -1 "$VERSIONS_DIR" | grep -E '^v[0-9]+\.[0-9]+' | sort -V))
    
    if [ ${#versions[@]} -eq 0 ]; then
        log_warning "未找到任何版本"
        return
    fi
    
    printf "%-15s %-20s %s\n" "VERSION" "CREATED" "RULES"
    printf "%-15s %-20s %s\n" "-------" "-------" "-----"
    
    for version in "${versions[@]}"; do
        local version_dir="${VERSIONS_DIR}/${version}"
        local created=$(stat -c '%y' "$version_dir" 2>/dev/null | cut -d' ' -f1)
        local rule_count=$(find "$version_dir" -type f \( -name "*.yaml" -o -name "*.json" -o -name "*.yar" \) 2>/dev/null | wc -l)
        
        printf "%-15s %-20s %s\n" "$version" "$created" "$rule_count"
    done
    
    echo ""
    log_info "版本目录：$VERSIONS_DIR"
}

##############################################
# 4. 恢复版本
##############################################

restore_version() {
    local version="$1"
    
    if [ -z "$version" ]; then
        log_error "请提供版本号"
        echo "用法：$0 restore <version>"
        list_versions
        exit 1
    fi
    
    local version_dir="${VERSIONS_DIR}/${version}"
    
    if [ ! -d "$version_dir" ]; then
        log_error "版本不存在：$version"
        list_versions
        exit 1
    fi
    
    log_warning "此操作将覆盖当前规则!"
    log_info "建议先备份当前规则：$0 backup manual_backup"
    
    read -p "确定要恢复版本 $version 吗？(y/N): " confirm
    if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
        log_info "操作已取消"
        exit 0
    fi
    
    # 备份当前规则
    local backup_dir="${VERSIONS_DIR}/backup_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$backup_dir"
    cp -r "$RULES_DIR"/*.yaml "$backup_dir/" 2>/dev/null || true
    cp -r "$RULES_DIR"/*.json "$backup_dir/" 2>/dev/null || true
    cp -r "$RULES_DIR"/*.yar "$backup_dir/" 2>/dev/null || true
    
    log_info "当前规则已备份到：$backup_dir"
    
    # 恢复版本
    log_info "恢复版本 $version..."
    cp "$version_dir"/*.yaml "$RULES_DIR/" 2>/dev/null || true
    cp "$version_dir"/*.json "$RULES_DIR/" 2>/dev/null || true
    cp "$version_dir"/*.yar "$RULES_DIR/" 2>/dev/null || true
    
    [ -d "$version_dir/sigma" ] && cp -r "$version_dir/sigma" "$RULES_DIR/"
    [ -d "$version_dir/yara" ] && cp -r "$version_dir/yara" "$RULES_DIR/"
    
    log_success "版本 $version 恢复成功!"
}

##############################################
# 5. 比较版本
##############################################

compare_versions() {
    local version1="$1"
    local version2="$2"
    
    if [ -z "$version1" ] || [ -z "$version2" ]; then
        log_error "请提供两个版本号"
        echo "用法：$0 compare <version1> <version2>"
        exit 1
    fi
    
    local dir1="${VERSIONS_DIR}/${version1}"
    local dir2="${VERSIONS_DIR}/${version2}"
    
    if [ ! -d "$dir1" ]; then
        log_error "版本不存在：$version1"
        exit 1
    fi
    
    if [ ! -d "$dir2" ]; then
        log_error "版本不存在：$version2"
        exit 1
    fi
    
    log_info "比较版本：$version1 vs $version2"
    echo ""
    
    # 使用 diff 比较
    local diff_report="${VERSIONS_DIR}/diff_${version1}_vs_${version2}.txt"
    
    diff -rq "$dir1" "$dir2" > "$diff_report" 2>&1 || true
    
    if [ -s "$diff_report" ]; then
        log_info "差异报告已保存：$diff_report"
        echo ""
        echo "文件差异:"
        cat "$diff_report"
    else
        log_success "两个版本内容完全相同"
    fi
    
    # 统计差异
    local count1=$(find "$dir1" -type f \( -name "*.yaml" -o -name "*.json" -o -name "*.yar" \) | wc -l)
    local count2=$(find "$dir2" -type f \( -name "*.yaml" -o -name "*.json" -o -name "*.yar" \) | wc -l)
    
    echo ""
    echo "统计:"
    echo "  $version1: $count1 规则文件"
    echo "  $version2: $count2 规则文件"
    echo "  差异：$((count2 - count1))"
}

##############################################
# 6. 删除版本
##############################################

delete_version() {
    local version="$1"
    
    if [ -z "$version" ]; then
        log_error "请提供版本号"
        exit 1
    fi
    
    local version_dir="${VERSIONS_DIR}/${version}"
    
    if [ ! -d "$version_dir" ]; then
        log_error "版本不存在：$version"
        exit 1
    fi
    
    log_warning "此操作将永久删除版本 $version"
    
    read -p "确定要删除版本 $version 吗？(y/N): " confirm
    if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
        log_info "操作已取消"
        exit 0
    fi
    
    rm -rf "$version_dir"
    log_success "版本 $version 已删除"
}

##############################################
# 7. 备份当前规则
##############################################

backup_current() {
    local name="${1:-backup_$(date +%Y%m%d_%H%M%S)}"
    local backup_dir="${VERSIONS_DIR}/${name}"
    
    mkdir -p "$backup_dir"
    
    log_info "备份当前规则到：$backup_dir"
    
    cp -r "$RULES_DIR"/*.yaml "$backup_dir/" 2>/dev/null || true
    cp -r "$RULES_DIR"/*.json "$backup_dir/" 2>/dev/null || true
    cp -r "$RULES_DIR"/*.yar "$backup_dir/" 2>/dev/null || true
    
    [ -d "$RULES_DIR/sigma" ] && cp -r "$RULES_DIR/sigma" "$backup_dir/"
    [ -d "$RULES_DIR/yara" ] && cp -r "$RULES_DIR/yara" "$backup_dir/"
    
    local rule_count=$(find "$backup_dir" -type f \( -name "*.yaml" -o -name "*.json" -o -name "*.yar" \) | wc -l)
    
    log_success "备份完成：$rule_count 个规则文件"
    log_info "备份位置：$backup_dir"
}

##############################################
# 帮助信息
##############################################

show_help() {
    cat << EOF
规则版本管理系统 v1.0

用法：$0 <command> [arguments]

命令:
  version <ver> [desc]  创建新版本 (例如：v1.0)
  list                  列出所有版本
  restore <ver>         恢复指定版本
  compare <v1> <v2>     比较两个版本
  delete <ver>          删除指定版本
  backup [name]         备份当前规则
  changelog             查看变更日志
  help                  显示此帮助信息

示例:
  $0 version v1.1 "优化检测率和误报率"
  $0 list
  $0 restore v1.0
  $0 compare v1.0 v1.1
  $0 backup manual_backup_2026

质量门禁标准:
  - 检测率 ≥80%
  - 误报率 <10%
  - F1 Score ≥85%
  - 单规则扫描 <10ms
  - 千规则扫描 <100ms

EOF
}

##############################################
# 主入口
##############################################

main() {
    local command="${1:-help}"
    shift || true
    
    case "$command" in
        version)
            create_version "$@"
            ;;
        list)
            list_versions
            ;;
        restore)
            restore_version "$@"
            ;;
        compare)
            compare_versions "$@"
            ;;
        delete)
            delete_version "$@"
            ;;
        backup)
            backup_current "$@"
            ;;
        changelog)
            if [ -f "$CHANGELOG_FILE" ]; then
                cat "$CHANGELOG_FILE"
            else
                log_info "CHANGELOG 不存在"
            fi
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "未知命令：$command"
            show_help
            exit 1
            ;;
    esac
}

main "$@"
