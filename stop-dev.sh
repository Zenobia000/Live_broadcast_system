#!/bin/bash
# stop-dev.sh - 停止智能簽到系統開發服務
# Usage: ./stop-dev.sh

# 顏色設定
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}  停止智能簽到系統開發服務${NC}"
echo -e "${YELLOW}========================================${NC}\n"

# 函數：檢查端口是否被佔用
check_port() {
    local port=$1
    if lsof -i :$port >/dev/null 2>&1; then
        return 0  # 端口被佔用
    else
        return 1  # 端口空閒
    fi
}

# 停止後端服務
echo -e "${BLUE}[1/3] 停止後端服務 (port 8000)...${NC}"
pkill -9 -f "uvicorn app.main:app" 2>/dev/null
sleep 1

if check_port 8000; then
    echo -e "${RED}⚠️  後端端口 8000 仍在使用，嘗試強制結束...${NC}"
    lsof -ti :8000 | xargs kill -9 2>/dev/null
    sleep 1
fi

if ! check_port 8000; then
    echo -e "${GREEN}✅ 後端服務已停止${NC}"
else
    echo -e "${RED}❌ 後端服務停止失敗${NC}"
fi

# 停止前端服務
echo -e "\n${BLUE}[2/3] 停止前端服務 (port 3000/5173)...${NC}"
pkill -9 -f "vite" 2>/dev/null
pkill -9 -f "npm run dev" 2>/dev/null
sleep 1

# 檢查前端端口
FRONTEND_STOPPED=true
for port in 3000 5173; do
    if check_port $port; then
        echo -e "${RED}⚠️  前端端口 $port 仍在使用，嘗試強制結束...${NC}"
        lsof -ti :$port | xargs kill -9 2>/dev/null
        sleep 1
        if check_port $port; then
            FRONTEND_STOPPED=false
        fi
    fi
done

if [ "$FRONTEND_STOPPED" = true ]; then
    echo -e "${GREEN}✅ 前端服務已停止${NC}"
else
    echo -e "${RED}❌ 部分前端服務停止失敗${NC}"
fi

# 清理日誌文件（可選）
echo -e "\n${BLUE}[3/3] 清理日誌...${NC}"
if [ -f /tmp/backend.log ]; then
    rm /tmp/backend.log
    echo -e "${GREEN}✅ 已清理後端日誌${NC}"
fi
if [ -f /tmp/frontend.log ]; then
    rm /tmp/frontend.log
    echo -e "${GREEN}✅ 已清理前端日誌${NC}"
fi

# 最終狀態報告
echo -e "\n${YELLOW}========================================${NC}"
echo -e "${YELLOW}  最終狀態${NC}"
echo -e "${YELLOW}========================================${NC}"

ALL_STOPPED=true

# 檢查後端
if ! check_port 8000; then
    echo -e "${GREEN}✅ 後端 (8000): 已停止${NC}"
else
    echo -e "${RED}❌ 後端 (8000): 仍在運行${NC}"
    ALL_STOPPED=false
fi

# 檢查前端
if ! check_port 3000 && ! check_port 5173; then
    echo -e "${GREEN}✅ 前端 (3000/5173): 已停止${NC}"
else
    echo -e "${RED}❌ 前端: 仍在運行${NC}"
    ALL_STOPPED=false
fi

echo ""
if [ "$ALL_STOPPED" = true ]; then
    echo -e "${GREEN}🎉 所有服務已成功停止！${NC}"
    exit 0
else
    echo -e "${RED}⚠️  部分服務停止失敗，請手動檢查${NC}"
    echo -e "\n${YELLOW}檢查命令：${NC}"
    echo "  lsof -i :8000  # 檢查後端"
    echo "  lsof -i :3000  # 檢查前端"
    echo "  ps aux | grep -E '(uvicorn|vite)' | grep -v grep"
    exit 1
fi
