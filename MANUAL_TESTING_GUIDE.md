# 📋 手動測試指南 - 一步一步完成測試

> **目標**: 驗證 Google Calendar 自動簽到功能完整運作
> **預計時間**: 30-45 分鐘
> **難度**: ⭐⭐ (中等)

---

## 🎯 快速開始 - 3 步驟測試法

如果時間有限，請按照以下最小化測試步驟：

### 🚀 快速測試 (10 分鐘)

1. **開啟 Swagger UI**: http://localhost:8000/api/docs
2. **點擊 Authorize** → 使用 Google 登入 → 授予 Calendar 權限
3. **測試 POST /attendance/auto-checkin-calendar**
   - 點擊 "Try it out" → "Execute"
   - 查看回應是否正常

✅ 如果以上 3 步都成功，基本功能正常！

---

## 📚 完整測試指南

### 準備階段 (5 分鐘)

#### 1. 確認後端運行

```bash
# 檢查後端是否運行
curl http://localhost:8000/api/v1/health

# 預期回應:
# {"status":"ok","version":"v1"}
```

**如果未運行**:
```bash
cd /home/bheadwei/Live_broadcast_system/src/backend
poetry run uvicorn app.main:app --reload --port 8000
```

#### 2. 創建測試用 Calendar 事件

1. 前往 Google Calendar: https://calendar.google.com
2. 點擊 **"建立"** 按鈕
3. 填寫事件資訊：
   - **標題**: 簽到系統測試
   - **日期**: 今天
   - **時間**: 當前時間 +5 分鐘
   - **持續時間**: 30 分鐘
4. 點擊 **"儲存"**

⏰ **重要**: 記下事件開始時間，測試時需要用到！

---

## 🧪 測試階段 1: Swagger UI API 測試 (15 分鐘)

### Step 1: 開啟 Swagger UI

1. 瀏覽器開啟: http://localhost:8000/api/docs
2. 你應該會看到完整的 API 文檔頁面

**預期畫面**:
```
Smart Attendance System API v1.0
╔════════════════════════════════╗
║  Authentication               ║
║  Calendar                      ║
║  Attendance                    ║
║  ...                           ║
╚════════════════════════════════╝
```

---

### Step 2: OAuth 認證

1. **找到右上角的 🔒 "Authorize" 按鈕** (綠色)
2. **點擊 "Authorize"**
3. 在彈出的對話框中：
   - 找到 **"OAuth2AuthorizationCodeBearer"** 區塊
   - 勾選所有 scopes:
     - ✅ `openid`
     - ✅ `email`
     - ✅ `profile`
     - ✅ `https://www.googleapis.com/auth/calendar.readonly`
     - ✅ `https://www.googleapis.com/auth/calendar.events.readonly`
   - 點擊 **"Authorize"** 按鈕

4. **Google OAuth 登入流程**:
   - 選擇你的 Google 帳號
   - 查看權限請求列表
   - ⚠️ **確保授予 Calendar 權限**
   - 點擊 **"允許"**

5. **認證成功**:
   - 對話框應該顯示 "Authorized"
   - 點擊 **"Close"** 關閉

✅ **驗證**: 頁面上的 🔒 圖示應該變成已鎖定狀態

---

### Step 3: 測試 Calendar API

#### 3.1 測試取得今日事件

1. **找到 `calendar` 區塊** (藍色標籤)
2. **展開 `GET /api/v1/calendar/events/today`**
3. 點擊 **"Try it out"** (右上角)
4. 點擊 **"Execute"** (藍色大按鈕)

**預期結果**:
```json
{
  "events": [
    {
      "id": "abc123...",
      "title": "簽到系統測試",
      "description": "",
      "start_time": "2025-10-18T14:00:00Z",
      "end_time": "2025-10-18T14:30:00Z"
    }
  ],
  "total": 1
}
```

✅ **成功**: Response Code = **200**，events 列表包含你的測試事件

❌ **失敗**: 如果返回 401 或 403，請重新執行 Step 2 認證

---

#### 3.2 測試簽到狀態檢查

