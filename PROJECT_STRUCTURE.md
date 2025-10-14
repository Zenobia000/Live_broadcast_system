# 📁 智能簽到系統 - 專案結構總覽

## 🎯 專案結構說明

本專案為基於事件驅動的自動化簽到與智能審核平台，以下是當前的完整目錄結構：

```
📦 智能簽到系統 (Smart Attendance System)
├── 📄 README.md                        # 🏠 專案總覽和快速開始
├── 📄 CLAUDE.md                        # ⭐ Claude 專案指南 (智能協作配置)
├── 📄 PROJECT_STRUCTURE.md             # 📁 本檔案：專案結構說明
├── 📄 .gitignore                       # 🚫 Git 忽略檔案配置
├── 📄 .mcp.json                        # 🔧 MCP 服務配置
├── 📁 docs/                            # 📚 專案文檔
│   ├── 📄 01_project_brief_and_prd.md      # 專案簡報與 PRD
│   ├── 📄 03_architecture_and_design_document.md # 架構與設計文檔
│   ├── 📄 04_api_design_specification.md   # API 設計規範
│   ├── 📄 05_module_specification_and_tests.md # 模組規格與測試
│   ├── 📄 06_wbs_development_plan.md       # WBS 開發計劃
│   ├── 📄 06_project_structure_guide.md   # 專案結構指南
│   ├── 📄 database_schema_design.md       # 資料庫設計文檔
│   └── 📁 adr/                             # 架構決策記錄
│       ├── 📄 README.md                    # ADR 索引
│       └── 📄 ADR-001-tech-stack-selection.md # 技術棧選型決策
├── 📁 src/                             # 🏗️ 源碼目錄
│   ├── 📁 backend/                         # 🔧 FastAPI 後端
│   │   ├── 📁 app/                         # 應用程式主目錄
│   │   │   ├── 📄 main.py                  # FastAPI 應用入口
│   │   │   ├── 📁 api/                     # API 層
│   │   │   │   ├── 📁 dependencies/         # API 依賴注入
│   │   │   │   └── 📁 v1/                   # v1 API 版本
│   │   │   │       ├── 📁 endpoints/        # API 端點
│   │   │   │       └── 📁 schemas/          # Pydantic 資料模型
│   │   │   ├── 📁 core/                    # 核心配置
│   │   │   ├── 📁 config/                  # 配置管理
│   │   │   ├── 📁 models/                  # ✅ SQLAlchemy 資料模型 (已完成)
│   │   │   │   ├── 📄 __init__.py          # 模型匯出
│   │   │   │   ├── 📄 base.py              # 基礎模型類別
│   │   │   │   ├── 📄 enums.py             # 列舉類型定義
│   │   │   │   ├── 📁 auth/                # 認證相關模型
│   │   │   │   ├── 📁 attendance/          # 出勤相關模型
│   │   │   │   ├── 📁 calendar/            # 行事曆相關模型
│   │   │   │   └── 📁 notification/        # 通知相關模型
│   │   │   ├── 📁 services/                # 業務邏輯服務層
│   │   │   │   ├── 📁 auth/                # 認證服務
│   │   │   │   ├── 📁 attendance/          # 出勤服務
│   │   │   │   ├── 📁 calendar/            # 行事曆服務
│   │   │   │   └── 📁 notification/        # 通知服務
│   │   │   ├── 📁 repositories/            # 資料存取層
│   │   │   │   ├── 📁 auth/                # 認證資料存取
│   │   │   │   ├── 📁 attendance/          # 出勤資料存取
│   │   │   │   └── 📁 calendar/            # 行事曆資料存取
│   │   │   └── 📁 utils/                   # 工具函式
│   │   ├── 📁 alembic/                     # ✅ 資料庫遷移 (已完成)
│   │   │   └── 📁 versions/                # 遷移版本檔案
│   │   ├── 📁 tests/                       # 後端測試
│   │   │   ├── 📁 unit/                    # 單元測試
│   │   │   ├── 📁 integration/             # 整合測試
│   │   │   └── 📁 e2e/                     # 端到端測試
│   │   └── 📄 requirements.txt             # Python 依賴套件
│   ├── 📁 frontend/                        # 🌟 React 前端 (部分完成)
│   │   ├── 📄 package.json                 # Node.js 依賴配置
│   │   ├── 📄 vite.config.ts               # Vite 建置配置
│   │   ├── 📄 tailwind.config.js           # ✅ Tailwind CSS 配置
│   │   ├── 📄 tsconfig.json                # TypeScript 配置
│   │   ├── 📁 public/                      # 靜態資源
│   │   ├── 📁 src/                         # ✅ 前端源碼 (結構已建立)
│   │   │   ├── 📄 main.tsx                 # React 應用入口
│   │   │   ├── 📄 App.tsx                  # 主應用組件
│   │   │   ├── 📄 vite-env.d.ts           # Vite 環境定義
│   │   │   ├── 📁 components/              # React 組件
│   │   │   ├── 📁 pages/                   # 頁面組件
│   │   │   ├── 📁 hooks/                   # 自定義 Hooks
│   │   │   ├── 📁 services/                # API 客戶端
│   │   │   ├── 📁 types/                   # TypeScript 類型定義
│   │   │   ├── 📁 utils/                   # 工具函式
│   │   │   └── 📁 styles/                  # 樣式檔案
│   │   └── 📁 tests/                       # 前端測試
│   └── 📁 shared/                          # 🔗 前後端共用代碼
│       ├── 📁 types/                       # 共用類型定義
│       ├── 📁 constants/                   # 共用常數
│       └── 📁 utils/                       # 共用工具函式
├── 📁 infrastructure/                   # 🚀 基礎設施配置
│   ├── 📁 docker/                          # ✅ Docker 容器化 (已完成)
│   │   ├── 📄 docker-compose.yml           # 開發環境配置
│   │   └── 📄 Dockerfile.backend           # 後端容器化檔案
│   ├── 📁 kubernetes/                      # K8s 部署配置
│   └── 📁 terraform/                       # 雲端基礎設施
├── 📁 scripts/                         # 🔧 自動化腳本
├── 📁 .github/                         # 🤖 GitHub Actions
│   └── 📁 workflows/                       # CI/CD 流程
├── 📁 .claude/                         # 🤖 Claude Code 智能協作系統
│   ├── 📄 TASKMASTER_README.md             # TaskMaster 技術文檔
│   ├── 📄 CROSS_PLATFORM_COMPATIBILITY.md # 跨平台相容性指南
│   ├── 📁 commands/                        # 🎛️ 自定義指令 (8個)
│   │   ├── 📄 task-status.md               # 專案狀態查詢
│   │   ├── 📄 task-next.md                 # 下個任務建議
│   │   ├── 📄 hub-delegate.md              # Hub 協調委派
│   │   ├── 📄 review-code.md               # 程式碼審查
│   │   ├── 📄 suggest-mode.md              # 建議模式調整
│   │   ├── 📄 check-quality.md             # 品質檢查
│   │   ├── 📄 template-check.md            # 範本檢查
│   │   └── 📄 task-init.md                 # 任務初始化
│   ├── 📁 taskmaster-data/                 # 💾 專案狀態資料
│   │   ├── 📄 project.json                 # 專案配置
│   │   └── 📄 wbs-todos.json               # WBS 任務列表
│   ├── 📁 agents/                          # 🤖 智能體配置 (8個)
│   │   ├── 📄 general-purpose.md           # 通用智能體
│   │   ├── 📄 code-quality-specialist.md   # 程式碼品質專家
│   │   ├── 📄 test-automation-engineer.md  # 測試自動化工程師
│   │   ├── 📄 security-infrastructure-auditor.md # 安全基礎設施稽核員
│   │   ├── 📄 deployment-operations-engineer.md # 部署維運工程師
│   │   ├── 📄 documentation-specialist.md  # 文檔專家
│   │   ├── 📄 workflow-template-manager.md # 工作流程範本管理員
│   │   └── 📄 e2e-validation-specialist.md # 端到端驗證專家
│   ├── 📁 context/                         # 📈 跨智能體上下文
│   │   ├── 📁 decisions/                   # 技術決策記錄
│   │   ├── 📁 quality/                     # 品質報告
│   │   ├── 📁 testing/                     # 測試報告
│   │   ├── 📁 e2e/                        # E2E 測試報告
│   │   ├── 📁 security/                    # 安全稽核報告
│   │   ├── 📁 deployment/                  # 部署報告
│   │   ├── 📁 docs/                        # 文檔管理
│   │   └── 📁 workflow/                    # 工作流程管理
│   ├── 📁 coordination/                    # 🤝 人機協作配置
│   ├── 📁 hooks/                           # 🔗 事件鉤子
│   ├── 📁 output-styles/                   # 🎨 輸出樣式範本 (14個)
│   └── 📁 ARCHIVE/                         # 🗃️ 歸檔檔案
└── 📁 VibeCoding_Workflow_Templates/   # 🎨 企業級開發範本庫
```

