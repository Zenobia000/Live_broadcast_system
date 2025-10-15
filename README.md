# 🎯 智能簽到系統 (Smart Attendance System)

**基於事件驅動的自動化簽到與智能審核平台**

> **專案狀態**: 50% 完成 (25h/50h) | **里程碑**: 可運行的 MVP 系統 ✅ | **下個目標**: 完整功能實作 🚀

## 🎯 系統特色

- **⚡ 事件驅動自動簽到** - 整合 Google Calendar，會議開始時自動觸發簽到
- **🤖 智能遲到判斷** - 基於時間與地理位置的多維度遲到檢測
- **📝 靈活請假補簽** - 支援事前請假與事後補簽申請流程
- **🔍 智能審核系統** - 管理員可批量審核請假與補簽申請
- **📊 即時統計報表** - 個人與團隊出勤統計，支援多種報表格式
- **🔔 多渠道通知** - Email + Slack 整合，重要事件即時通知

## 🎉 **當前可用功能**

### ✅ 已實現 (MVP 階段)
- **🏗️ 基礎設施**: 完整的開發環境建置 (Docker + 資料庫)
- **📊 架構設計**: 高品質的系統架構文檔與設計
- **🔧 FastAPI 後端**: 可運行的 MVP API 服務器 (localhost:8000)
- **⚛️ React 前端**: 基本的 UI 框架與開發環境 (localhost:3000)
- **🔐 安全基礎**: 環境變數管理與 Docker 安全配置
- **🧪 測試框架**: Pytest + Vitest + Playwright 基礎設施

### 🔄 開發中
- **🔑 Google OAuth 認證**: 架構已設計，實作進行中
- **📱 前端頁面**: Steve Jobs 風格設計已完成，React 組件開發中
- **📡 API 整合**: 前後端連接與資料流建立中

### ⏳ 待開發
- **📅 Google Calendar 整合**: 事件同步與自動簽到
- **📝 請假補簽系統**: 申請流程與審核機制
- **📧 通知服務**: Email 與 Slack 整合
- **📊 報表系統**: 出勤統計與資料匯出

---

## 🚀 **快速開始**

### 1️⃣ 克隆專案
```bash
git clone <repository-url>
cd Live_broadcast_system
```