1. **展開 `GET /api/v1/calendar/check-in-status`**
2. 點擊 **"Try it out"**
3. 點擊 **"Execute"**

**情況 A: 事件未開始**
```json
{
  "should_check_in": false,
  "current_event": null,
  "message": "No event happening right now"
}
```

**情況 B: 事件進行中** (當測試事件開始後)
```json
{
  "should_check_in": true,
  "current_event": {
    "id": "abc123...",
    "title": "簽到系統測試",
    "start_time": "2025-10-18T14:00:00Z",
    "end_time": "2025-10-18T14:30:00Z"
  },
  "message": "You should be in '簽到系統測試' right now"
}
```

---

#### 3.3 測試自動簽到 ⭐ (重點)

**⏰ 時機**: 等到測試事件開始後執行

1. **展開 `POST /api/v1/attendance/auto-checkin-calendar`**
2. 點擊 **"Try it out"**
3. 點擊 **"Execute"**

**第一次執行 - 成功簽到**:
```json
{
  "checked_in": true,
  "message": "Successfully checked in for '簽到系統測試'",
  "event": {
    "id": "evt_123",
    "title": "簽到系統測試",
    "start_time": "2025-10-18T14:00:00Z",
    "end_time": "2025-10-18T14:30:00Z"
  },
  "attendance": {
    "id": "att_456",
    "status": "PRESENT",  // 或 "LATE"
    "check_in_time": "2025-10-18T14:03:00Z",
    "is_late": false,     // 或 true
    "late_minutes": 0     // 或實際遲到分鐘數
  }
}
```

**第二次執行 - 重複簽到防護**:
```json
{
  "checked_in": true,
  "message": "Already checked in for this event",
  "event": { ... },
  "attendance": { ... }  // 相同的簽到記錄
}
```

**無事件時**:
```json
{
  "checked_in": false,
  "message": "No calendar event happening right now",
  "event": null,
  "attendance": null
}
```

---

### Step 4: 驗證簽到記錄

1. **展開 `GET /api/v1/attendance/history`**
2. 點擊 **"Try it out"**
3. 設定 `limit` = 10
4. 點擊 **"Execute"**

**預期結果**:
```json
{
  "success": true,
  "data": [
    {
      "id": "att_456",
      "userId": "usr_123",
      "eventId": "evt_123",
      "eventTitle": "簽到系統測試",
      "status": "present",
      "checkedInAt": "2025-10-18T14:03:00Z",
      "createdAt": "2025-10-18T14:03:00Z"
    }
  ]
}
```

✅ **驗證**: 列表中應該包含剛才的簽到記錄

---

## 🧪 測試階段 2: 前端 Dashboard 測試 (20 分鐘)

### Step 1: 啟動前端開發伺服器

```bash
cd /home/bheadwei/Live_broadcast_system/src/frontend
npm run dev
```

