# 🔧 Google OAuth 403 錯誤修復指南

> **錯誤訊息**: `錯誤 403：access_denied`
> **發生時間**: 2025-10-18
> **狀態**: 🔴 需要修復

---

## 📋 問題診斷

### 您遇到的錯誤

```
錯誤 403：access_denied
要求詳情：
- access_type=online
- scope=openid email profile calendar.readonly calendar.events.readonly
- response_type=code
- redirect_uri=http://localhost:8000/api/v1/auth/callback/google
- client_id=549912313617-457ltj9mlc7igrgmouhv9cd7rk0b20bf.apps.googleusercontent.com
```

### 錯誤原因分析

Google OAuth 403 錯誤通常由以下原因造成：

1. ❌ **Redirect URI 未在 Google Cloud Console 授權**
2. ❌ **請求的 Scopes 未啟用或未授權**
3. ❌ **OAuth 同意畫面未正確配置**
4. ❌ **應用程式處於測試模式，但測試使用者未添加**

---

## 🔍 檢查清單

### Step 1: 檢查 Google Cloud Console 設定

前往: https://console.cloud.google.com/apis/credentials

#### 1.1 檢查 OAuth 2.0 Client ID

找到您的 Client ID: `549912313617-457ltj9mlc7igrgmouhv9cd7rk0b20bf`

**必須配置的 Redirect URIs**:
```
http://localhost:8000/api/v1/auth/callback/google
http://127.0.0.1:8000/api/v1/auth/callback/google
```

#### 1.2 檢查 OAuth 同意畫面

前往: https://console.cloud.google.com/apis/credentials/consent

**必要設定**:
- ✅ 使用者類型: **外部** (External)
- ✅ 發布狀態: **測試中** (Testing) 或 **已發布** (In Production)
- ✅ 測試使用者: 添加您的 Google 帳號

#### 1.3 檢查啟用的 API

前往: https://console.cloud.google.com/apis/library

**必須啟用的 APIs**:
- ✅ Google Calendar API
- ✅ Google+ API (或 People API)

---

## 🛠️ 修復步驟

### 方法 1: 在 Google Cloud Console 添加 Redirect URI (推薦)

1. **前往 OAuth 2.0 Client ID 設定**
   ```
   https://console.cloud.google.com/apis/credentials
   ```

2. **點擊您的 Client ID**
   - 名稱: Smart Attendance System (或您的專案名稱)
   - Client ID: `549912313617-457ltj9mlc7igrgmouhv9cd7rk0b20bf`

3. **在 "已授權的重新導向 URI" 區段添加**:
   ```
   http://localhost:8000/api/v1/auth/callback/google
   http://127.0.0.1:8000/api/v1/auth/callback/google
   ```

4. **點擊 "儲存"**

5. **等待 5-10 分鐘**讓設定生效

---

### 方法 2: 添加測試使用者

如果您的應用程式處於測試模式：

1. **前往 OAuth 同意畫面**
   ```
   https://console.cloud.google.com/apis/credentials/consent
   ```

2. **點擊 "測試使用者" (Test Users)**

3. **添加您的 Google 帳號**
   - 點擊 "+ ADD USERS"
   - 輸入您的 Gmail 地址
   - 點擊 "儲存"

---

### 方法 3: 簡化 Scopes 請求 (暫時解決)

如果 Calendar scopes 導致問題，可以先測試基本認證：

**修改 `.env` 文件** (暫時移除 Calendar scopes):

```bash
# 原始設定
GOOGLE_CALENDAR_SCOPES=https://www.googleapis.com/auth/calendar.readonly,https://www.googleapis.com/auth/calendar.events.readonly

# 暫時改為空 (僅測試基本認證)
GOOGLE_CALENDAR_SCOPES=
```

**重啟後端**:
```bash
cd /home/bheadwei/Live_broadcast_system/src/backend
# 停止現有服務
pkill -f uvicorn

# 重新啟動
poetry run uvicorn app.main:app --reload --port 8000
```

**測試基本認證**:
- 前往 http://localhost:3001
- 嘗試登入
- 如果成功，說明是 Calendar scopes 的問題

---

### 方法 4: 發布應用程式 (生產環境)

如果您不想維護測試使用者清單：

1. **前往 OAuth 同意畫面**
   ```
   https://console.cloud.google.com/apis/credentials/consent
   ```

