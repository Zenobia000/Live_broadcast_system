#!/bin/bash
# start-dev.sh - 啟動智能簽到系統開發服務
# Usage: ./start-dev.sh

# 顏色設定
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 專案根目錄
PROJECT_ROOT="/home/bheadwei/Live_broadcast_system"

echo -e "${CYAN}"
echo "=========================================="
echo "  智能簽到系統 - 開發環境啟動"
echo "=========================================="
echo -e "${NC}\n"

# 函數：檢查端口是否被佔用
check_port() {
    local port=$1
    if lsof -i :$port >/dev/null 2>&1; then
        return 0  # 端口被佔用
    else
        return 1  # 端口空閒
    fi
}

# 函數：等待服務啟動
wait_for_service() {
    local url=$1
    local max_attempts=30
    local attempt=0

    while [ $attempt -lt $max_attempts ]; do
        if curl -s "$url" >/dev/null 2>&1; then
            return 0
        fi
        sleep 1
        attempt=$((attempt + 1))
        echo -n "."
    done
    echo ""
    return 1
}

# 步驟 0: 清理舊服務
echo -e "${BLUE}[0/4] 檢查並清理舊服務...${NC}"
pkill -9 -f "uvicorn app.main:app" 2>/dev/null
pkill -9 -f "vite" 2>/dev/null
pkill -9 -f "npm run dev" 2>/dev/null
sleep 2

# 檢查端口
if check_port 8000 || check_port 3000 || check_port 5173; then
    echo -e "${YELLOW}⚠️  檢測到端口仍被佔用，嘗試強制清理...${NC}"
    for port in 8000 3000 5173; do
        lsof -ti :$port 2>/dev/null | xargs kill -9 2>/dev/null
    done
    sleep 1
fi

echo -e "${GREEN}✅ 舊服務已清理${NC}\n"

# 步驟 1: 啟動後端服務
echo -e "${BLUE}[1/4] 啟動後端服務...${NC}"

# 檢查後端目錄
if [ ! -d "$PROJECT_ROOT/src/backend" ]; then
    echo -e "${RED}❌ 後端目錄不存在: $PROJECT_ROOT/src/backend${NC}"
    exit 1
fi

cd "$PROJECT_ROOT/src/backend"

# 檢查 poetry 環境
if ! command -v poetry &> /dev/null; then
    echo -e "${RED}❌ Poetry 未安裝，請先安裝 Poetry${NC}"
    exit 1
fi

# 啟動後端
nohup poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > /tmp/backend.log 2>&1 &
BACKEND_PID=$!

echo -n "等待後端啟動"
if wait_for_service "http://localhost:8000/api/v1/health"; then
    echo -e "\n${GREEN}✅ 後端服務啟動成功 (PID: $BACKEND_PID)${NC}"
    echo -e "   ${CYAN}API 地址: http://localhost:8000${NC}"
    echo -e "   ${CYAN}API 文檔: http://localhost:8000/api/docs${NC}"
    echo -e "   ${CYAN}日誌位置: /tmp/backend.log${NC}"
else
    echo -e "\n${RED}❌ 後端服務啟動失敗${NC}"
    echo -e "${YELLOW}查看日誌: tail -f /tmp/backend.log${NC}"
    exit 1
fi

# 步驟 2: 啟動前端服務
echo -e "\n${BLUE}[2/4] 啟動前端服務...${NC}"

# 檢查前端目錄
if [ ! -d "$PROJECT_ROOT/src/frontend" ]; then
    echo -e "${RED}❌ 前端目錄不存在: $PROJECT_ROOT/src/frontend${NC}"
    exit 1
fi

cd "$PROJECT_ROOT/src/frontend"

# 檢查 node_modules
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}⚠️  node_modules 不存在，正在安裝依賴...${NC}"
    npm install
fi

# 啟動前端
nohup npm run dev > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!

echo -n "等待前端啟動"
if wait_for_service "http://localhost:3000"; then
    echo -e "\n${GREEN}✅ 前端服務啟動成功 (PID: $FRONTEND_PID)${NC}"
    echo -e "   ${CYAN}應用地址: http://localhost:3000${NC}"
    echo -e "   ${CYAN}日誌位置: /tmp/frontend.log${NC}"
else
    echo -e "\n${YELLOW}⚠️  前端可能在端口 5173 啟動${NC}"
    if wait_for_service "http://localhost:5173"; then
        echo -e "${GREEN}✅ 前端服務啟動成功 (PID: $FRONTEND_PID)${NC}"
        echo -e "   ${CYAN}應用地址: http://localhost:5173${NC}"
        echo -e "   ${CYAN}日誌位置: /tmp/frontend.log${NC}"
    else
        echo -e "${RED}❌ 前端服務啟動失敗${NC}"
        echo -e "${YELLOW}查看日誌: tail -f /tmp/frontend.log${NC}"
    fi
fi

# 步驟 3: 健康檢查
echo -e "\n${BLUE}[3/4] 健康檢查...${NC}"

BACKEND_HEALTH=$(curl -s http://localhost:8000/api/v1/health 2>/dev/null)
if echo "$BACKEND_HEALTH" | grep -q "ok"; then
    echo -e "${GREEN}✅ 後端健康檢查通過${NC}"
else
    echo -e "${RED}❌ 後端健康檢查失敗${NC}"
fi

if curl -s http://localhost:3000 >/dev/null 2>&1 || curl -s http://localhost:5173 >/dev/null 2>&1; then
    echo -e "${GREEN}✅ 前端健康檢查通過${NC}"
else
    echo -e "${RED}❌ 前端健康檢查失敗${NC}"
fi

# 步驟 4: 顯示摘要
echo -e "\n${BLUE}[4/4] 服務啟動摘要${NC}"
echo -e "${CYAN}=========================================="
echo -e "  服務狀態總覽"
echo -e "==========================================${NC}"

# 後端狀態
if check_port 8000; then
    echo -e "${GREEN}✅ 後端 API${NC}"
    echo -e "   地址: http://localhost:8000"
    echo -e "   文檔: http://localhost:8000/api/docs"
    echo -e "   PID: $BACKEND_PID"
else
    echo -e "${RED}❌ 後端未運行${NC}"
fi

echo ""

# 前端狀態
if check_port 3000; then
    echo -e "${GREEN}✅ 前端應用${NC}"
    echo -e "   地址: http://localhost:3000"
    echo -e "   PID: $FRONTEND_PID"
elif check_port 5173; then
    echo -e "${GREEN}✅ 前端應用${NC}"
    echo -e "   地址: http://localhost:5173"
    echo -e "   PID: $FRONTEND_PID"
else
    echo -e "${RED}❌ 前端未運行${NC}"
fi

# 日誌查看指令
echo -e "\n${YELLOW}=========================================="
echo -e "  日誌查看指令"
echo -e "==========================================${NC}"
echo -e "後端日誌: ${CYAN}tail -f /tmp/backend.log${NC}"
echo -e "前端日誌: ${CYAN}tail -f /tmp/frontend.log${NC}"

# 停止服務指令
echo -e "\n${YELLOW}=========================================="
echo -e "  停止服務"
echo -e "==========================================${NC}"
echo -e "執行: ${CYAN}./stop-dev.sh${NC}"

echo -e "\n${GREEN}🚀 開發環境已就緒！${NC}\n"

# 返回專案根目錄
cd "$PROJECT_ROOT"