**預期輸出**:
```
  VITE v5.4.20  ready in XXX ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

---

### Step 2: 登入 Dashboard

1. **開啟瀏覽器**: http://localhost:5173
2. **點擊 "使用 Google 登入"**
3. **完成 OAuth 流程** (與 Swagger UI 相同)
4. **成功後應重定向到 Dashboard**

---

### Step 3: 觀察自動簽到

#### 準備：開啟瀏覽器開發者工具

1. 按 `F12` 或 `Ctrl+Shift+I` (Windows/Linux)
2. 切換到 **Console** 標籤
3. 過濾日誌：輸入 `Auto Check-in`

#### 測試 A: 頁面載入自動簽到

**操作**: 刷新頁面 (F5)

**觀察點**:
1. **Console 日誌**:
   ```
   [Auto Check-in] Checking...
   [Auto Check-in] No event or error: No calendar event happening right now
   ```
   OR (如果事件進行中):
   ```
   [Auto Check-in] Successful check-in
   ```

2. **Toast 通知** (如果簽到成功):
   - ✅ 綠色通知: "✅ 準時簽到：簽到系統測試"
   - ⏰ 黃色通知: "⏰ 遲到簽到：簽到系統測試 (遲到 X 分鐘)"

3. **Today Status 卡片**:
   - 狀態從 "未簽到" 變為 "已簽到"
   - 顯示簽到時間

---

#### 測試 B: 手動按鈕觸發

**操作**: 點擊 "📅 Calendar 簽到" 按鈕

**觀察點**:
1. 先顯示 "檢查中..." Toast (2秒)
2. 然後顯示結果通知
3. Console 有對應日誌

**預期通知**:
- 有事件且未簽到: "✅ 準時簽到：..."
- 有事件但已簽到: "ℹ️ 已經簽到過此事件"
- 無事件: "ℹ️ 目前沒有需要簽到的事件"
- 錯誤: "❌ 自動簽到檢查失敗"

---

#### 測試 C: 定期輪詢 (可選)

**操作**: 保持 Dashboard 頁面開啟 5 分鐘

**觀察點**:
- 每 5 分鐘，Console 應顯示:
  ```
  [Auto Check-in] Periodic check at [時間]
  ```
- 如果期間有事件開始，應自動簽到並顯示通知

**驗證方法**: 查看 Console 時間戳，確認間隔約 5 分鐘

---

#### 測試 D: 頁面焦點觸發

**操作**:
1. 切換到其他瀏覽器分頁
2. 等待 30 秒
3. 切換回 Dashboard

**預期**: Console 顯示
```
[Auto Check-in] Visibility change triggered check
```

---

### Step 4: 驗證簽到歷史

在 Dashboard 中：

1. **查看 "Today Status" 卡片**:
   - ✅ 顯示 "已簽到"
   - 顯示簽到時間
   - 如果遲到，顯示遲到分鐘數

2. **查看 "Attendance History" 列表**:
   - ✅ 新增一筆記錄
   - 記錄包含：
     - 事件標題: "簽到系統測試"
     - 狀態: PRESENT 或 LATE
     - 簽到時間

---

## 🧪 測試階段 3: 遲到簽到測試 (10 分鐘)

### 目標：驗證遲到判斷邏輯

#### 準備：創建新測試事件

1. **Google Calendar 創建事件**:
   - 標題: "遲到測試事件"
   - 時間: 當前時間 +3 分鐘
   - 持續: 30 分鐘

2. **等待事件開始後 10 分鐘**
   - 例如：事件 14:00 開始，等到 14:10

3. **在 Dashboard 點擊 "Calendar 簽到"**

#### 預期結果

**Toast 通知**:
```
⏰ 遲到簽到：遲到測試事件 (遲到 10 分鐘)
```

**Attendance 記錄**:
```json
{
  "status": "LATE",
  "is_late": true,
  "late_minutes": 10
}
```

**驗證點**:
- ✅ status 為 "LATE"
- ✅ late_minutes 計算正確 (實際時間 - 開始時間 - grace period)
- ✅ Toast 顯示遲到時間

---

## 📊 測試結果記錄表

請在測試時填寫：

### Swagger UI 測試

| 測試項目 | 結果 | 備註 |
|---------|------|------|
| OAuth 認證 | ⬜ 通過 / ⬜ 失敗 |  |
| GET /calendar/events/today | ⬜ 通過 / ⬜ 失敗 |  |
| GET /calendar/check-in-status | ⬜ 通過 / ⬜ 失敗 |  |
| POST /attendance/auto-checkin-calendar | ⬜ 通過 / ⬜ 失敗 |  |
| GET /attendance/history | ⬜ 通過 / ⬜ 失敗 |  |

### Dashboard 前端測試

| 測試項目 | 結果 | 備註 |
|---------|------|------|
| 頁面載入自動簽到 | ⬜ 通過 / ⬜ 失敗 |  |
| 手動按鈕觸發 | ⬜ 通過 / ⬜ 失敗 |  |
| Toast 通知正確顯示 | ⬜ 通過 / ⬜ 失敗 |  |
| Today Status 更新 | ⬜ 通過 / ⬜ 失敗 |  |
| Attendance History 更新 | ⬜ 通過 / ⬜ 失敗 |  |
| 定期輪詢 (5分鐘) | ⬜ 通過 / ⬜ 失敗 |  |
| 頁面焦點觸發 | ⬜ 通過 / ⬜ 失敗 |  |

### 遲到簽到測試

| 測試項目 | 結果 | 備註 |
|---------|------|------|
| 遲到狀態判斷 | ⬜ 通過 / ⬜ 失敗 |  |
| 遲到分鐘計算 | ⬜ 通過 / ⬜ 失敗 |  |
| Toast 顯示遲到資訊 | ⬜ 通過 / ⬜ 失敗 |  |

---

## ❌ 常見問題排解

### 問題 1: Swagger UI 認證失敗

**症狀**: 點擊 Authorize 後無反應，或返回錯誤

**解決方案**:
1. 檢查後端是否運行: `curl http://localhost:8000/api/v1/health`
2. 檢查 Google OAuth 設定:
   ```bash
   # 查看環境變數
   echo $GOOGLE_CLIENT_ID
   echo $GOOGLE_CLIENT_SECRET
   ```
