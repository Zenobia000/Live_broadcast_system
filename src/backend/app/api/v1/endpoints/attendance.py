"""
Attendance API endpoints.

Design Philosophy:
- RESTful API design for attendance operations
- Event-driven auto check-in functionality
- Role-based access control for management features
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies.attendance import AttendanceServiceDep
from app.api.dependencies.auth import AdminUser, CurrentUser
from app.api.v1.schemas.attendance import (
    AttendanceResponse,
    AttendanceWithDetails,
    AutoCheckInResponse,
    CheckInRequest,
    CheckInResponse,
)

router = APIRouter()


@router.get("/today")
async def get_today_status(current_user: CurrentUser):
    """Get today's attendance status for current user.

    Returns:
        Simple status overview for today
    """
    from datetime import date

    today = date.today()

    return {
        "date": today.isoformat(),
        "user_id": str(current_user.id),
        "user_name": current_user.name,
        "status": "active",
        "message": f"Today's status for {current_user.name}"
    }


@router.post("/auto-checkin", response_model=AutoCheckInResponse)
async def auto_check_in(
    current_user: CurrentUser,
    attendance_service: AttendanceServiceDep
):
    """Automatically check in user for ongoing events.

    This is the core event-driven functionality:
    1. Find all currently ongoing events
    2. Check if user hasn't checked in yet
    3. Perform automatic check-in with late detection

    Returns:
        List of events user was checked in for
    """
    try:
        attendances = await attendance_service.auto_check_in_user(current_user.id)

        checked_in_events = [
            {
                "event_id": str(attendance.event_id),
                "attendance_id": str(attendance.id),
                "status": attendance.status.value,
                "check_in_time": attendance.check_in_time,
                "was_late": attendance.status.value == "LATE"
            }
            for attendance in attendances
        ]

        return AutoCheckInResponse(
            checked_in_events=checked_in_events,
            total_checked_in=len(attendances),
            message=f"Successfully checked in for {len(attendances)} events"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Auto check-in failed: {str(e)}"
        )


@router.post("/checkin", response_model=CheckInResponse)
async def manual_check_in(
    checkin_request: CheckInRequest,
    current_user: CurrentUser,
    attendance_service: AttendanceServiceDep
):
    """Manual check-in for specific event.

    Args:
        checkin_request: Check-in request with event ID and optional time
        current_user: Current authenticated user

    Returns:
        Check-in result with attendance record
    """
    try:
        attendance = await attendance_service.manual_check_in(
            user_id=current_user.id,
            event_id=checkin_request.event_id,
            check_in_time=checkin_request.check_in_time
        )

        was_late = attendance.status.value == "LATE"

        return CheckInResponse(
            attendance=AttendanceResponse(
                id=attendance.id,
                user_id=attendance.user_id,
                event_id=attendance.event_id,
                status=attendance.status.value,
                check_in_time=attendance.check_in_time,
                note=attendance.note,
                created_at=attendance.created_at,
                updated_at=attendance.updated_at
            ),
            was_late=was_late,
            message="Successfully checked in" + (" (late)" if was_late else "")
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Check-in failed: {str(e)}"
        )


@router.get("/my-attendance", response_model=List[AttendanceWithDetails])
async def get_my_attendance(
    current_user: CurrentUser,
    attendance_service: AttendanceServiceDep,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    """Get current user's attendance records.

    Args:
        current_user: Current authenticated user
        start_date: Filter start date (optional)
        end_date: Filter end date (optional)

    Returns:
        List of attendance records with event details
    """
    try:
        attendances = await attendance_service.get_user_attendance(
            user_id=current_user.id,
            start_date=start_date,
            end_date=end_date
        )

        # For now, return attendance without event details since we'd need to join
        # In a full implementation, we'd modify the service to include event data
        return [
            AttendanceWithDetails(
                id=attendance.id,
                user_id=attendance.user_id,
                event_id=attendance.event_id,
                status=attendance.status.value,
                check_in_time=attendance.check_in_time,
                note=attendance.note,
                created_at=attendance.created_at,
                updated_at=attendance.updated_at,
                event_title="Event details to be implemented",  # TODO: Join with event
                event_start_time=None,  # TODO: Join with event
                event_end_time=None     # TODO: Join with event
            )
            for attendance in attendances
        ]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve attendance: {str(e)}"
        )


@router.get("/events/{event_id}/attendance", response_model=List[AttendanceWithDetails])
async def get_event_attendance(
    event_id: UUID,
    admin_user: AdminUser
):
    """Get attendance records for specific event (admin only).

    Args:
        event_id: Event ID
        admin_user: Current admin user

    Returns:
        List of attendance records for the event
    """
    # TODO: Implement with proper dependency injection
    return []


@router.get("/{attendance_id}", response_model=AttendanceResponse)
async def get_attendance_record(
    attendance_id: UUID,
    current_user: CurrentUser
):
    """Get specific attendance record.

    Args:
        attendance_id: Attendance record ID
        current_user: Current authenticated user

    Returns:
        Attendance record details

    Raises:
        HTTPException: If record not found or access denied
    """
    # TODO: Implement with proper dependency injection and access control
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Attendance record not found"
    )


@router.put("/{attendance_id}/note")
async def update_attendance_note(
    attendance_id: UUID,
    note: str,
    admin_user: AdminUser
):
    """Update attendance record note (admin only).

    Args:
        attendance_id: Attendance record ID
        note: New note text
        admin_user: Current admin user

    Returns:
        Updated attendance record
    """
    # TODO: Implement with proper dependency injection
    return {"message": "Note update functionality will be available after dependency injection setup"}


@router.delete("/{attendance_id}")
async def soft_delete_attendance(
    attendance_id: UUID,
    admin_user: AdminUser
):
    """Soft delete attendance record (admin only).

    Args:
        attendance_id: Attendance record ID
        admin_user: Current admin user

    Returns:
        Deletion confirmation
    """
    # TODO: Implement with proper dependency injection
    return {"message": "Attendance record deletion functionality will be available after dependency injection setup"}