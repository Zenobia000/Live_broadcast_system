#!/usr/bin/env python3
"""
Create a test event starting from current time.
"""
import sqlite3
from datetime import datetime, timedelta, timezone

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

# Get current time (timezone-aware)
now = datetime.now(timezone.utc)
local_now = datetime.now()

print(f"\n當前時間:")
print(f"  本地時間: {local_now.strftime('%Y/%m/%d %H:%M:%S')}")
print(f"  UTC 時間: {now.strftime('%Y/%m/%d %H:%M:%S')}")

# Create event starting now and lasting 2 hours
event_start = now
event_end = now + timedelta(hours=2)
created_at = now.isoformat()

cursor.execute("""
INSERT INTO events (title, description, start_time, end_time, google_event_id, created_by, grace_period_minutes, created_at, updated_at)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    "即時測試會議",
    "這是從當前時間開始的測試事件",
    event_start.isoformat(),
    event_end.isoformat(),
    f"test-event-now-{int(now.timestamp())}",
    user_id,
    5,
    created_at,
    created_at
))

conn.commit()

print("\n✅ 成功創建測試事件:")
print(f"   事件名稱: 即時測試會議")
print(f"   開始時間: {event_start.strftime('%Y/%m/%d %H:%M')} UTC")
print(f"   結束時間: {event_end.strftime('%Y/%m/%d %H:%M')} UTC")
print(f"   持續時間: 2小時")

# Verify
cursor.execute("SELECT COUNT(*) FROM events")
event_count = cursor.fetchone()[0]
print(f"\n📊 總事件數量: {event_count}")

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
""", (now.isoformat(), now.isoformat(), now.isoformat()))

print("\n📋 最近的事件:")
for row in cursor.fetchall():
    print(f"  {row[3]} {row[0]}")
    start = datetime.fromisoformat(row[1])
    end = datetime.fromisoformat(row[2])
    print(f"    {start.strftime('%m/%d %H:%M')} - {end.strftime('%m/%d %H:%M')}")

conn.close()

print("\n🎉 現在刷新 Dashboard 頁面，你應該能看到這個新事件並進行簽到！")
print("💡 提示：點擊「手動簽到」按鈕來簽到這個剛創建的會議")
