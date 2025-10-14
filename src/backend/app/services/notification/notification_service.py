"""
Unified notification service.

Design Philosophy (Linus: "Good Taste"):
- Single interface for all notification channels
- Graceful degradation if channels fail
- Template-based notification content
"""

from typing import Optional

from app.models.attendance.leave_request import LeaveRequest
from app.models.attendance.makeup_request import MakeupRequest
from app.models.auth.user import User
from app.models.calendar.event import Event
from app.services.notification.email_service import EmailService
from app.services.notification.slack_service import SlackService


class NotificationService:
    """Unified notification service for email and Slack."""

    def __init__(
        self,
        email_service: EmailService,
        slack_service: SlackService
    ):
        self.email_service = email_service
        self.slack_service = slack_service

    async def notify_leave_request_submitted(
        self,
        leave_request: LeaveRequest,
        user: User,
        event: Event
    ) -> dict:
        """Notify about new leave request submission.

        Args:
            leave_request: Leave request object
            user: User who submitted the request
            event: Event for the leave request

        Returns:
            Notification results
        """
        results = {
            "email_sent": False,
            "slack_sent": False,
            "errors": []
        }

        # Send Slack notification to admin channel
        try:
            results["slack_sent"] = await self.slack_service.notify_leave_request_submitted(
                user_name=user.name,
                event_title=event.title,
                leave_type=leave_request.leave_type.value
            )
        except Exception as e:
            results["errors"].append(f"Slack notification failed: {str(e)}")

        return results

    async def notify_makeup_request_submitted(
        self,
        makeup_request: MakeupRequest,
        user: User,
        event: Event
    ) -> dict:
        """Notify about new makeup request submission.

        Args:
            makeup_request: Makeup request object
            user: User who submitted the request
            event: Event for the makeup request

        Returns:
            Notification results
        """
        results = {
            "email_sent": False,
            "slack_sent": False,
            "errors": []
        }

        # Send Slack notification to admin channel
        try:
            results["slack_sent"] = await self.slack_service.notify_makeup_request_submitted(
                user_name=user.name,
                event_title=event.title
            )
        except Exception as e:
            results["errors"].append(f"Slack notification failed: {str(e)}")

        return results

    async def notify_leave_request_approved(
        self,
        leave_request: LeaveRequest,
        user: User,
        event: Event,
        reviewer: User
    ) -> dict:
        """Notify about leave request approval.

        Args:
            leave_request: Approved leave request
            user: User who submitted the request
            event: Event for the leave request
            reviewer: Admin who approved the request

        Returns:
            Notification results
        """
        results = {
            "email_sent": False,
            "slack_sent": False,
            "errors": []
        }

        # Send email to user
        try:
            results["email_sent"] = await self.email_service.send_leave_approval_email(
                user_email=user.email,
                user_name=user.name,
                event_title=event.title,
                note=leave_request.review_note
            )
        except Exception as e:
            results["errors"].append(f"Email notification failed: {str(e)}")

        # Send Slack notification
        try:
            results["slack_sent"] = await self.slack_service.notify_request_approved(
                request_type="leave",
                user_name=user.name,
                event_title=event.title
            )
        except Exception as e:
            results["errors"].append(f"Slack notification failed: {str(e)}")

        return results

    async def notify_leave_request_rejected(
        self,
        leave_request: LeaveRequest,
        user: User,
        event: Event,
        reviewer: User
    ) -> dict:
        """Notify about leave request rejection.

        Args:
            leave_request: Rejected leave request
            user: User who submitted the request
            event: Event for the leave request
            reviewer: Admin who rejected the request

        Returns:
            Notification results
        """
        results = {
            "email_sent": False,
            "slack_sent": False,
            "errors": []
        }

        # Send email to user
        try:
            results["email_sent"] = await self.email_service.send_leave_rejection_email(
                user_email=user.email,
                user_name=user.name,
                event_title=event.title,
                note=leave_request.review_note or "No reason provided"
            )
        except Exception as e:
            results["errors"].append(f"Email notification failed: {str(e)}")

        # Send Slack notification
        try:
            results["slack_sent"] = await self.slack_service.notify_request_rejected(
                request_type="leave",
                user_name=user.name,
                event_title=event.title,
                reason=leave_request.review_note or "No reason provided"
            )
        except Exception as e:
            results["errors"].append(f"Slack notification failed: {str(e)}")

        return results

    async def notify_makeup_request_approved(
        self,
        makeup_request: MakeupRequest,
        user: User,
        event: Event,
        reviewer: User
    ) -> dict:
        """Notify about makeup request approval."""
        results = {
            "email_sent": False,
            "slack_sent": False,
            "errors": []
        }

        # Send email to user
        try:
            results["email_sent"] = await self.email_service.send_makeup_approval_email(
                user_email=user.email,
                user_name=user.name,
                event_title=event.title,
                note=makeup_request.review_note
            )
        except Exception as e:
            results["errors"].append(f"Email notification failed: {str(e)}")

        # Send Slack notification
        try:
            results["slack_sent"] = await self.slack_service.notify_request_approved(
                request_type="makeup",
                user_name=user.name,
                event_title=event.title
            )
        except Exception as e:
            results["errors"].append(f"Slack notification failed: {str(e)}")

        return results

    async def notify_makeup_request_rejected(
        self,
        makeup_request: MakeupRequest,
        user: User,
        event: Event,
        reviewer: User
    ) -> dict:
        """Notify about makeup request rejection."""
        results = {
            "email_sent": False,
            "slack_sent": False,
            "errors": []
        }

        # Send email to user
        try:
            results["email_sent"] = await self.email_service.send_makeup_rejection_email(
                user_email=user.email,
                user_name=user.name,
                event_title=event.title,
                note=makeup_request.review_note or "No reason provided"
            )
        except Exception as e:
            results["errors"].append(f"Email notification failed: {str(e)}")

        # Send Slack notification
        try:
            results["slack_sent"] = await self.slack_service.notify_request_rejected(
                request_type="makeup",
                user_name=user.name,
                event_title=event.title,
                reason=makeup_request.review_note or "No reason provided"
            )
        except Exception as e:
            results["errors"].append(f"Slack notification failed: {str(e)}")

        return results

    async def send_daily_summary(
        self, attendance_stats: dict, channel: Optional[str] = None
    ) -> bool:
        """Send daily attendance summary to Slack.

        Args:
            attendance_stats: Dictionary with attendance statistics
            channel: Slack channel (optional)

        Returns:
            True if message sent successfully, False otherwise
        """
        text = "📊 每日出勤統計"

        fields = [
            {"title": "總活動數", "value": str(attendance_stats.get("total_events", 0))},
            {"title": "準時出席", "value": str(attendance_stats.get("present", 0))},
            {"title": "遲到", "value": str(attendance_stats.get("late", 0))},
            {"title": "缺席", "value": str(attendance_stats.get("absent", 0))},
            {"title": "請假", "value": str(attendance_stats.get("leave", 0))},
            {"title": "出席率", "value": f"{attendance_stats.get('attendance_rate', 0):.1%}"}
        ]

        return await self.send_rich_message(
            title="每日出勤統計",
            fields=fields,
            color="#36a64f",  # Green for summary
            channel=channel
        )