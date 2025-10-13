# 整合性架構與設計文件 - 智能簽到系統

---

**文件版本 (Document Version):** `v1.0`
**最後更新 (Last Updated):** `2025-10-13`
**主要作者 (Lead Author):** `[技術架構師]`
**審核者 (Reviewers):** `[架構委員會, 核心開發團隊]`
**狀態 (Status):** `草稿 (Draft)`

---

## 目錄 (Table of Contents)

- [第 1 部分：架構總覽 (Architecture Overview)](#第-1-部分架構總覽-architecture-overview)
  - [1.1 C4 模型：視覺化架構](#11-c4-模型視覺化架構)
  - [1.2 DDD 戰略設計 (Strategic DDD)](#12-ddd-戰略設計-strategic-ddd)
  - [1.3 Clean Architecture 分層](#13-clean-architecture-分層)
  - [1.4 技術選型與決策](#14-技術選型與決策)
- [第 2 部分：詳細設計 (Detailed Design)](#第-2-部分詳細設計-detailed-design)
  - [2.1 MVP 與模組優先級 (MVP & Module Priority)](#21-mvp-與模組優先級-mvp--module-priority)
  - [2.2 核心功能：模組設計](#22-核心功能模組設計)
  - [2.3 非功能性需求設計 (NFRs Design)](#23-非功能性需求設計-nfrs-design)

---

**目的**: 本文件旨在將 `智能簽到系統` 的業務需求轉化為一個完整、內聚的技術藍圖。它從高層次的系統架構開始，逐步深入到具體的模組級實現細節，以確保系統的穩固性、可擴展性與可維護性。

---

## 第 1 部分：架構總覽 (Architecture Overview)

*此部分關注系統的宏觀結構與指導原則，回答「系統由什麼組成？」以及「它們之間如何互動？」。*

### 1.1 C4 模型：視覺化架構

*我們使用 C4 模型來從不同層次視覺化軟體架構。*

*   **L1 - 系統情境圖 (System Context Diagram):**
    *   *描述本系統與外部使用者/系統的互動。系統核心是圍繞一個整合的簽到流程，連接使用者、行事曆與通知服務。*
    ```mermaid
    graph TD
        subgraph "智能簽到系統"
            A["Smart Attendance System"]
        end

        User[成員/管理員] -- "透過 Web/Mobile App 進行簽到、請假、審核" --> A
        A -- "同步活動排程, 更新出席狀態" --> GoogleCalendar[Google Calendar API]
        A -- "發送補簽/請假通知" --> Slack[Slack API]
        A -- "發送補簽/請假通知" --> Email[Email Service]

    ```

*   **L2 - 容器圖 (Container Diagram):**
    *   *描述系統由哪些可部署單元組成。我們採用前後端分離的現代 Web 應用架構，後端採用模組化的服務設計，並搭配一個關聯式資料庫。*
    ```mermaid
    graph TD
        User[成員/管理員]

        subgraph "智能簽到系統"
            Frontend[/React SPA<br/>(Vercel)/]
            Backend[/Backend API<br/>(FastAPI on Cloud Run)/]
            Database[(PostgreSQL DB<br/>(Cloud SQL))]
            Notification[/Notification Service<br/>(Background Worker)/]
        end

        User -- "HTTPS" --> Frontend
        Frontend -- "HTTPS/API" --> Backend
        Backend -- "TCP" --> Database
        Backend -- "非同步任務" --> Notification
        Notification -- "HTTPS" --> GoogleCalendar[Google Calendar API]
        Notification -- "HTTPS" --> Slack[Slack API]
        Notification -- "SMTP" --> Email[Email Service]
    ```

### 1.2 DDD 戰略設計 (Strategic DDD)

*   **通用語言 (Ubiquitous Language):**
    *   **Event**: 指一個需要記錄出缺勤的活動，如會議、課程。
    *   **Attendance**: 記錄某位 `User` 對於某個 `Event` 的出席狀態 (`Present`, `Late`, `Absent`, `Leave`, `EarlyLeave`)。
    *   **Leave Request**: 成員提交的請假申請，包含假別、事由、時間。
    *   **Makeup Request**: 成員提交的補簽申請。
    *   **Policy**: 系統用來自動判斷狀態（如遲到）的規則。

*   **限界上下文 (Bounded Contexts):**
    *   **Attendance Context**: 核心上下文，負責處理所有與簽到、補簽、狀態計算相關的邏輯。
    *   **Scheduling Context**: 負責與外部行事曆（Google Calendar）同步 `Event`。
    *   **Notification Context**: 負責向使用者和管理員發送通知。
    *   **User Management Context**: 負責使用者身份驗證與資料管理。

### 1.3 Clean Architecture 分層

*我們的系統將遵循 Clean Architecture 原則，以確保關注點分離，並在 `src/` 目錄下體現。*

*   **Domain Layer**: 包含核心業務規則與邏輯 (例如：`Attendance` 實體、`LeaveRequest` 的狀態變更邏輯)。
*   **Application Layer**: 包含應用程式特定的流程 (Use Cases)，例如 `CreateLeaveRequestUseCase`，協調 Domain 和 Infrastructure。
*   **Infrastructure Layer**: 包含與外部世界互動的實現細節，如資料庫存取 (Repositories)、對外 API (FastAPI Routers)、第三方服務客戶端 (Google Calendar Client)。

### 1.4 技術選型與決策

*   **技術棧 (Tech Stack):**
    *   **前端**: React (with Vite), Tailwind CSS, Apple Human Interface Style
    *   **後端**: Python / FastAPI
    *   **資料庫**: PostgreSQL
    *   **通知**: Email/Slack
    *   **部署**: Docker, Google Cloud Run (for Backend), Vercel (for Frontend)

*   **架構決策記錄 (ADR):**
    *   所有重大的架構決策都應被記錄。
    *   **-> 參考: [docs/ADR-001-Tech-Stack-Selection.md](./ADR-001-Tech-Stack-Selection.md) (待建立)**

---

## 第 2 部分：詳細設計 (Detailed Design)

*此部分關注具體模組的實現細節，回答「每個部分如何工作？」。*

### 2.1 MVP 與模組優先級 (MVP & Module Priority)

*根據 [PRD](./01_project_brief_and_prd.md) 中的使用者故事，定義最小可行產品 (MVP) 的範圍。*

*   **關鍵模組 (MVP Scope - Sprint 1):**
    *   `User Management Context`: 透過 Google OAuth 進行登入。
    *   `Attendance Context`: 實現登入後自動簽到的核心邏輯。
*   **後續模組 (Post-MVP):**
    *   `Leave & Makeup Modules` (Sprint 2)
    *   `Scheduling & Notification Contexts` (Sprint 3)
    *   `Admin Dashboard & Reporting` (Sprint 4)

### 2.2 核心功能：模組設計

*針對 MVP 的**關鍵模組**進行詳細設計。*

#### 核心流程: `登入即簽到 (Event-driven Flow)`

*   **對應 BDD Feature**: [Link to `02_behavior_driven_development.feature`]
*   **職責 (Responsibility)**: 在使用者登入成功後，系統自動為其在當前時間點的活動中記錄出席狀態。
*   **API 設計**:
    *   此流程由後端事件觸發，而非直接由前端 API 呼叫。主要涉及 `/auth/login` 端點成功後觸發的內部流程。
    *   **-> 參考: [API 設計規格](./04_api_design_specification.md)**
*   **資料模型 (Data Model)**:
    *   **完整 ER 圖請參閱下方 2.2.1 節**
    *   核心表: `user`, `event`, `attendance`, `leave_request`, `makeup_request`.
*   **關鍵流程 (Sequence Diagram)**:
    ```mermaid
    sequenceDiagram
        participant User
        participant Frontend
        participant AuthService
        participant CalendarService
        participant AttendanceService
        participant DB

        User->>Frontend: 使用 Google 帳號登入
        Frontend->>AuthService: POST /auth/google/callback
        AuthService->>AuthService: 驗證 Token, 取得或創建 User
        alt 登入成功
            AuthService->>CalendarService: 異步查詢當前活動 GetCurrentEvents(user)
            CalendarService-->>AttendanceService: 返回 Event 列表 [event1, event2]
            loop 為每個活動記錄
                AttendanceService->>AttendanceService: 判斷 event 是否遲到
                AttendanceService->>DB: 寫入/更新 attendance 記錄 (status=PRESENT/LATE)
            end
            AuthService-->>Frontend: 返回登入成功 Session/JWT
            Frontend-->>User: 顯示儀表板與「簽到成功」訊息
        end
    end
    ```

#### 2.2.1 資料庫 ER 圖 (Entity-Relationship Diagram)

*完整的資料模型設計，遵循 DDD 限界上下文劃分與 Clean Architecture 原則。*

**設計原則**:
- ✅ 每個實體職責單一明確 (Single Responsibility)
- ✅ 使用 UUID 作為主鍵，支援分散式系統
- ✅ 軟刪除僅用於核心業務表 (Attendance, LeaveRequest, MakeupRequest)
- ✅ `UNIQUE(user_id, event_id)` 約束防止重複簽到記錄

**ER 圖**:

```mermaid
erDiagram
    %% ==========================================
    %% User Management Context
    %% ==========================================
    User {
        uuid id PK "主鍵"
        string email UK "Google OAuth 郵箱 (唯一)"
        string name "使用者名稱"
        string google_id UK "Google OAuth ID (唯一)"
        string avatar_url "頭像 URL (可選)"
        enum role "角色: MEMBER, ADMIN"
        timestamp created_at "建立時間"
        timestamp updated_at "更新時間"
    }

    %% ==========================================
    %% Scheduling Context
    %% ==========================================
    Event {
        uuid id PK "主鍵"
        string title "活動標題"
        text description "活動描述 (可選)"
        timestamp start_time "開始時間"
        timestamp end_time "結束時間"
        int grace_period_minutes "寬限期 (分鐘, 預設 5)"
        string google_event_id UK "Google Calendar Event ID (唯一)"
        uuid created_by FK "創建者 (User.id, nullable - 系統同步時為 NULL)"
        timestamp created_at "建立時間"
        timestamp updated_at "更新時間"
    }

    %% ==========================================
    %% Attendance Context (核心)
    %% ==========================================
    Attendance {
        uuid id PK "主鍵"
        uuid user_id FK "使用者 (User.id)"
        uuid event_id FK "活動 (Event.id)"
        enum status "狀態: PRESENT, LATE, ABSENT, LEAVE, MAKEUP, EARLY_LEAVE"
        timestamp check_in_time "簽到時間 (可選)"
        text note "備註 (補簽/請假原因, 可選)"
        timestamp deleted_at "軟刪除時間 (可選)"
        timestamp created_at "建立時間"
        timestamp updated_at "更新時間"
        unique user_event_idx "UNIQUE(user_id, event_id) - 防止重複簽到"
    }

    %% ==========================================
    %% Leave & Makeup Request Context
    %% ==========================================
    LeaveRequest {
        uuid id PK "主鍵"
        uuid user_id FK "申請人 (User.id)"
        uuid event_id FK "活動 (Event.id)"
        enum leave_type "假別: SICK, PERSONAL, OFFICIAL, OTHER"
        text reason "請假事由"
        timestamp start_time "請假開始時間"
        timestamp end_time "請假結束時間"
        enum status "審核狀態: PENDING, APPROVED, REJECTED"
        uuid reviewed_by FK "審核者 (User.id, nullable - 待審核時為 NULL)"
        text review_note "審核備註 (可選)"
        timestamp reviewed_at "審核時間 (可選)"
        timestamp deleted_at "軟刪除時間 (可選)"
        timestamp created_at "建立時間"
        timestamp updated_at "更新時間"
    }

    MakeupRequest {
        uuid id PK "主鍵"
        uuid user_id FK "申請人 (User.id)"
        uuid event_id FK "活動 (Event.id)"
        text reason "補簽原因"
        enum status "審核狀態: PENDING, APPROVED, REJECTED"
        uuid reviewed_by FK "審核者 (User.id, nullable - 待審核時為 NULL)"
        text review_note "審核備註 (可選)"
        timestamp reviewed_at "審核時間 (可選)"
        timestamp deleted_at "軟刪除時間 (可選)"
        timestamp created_at "建立時間"
        timestamp updated_at "更新時間"
    }

    %% ==========================================
    %% Relationships (關聯關係)
    %% ==========================================
    User ||--o{ Event : "creates (創建活動, nullable)"
    User ||--o{ Attendance : "has (擁有簽到記錄)"
    Event ||--o{ Attendance : "contains (包含簽到記錄)"

    User ||--o{ LeaveRequest : "submits (提交請假申請)"
    Event ||--o{ LeaveRequest : "receives (接收請假申請)"
    User ||--o{ LeaveRequest : "reviews (審核請假申請, nullable)"

    User ||--o{ MakeupRequest : "submits (提交補簽申請)"
    Event ||--o{ MakeupRequest : "receives (接收補簽申請)"
    User ||--o{ MakeupRequest : "reviews (審核補簽申請, nullable)"
```

**關鍵設計決策 (ADR-002: Database Schema Design)**:

1. **為何分離 `LeaveRequest` 與 `MakeupRequest`？**
   - 請假與補簽是不同的業務流程，狀態機不同
   - 請假影響未來事件，補簽修正過去記錄
   - 分離避免 `if type == 'leave' then ... else ...` 的特殊判斷 (Linus: "Good taste")

2. **為何使用 `enum status` 而非布林標記？**
   - 單一欄位表達所有狀態，無需多個布林欄位組合
   - 避免 `is_present AND is_late` 這種邏輯矛盾
   - 擴展新狀態時無需修改表結構 (Open-Closed Principle)

3. **為何 `Attendance` 不直接關聯到 `LeaveRequest`？**
   - `Attendance` 是事實記錄 (what happened)
   - `LeaveRequest` 是申請流程 (what's requested)
   - 解耦使狀態變更更簡單：審核通過後直接更新 `Attendance.status = 'LEAVE'`

4. **為何僅核心表使用軟刪除？**
   - 審計需求僅針對核心業務記錄 (Attendance, LeaveRequest, MakeupRequest)
   - `User` 與 `Event` 表應該永不刪除，僅標記為 inactive (未來擴展)

5. **為何 `Event.created_by` 允許 nullable？**
   - 活動可能來自 Google Calendar 系統自動同步
   - Nullable 避免創建虛擬「系統使用者」(Linus: "Simplicity")

**索引策略 (Performance Optimization)**:
- `User.email`, `User.google_id`: 唯一索引 (UK)
- `Event.google_event_id`: 唯一索引 (UK)
- `Attendance(user_id, event_id)`: 複合唯一索引 (防重複 + 查詢優化)
- `LeaveRequest.status`, `MakeupRequest.status`: 一般索引 (審核查詢)
- `Attendance.deleted_at`, `LeaveRequest.deleted_at`, `MakeupRequest.deleted_at`: 軟刪除過濾索引

### 2.3 非功能性需求設計 (NFRs Design)

*描述如何實現 PRD 中定義的非功能性需求。*

*   **性能 (Performance)**:
    *   `自動簽到` 流程將採用異步事件驅動，避免阻塞登入主流程，確保登入回應時間小於 500ms。
    *   Dashboard 的統計數據將使用 Redis 進行快取，減少資料庫讀取壓力。
*   **安全性 (Security)**:
    *   所有 API 將透過 API Gateway (Cloudflare/Nginx) 並強制執行 JWT 驗證。
    *   不直接儲存使用者密碼，完全依賴 Google OAuth 2.0。
*   **可擴展性 (Scalability)**:
    *   後端服務設計為無狀態 (Stateless)，可透過 Cloud Run 進行水平擴展。
    *   非同步通知任務將由獨立的 Worker 處理，可獨立擴展。
*   **可靠性 (Reliability)**:
    *   簽到、請假等核心操作應設計為冪等的，以防止網路問題導致的重複請求產生非預期副作用。
