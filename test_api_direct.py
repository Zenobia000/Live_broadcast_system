#!/usr/bin/env python3
"""
Direct test of attendance/today API logic
"""
from datetime import datetime, timezone, timedelta, date, time
import sqlite3

# Taipei timezone (UTC+8)
TAIPEI_TZ = timezone(timedelta(hours=8))

# Use timezone-aware datetime
now_utc = datetime.now(timezone.utc)
now_taipei = now_utc.astimezone(TAIPEI_TZ)
today = now_taipei.date()

print(f"=== Current Time ===")
print(f"UTC:    {now_utc.strftime('%Y/%m/%d %H:%M:%S')}")
print(f"Taipei: {now_taipei.strftime('%Y/%m/%d %H:%M:%S')}")
print(f"Today (Taipei date): {today}")
print()

# Get today's attendance records (timezone-aware, using Taipei timezone)
today_start = datetime.combine(today, time.min, tzinfo=TAIPEI_TZ).astimezone(timezone.utc)
today_end = datetime.combine(today, time.max, tzinfo=TAIPEI_TZ).astimezone(timezone.utc)

print(f"=== Today's Range (Taipei timezone) ===")
print(f"Start: {today_start.isoformat()}")
print(f"End:   {today_end.isoformat()}")
print()

# Connect to database
conn = sqlite3.connect('src/backend/attendance.db')
cursor = conn.cursor()

# Check for attendance today
cursor.execute('''
    SELECT a.id, e.title, a.check_in_time
    FROM attendance a
    JOIN events e ON a.event_id = e.id
    WHERE e.start_time >= ? AND e.start_time <= ?
    ORDER BY e.start_time DESC
    LIMIT 1
''', (today_start.isoformat(), today_end.isoformat()))

attendance = cursor.fetchone()
if attendance:
    print(f"✅ Found attendance today: {attendance[1]}")
    print()
else:
    print(f"❌ No attendance found today")
    print()

    # Check for current ongoing events
    print(f"=== Checking for Current Ongoing Events ===")
    print(f"Query: start_time <= {now_utc.isoformat()} AND end_time >= {now_utc.isoformat()}")
    print()

    cursor.execute('''
        SELECT id, title, start_time, end_time
        FROM events
        WHERE start_time <= ? AND end_time >= ?
        ORDER BY start_time DESC
        LIMIT 1
    ''', (now_utc.isoformat(), now_utc.isoformat()))

    current_event = cursor.fetchone()
    if current_event:
        print(f"✅ Found current event: {current_event[1]}")
        start = datetime.fromisoformat(current_event[2])
        end = datetime.fromisoformat(current_event[3])
        start_taipei = start.astimezone(TAIPEI_TZ)
        end_taipei = end.astimezone(TAIPEI_TZ)

        print(f"   Start (UTC):    {current_event[2]}")
        print(f"   Start (Taipei): {start_taipei.strftime('%H:%M')}")
        print(f"   End (UTC):      {current_event[3]}")
        print(f"   End (Taipei):   {end_taipei.strftime('%H:%M')}")
        print()
        print(f"✅ Should show event with check-in buttons!")
    else:
        print(f"❌ No current ongoing event found")
        print()

        # Check for next event
        print(f"=== Checking for Next Event ===")
        cursor.execute('''
            SELECT id, title, start_time, end_time
            FROM events
            WHERE start_time > ?
            ORDER BY start_time ASC
            LIMIT 1
        ''', (now_utc.isoformat(),))

        next_event = cursor.fetchone()
        if next_event:
            print(f"Found next event: {next_event[1]}")
            start = datetime.fromisoformat(next_event[2])
            end = datetime.fromisoformat(next_event[3])
            start_taipei = start.astimezone(TAIPEI_TZ)
            end_taipei = end.astimezone(TAIPEI_TZ)

            print(f"   Start (UTC):    {next_event[2]}")
            print(f"   Start (Taipei): {start_taipei.strftime('%H:%M')}")
            print(f"   End (UTC):      {next_event[3]}")
            print(f"   End (Taipei):   {end_taipei.strftime('%H:%M')}")

            # Check if it's already ended
            if end < now_utc:
                print(f"   ❌ WARNING: This event already ended!")
            elif start < now_utc:
                print(f"   ❌ WARNING: This event already started but query missed it!")
            else:
                print(f"   ✅ Valid future event")

conn.close()
