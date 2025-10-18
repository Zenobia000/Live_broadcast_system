#!/usr/bin/env python3
"""
Create event using Taipei time (UTC+8).
"""
import sqlite3
from datetime import datetime, timedelta, timezone

# Taipei timezone (UTC+8)
TAIPEI_TZ = timezone(timedelta(hours=8))

# Connect to database
db_path = "src/backend/attendance.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get user ID
cursor.execute("SELECT id FROM users LIMIT 1")
user_row = cursor.fetchone()

if not user_row:
    print("❌ No user found. Please login first.")
    exit(1)

user_id = user_row[0]
print(f"✅ Found user ID: {user_id}")

# Create event at Taipei time 2025/10/19 00:30
taipei_now = datetime(2025, 10, 19, 0, 30, 0, tzinfo=TAIPEI_TZ)
utc_now = taipei_now.astimezone(timezone.utc)

print(f"\n當前時間:")
print(f"  台北時間: {taipei_now.strftime('%Y/%m/%d %H:%M:%S')} (UTC+8)")
print(f"  UTC 時間: {utc_now.strftime('%Y/%m/%d %H:%M:%S')}")

# Create event starting now and lasting 2 hours
event_start = utc_now
event_end = utc_now + timedelta(hours=2)
created_at = utc_now.isoformat()

cursor.execute("""
INSERT INTO events (title, description, start_time, end_time, google_event_id, created_by, grace_period_minutes, created_at, updated_at)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    "深夜開發會議",
    f"台北時間 {taipei_now.strftime('%Y/%m/%d %H:%M')} 開始的測試事件",
    event_start.isoformat(),
    event_end.isoformat(),
    f"test-event-taipei-{int(utc_now.timestamp())}",
    user_id,
    5,
    created_at,
    created_at
))

conn.commit()

print("\n✅ 成功創建測試事件:")
print(f"   事件名稱: 深夜開發會議")
print(f"   開始時間: {taipei_now.strftime('%Y/%m/%d %H:%M')} (台北時間)")
print(f"   結束時間: {(taipei_now + timedelta(hours=2)).strftime('%Y/%m/%d %H:%M')} (台北時間)")
print(f"   持續時間: 2小時")
print(f"   UTC 時間: {event_start.strftime('%Y/%m/%d %H:%M')} - {event_end.strftime('%Y/%m/%d %H:%M')}")

# Show ongoing events
cursor.execute("""
    SELECT title, start_time, end_time,
           CASE
               WHEN start_time <= ? AND end_time >= ? THEN '✅ 進行中'
               WHEN start_time > ? THEN '⏳ 未開始'
               ELSE '❌ 已結束'
           END as status
    FROM events
    ORDER BY start_time DESC
    LIMIT 5
""", (utc_now.isoformat(), utc_now.isoformat(), utc_now.isoformat()))

print("\n📋 最近的事件 (UTC 時間):")
for row in cursor.fetchall():
    print(f"  {row[3]} {row[0]}")
    start = datetime.fromisoformat(row[1])
    end = datetime.fromisoformat(row[2])
    # Convert to Taipei time for display
    start_taipei = start.replace(tzinfo=timezone.utc).astimezone(TAIPEI_TZ)
    end_taipei = end.replace(tzinfo=timezone.utc).astimezone(TAIPEI_TZ)
    print(f"    台北時間: {start_taipei.strftime('%m/%d %H:%M')} - {end_taipei.strftime('%m/%d %H:%M')}")
    print(f"    UTC 時間: {start.strftime('%m/%d %H:%M')} - {end.strftime('%m/%d %H:%M')}")

conn.close()

print("\n🎉 現在刷新 Dashboard 頁面 (Ctrl+Shift+R)，你應該能看到這個新事件！")
print("💡 提示：點擊「手動簽到」按鈕來測試簽到功能")
print("\n⏰ 所有時間都以 UTC 格式存儲，但顯示時會轉換為台北時間")