### 2️⃣ 後端環境設置
```bash
cd src/backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3️⃣ 前端環境設置
```bash
cd src/frontend
npm install
npm run dev
```

### 4️⃣ 資料庫環境啟動
```bash
cd infrastructure/docker
docker-compose up -d
```

### 5️⃣ 啟動後端服務
```bash
cd src/backend
uvicorn app.main:app --reload
```

現在您可以透過以下網址存取：
- **前端應用**: http://localhost:3000
- **後端 API**: http://localhost:8000
- **API 文檔**: http://localhost:8000/docs

## 🏗️ **技術架構**

### 🔧 **後端技術棧**
- **框架**: FastAPI + Uvicorn
- **資料庫**: PostgreSQL + SQLAlchemy + Alembic
- **快取**: Redis
- **認證**: Google OAuth 2.0 + JWT
- **API**: RESTful + OpenAPI/Swagger

### 🌟 **前端技術棧**
- **框架**: React 18 + TypeScript
- **建置工具**: Vite
- **樣式**: Tailwind CSS (Apple Human Interface Style)
- **路由**: React Router
- **API 客戶端**: Axios

### 🚀 **基礎設施**
- **容器化**: Docker + Docker Compose
- **部署**: Google Cloud Run + Vercel
- **CI/CD**: GitHub Actions
- **監控**: Cloud Logging

## 📊 **專案進度狀態**

### ✅ **已完成項目** (25% 完成)
1. **專案初始化與架構設計** (100%)
   - ✅ 專案簡報與 PRD 文檔
   - ✅ 系統架構設計文檔
   - ✅ 資料庫 ER 圖與模型設計
   - ✅ SQLAlchemy 模型定義
   - ✅ Alembic 遷移腳本

2. **開發環境建置** (100%)
   - ✅ FastAPI 後端專案結構
   - ✅ React + Vite 前端環境
   - ✅ Tailwind CSS 設計系統
   - ✅ Docker 容器化配置
   - ✅ PostgreSQL & Redis 環境

### 🔄 **進行中項目**
- 專案文檔持續更新
- API 設計規範完善

### ⏳ **待開始項目**
- 認證與授權模組 (Google OAuth 2.0)
- 自動簽到核心功能
- 前端頁面開發
- Google Calendar API 整合
- 測試框架建立

### 📅 **開發計劃**
- **Week 1**: 認證模組開發 (當前重點)
- **Week 2-3**: 自動簽到核心功能
- **Week 4**: 請假補簽流程
- **Week 5**: 前端頁面與整合
- **Week 6**: 測試與優化
- **Week 7**: 部署與上線

## 📚 **專案文檔**

### 🏗️ **架構與設計文檔**
- **[專案簡報與 PRD](docs/01_project_brief_and_prd.md)** - 專案需求與產品規格
- **[系統架構設計](docs/03_architecture_and_design_document.md)** - 完整系統架構設計
- **[API 設計規範](docs/04_api_design_specification.md)** - RESTful API 設計標準
- **[資料庫設計](docs/database_schema_design.md)** - ER 圖與資料表結構

### 📋 **開發指南**
- **[模組規格與測試](docs/05_module_specification_and_tests.md)** - 模組開發規範
- **[WBS 開發計劃](docs/06_wbs_development_plan.md)** - 完整工作分解結構
- **[專案結構指南](PROJECT_STRUCTURE.md)** - 目錄結構說明

### 🤖 **智能協作系統**
- **[TaskMaster 技術文檔](.claude/TASKMASTER_README.md)** - 智能協作系統說明
- **[跨平台相容性](.claude/CROSS_PLATFORM_COMPATIBILITY.md)** - 跨平台使用指南

## 🚀 **TaskMaster 指令系統**

### 🎛️ **核心指令**
| 指令 | 功能 | 使用時機 |
|------|------|---------|
| **`/task-status`** 📊 | 查看完整專案狀態與進度 | 隨時查看開發進度 |
| **`/task-next`** 🎯 | 獲得下個任務建議 | 不確定下步該做什麼 |
| **`/hub-delegate`** 🤖 | 智能體協作委派 | 複雜任務需要專業協助 |
| **`/review-code`** 🔍 | 程式碼品質審查 | 程式碼完成後品質檢查 |

## 🗂️ **專案目錄結構**

```
📦 智能簽到系統 (Smart Attendance System)
├── 📄 README.md                        # 專案總覽 (本檔案)
├── 📄 CLAUDE.md                        # Claude 智能協作指南
├── 📄 PROJECT_STRUCTURE.md             # 詳細專案結構說明
├── 📁 docs/                            # 專案文檔
│   ├── 📄 01_project_brief_and_prd.md      # ✅ 專案簡報與 PRD
│   ├── 📄 03_architecture_and_design_document.md # ✅ 系統架構設計
│   ├── 📄 04_api_design_specification.md   # 🔄 API 設計規範
│   ├── 📄 06_wbs_development_plan.md       # ✅ WBS 開發計劃
│   └── 📄 database_schema_design.md       # ✅ 資料庫設計
├── 📁 src/                             # 源碼目錄
│   ├── 📁 backend/                         # ✅ FastAPI 後端 (結構完成)
│   │   ├── 📁 app/                         # 應用程式主目錄
│   │   │   ├── 📁 models/                  # ✅ SQLAlchemy 資料模型
│   │   │   ├── 📁 api/v1/                  # API 路由與端點
│   │   │   ├── 📁 services/                # 業務邏輯服務層
│   │   │   └── 📁 repositories/            # 資料存取層
│   │   └── 📁 alembic/                     # ✅ 資料庫遷移
│   ├── 📁 frontend/                        # ✅ React 前端 (結構完成)
│   │   └── 📁 src/                         # ✅ 前端源碼
│   └── 📁 shared/                          # 前後端共用代碼
├── 📁 infrastructure/                   # ✅ 基礎設施 (Docker 完成)
│   └── 📁 docker/                          # ✅ Docker 容器化配置
└── 📁 .claude/                         # 🤖 Claude 智能協作系統
    ├── 📁 commands/                        # TaskMaster 指令系統
    ├── 📁 agents/                          # 專業智能體配置
    └── 📁 taskmaster-data/                 # 專案狀態資料
```

## 🔧 **開發流程**

### 📋 **功能開發工作流程**
1. **建立功能分支**: `git checkout -b feature/功能名稱`
2. **實作功能**: 遵循 Clean Architecture 分層設計
3. **撰寫測試**: 單元測試 + 整合測試
4. **程式碼審查**: 使用 `/review-code` 指令
5. **合併主分支**: 確保所有測試通過

### 🧪 **測試策略**
- **單元測試**: ≥ 80% 覆蓋率 (pytest)
- **整合測試**: API 層級測試
- **E2E 測試**: 完整使用者流程驗證

## 🚀 **下一步行動**

根據 WBS 開發計劃，當前重點任務：

### 🎯 **Week 1 優先任務**
1. **認證模組開發**
   - User 資料模型實作
   - Google OAuth 2.0 整合
   - JWT Token 機制實作

2. **前端認證頁面**
   - 登入頁面設計
   - Google OAuth 整合
   - 使用者狀態管理

3. **API 端點開發**
   - 登入/登出 API
   - 使用者資訊 API
   - 認證中間件

## 🤖 **智能協作支援**

### 🎛️ **使用 TaskMaster 指令開始開發**
```bash
# 查看當前專案狀態
/task-status

# 獲得下個任務建議
/task-next

# 委派複雜任務給專業智能體
/hub-delegate [agent-name]

# 程式碼品質審查
/review-code
```

### 🔍 **專業智能體協助**
- **test-automation-engineer**: 測試框架建立
- **security-infrastructure-auditor**: OAuth 安全檢查
- **code-quality-specialist**: 程式碼品質審查
- **documentation-specialist**: API 文檔撰寫

---

**目前進度**: 25% 完成 | **下個里程碑**: 認證模組開發 🚀

> 💡 **開發提醒**: 遵循 CLAUDE.md 中的 Linus Torvalds 開發心法，確保程式碼品質與可維護性