"""
Leave and Makeup requests API endpoints.

Design Philosophy:
- RESTful API for request management
- Unified review workflow for both request types
- Role-based access control for admin operations
"""

from datetime import datetime
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies.auth import AdminUser, CurrentUser
from app.api.v1.schemas.requests import (
    LeaveRequestCreate,
    LeaveRequestResponse,
    MakeupRequestCreate,
    MakeupRequestResponse,
    PendingReviewsResponse,
    ReviewRequest,
    ReviewResponse,
    UserRequestsResponse,
)
from app.models.enums import RequestStatus

router = APIRouter()


# Leave Request Endpoints
@router.post("/leave")
async def submit_leave_request(
    leave_request: LeaveRequestCreate,
    current_user: CurrentUser
):
    """Submit a new leave request.

    Args:
        leave_request: Leave request data
        current_user: Current authenticated user

    Returns:
        Created leave request with simple response

    Raises:
        HTTPException: If request creation fails
    """
    from datetime import datetime as dt
    import uuid

    # TODO: Implement with proper dependency injection and database storage
    # For now, return a simple response that matches frontend expectations

    return {
        "id": str(uuid.uuid4()),
        "userId": str(current_user.id),
        "startDate": leave_request.startDate,
        "endDate": leave_request.endDate,
        "type": leave_request.type,
        "reason": leave_request.reason,
        "description": leave_request.description,
        "status": "pending",
        "emergencyContact": leave_request.emergencyContact,
        "reviewedBy": None,
        "reviewedAt": None,
        "createdAt": dt.utcnow().isoformat(),
        "updatedAt": dt.utcnow().isoformat()
    }


@router.get("/leave/my", response_model=List[LeaveRequestResponse])
async def get_my_leave_requests(current_user: CurrentUser):
    """Get current user's leave requests.

    Args:
        current_user: Current authenticated user

    Returns:
        List of user's leave requests
    """
    # TODO: Implement with proper dependency injection
    return []


# Makeup Request Endpoints
@router.post("/makeup")
async def submit_makeup_request(
    makeup_request: MakeupRequestCreate,
    current_user: CurrentUser
):
    """Submit a new makeup request.

    Args:
        makeup_request: Makeup request data
        current_user: Current authenticated user

    Returns:
        Created makeup request with simple response

    Raises:
        HTTPException: If request creation fails
    """
    from datetime import datetime as dt
    import uuid

    # TODO: Implement with proper dependency injection and database storage
    # For now, return a simple response that matches frontend expectations

    return {
        "id": str(uuid.uuid4()),
        "userId": str(current_user.id),
        "missedDate": makeup_request.missedDate,
        "reason": makeup_request.reason,
        "description": makeup_request.description,
        "status": "pending",
        "reviewedBy": None,
        "reviewedAt": None,
        "createdAt": dt.utcnow().isoformat(),
        "updatedAt": dt.utcnow().isoformat()
    }


@router.get("/makeup/my", response_model=List[MakeupRequestResponse])
async def get_my_makeup_requests(current_user: CurrentUser):
    """Get current user's makeup requests.

    Args:
        current_user: Current authenticated user

    Returns:
        List of user's makeup requests
    """
    # TODO: Implement with proper dependency injection
    return []


# Unified Request Management
@router.get("/my", response_model=UserRequestsResponse)
async def get_my_requests(current_user: CurrentUser):
    """Get all current user's requests.

    Args:
        current_user: Current authenticated user

    Returns:
        All user's leave and makeup requests
    """
    # TODO: Implement with proper dependency injection
    return UserRequestsResponse(
        leave_requests=[],
        makeup_requests=[],
        total_leave=0,
        total_makeup=0,
        total_requests=0
    )


# Admin Review Endpoints
@router.get("/pending", response_model=PendingReviewsResponse, dependencies=[Depends(AdminUser)])
async def get_pending_reviews(
    limit: int = 50,
    offset: int = 0
):
    """Get all pending requests for admin review.

    Args:
        limit: Maximum number of requests to return
        offset: Number of requests to skip

    Returns:
        Pending leave and makeup requests
    """
    # TODO: Implement with proper dependency injection
    return PendingReviewsResponse(
        leave_requests=[],
        makeup_requests=[],
        total_leave=0,
        total_makeup=0,
        total_pending=0
    )


@router.post("/leave/{request_id}/review", response_model=ReviewResponse, dependencies=[Depends(AdminUser)])
async def review_leave_request(
    request_id: UUID,
    review: ReviewRequest,
    admin_user: AdminUser
):
    """Review leave request (admin only).

    Args:
        request_id: Leave request ID
        review: Review action and note
        admin_user: Current admin user

    Returns:
        Review result

    Raises:
        HTTPException: If request not found or review fails
    """
    # Validate rejection requires note
    if review.action == "reject" and not review.note:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Review note is required for rejection"
        )

    # TODO: Implement with proper dependency injection
    return ReviewResponse(
        request_id=request_id,
        request_type="leave",
        action=review.action,
        reviewer_id=admin_user.id,
        message=f"Leave request {review.action}d successfully"
    )


@router.post("/makeup/{request_id}/review", response_model=ReviewResponse, dependencies=[Depends(AdminUser)])
async def review_makeup_request(
    request_id: UUID,
    review: ReviewRequest,
    admin_user: AdminUser
):
    """Review makeup request (admin only).

    Args:
        request_id: Makeup request ID
        review: Review action and note
        admin_user: Current admin user

    Returns:
        Review result

    Raises:
        HTTPException: If request not found or review fails
    """
    # Validate rejection requires note
    if review.action == "reject" and not review.note:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Review note is required for rejection"
        )

    # TODO: Implement with proper dependency injection
    return ReviewResponse(
        request_id=request_id,
        request_type="makeup",
        action=review.action,
        reviewer_id=admin_user.id,
        message=f"Makeup request {review.action}d successfully"
    )


@router.delete("/leave/{request_id}")
async def cancel_leave_request(
    request_id: UUID,
    current_user: CurrentUser
):
    """Cancel pending leave request.

    Args:
        request_id: Leave request ID
        current_user: Current authenticated user

    Returns:
        Cancellation confirmation

    Raises:
        HTTPException: If request not found or cannot be cancelled
    """
    # TODO: Implement with proper dependency injection
    return {"message": "Leave request cancelled successfully"}


@router.delete("/makeup/{request_id}")
async def cancel_makeup_request(
    request_id: UUID,
    current_user: CurrentUser
):
    """Cancel pending makeup request.

    Args:
        request_id: Makeup request ID
        current_user: Current authenticated user

    Returns:
        Cancellation confirmation

    Raises:
        HTTPException: If request not found or cannot be cancelled
    """
    # TODO: Implement with proper dependency injection
    return {"message": "Makeup request cancelled successfully"}