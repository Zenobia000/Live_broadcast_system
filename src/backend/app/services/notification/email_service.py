"""
Email notification service.

Design Philosophy:
- Clean abstraction for email sending
- Template-based email content
- Robust error handling for email delivery
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Optional

from app.core.config import settings


class EmailService:
    """Email notification service."""

    def __init__(self):
        self.smtp_host = getattr(settings, 'SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = getattr(settings, 'SMTP_PORT', 587)
        self.smtp_user = getattr(settings, 'SMTP_USER', None)
        self.smtp_password = getattr(settings, 'SMTP_PASSWORD', None)

    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        is_html: bool = False
    ) -> bool:
        """Send email to recipient.

        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body content
            is_html: Whether body is HTML content

        Returns:
            True if email sent successfully, False otherwise
        """
        if not self.smtp_user or not self.smtp_password:
            print("Email service not configured - SMTP credentials missing")
            return False

        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.smtp_user
            msg['To'] = to_email
            msg['Subject'] = subject

            # Attach body
            if is_html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))

            # Send email
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            server.starttls()
            server.login(self.smtp_user, self.smtp_password)
            text = msg.as_string()
            server.sendmail(self.smtp_user, to_email, text)
            server.quit()

            return True

        except Exception as e:
            print(f"Failed to send email to {to_email}: {str(e)}")
            return False

    async def send_bulk_email(
        self,
        recipients: List[str],
        subject: str,
        body: str,
        is_html: bool = False
    ) -> dict:
        """Send email to multiple recipients.

        Args:
            recipients: List of recipient email addresses
            subject: Email subject
            body: Email body content
            is_html: Whether body is HTML content

        Returns:
            Dictionary with send results
        """
        results = {
            "total": len(recipients),
            "sent": 0,
            "failed": 0,
            "failed_emails": []
        }

        for email in recipients:
            success = await self.send_email(
                to_email=email,
                subject=subject,
                body=body,
                is_html=is_html
            )

            if success:
                results["sent"] += 1
            else:
                results["failed"] += 1
                results["failed_emails"].append(email)

        return results

    # Template methods for common notifications
    async def send_leave_approval_email(
        self, user_email: str, user_name: str, event_title: str, note: Optional[str] = None
    ) -> bool:
        """Send leave request approval notification."""
        subject = f"請假申請已核准 - {event_title}"
        body = f"""
親愛的 {user_name}，

您針對「{event_title}」活動的請假申請已經核准。

{f"審核備註: {note}" if note else ""}

系統將自動更新您的出勤記錄。

智能簽到系統
        """.strip()

        return await self.send_email(user_email, subject, body)

    async def send_leave_rejection_email(
        self, user_email: str, user_name: str, event_title: str, note: str
    ) -> bool:
        """Send leave request rejection notification."""
        subject = f"請假申請已拒絕 - {event_title}"
        body = f"""
親愛的 {user_name}，

很抱歉，您針對「{event_title}」活動的請假申請已被拒絕。

拒絕原因: {note}

如有疑問，請聯繫管理員。

智能簽到系統
        """.strip()

        return await self.send_email(user_email, subject, body)

    async def send_makeup_approval_email(
        self, user_email: str, user_name: str, event_title: str, note: Optional[str] = None
    ) -> bool:
        """Send makeup request approval notification."""
        subject = f"補簽申請已核准 - {event_title}"
        body = f"""
親愛的 {user_name}，

您針對「{event_title}」活動的補簽申請已經核准。

{f"審核備註: {note}" if note else ""}

系統已更新您的出勤記錄。

智能簽到系統
        """.strip()

        return await self.send_email(user_email, subject, body)

    async def send_makeup_rejection_email(
        self, user_email: str, user_name: str, event_title: str, note: str
    ) -> bool:
        """Send makeup request rejection notification."""
        subject = f"補簽申請已拒絕 - {event_title}"
        body = f"""
親愛的 {user_name}，

很抱歉，您針對「{event_title}」活動的補簽申請已被拒絕。

拒絕原因: {note}

如有疑問，請聯繫管理員。

智能簽到系統
        """.strip()

        return await self.send_email(user_email, subject, body)