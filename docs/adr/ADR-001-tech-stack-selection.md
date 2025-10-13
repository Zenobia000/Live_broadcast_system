# ADR-001: 技術棧選型決策

---

**狀態 (Status):** `已接受 (Accepted)`

**決策者 (Deciders):** `技術負責人, 架構師, TaskMaster Hub`

**日期 (Date):** `2025-10-13`

**技術顧問 (Consulted):** `開發團隊, DevOps 團隊`

**受影響團隊 (Informed):** `前端開發團隊, 後端開發團隊, QA 團隊`

---

## 1. 背景與問題陳述 (Context and Problem Statement)

### 上下文 (Context)

智能簽到系統是一個全新的專案，旨在打造以事件驅動為核心的自動化簽到與智能審核平台。系統需要：
- 整合 Google Calendar API 實現自動簽到
- 支援 Google OAuth 2.0 認證
- 提供 Apple 風格的現代化 UI
- 支援未來 2 年內的功能擴展
- 快速開發 MVP（7週時程）

團隊規模：2-3 名開發人員，具備全端開發能力。

### 問題陳述 (Problem Statement)

專案啟動階段需要選擇合適的技術棧，以滿足以下需求：
1. **快速開發**: MVP 需在 7 週內完成
2. **現代化架構**: 前後端分離，易於維護和擴展
3. **整合友善**: 與 Google APIs 無縫整合
4. **效能需求**: 自動簽到響應時間 < 1 秒
5. **團隊熟悉度**: 降低學習曲線，提高開發效率

### 驅動因素/約束條件 (Drivers / Constraints)

**驅動因素:**
- 需要支持異步處理（事件驅動的自動簽到）
- 需要快速建立 RESTful API
- 需要現代化的前端 UI/UX（Apple 風格）
- 需要良好的 Google API 整合支援

**約束條件:**
- MVP 開發時程：7 週（50 小時）
- 團隊對 Python 和 JavaScript/TypeScript 有經驗
- 基礎設施成本需控制（使用 Google Cloud Free Tier + Vercel Free Tier）
- 需要良好的開發工具生態系統（型別檢查、測試框架）

---

## 2. 考量的選項 (Considered Options)

### 選項一：Python/FastAPI + React + PostgreSQL（推薦方案）

**描述：**
- **後端**: Python 3.11+ with FastAPI
- **前端**: React 18 with Vite + TypeScript
- **資料庫**: PostgreSQL 16
- **快取**: Redis 7
- **部署**: Google Cloud Run (Backend) + Vercel (Frontend)

**優點 (Pros):**
- ✅ **快速開發**: FastAPI 自動生成 OpenAPI 文檔，減少 API 溝通成本
- ✅ **異步支援**: FastAPI 原生支援 async/await，適合事件驅動架構
- ✅ **型別安全**: Python type hints + TypeScript 提供全棧型別檢查
- ✅ **生態系統**: 豐富的 Google API Python 客戶端庫
- ✅ **團隊熟悉**: 團隊對 Python 和 React 都有實戰經驗
- ✅ **測試友善**: pytest + Vitest 提供完整測試解決方案
- ✅ **成本效益**: 使用免費層級即可支撐 MVP 階段

**缺點 (Cons):**
- ❌ **效能上限**: Python GIL 可能在極高併發下成為瓶頸（但 FastAPI + async 已大幅改善）
- ❌ **型別系統**: Python 的型別檢查不如靜態語言嚴格（可用 Pydantic 彌補）

**成本/複雜度評估:**
- 開發成本: **低**（團隊熟悉，快速上手）
- 維護成本: **中**（成熟的生態系統，但需注意依賴管理）
- 基礎設施成本: **低**（Cloud Run + Vercel Free Tier 足夠）
- 技術複雜度: **中**（前後端分離架構，需良好的 API 設計）

---

### 選項二：Node.js/NestJS + React + MongoDB

**描述：**
- **後端**: Node.js with NestJS (TypeScript)
- **前端**: React with Next.js
- **資料庫**: MongoDB Atlas
- **部署**: Vercel (Full-stack)

**優點 (Pros):**
- ✅ **全棧 TypeScript**: 前後端統一語言，代碼共用容易
- ✅ **統一部署**: Vercel 可同時部署前後端
- ✅ **社群活躍**: JavaScript 生態系統龐大
- ✅ **即時功能**: Node.js 適合 WebSocket 等即時功能

