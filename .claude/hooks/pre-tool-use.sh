#!/bin/bash

# TaskMaster Pre Tool Use Hook
# 在工具使用前檢查 TaskMaster 狀態並提供上下文

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

# 獲取工具名稱和參數
TOOL_NAME="$1"
TOOL_ARGS="$2"

log_info "🪝 Pre Tool Use Hook 觸發: $TOOL_NAME (Platform: $PLATFORM)"
log_debug "工具參數: $TOOL_ARGS"

# 如果 TaskMaster 已初始化，提供當前狀態上下文
show_taskmaster_summary "$PROJECT_ROOT"

# 特定工具的預處理
case "$TOOL_NAME" in
    "Write"|"edit_file")
        log_info "📝 工具 ($TOOL_NAME) 即將寫入/編輯檔案"
        # 檢查是否為文檔目錄寫入
        if is_project_document "$TOOL_ARGS"; then
            log_info "📄 即將寫入專案文檔，寫入後將觸發審查流程"
        elif is_taskmaster_core "$TOOL_ARGS"; then
            log_warning "⚙️ 即將編輯 TaskMaster 核心檔案"
        fi
        ;;

    "Read"|"read_file")
        log_info "📖 工具 ($TOOL_NAME) 即將讀取檔案"
        # 如果讀取 VibeCoding 範本，提供上下文
        if is_vibecoding_template "$TOOL_ARGS"; then
            log_info "🎨 即將讀取 VibeCoding 範本"
        fi
        ;;

    "Task"|"todo_write")
        log_info "🤖 工具 ($TOOL_NAME) 即將變更任務列表"
        # 提供智能體協調上下文
        if check_taskmaster_status "$PROJECT_ROOT"; then
            log_info "🤖 TaskMaster Hub 協調模式啟用，所有委派將記錄在 WBS Todo List"
        fi
        ;;
esac

log_info "✅ Pre Tool Use Hook 處理完成"
exit 0