2. **點擊 "發布應用程式" (PUBLISH APP)**

3. **確認發布**

**注意**: 發布後應用程式會進入審核流程，但在審核完成前仍可使用。

---

## 🧪 驗證修復

### 測試步驟

1. **清除瀏覽器快取和 Cookie**
   - Chrome: `Ctrl+Shift+Del` → 選擇 "Cookie 和其他網站資料"

2. **前往前端登入頁面**
   ```
   http://localhost:3001
   ```

3. **點擊 "使用 Google 登入"**

4. **觀察 OAuth 流程**:
   - ✅ 應該看到 Google 登入頁面
   - ✅ 選擇帳號後，應該看到權限請求
   - ✅ 授權後，應該重定向回 Dashboard

### 預期的權限請求畫面

```
Smart Attendance System 要求權限：
□ 查看您的電子郵件地址
□ 查看您的個人資訊
□ 查看您的 Google 日曆活動 (唯讀)
```

---

## 📊 當前系統狀態

### 已修復的問題 ✅

1. **CORS 設定已更新**
   - 添加了 port 3000, 3001, 5173
   - 包含 localhost 和 127.0.0.1

2. **前端服務運行中**
   - URL: http://localhost:3001
   - Status: ✅ 200 OK

3. **後端服務運行中**
   - URL: http://localhost:8000
   - Health: ✅ {"status":"ok","version":"v1"}

### 待修復的問題 🔧

1. **Google OAuth 403 錯誤**
   - 原因: Redirect URI 或測試使用者未配置
   - 解決方案: 按照上述步驟 1-4 修復

---

## 🚀 快速修復流程 (5 分鐘)

如果您急著測試，請按照以下最快的步驟：

### Option A: 添加 Redirect URI (推薦)

```bash
1. 開啟 https://console.cloud.google.com/apis/credentials
2. 點擊您的 OAuth Client ID
3. 添加: http://localhost:8000/api/v1/auth/callback/google
4. 儲存
5. 等待 5 分鐘
6. 重新測試登入
```

### Option B: 添加測試使用者 (最快)

```bash
1. 開啟 https://console.cloud.google.com/apis/credentials/consent
2. 點擊 "測試使用者"
3. 添加您的 Gmail 地址
4. 儲存
5. 立即重新測試登入
```

---

## 🔗 相關資源

- [Google Cloud Console - Credentials](https://console.cloud.google.com/apis/credentials)
- [Google OAuth 2.0 文檔](https://developers.google.com/identity/protocols/oauth2)
- [測試指南](./MANUAL_TESTING_GUIDE.md)

---

## ❓ 常見問題

### Q1: 為什麼我的設定修改沒有立即生效？

**A**: Google Cloud 的設定更新通常需要 5-10 分鐘才會傳播到所有伺服器。請耐心等待。

### Q2: 我已經添加了 Redirect URI，但還是 403

**A**:
1. 確認 URI 完全一致（包括協議、域名、端口、路徑）
2. 清除瀏覽器快取和 Cookie
3. 等待 10 分鐘讓設定生效
4. 檢查是否添加了測試使用者

### Q3: 可以跳過 Calendar 權限嗎？

**A**: 可以。暫時移除 `.env` 中的 `GOOGLE_CALENDAR_SCOPES` 設定，先測試基本認證。成功後再逐步添加 Calendar 權限。

### Q4: 測試模式和生產模式有什麼區別？

**A**:
- **測試模式**: 只有添加到測試使用者清單的帳號可以登入（最多 100 個）
- **生產模式**: 任何 Google 帳號都可以登入，但需要通過 Google 審核

---

## 📝 修復記錄模板

完成修復後，請記錄：

```markdown
### OAuth 修復記錄

**修復日期**: YYYY-MM-DD HH:mm
**執行的操作**:
- [ ] 添加 Redirect URI
- [ ] 添加測試使用者
- [ ] 啟用 Calendar API
- [ ] 簡化 Scopes
- [ ] 其他: _______

**修復結果**:
- [ ] 成功登入
- [ ] 授權 Calendar 權限成功
- [ ] 可以訪問 Dashboard

**遇到的問題**:
[記錄任何問題]

**解決方案**:
[記錄解決方案]
```

---

**修復完成後，請前往 http://localhost:3001 測試登入！** 🚀
