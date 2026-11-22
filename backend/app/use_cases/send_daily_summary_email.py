import asyncio
from app.services.email_service import EmailService
from app.templates.renderer import render_daily_summary


class SendDailySummaryEmailCase:
    def __init__(self, email_service: EmailService):
        self.email_service = email_service

    async def execute(self, recipient_email: str, username: str, summary_text: str) -> None:
        subject = "Твоя ежедневная сводка задач 📋"
        body = (
            f"Привет, {username}!\n\n"
            f"Вот твоя персональная сводка по задачам на сегодня:\n\n"
            f"{summary_text}\n\n"
            f"Продуктивного дня!\n"
            f"Команда TaskTracker"
        )
        html_body = render_daily_summary(
            username=username,
            summary_text=summary_text,
        )
        await asyncio.to_thread(
            self.email_service.send_email,
            recipient_email=recipient_email,
            subject=subject,
            body=body,
            html_body=html_body,
        )
