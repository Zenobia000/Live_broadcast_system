#!/bin/bash

# TaskMaster Post Write Hook
# 當 Claude Code 寫入檔案後觸發，特別關注文檔生成

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

# 獲取寫入的檔案路徑
FILE_PATH="$1"

log_info "🪝 Post Write Hook 觸發: $FILE_PATH (Platform: $PLATFORM)"

# 檢查是否為專案文檔
if is_project_document "$FILE_PATH"; then
    log_info "📋 專案文檔更新: $FILE_PATH"

    # 如果 TaskMaster 已初始化，觸發文檔生成完成處理
    if check_taskmaster_status "$PROJECT_ROOT"; then
        log_debug "🔔 通知 TaskMaster 文檔生成完成"
        trigger_taskmaster "$PROJECT_ROOT" "document-generated" --file="$FILE_PATH"

        # 顯示駕駛員審查提示
        show_driver_notification "📄 文檔生成完成" \
            "檔案: $(basename "$FILE_PATH")\n請檢查生成的文檔內容，確認品質。" \
            "✅ 批准: /task-review approve\n🔄 修改: /task-review revise"
    fi
fi

# 檢查是否為 VibeCoding 範本更新
if is_vibecoding_template "$FILE_PATH"; then
    log_info "🎨 VibeCoding 範本更新: $FILE_PATH"
fi

# 檢查是否為 TaskMaster 核心檔案更新
if is_taskmaster_core "$FILE_PATH"; then
    log_warning "🔧 TaskMaster 核心檔案更新: $FILE_PATH"
fi

# 檢查是否為 hooks 配置更新
if [[ "$FILE_PATH" == *"hooks-config.json"* ]] || [[ "$FILE_PATH" == *"settings.local.json"* ]]; then
    log_info "⚙️ Hooks 配置檔案更新: $FILE_PATH"
fi

log_info "✅ Post Write Hook 處理完成"
exit 0