## 📊 專案進度狀態

### ✅ **已完成項目**
1. **專案初始化與架構設計** (100% 完成)
   - ✅ 專案簡報與 PRD 完成
   - ✅ 系統架構設計完成
   - ✅ 資料庫 ER 圖與模型設計完成
   - ✅ SQLAlchemy 模型定義完成
   - ✅ Alembic 遷移腳本建立完成

2. **開發環境建置** (100% 完成)
   - ✅ FastAPI 後端專案結構建立
   - ✅ React + Vite 前端環境配置
   - ✅ Tailwind CSS 設計系統整合
   - ✅ Docker 容器化配置完成
   - ✅ PostgreSQL & Redis 資料庫環境

3. **Claude Code 智能協作系統** (100% 完成)
   - ✅ TaskMaster 指令系統 (8個指令)
   - ✅ 智能體配置完成 (8個智能體)
   - ✅ 專案狀態追蹤機制
   - ✅ WBS 開發計劃建立

### 🔄 **進行中項目**
- 專案文檔持續更新
- API 設計規範完善中

### ⏳ **待開始項目**
- 認證與授權模組 (Google OAuth 2.0)
- 自動簽到核心功能
- 前端頁面開發
- Google Calendar API 整合
- 測試框架建立

## 🎯 技術棧概覽