3. 確保 Redirect URI 設定正確:
   - http://localhost:8000/api/v1/auth/callback/google

---

### 問題 2: Calendar API 返回 403

**症狀**: API 調用返回 "Calendar access not granted"

**解決方案**:
1. 重新執行 OAuth 認證
2. **確保勾選 Calendar 相關 scopes**:
   - `https://www.googleapis.com/auth/calendar.readonly`
   - `https://www.googleapis.com/auth/calendar.events.readonly`
3. 檢查 User 表的 google_access_token 是否存在

---

### 問題 3: 前端無法連接後端

**症狀**: Dashboard 無法載入，Console 顯示 CORS 錯誤

**解決方案**:
1. 確認後端運行: http://localhost:8000
2. 檢查前端 `.env` 檔案:
   ```
   VITE_API_BASE_URL=http://localhost:8000
   ```
3. 重啟前端開發伺服器

---

### 問題 4: 自動簽到無反應

**症狀**: 點擊按鈕無反應，Console 無日誌

**解決方案**:
1. 開啟 Console，查看錯誤訊息
2. 檢查是否已登入 (有 Bearer Token)
3. 檢查 Calendar 事件是否存在且正在進行中
4. 查看後端日誌: `tail -f /tmp/backend.log`

---

### 問題 5: Token 過期

**症狀**: API 返回 401 Unauthorized

**解決方案**:
1. 系統應自動刷新 Token
2. 如果刷新失敗，請重新登入
3. 檢查後端日誌是否有 token refresh 錯誤

---

## 🎯 測試完成標準

所有測試項目應符合以下標準：

✅ **Swagger UI 測試** (5/5 通過)
- OAuth 認證成功
- 所有 Calendar API 返回 200
- Auto check-in API 正常運作
- 回應格式符合預期
- 重複簽到有防護

✅ **Dashboard 測試** (7/7 通過)
- 頁面載入自動簽到
- 手動按鈕正常運作
- Toast 通知正確顯示
- UI 狀態正確更新
- 定期輪詢運作
- 頁面焦點觸發
- Console 日誌正常

✅ **遲到測試** (3/3 通過)
- 遲到狀態正確判斷
- 遲到時間計算準確
- Toast 顯示遲到資訊

---

## 📝 完成後

### 提交測試報告

將填寫好的測試結果記錄表存檔為：
```
TESTING_RESULTS_[日期].md
```

### 發現問題

如果發現任何問題，請記錄：
1. **問題描述**
2. **重現步驟**
3. **預期行為**
4. **實際行為**
5. **截圖/日誌**

---

## 🔗 參考文檔

- [測試執行報告](./TESTING_EXECUTION_REPORT.md)
- [完整實作報告](./IMPLEMENTATION_COMPLETE_REPORT.md)
- [API 測試指南](./API_TESTING_GUIDE.md)

---

**準備好了嗎？開始測試吧！** 🚀

**預計完成時間**: 45 分鐘
**建議先從 Swagger UI 開始**: 最快速驗證基本功能 ✨
