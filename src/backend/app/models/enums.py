"""
Enum types for database models.

Design Philosophy (Linus: "Good Taste"):
- Use ENUM instead of boolean flags or string literals
- Single status field eliminates special cases (no "is_present AND is_late" contradictions)
- Extensible without schema changes
"""

import enum


class UserRole(str, enum.Enum):
    """User role enumeration.

    Design Note:
    - Simple two-tier system for MVP
    - Can extend to MODERATOR, GUEST, etc. without schema changes
    """

    MEMBER = "MEMBER"  # Regular user
    ADMIN = "ADMIN"    # Administrator with review permissions


class AttendanceStatus(str, enum.Enum):
    """Attendance status enumeration.

    State Machine:
    - ABSENT (initial) → PRESENT/LATE (on check-in)
    - ABSENT → LEAVE (on leave approval)
    - ABSENT/LATE → MAKEUP (on makeup approval)
    - PRESENT/LATE → EARLY_LEAVE (if left early)

    Design Decision (Linus: "Eliminate Special Cases"):
    - Single status field instead of multiple booleans
    - No "is_present=True AND is_late=True" contradictions
    - Clear state transitions
    """

    PRESENT = "PRESENT"          # On-time check-in
    LATE = "LATE"                # Late check-in (after grace period)
    ABSENT = "ABSENT"            # Did not check in
    LEAVE = "LEAVE"              # Approved leave
    MAKEUP = "MAKEUP"            # Approved retroactive check-in (補簽)
    EARLY_LEAVE = "EARLY_LEAVE"  # Left before event ended


class LeaveType(str, enum.Enum):
    """Leave type enumeration.

    Common leave categories in Taiwan:
    - SICK: 病假
    - PERSONAL: 事假
    - OFFICIAL: 公假
    - OTHER: 其他
    """

    SICK = "SICK"          # Sick leave (病假)
    PERSONAL = "PERSONAL"  # Personal leave (事假)
    OFFICIAL = "OFFICIAL"  # Official duty (公假)
    OTHER = "OTHER"        # Other types


class RequestStatus(str, enum.Enum):
    """Request approval status enumeration.

    Used for both LeaveRequest and MakeupRequest.

    State Machine:
    - PENDING (initial) → APPROVED/REJECTED (after review)
    - Terminal states: APPROVED, REJECTED (no further transitions)

    Design Note:
    - Shared enum for both request types (DRY principle)
    - CHECK constraint in DB ensures review metadata consistency
    """

    PENDING = "PENDING"      # Awaiting admin review
    APPROVED = "APPROVED"    # Approved by admin
    REJECTED = "REJECTED"    # Rejected by admin
