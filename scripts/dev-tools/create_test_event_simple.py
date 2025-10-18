#!/usr/bin/env python3
"""
Create test events for attendance system testing.
Simple version using direct SQL.
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

# Event 1: Ongoing event (started 10 minutes ago, ends in 50 minutes)
event1_start = (now - timedelta(minutes=10)).isoformat()
event1_end = (now + timedelta(minutes=50)).isoformat()
created_at = now.isoformat()

cursor.execute("""
INSERT INTO events (title, description, start_time, end_time, google_event_id, created_by, grace_period_minutes, created_at, updated_at)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    "測試會議 - 正在進行",
    "這是一個測試事件，用於測試簽到功能",
    event1_start,
    event1_end,
    f"test-event-ongoing-{int(now.timestamp())}",
    user_id,
    5,
    created_at,
    created_at
))

# Event 2: Upcoming event (starts in 1 hour)
event2_start = (now + timedelta(hours=1)).isoformat()
event2_end = (now + timedelta(hours=2)).isoformat()

cursor.execute("""
INSERT INTO events (title, description, start_time, end_time, google_event_id, created_by, grace_period_minutes, created_at, updated_at)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    "下午團隊會議",
    "每日站立會議",
    event2_start,
    event2_end,
    f"test-event-upcoming-{int(now.timestamp())}",
    user_id,
    5,
    created_at,
    created_at
))

# Event 3: Tomorrow morning event
tomorrow = now + timedelta(days=1)
tomorrow_morning = tomorrow.replace(hour=9, minute=0, second=0, microsecond=0)
event3_start = tomorrow_morning.isoformat()
event3_end = (tomorrow_morning + timedelta(hours=1)).isoformat()

cursor.execute("""
INSERT INTO events (title, description, start_time, end_time, google_event_id, created_by, grace_period_minutes, created_at, updated_at)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    "明日晨會",
    "每日晨間會議",
    event3_start,
    event3_end,
    f"test-event-tomorrow-{int(now.timestamp())}",
    user_id,
    10,
    created_at,
    created_at
))

conn.commit()

print("\n✅ 成功創建測試事件:")
print(f"   1. 測試會議 - 正在進行")
print(f"      開始: {datetime.fromisoformat(event1_start).strftime('%Y-%m-%d %H:%M')} UTC (正在進行)")
print(f"      結束: {datetime.fromisoformat(event1_end).strftime('%Y-%m-%d %H:%M')} UTC")
print(f"\n   2. 下午團隊會議")
print(f"      開始: {datetime.fromisoformat(event2_start).strftime('%Y-%m-%d %H:%M')} UTC (1小時後)")
print(f"      結束: {datetime.fromisoformat(event2_end).strftime('%Y-%m-%d %H:%M')} UTC")
print(f"\n   3. 明日晨會")
print(f"      開始: {datetime.fromisoformat(event3_start).strftime('%Y-%m-%d %H:%M')} UTC (明天)")
print(f"      結束: {datetime.fromisoformat(event3_end).strftime('%Y-%m-%d %H:%M')} UTC")

# Verify
cursor.execute("SELECT count(*) FROM events")
event_count = cursor.fetchone()[0]
print(f"\n📊 總事件數量: {event_count}")

conn.close()

print("\n🎉 現在刷新 Dashboard 頁面 (Ctrl+Shift+R)，你應該能看到簽到按鈕了！")
print("💡 提示：點擊「手動簽到」或「📅 Calendar 簽到」按鈕來測試簽到功能")
