import asyncio

from app.core.config import settings
from app.services.email_service import EmailService
from app.templates.renderer import render_welcome_email


class SendRegistrationEmailCase:
    def __init__(self,  email_service: EmailService):
        self.email_service = email_service

    async def execute(self, recipient_email: str, username: str, app_url: str = settings.FRONTEND_URL) -> None:
        subject = "Добро пожаловать в TaskTracker! 🎉"
        body = (
            f"Добро пожаловать, {username}!\n\n"
            f"Твой аккаунт в TaskTracker успешно создан. Теперь ты можешь организовывать задачи на досках "
            f"и получать ежедневные аналитические сводки от ИИ.\n\n"
            f"Перейти к задачам: {app_url}\n\n"
            f"Продуктивного дня!\n"
            f"Команда TaskTracker"
        )
        html_body = render_welcome_email(username=username)
        await asyncio.to_thread(
            self.email_service.send_email,
            recipient_email=recipient_email,
            subject=subject,
            body=body,
            html_body=html_body,
        )