**缺點 (Cons):**
- ❌ **MongoDB 學習曲線**: 團隊對關聯式資料庫更熟悉
- ❌ **NestJS 複雜度**: NestJS 框架較重，學習曲線較陡
- ❌ **資料模型**: 簽到系統的關聯性資料更適合關聯式資料庫
- ❌ **Google API**: Node.js 的 Google API 庫文檔較 Python 少

**成本/複雜度評估:**
- 開發成本: **中**（NestJS 需要學習時間）
- 維護成本: **中**
- 基礎設施成本: **低**
- 技術複雜度: **中高**（NestJS 架構較複雜）

---

### 選項三：Go + React + PostgreSQL

**描述：**
- **後端**: Go with Gin or Fiber
- **前端**: React with Vite
- **資料庫**: PostgreSQL
- **部署**: Google Cloud Run + Vercel

**優點 (Pros):**
- ✅ **極致效能**: Go 的並發模型非常適合高負載場景
- ✅ **靜態型別**: 編譯期型別檢查，減少執行時錯誤
- ✅ **單一二進位**: 部署簡單，容器化效率高
- ✅ **資源占用**: 記憶體使用少，適合 Serverless

**缺點 (Cons):**
- ❌ **學習曲線**: 團隊對 Go 不熟悉，需要學習時間
- ❌ **開發速度**: 相較於 Python，Go 的開發速度較慢
- ❌ **Google API**: Go 的 Google API 庫文檔和範例較少
- ❌ **時程風險**: 7 週時程內學習 Go 會增加專案風險

**成本/複雜度評估:**
- 開發成本: **高**（需要學習 Go）
- 維護成本: **低**（編譯語言，錯誤在編譯期捕捉）
- 基礎設施成本: **低**
- 技術複雜度: **中**（Go 語法簡潔，但並發模型需理解）

---

## 3. 決策 (Decision Outcome)

**最終選擇的方案：** `選項一：Python/FastAPI + React + PostgreSQL`

### 選擇理由 (Rationale)

**1. 開發效率優先（符合 7 週時程約束）**
- FastAPI 提供自動 API 文檔生成，減少前後端溝通成本
- 團隊對 Python 和 React 都熟悉，可立即上手，無需學習新語言
- Python 的 Google API 客戶端庫文檔完善，範例豐富，降低整合風險

**2. 技術需求匹配**
- FastAPI 的異步支援完美適配事件驅動的自動簽到邏輯
- PostgreSQL 的關聯式模型更適合簽到系統的資料結構（User-Event-Attendance 關係）
- Pydantic 提供強大的資料驗證，減少 API 錯誤

**3. 與 Linus 實用主義哲學一致**
> "選擇你知道能 work 的技術，而不是理論上最完美的技術。"

- 團隊已驗證過 FastAPI 的快速開發能力
- PostgreSQL 是久經考驗的穩定資料庫
- React + Vite 的組合提供優秀的開發體驗

**4. 成本效益分析**
- Google Cloud Run 的 FastAPI 部署成本極低（Free Tier: 2M requests/month）
- Vercel 前端部署完全免費（Hobby Plan）
- 總體基礎設施成本 < $10/月（MVP 階段）

**5. 權衡分析**
vs. **NestJS 方案**：雖然全棧 TypeScript 吸引人，但 NestJS 的學習曲線會延遲 MVP 交付，且 MongoDB 不適合關聯性資料。

vs. **Go 方案**：雖然效能卓越，但團隊不熟悉 Go，7 週時程內學習風險太高。FastAPI + async 的效能已足夠應對 MVP 階段需求。

**6. 與長期架構目標一致**
- Clean Architecture + DDD：Python 的動態特性更容易實現領域驅動設計
- 可擴展性：未來可輕鬆引入 Celery 實現背景任務處理
- 可維護性：Python 的可讀性和社群支援降低維護成本

---

## 4. 決策的後果與影響 (Consequences)

### 正面影響 / 預期收益

**開發效率:**
- ✅ 預計可節省 10-15 小時的技術學習時間
- ✅ FastAPI 自動文檔生成可節省 5 小時 API 文檔撰寫時間
- ✅ 豐富的 Google API Python 範例降低整合風險

**系統效能:**
- ✅ FastAPI + async 可支援 1000+ requests/sec（遠超 MVP 需求）
- ✅ 自動簽到響應時間預期 < 500ms（目標 < 1s）

**成本控制:**
- ✅ MVP 階段基礎設施成本 < $10/月
- ✅ 開發成本降低（團隊熟悉度高）

### 負面影響 / 引入的風險

