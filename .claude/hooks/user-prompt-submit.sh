#!/bin/bash

# TaskMaster User Prompt Submit Hook
# 當用戶提交 prompt 時檢查是否包含 TaskMaster 相關命令

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# 載入共用工具函數
# shellcheck source=.claude/hooks/hook-utils.sh
if [ -f "$SCRIPT_DIR/hook-utils.sh" ]; then
    source "$SCRIPT_DIR/hook-utils.sh"
else
    echo "❌ [ERROR] Hook utilities not found at $SCRIPT_DIR/hook-utils.sh" >&2
    exit 0
fi

# 平台檢測與執行選項設定
PLATFORM=$(detect_platform)
set_execution_options "$PLATFORM"

CLAUDE_DIR="$PROJECT_ROOT/.claude"

# 獲取用戶輸入（如果有的話）
USER_INPUT="$1"

log_info "🪝 User Prompt Submit Hook 觸發 (Platform: $PLATFORM)"
log_debug "用戶輸入: $USER_INPUT"

# 檢查用戶輸入是否包含 TaskMaster 相關命令
if [[ "$USER_INPUT" == *"/task-"* ]]; then
    log_info "🎯 偵測到 TaskMaster 命令: $USER_INPUT"

    # 觸發 TaskMaster 處理器
    trigger_taskmaster "$PROJECT_ROOT" "user-prompt" --message="$USER_INPUT"

    exit 0
fi

# 檢查是否包含文檔相關操作
if [[ "$USER_INPUT" == *"docs/"* ]] || [[ "$USER_INPUT" == *".md"* ]]; then
    log_info "📄 偵測到文檔相關操作"

    # 如果 TaskMaster 已初始化，觸發狀態檢查
    if check_taskmaster_status "$PROJECT_ROOT"; then
        log_debug "🔄 TaskMaster 已初始化，觸發文檔相關操作處理"
        trigger_taskmaster "$PROJECT_ROOT" "document-related" --message="$USER_INPUT"
    fi
fi

log_info "✅ User Prompt Submit Hook 處理完成"
exit 0