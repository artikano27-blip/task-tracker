import logging
import smtplib
from email.message import EmailMessage

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    def send_email(
        self,
        recipient_email: str,
        subject: str,
        body: str,
        html_body: str | None = None,
    ) -> None:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = settings.SMTP_FROM_EMAIL
        msg["To"] = recipient_email
        msg.set_content(body)

        if html_body:
            msg.add_alternative(html_body, subtype="html")

        with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)

        logger.info(f"Email successfully sent to {recipient_email}")