**技術債務:**
- ⚠️ Python GIL 在極高併發下可能成為瓶頸
  - **緩解措施**: MVP 階段流量不會達到瓶頸，未來可考慮引入 Rust/Go 的關鍵服務

- ⚠️ 動態型別可能導致執行時錯誤
  - **緩解措施**: 強制使用 Pydantic + mypy 型別檢查，測試覆蓋率 ≥ 80%

**維護風險:**
- ⚠️ Python 依賴管理可能較複雜
  - **緩解措施**: 使用 Poetry 管理依賴，Docker 確保環境一致性

### 對其他組件/團隊的影響

**前端團隊:**
- 需要適應 FastAPI 自動生成的 OpenAPI Schema
- 可使用 openapi-typescript-codegen 自動生成型別定義

**DevOps 團隊:**
- 需要設置 Google Cloud Run 和 Vercel 的 CI/CD Pipeline
- Docker 容器化已簡化部署流程

**QA 團隊:**
- 可使用 pytest 進行後端測試
- 可使用 Playwright 進行 E2E 測試
- FastAPI 的 TestClient 簡化 API 測試

### 未來可能需要重新評估的觸發條件

**效能瓶頸:**
- 如果 API P95 延遲 > 2s，且確認為 Python GIL 問題
- 如果併發請求 > 5000/sec 導致系統不穩定

**團隊能力變化:**
- 如果團隊成員全部熟悉 Go/Rust，且需要極致效能
- 如果需要重寫關鍵服務以支援更高併發

**業務需求變化:**
- 如果需要強即時性功能（如即時聊天），可能考慮 Node.js + WebSocket
- 如果需要複雜的圖形計算，可能考慮 Go + gRPC

---

## 5. 執行計畫概要 (Implementation Plan Outline)

**Phase 1: 環境建置（Week 1）** ✅ 已完成
1. ✅ 建立專案目錄結構
2. ✅ 配置 Docker Compose (PostgreSQL + Redis + Backend)
3. ✅ 初始化 FastAPI 專案（含 CORS, 健康檢查）
4. 🔄 初始化 React + Vite 專案（進行中）

**Phase 2: 核心基礎建置（Week 1-2）**
1. 完成資料庫 Schema 設計（SQLAlchemy Models）
2. 建立 Alembic 遷移腳本
3. 實作基礎 API 端點（健康檢查、認證基礎）
4. 建立前端基礎組件庫（Apple 風格）

**Phase 3: 功能開發（Week 2-5）**
1. 認證與授權模組（Google OAuth 2.0）
2. 自動簽到核心模組（Google Calendar 整合）
3. 請假與補簽模組
4. 通知服務（Email + Slack）

**Phase 4: 測試與優化（Week 4-6）**
1. 單元測試覆蓋率 ≥ 80%
2. API 整合測試
3. E2E 測試關鍵流程
4. 效能測試與優化

**Phase 5: 部署上線（Week 6-7）**
1. Google Cloud Run 生產環境配置
2. Vercel 前端部署
3. CI/CD Pipeline 建立
4. UAT 驗收測試

---

## 6. 相關參考 (References)

### 官方文檔
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Google Cloud Run Pricing](https://cloud.google.com/run/pricing)

### 技術驗證
- FastAPI 效能基準測試: [TechEmpower Benchmarks](https://www.techempower.com/benchmarks/)
- Google API Python 客戶端: [google-api-python-client](https://github.com/googleapis/google-api-python-client)

### 專案文檔
- [專案簡報與 PRD](../01_project_brief_and_prd.md)
- [系統架構設計文檔](../03_architecture_and_design_document.md)
- [WBS 開發計劃](../06_wbs_development_plan.md)

---

## ADR 審核記錄 (Review History)

| 日期 | 審核人 | 角色 | 備註/主要問題 |
| :--- | :--- | :--- | :--- |
| 2025-10-13 | TaskMaster Hub | AI 架構師 | 基於團隊能力、時程約束和技術需求，推薦此方案 |
| 2025-10-13 | 技術負責人 | 人類決策者 | 同意方案，批准執行 |
| 2025-10-14 | Linus (AI Persona) | 技術顧問 | "實用主義的好選擇。選你知道能 work 的技術。" |

---

**下一個 ADR**: ADR-002: Google OAuth 2.0 認證方案（計劃於 Week 2 建立）

**相關 WBS 任務**:
- Task 2.1.1: 技術選型決策（已完成）
- Task 3.1.1: 專案結構初始化（已完成）
- Task 3.2.1: FastAPI 專案初始化（已完成）
