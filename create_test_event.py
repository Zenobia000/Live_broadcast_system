#!/usr/bin/env python3
"""
Create test events for attendance system testing.
"""
import sys
import asyncio
from datetime import datetime, timedelta
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "src" / "backend"))

from sqlalchemy import select
from app.core.database import get_async_session_context
from app.models.calendar.event import Event
from app.models.auth.user import User


async def create_test_events():
    """Create test events for the attendance system."""

    async with get_async_session_context() as session:
        # Get the first user
        result = await session.execute(select(User).limit(1))
        user = result.scalar_one_or_none()

        if not user:
            print("❌ No user found. Please login first.")
            return

        print(f"✅ Found user: {user.email}")

        # Create events
        now = datetime.utcnow()

        # Event 1: Ongoing event (started 10 minutes ago, ends in 50 minutes)
        event1 = Event(
            title="測試會議 - 正在進行",
            description="這是一個測試事件，用於測試簽到功能",
            start_time=now - timedelta(minutes=10),
            end_time=now + timedelta(minutes=50),
            google_event_id=f"test-event-ongoing-{int(now.timestamp())}",
            created_by=user.id,
            grace_period_minutes=5
        )

        # Event 2: Upcoming event (starts in 1 hour)
        event2 = Event(
            title="下午團隊會議",
            description="每日站立會議",
            start_time=now + timedelta(hours=1),
            end_time=now + timedelta(hours=2),
            google_event_id=f"test-event-upcoming-{int(now.timestamp())}",
            created_by=user.id,
            grace_period_minutes=5
        )

        # Event 3: Tomorrow morning event
        tomorrow = now + timedelta(days=1)
        tomorrow_morning = tomorrow.replace(hour=9, minute=0, second=0, microsecond=0)
        event3 = Event(
            title="明日晨會",
            description="每日晨間會議",
            start_time=tomorrow_morning,
            end_time=tomorrow_morning + timedelta(hours=1),
            google_event_id=f"test-event-tomorrow-{int(now.timestamp())}",
            created_by=user.id,
            grace_period_minutes=10
        )

        session.add_all([event1, event2, event3])
        await session.commit()

        print("\n✅ 成功創建測試事件:")
        print(f"   1. {event1.title}")
        print(f"      開始: {event1.start_time.strftime('%Y-%m-%d %H:%M')} (正在進行)")
        print(f"      結束: {event1.end_time.strftime('%Y-%m-%d %H:%M')}")
        print(f"\n   2. {event2.title}")
        print(f"      開始: {event2.start_time.strftime('%Y-%m-%d %H:%M')} (1小時後)")
        print(f"      結束: {event2.end_time.strftime('%Y-%m-%d %H:%M')}")
        print(f"\n   3. {event3.title}")
        print(f"      開始: {event3.start_time.strftime('%Y-%m-%d %H:%M')} (明天)")
        print(f"      結束: {event3.end_time.strftime('%Y-%m-%d %H:%M')}")
        print("\n🎉 現在刷新 Dashboard 頁面，你應該能看到簽到按鈕了！")


if __name__ == "__main__":
    asyncio.run(create_test_events())