### 後端 (FastAPI)
- **框架**: FastAPI + Uvicorn
- **資料庫**: PostgreSQL + SQLAlchemy + Alembic
- **快取**: Redis
- **認證**: Google OAuth 2.0 + JWT
- **API**: RESTful + OpenAPI/Swagger

### 前端 (React)
- **框架**: React 18 + TypeScript
- **建置工具**: Vite
- **樣式**: Tailwind CSS (Apple Human Interface Style)
- **路由**: React Router
- **狀態管理**: 待選定
- **API 客戶端**: Axios

### 基礎設施
- **容器化**: Docker + Docker Compose
- **部署**: Google Cloud Run + Vercel
- **CI/CD**: GitHub Actions
- **監控**: Cloud Logging

## 🗂️ 目錄結構特點

### 📁 **Clean Architecture 分層**
- **API 層**: 處理 HTTP 請求與回應
- **服務層**: 業務邏輯處理
- **資料存取層**: 資料庫操作
- **模型層**: 資料結構定義

### 🎨 **前端組件化**
- **原子設計**: Atoms, Molecules, Organisms
- **Apple 風格**: 簡潔、直覺的 UI 設計
- **響應式**: 支援多種裝置尺寸

### 🤖 **智能協作整合**
- **TaskMaster**: 專案管理與任務協調
- **智能體系統**: 8個專業智能體
- **上下文共享**: 跨智能體協作機制

## 📈 開發工作流程

### 1. **功能開發**
```bash
1. 建立功能分支
2. 實作功能 (遵循 Clean Architecture)
3. 撰寫測試
4. 程式碼審查
5. 合併到主分支
```

### 2. **測試策略**
- **單元測試**: ≥ 80% 覆蓋率
- **整合測試**: API 層級測試
- **E2E 測試**: 完整使用者流程

### 3. **部署流程**
- **開發環境**: Docker Compose 本地開發
- **測試環境**: GitHub Actions 自動部署
- **生產環境**: Google Cloud Run + Vercel

## 📚 文檔體系

### 🏗️ **架構文檔**
- PRD 與需求規格
- 系統架構設計
- API 設計規範
- 資料庫設計

### 📋 **開發指南**
- 專案結構指南
- 程式碼規範
- 測試指南
- 部署手冊

### 🤖 **智能協作**
- TaskMaster 使用指南
- 智能體配置文檔
- 工作流程範本

---

**目前進度**: 25% 完成 (12.5h/50h) | **下個里程碑**: 認證模組開發 🚀