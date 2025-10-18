# Google Calendar 整合 API 測試指南

> **測試日期**: 2025-10-18
> **後端狀態**: ✅ 運行中 (http://localhost:8000)
> **資料庫**: ✅ 已更新 (Calendar token欄位已添加)

---

## 🎯 可用的 Calendar API 端點

### 1. 列出日曆事件
```bash
GET /api/v1/calendar/events?days_ahead=7
```

**功能**: 列出未來 N 天的日曆事件

**參數**:
- `days_ahead` (查詢參數, 可選): 往前看幾天 (1-30天，預設7天)

**回應範例**:
```json
{
  "events": [
    {
      "id": "abc123",
      "title": "Team Meeting",
      "description": "Weekly standup",
      "start_time": "2025-10-18T09:00:00Z",
      "end_time": "2025-10-18T10:00:00Z",
      "creator": {
        "email": "user@example.com"
      }
    }
  ],
  "total": 1
}
```

---

### 2. 取得今日事件
```bash
GET /api/v1/calendar/events/today
```

**功能**: 取得今天的所有日曆事件

**回應**: 與上面相同的格式

---

### 3. 檢查簽到狀態
```bash
GET /api/v1/calendar/check-in-status
```

**功能**: 檢查使用者當前是否應該簽到

**回應範例**:
```json
{
  "should_check_in": true,
  "current_event": {
    "id": "xyz789",
    "title": "Project Review",
    "start_time": "2025-10-18T14:00:00Z",
    "end_time": "2025-10-18T15:00:00Z"
  },
  "message": "You should be in 'Project Review' right now"
}
```

---

### 4. 取得特定事件
```bash
GET /api/v1/calendar/events/{event_id}
```

**功能**: 取得特定日曆事件的詳細資訊

**參數**:
- `event_id` (路徑參數): Google Calendar 事件 ID

---

### 5. 自動簽到 (M2 核心功能) ⭐
```bash
POST /api/v1/attendance/auto-checkin-calendar
```

**功能**:
- 檢查使用者當前是否有進行中的事件
- 自動將事件同步到 Event 表
- 創建 Attendance 記錄
- 判斷 PRESENT 或 LATE 狀態

**回應範例 (成功簽到)**:
```json
{
  "checked_in": true,
  "message": "Successfully checked in for 'Team Meeting'",
  "event": {
    "id": "abc123",
    "title": "Team Meeting",
    "start_time": "2025-10-18T09:00:00Z",
    "end_time": "2025-10-18T10:00:00Z"
  },
  "attendance": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "LATE",
    "check_in_time": "2025-10-18T09:08:00Z",
    "is_late": true,
    "late_minutes": 8
  }
}
```

**回應範例 (無事件)**:
```json
{
  "checked_in": false,
  "message": "No calendar event happening right now",
  "event": null,
  "attendance": null
}
```

**回應範例 (無權限)**:
```json
{
  "checked_in": false,
  "message": "Calendar access not granted. Please re-authenticate with Calendar permissions.",
  "event": null,
  "attendance": null
}
```

---

## 🔐 如何測試 (需要認證)

### 方法 1: 使用 Swagger UI (推薦) ✅

1. **開啟 API 文檔**:
   ```
   http://localhost:8000/api/docs
   ```

2. **登入認證**:
   - 點擊右上角 🔒 **Authorize** 按鈕
   - 使用 Google OAuth 登入
   - 確保授予 Calendar 權限

3. **測試端點**:
   - 展開 `calendar` 或 `attendance` 標籤
   - 點擊 "Try it out"
   - 執行請求並查看回應

---

### 方法 2: cURL 命令行

**步驟 1**: 取得 JWT Token

先透過前端完成 Google OAuth 登入，從瀏覽器開發者工具中複製 JWT token

**步驟 2**: 使用 Token 測試

```bash
# 設定你的 token
export TOKEN="your_jwt_token_here"

# 測試今天的事件
curl -X GET "http://localhost:8000/api/v1/calendar/events/today" \
  -H "Authorization: Bearer $TOKEN"

# 測試簽到狀態
curl -X GET "http://localhost:8000/api/v1/calendar/check-in-status" \
  -H "Authorization: Bearer $TOKEN"

# 執行自動簽到
curl -X POST "http://localhost:8000/api/v1/attendance/auto-checkin-calendar" \
  -H "Authorization: Bearer $TOKEN"
```

---

### 方法 3: 前端整合 (推薦用於生產環境)

在 Dashboard 組件中：

```typescript
// 自動簽到範例
const autoCheckIn = async () => {
  try {
    const response = await fetch('/api/v1/attendance/auto-checkin-calendar', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });

    const data = await response.json();

    if (data.checked_in) {
      console.log('✅ 簽到成功:', data.event.title);
      console.log('📊 狀態:', data.attendance.status);

      if (data.attendance.is_late) {
        console.log('⏰ 遲到', data.attendance.late_minutes, '分鐘');
      }
    } else {
      console.log('ℹ️', data.message);
    }
  } catch (error) {
    console.error('❌ 自動簽到失敗:', error);
  }
};

// 頁面載入時執行
useEffect(() => {
  autoCheckIn();
}, []);

// 定期檢查 (每5分鐘)
useEffect(() => {
  const interval = setInterval(autoCheckIn, 5 * 60 * 1000);
  return () => clearInterval(interval);
}, []);
```

---

## 📊 資料流程

```
1. 使用者登入 (Google OAuth + Calendar權限)
   ↓
2. Token儲存 (JWT + Refresh Token)
   ↓
3. 前端呼叫 auto-checkin-calendar
   ↓
4. 後端檢查 Google Calendar
   ↓
5. 同步事件到 Event表 (如果不存在)
   ↓
6. 創建 Attendance記錄
   ↓
7. 判斷 PRESENT/LATE 狀態
   ↓
8. 返回完整簽到資訊
```

---

## ✅ 實作完成項目

- ✅ Google Calendar API 整合
- ✅ 自動 Token 刷新機制
- ✅ 事件驅動自動簽到
- ✅ 智能遲到判斷
- ✅ Event 自動同步
- ✅ Attendance 記錄創建
- ✅ RESTful API 設計
- ✅ 完整錯誤處理

---

## 🚀 下一步

1. **前端整合**: 在 Dashboard 實作自動簽到 UI
2. **測試驗證**: 使用實際的 Google Calendar 事件測試
3. **錯誤處理**: 優化使用者體驗與錯誤提示
4. **通知系統**: 實作簽到提醒功能

---

**後端服務狀態**: 🟢 運行中
**API 文檔**: http://localhost:8000/api/docs
**Health Check**: http://localhost:8000/api/v1/health
