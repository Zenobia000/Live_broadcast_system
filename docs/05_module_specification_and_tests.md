# 模組規格與測試案例 - 智能簽到系統

---

**文件版本 (Document Version):** `v1.0`
**最後更新 (Last Updated):** `2025-10-13`
**主要作者 (Lead Author):** `[開發工程師]`
**審核者 (Reviewers):** `[技術負責人]`
**狀態 (Status):** `待開發 (To Do)`

---

## 目錄 (Table of Contents)

- [模組: `AttendanceService`](#-模組-attendanceservice)
  - [規格 1: `record_auto_attendance`](#-規格-1-record_auto_attendance)
  - [測試情境與案例 (Test Scenarios & Cases)](#-測試情境與案例-test-scenarios--cases)

---

**目的**: 本文件旨在將高層次的 BDD 情境分解到具體的 `AttendanceService` 模組，定義其核心功能 `record_auto_attendance` 的詳細規格與測試場景。這是指導 TDD (測試驅動開發) 實踐的最低層級規格。

---

## 模組: `AttendanceService`

**對應架構文件**: `[Link to ./03_architecture_and_design_document.md]`
**對應 BDD Feature**: `[Link to ./02_behavior_driven_development.feature]`

---

### 規格 1: `record_auto_attendance`

**簽名 (Signature)**:
`record_auto_attendance(user_id: str, login_time: datetime) -> Optional[Attendance]`

**描述 (Description)**:
根據使用者登入時間，尋找對應的當前活動。如果找到活動，則根據系統的遲到策略計算出勤狀態（出席或遲到），並創建或更新一筆出勤記錄。

**契約式設計 (Design by Contract, DbC)**:
*   **前置條件 (Preconditions)**:
    1.  `user_id` 必須對應到一個已存在的使用者。
    2.  `login_time` 是一個有效的 `datetime` 物件。
*   **後置條件 (Postconditions)**:
    1.  **若找到相關活動**:
        *   資料庫中會存在一筆對應 `user_id` 和 `event_id` 的 `Attendance` 記錄。
        *   該記錄的 `status` 會根據 `login_time` 和 `event.start_time` 被設為 `PRESENT` 或 `LATE`。
        *   函式返回被創建或更新的 `Attendance` 物件。
    2.  **若未找到相關活動**:
        *   資料庫中不會創建任何新的 `Attendance` 記錄。
        *   函式返回 `None`。
*   **不變性 (Invariants)**:
    1.  一個使用者在同一個活動中，永遠只會有一筆最終的出勤記錄。

---

### 測試情境與案例 (Test Scenarios & Cases)

*以下是針對 `record_auto_attendance` 規格需要覆蓋的測試情境。*

#### 情境 1: 正常路徑 (Happy Path)

*   **測試案例 ID**: `TC-AA-001`
*   **描述**: 使用者在活動開始後、遲到寬限時間內登入，應被記為「出席」。
*   **測試步驟 (Arrange-Act-Assert)**:
    1.  **Arrange**:
        *   設定系統時間為 `2025-10-14 09:01`。
        *   資料庫中存在活動 `每日站立會議` (開始時間 `09:00`, 遲到寬限 `5` 分鐘)。
        *   使用者 `damon@workspace.com` 尚未有該活動的簽到記錄。
    2.  **Act**: 呼叫 `record_auto_attendance(user_id="damon_id", login_time="2025-10-14 09:01")`。
    3.  **Assert**:
        *   驗證函式返回一個 `Attendance` 物件。
        *   驗證資料庫中新增了一筆記錄，其 `status` 為 `PRESENT`。

#### 情境 2: 業務規則 - 遲到

*   **測試案例 ID**: `TC-AA-002`
*   **描述**: 使用者在遲到寬限時間之後登入，應被記為「遲到」。
*   **測試步驟 (Arrange-Act-Assert)**:
    1.  **Arrange**:
        *   設定系統時間為 `2025-10-14 09:06`。
        *   資料庫中存在活動 `每日站立會議` (開始時間 `09:00`, 遲到寬限 `5` 分鐘)。
    2.  **Act**: 呼叫 `record_auto_attendance(user_id="damon_id", login_time="2025-10-14 09:06")`。
    3.  **Assert**:
        *   驗證函式返回一個 `Attendance` 物件。
        *   驗證資料庫中新增了一筆記錄，其 `status` 為 `LATE`。

#### 情境 3: 邊界情況 - 壓線登入

*   **測試案例 ID**: `TC-AA-003`
*   **描述**: 使用者恰好在遲到寬限時間的邊界登入，應被記為「出席」。
*   **測試步驟 (Arrange-Act-Assert)**:
    1.  **Arrange**:
        *   設定系統時間為 `2025-10-14 09:05:00`。
        *   活動開始時間 `09:00`, 遲到寬限 `5` 分鐘。
    2.  **Act**: 呼叫 `record_auto_attendance(user_id="damon_id", login_time="2025-10-14 09:05:00")`。
    3.  **Assert**:
        *   驗證返回記錄的 `status` 為 `PRESENT`。

#### 情境 4: 無效路徑 - 無對應活動

*   **測試案例 ID**: `TC-AA-004`
*   **描述**: 使用者登入時，當前沒有任何進行中或即將開始的活動。
*   **測試步驟 (Arrange-Act-Assert)**:
    1.  **Arrange**:
        *   設定系統時間為 `2025-10-14 10:00` (所有活動都已結束)。
    2.  **Act**: 呼叫 `record_auto_attendance(user_id="damon_id", login_time="2025-10-14 10:00")`。
    3.  **Assert**:
        *   驗證函式返回 `None`。
        *   驗證資料庫中沒有新增任何 `Attendance` 記錄。

#### 情境 5: 冪等性 - 重複觸發

*   **測試案例 ID**: `TC-AA-005`
*   **描述**: 使用者已經有「出席」記錄後，再次意外觸發了簽到流程。
*   **測試步驟 (Arrange-Act-Assert)**:
    1.  **Arrange**:
        *   資料庫中已存在 `damon@workspace.com` 在 `每日站立會議` 的 `PRESENT` 記錄。
    2.  **Act**: 再次呼叫 `record_auto_attendance(user_id="damon_id", login_time="2025-10-14 09:02")`。
    3.  **Assert**:
        *   驗證函式返回已存在的那筆 `Attendance` 物件。
        *   驗證資料庫中 `Attendance` 記錄總數未增加。
