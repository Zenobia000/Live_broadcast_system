# API 設計規範 - 智能簽到系統

---

**文件版本 (Document Version):** `v1.0`
**最後更新 (Last Updated):** `2025-10-13`
**主要作者/設計師 (Lead Author/Designer):** `[技術架構師]`
**狀態 (Status):** `草稿 (Draft)`
**相關 SD 文檔:** `[Link to ./03_architecture_and_design_document.md]`
**OpenAPI (Swagger) 定義文件:** `[Link to openapi.yaml] (待建立)`

---

## 1. 引言 (Introduction)

### 1.1 目的 (Purpose)
*   為 `智能簽到系統` 的消費者 (前端 App) 和實現者 (後端開發者) 提供一個統一、明確的接口契約。

### 1.2 快速入門 (Quick Start)

*   **第 1 步: 透過前端應用完成 Google 登入**
    *   所有 API 請求都需要一個有效的 `Bearer Token`。
*   **第 2 步: 獲取個人資訊**
    ```bash
    curl --request GET \
      --url https://api.attend.com/v1/auth/me \
      --header 'Authorization: Bearer YOUR_ACCESS_TOKEN'
    ```

---

## 2. 設計原則與約定

*   **API 風格:** RESTful
*   **基本 URL:** `https://api.attend.com/v1`
*   **請求與回應格式:** `application/json` (UTF-8)
*   **命名約定:**
    *   **資源路徑:** `kebab-case`, 複數 (e.g., `/leave-requests`)
    *   **JSON 欄位:** `snake_case` (e.g., `user_id`)
*   **日期與時間格式:** ISO 8601 UTC (e.g., `2025-10-13T10:00:00Z`)

---

## 3. 認證與授權

*   **認證機制:** OAuth 2.0 (Authorization Code Grant with Google)。客戶端需在 `Authorization` header 中提供 `Bearer <access_token>`。
*   **授權模型:** 基於角色的訪問控制 (RBAC)。
    *   `member`: 普通成員權限。
    *   `admin`: 管理員權限。
*   **權限失敗:**
    *   `401 Unauthorized`: 未提供 Token 或 Token 無效。
    *   `403 Forbidden`: Token 有效但無權訪問該資源。

---

## 4. 通用 API 行為

*   **分頁:** 採用基於偏移量 (Offset-based) 的分頁。
    *   **查詢參數:** `offset` (預設 0), `limit` (預設 25, 最大 100)。
    *   **回應結構:**
        ```json
        {
          "data": [ ... ],
          "total": 150,
          "offset": 0,
          "limit": 25
        }
        ```

---

## 5. 錯誤處理

*   **標準錯誤回應格式:**
    ```json
    {
      "error": {
        "code": "parameter_invalid",
        "message": "The 'status' parameter is invalid.",
        "request_id": "uuid-v4-request-id"
      }
    }
    ```
*   **通用 HTTP 狀態碼:** `400 Bad Request`, `401 Unauthorized`, `403 Forbidden`, `404 Not Found`, `409 Conflict`, `500 Internal Server Error`。

---

## 6. API 端點詳述

### 6.1 資源：認證 (Authentication)

*   **資源路徑:** `/auth`

#### `GET /auth/google/login`
*   **描述:** 重定向到 Google OAuth 登入頁面。由前端發起。

#### `GET /auth/google/callback`
*   **描述:** 處理 Google 回調，生成 JWT。此過程後端處理，前端接收最終 Token。

#### `GET /auth/me`
*   **描述:** 獲取當前登入用戶的資訊。
*   **授權:** `member`
*   **成功回應 (200 OK):** `User`

---

### 6.2 資源：出缺勤 (Attendance)

*   **資源路徑:** `/attendances`

#### `GET /attendances/me`
*   **描述:** 獲取我自己的出缺勤記錄。
*   **授權:** `member`
*   **查詢參數:** `offset`, `limit`, `event_id` (可選)
*   **成功回應 (200 OK):** `Pagination(Attendance)`

#### `POST /attendances/makeup`
*   **描述:** 提交一筆補簽申請。
*   **授權:** `member`
*   **請求體:** `MakeupRequestCreate`
*   **成功回應 (201 Created):** `MakeupRequest`
*   **錯誤回應:**
    *   `409 Conflict`: 如果該活動的 `Attendance` 狀態已為 `PRESENT` 或 `LEAVE`。

---

### 6.3 資源：請假 (Leave)

*   **資源路徑:** `/leave-requests`

#### `POST /leave-requests`
*   **描述:** 提交一筆請假申請。
*   **授權:** `member`
*   **請求體:** `LeaveRequestCreate`
*   **成功回應 (201 Created):** `LeaveRequest`

---

### 6.4 資源：管理 (Admin)

*   **資源路徑:** `/admin`
*   **授權:** 所有端點皆需 `admin` 權限。

#### `GET /admin/requests`
*   **描述:** 獲取所有待審核的申請 (補簽/請假)。
*   **查詢參數:** `offset`, `limit`, `type` (`makeup` 或 `leave`)
*   **成功回應 (200 OK):** `Pagination(MakeupRequest | LeaveRequest)`

#### `POST /admin/requests/{request_id}/approve`
*   **描述:** 批准一筆申請。
*   **成功回應 (204 No Content):**

#### `POST /admin/requests/{request_id}/reject`
*   **描述:** 駁回一筆申請。
*   **請求體:** `{ "reason": "string" }` (必填)
*   **成功回應 (204 No Content):**

---

## 7. 資料模型/Schema 定義

### `User`
```json
{
  "id": "user_string_id",
  "name": "陳大文",
  "email": "damon@workspace.com",
  "avatar_url": "https://...",
  "role": "member" // or "admin"
}
```

### `Attendance`
```json
{
  "id": "attendance_string_id",
  "user_id": "user_string_id",
  "event_id": "event_string_id",
  "status": "PRESENT" // PRESENT, LATE, ABSENT, LEAVE, MAKEUP, EARLY_LEAVE
}
```

### `LeaveRequestCreate` (Request Body)
```json
{
  "event_id": "string (required)",
  "type": "SICK_LEAVE", // SICK_LEAVE, PERSONAL_LEAVE
  "reason": "string (required)",
  "start_time": "string (date-time, optional)",
  "end_time": "string (date-time, optional)"
}
```

### `MakeupRequestCreate` (Request Body)
```