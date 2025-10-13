#!/bin/bash

# TaskMaster Session Start Hook
# 當 Claude Code 會話開始時自動執行
# 跨平台支援：Windows (Git Bash)、Windows WSL、macOS、Linux

# ============================================================================
# 初始化與環境設定
# ============================================================================

# 跨平台路徑處理
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." 2>/dev/null && pwd)"

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

# 路徑驗證
if [ -z "$PROJECT_ROOT" ] || [ -z "$CLAUDE_DIR" ]; then
    log_error "無法確定專案路徑 (Platform: $PLATFORM)"
    exit 0
fi

log_info "🪝 TaskMaster Session Start Hook 觸發 (Platform: $PLATFORM)"

# 檢查是否存在 CLAUDE_TEMPLATE.md
if [ -f "$PROJECT_ROOT/CLAUDE_TEMPLATE.md" ]; then
    log_info "📄 偵測到 CLAUDE_TEMPLATE.md"

    # 檢查是否已經初始化過
    if [ ! -f "$CLAUDE_DIR/taskmaster-data/project.json" ]; then
        log_info "🚀 準備自動觸發 TaskMaster 初始化"

        # 顯示提示訊息（Jobs 式極簡設計）
        echo ""
        echo -e "\033[1;37m╭─────────────────────────────────────────────────────────────╮\033[0m"
        echo -e "\033[1;37m│\033[0m                                                             \033[1;37m│\033[0m"
        echo -e "\033[1;37m│\033[0m     \033[1;97m🚀 TaskMaster Ready\033[0m                                  \033[1;37m│\033[0m"
        echo -e "\033[1;37m│\033[0m                                                             \033[1;37m│\033[0m"
        echo -e "\033[1;37m│\033[0m     \033[0;90mTemplate detected. Start with:\033[0m                      \033[1;37m│\033[0m"
        echo -e "\033[1;37m│\033[0m     \033[1;36m/task-init [project-name]\033[0m                           \033[1;37m│\033[0m"
        echo -e "\033[1;37m│\033[0m                                                             \033[1;37m│\033[0m"
        echo -e "\033[1;37m├─────────────────────────────────────────────────────────────┤\033[0m"
        echo -e "\033[1;37m│\033[0m \033[1;97mWorkflow\033[0m                                                   \033[1;37m│\033[0m"
        echo -e "\033[1;37m│\033[0m                                                             \033[1;37m│\033[0m"
        echo -e "\033[1;37m│\033[0m   \033[1;32m①\033[0m  \033[0;37mCollect requirements\033[0m           \033[0;90m→ Human review\033[0m    \033[1;37m│\033[0m"
        echo -e "\033[1;37m│\033[0m   \033[1;33m②\033[0m  \033[0;37mGenerate project docs\033[0m          \033[0;90m→ Quality gate\033[0m    \033[1;37m│\033[0m"
        echo -e "\033[1;37m│\033[0m   \033[1;36m③\033[0m  \033[0;37mStart development\033[0m              \033[0;90m→ After approval\033[0m  \033[1;37m│\033[0m"
        echo -e "\033[1;37m│\033[0m                                                             \033[1;37m│\033[0m"
        echo -e "\033[1;37m╰─────────────────────────────────────────────────────────────╯\033[0m"
        echo ""

        # 觸發 TaskMaster Node.js 處理器
        trigger_taskmaster "$PROJECT_ROOT" "session-start"
        exit 0
    else
        log_info "ℹ️ TaskMaster 已初始化，顯示狀態摘要"
        show_taskmaster_summary "$PROJECT_ROOT"
        exit 0
    fi
else
    log_info "ℹ️ 未偵測到 CLAUDE_TEMPLATE.md，TaskMaster 待命中"
    exit 0
fi