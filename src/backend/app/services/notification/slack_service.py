"""
Slack notification service.

Design Philosophy:
- Clean abstraction for Slack webhook integration
- Template-based message formatting
- Fallback handling for webhook failures
"""

import json
from datetime import datetime
from typing import Dict, List, Optional

import httpx

from app.core.config import settings


class SlackService:
    """Slack notification service using webhooks."""

    def __init__(self):
        self.webhook_url = getattr(settings, 'SLACK_WEBHOOK_URL', None)

    async def send_message(
        self,
        text: str,
        channel: Optional[str] = None,
        username: Optional[str] = "智能簽到系統",
        emoji: Optional[str] = ":calendar:"
    ) -> bool:
        """Send message to Slack channel.

        Args:
            text: Message text
            channel: Slack channel (optional, uses webhook default)
            username: Bot username
            emoji: Bot emoji

        Returns:
            True if message sent successfully, False otherwise
        """
        if not self.webhook_url:
            print("Slack service not configured - webhook URL missing")
            return False

        payload = {
            "text": text,
            "username": username,
            "icon_emoji": emoji
        }

        if channel:
            payload["channel"] = channel

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.webhook_url,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                return response.status_code == 200

        except Exception as e:
            print(f"Failed to send Slack message: {str(e)}")
            return False

    async def send_rich_message(
        self,
        title: str,
        fields: List[Dict[str, str]],
        color: str = "#36a64f",
        channel: Optional[str] = None
    ) -> bool:
        """Send rich message with attachments to Slack.

        Args:
            title: Message title
            fields: List of field dictionaries with 'title' and 'value'
            color: Message color (hex code)
            channel: Slack channel (optional)

        Returns:
            True if message sent successfully, False otherwise
        """
        if not self.webhook_url:
            print("Slack service not configured - webhook URL missing")
            return False

        attachment = {
            "color": color,
            "title": title,
            "fields": [
                {
                    "title": field["title"],
                    "value": field["value"],
                    "short": field.get("short", True)
                }
                for field in fields
            ],
            "footer": "智能簽到系統",
            "ts": int(datetime.utcnow().timestamp())
        }

        payload = {
            "username": "智能簽到系統",
            "icon_emoji": ":calendar:",
            "attachments": [attachment]
        }

        if channel:
            payload["channel"] = channel

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.webhook_url,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                return response.status_code == 200

        except Exception as e:
            print(f"Failed to send Slack rich message: {str(e)}")
            return False

    # Template methods for common notifications
    async def notify_leave_request_submitted(
        self, user_name: str, event_title: str, leave_type: str
    ) -> bool:
        """Notify admin about new leave request."""
        text = f"📝 新的請假申請"

        fields = [
            {"title": "申請人", "value": user_name},
            {"title": "活動", "value": event_title},
            {"title": "請假類型", "value": leave_type},
            {"title": "狀態", "value": "待審核"}
        ]

        return await self.send_rich_message(
            title="新的請假申請",
            fields=fields,
            color="#ffa500"  # Orange for pending
        )

    async def notify_makeup_request_submitted(
        self, user_name: str, event_title: str
    ) -> bool:
        """Notify admin about new makeup request."""
        text = f"🔄 新的補簽申請"

        fields = [
            {"title": "申請人", "value": user_name},
            {"title": "活動", "value": event_title},
            {"title": "狀態", "value": "待審核"}
        ]

        return await self.send_rich_message(
            title="新的補簽申請",
            fields=fields,
            color="#ffa500"  # Orange for pending
        )

    async def notify_request_approved(
        self, request_type: str, user_name: str, event_title: str
    ) -> bool:
        """Notify about approved request."""
        request_type_zh = "請假" if request_type == "leave" else "補簽"
        text = f"✅ {request_type_zh}申請已核准"

        fields = [
            {"title": "申請人", "value": user_name},
            {"title": "活動", "value": event_title},
            {"title": "申請類型", "value": request_type_zh},
            {"title": "狀態", "value": "已核准"}
        ]

        return await self.send_rich_message(
            title=f"{request_type_zh}申請已核准",
            fields=fields,
            color="#36a64f"  # Green for approved
        )

    async def notify_request_rejected(
        self, request_type: str, user_name: str, event_title: str, reason: str
    ) -> bool:
        """Notify about rejected request."""
        request_type_zh = "請假" if request_type == "leave" else "補簽"
        text = f"❌ {request_type_zh}申請已拒絕"

        fields = [
            {"title": "申請人", "value": user_name},
            {"title": "活動", "value": event_title},
            {"title": "申請類型", "value": request_type_zh},
            {"title": "拒絕原因", "value": reason},
            {"title": "狀態", "value": "已拒絕"}
        ]

        return await self.send_rich_message(
            title=f"{request_type_zh}申請已拒絕",
            fields=fields,
            color="#ff0000"  # Red for rejected
        )