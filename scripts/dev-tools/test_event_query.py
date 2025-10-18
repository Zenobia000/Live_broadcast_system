#!/usr/bin/env python3
"""
Test event query with SQLAlchemy to debug timezone issues.
"""
import sys
import asyncio
from pathlib import Path
from datetime import datetime, timezone, timedelta

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "src" / "backend"))

from sqlalchemy import select, and_
from app.core.database import get_async_session_context
from app.models.calendar.event import Event

TAIPEI_TZ = timezone(timedelta(hours=8))

async def test_query():
    """Test querying ongoing events."""

    async with get_async_session_context() as session:
        now_utc = datetime.now(timezone.utc)
        now_taipei = now_utc.astimezone(TAIPEI_TZ)

        print(f"=== 當前時間 ===")
        print(f"UTC:    {now_utc.strftime('%Y/%m/%d %H:%M:%S')} (tzinfo: {now_utc.tzinfo})")
        print(f"Taipei: {now_taipei.strftime('%Y/%m/%d %H:%M:%S')}")
        print()

        # Test query
        print(f"=== Testing SQLAlchemy Query ===")
        print(f"Querying: start_time <= {now_utc.isoformat()} AND end_time >= {now_utc.isoformat()}")
        print()

        query = (
            select(Event)
            .where(
                and_(
                    Event.start_time <= now_utc,
                    Event.end_time >= now_utc
                )
            )
            .order_by(Event.start_time.desc())
        )

        result = await session.execute(query)
        events = result.scalars().all()

        print(f"Found {len(events)} ongoing events:")
        for event in events:
            print(f"\n  Event: {event.title}")
            print(f"    start_time: {event.start_time} (tzinfo: {event.start_time.tzinfo})")
            print(f"    end_time:   {event.end_time} (tzinfo: {event.end_time.tzinfo})")

            # Test comparison
            is_started = event.start_time <= now_utc
            is_not_ended = event.end_time >= now_utc
            print(f"    start_time <= now_utc: {is_started}")
            print(f"    end_time >= now_utc:   {is_not_ended}")
            print(f"    Should match: {is_started and is_not_ended}")

        if len(events) == 0:
            print("\n  ❌ No events found! Let's check all events:")
            all_query = select(Event).order_by(Event.start_time.desc()).limit(5)
            all_result = await session.execute(all_query)
            all_events = all_result.scalars().all()

            for event in all_events:
                print(f"\n  Event: {event.title}")
                print(f"    start_time: {event.start_time} (type: {type(event.start_time)}, tzinfo: {event.start_time.tzinfo})")
                print(f"    end_time:   {event.end_time} (type: {type(event.end_time)}, tzinfo: {event.end_time.tzinfo})")

                # Try comparison
                try:
                    is_started = event.start_time <= now_utc
                    is_not_ended = event.end_time >= now_utc
                    print(f"    Comparison works: start <= now: {is_started}, end >= now: {is_not_ended}")
                except Exception as e:
                    print(f"    ❌ Comparison failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_query())
