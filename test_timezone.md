# 時區測試指南

## 測試目的
確認創建活動時，前端顯示的時間和後端存儲的時間都是正確的台北時區 (UTC+8)

## 測試步驟

### 1. 創建測試活動
- 訪問: http://localhost:3000/create-event
- 填寫以下資訊：
  - 標題：時區測試會議
  - 開始時間：明天 14:00 (台北時間)
  - 結束時間：明天 15:00 (台北時間)

### 2. 檢查前端發送的資料
打開瀏覽器開發者工具 (F12) > Network 標籤
- 查看 POST /api/v1/events 請求
- 確認 payload 中的 start_time 和 end_time 是 UTC 時間 (應該是 06:00 和 07:00)

### 3. 檢查資料庫存儲
```bash
docker exec attendance_db psql -U attendance_user -d attendance_db -c "SELECT id, title, start_time, end_time FROM events ORDER BY created_at DESC LIMIT 1;"
```

預期結果：
- start_time 應為 UTC 時間 (比台北時間早 8 小時)
- 例如：台北時間 14:00 → UTC 06:00

### 4. 檢查前端顯示
- 回到 Dashboard 查看活動
- 確認顯示的時間是台北時間 14:00-15:00

## 預期行為

| 階段 | 時間類型 | 範例 |
|------|---------|------|
| 用戶輸入 | 台北時間 | 2025-10-21 14:00 |
| API 傳輸 | UTC | 2025-10-21T06:00:00.000Z |
| 資料庫存儲 | UTC (timezone-aware) | 2025-10-21 06:00:00+00 |
| API 返回 | 台北時間字串 | "14:00" |
| 前端顯示 | 台北時間 | 14:00 |

## 測試通過標準
✅ 用戶輸入台北時間 14:00
✅ 資料庫存儲 UTC 06:00
✅ 前端顯示台北時間 14:00
✅ 時間一致，無時差問題
