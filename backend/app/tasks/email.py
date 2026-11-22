import smtplib
from sqlalchemy.exc import OperationalError

from typing import AsyncGenerator

from contextlib import asynccontextmanager

import asyncio
import logging
import uuid
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine

from app.core.celery_app import celery_app
from app.core.config import settings
from app.core.providers import get_email_service, get_event_service, get_uow
from app.core.unit_of_work import SqlAlchemyUnitOfWork

logger = logging.getLogger(__name__)


@asynccontextmanager
async def get_celery_uow() -> AsyncGenerator[SqlAlchemyUnitOfWork, None]:
    celery_engine = create_async_engine(
        url=settings.DATABASE_URL,
        poolclass=NullPool,
    )
    celery_session_maker = async_sessionmaker[AsyncSession](
        celery_engine,
        expire_on_commit=False,
    )
    try:
        yield SqlAlchemyUnitOfWork(celery_session_maker)
    finally:
        await celery_engine.dispose()


@celery_app.task(
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(TimeoutError, OSError, smtplib.SMTPException),
    rate_limit="2/s",
    retry_backoff=True,
)
def send_registration_email(recipient_email: str, username: str) -> None:
    from app.use_cases.send_registration_email import SendRegistrationEmailCase

    async def _run() -> None:
        email_service = get_email_service()
        use_case = SendRegistrationEmailCase(email_service)
        await use_case.execute(
            recipient_email=recipient_email,
            username=username,
            app_url=settings.FRONTEND_URL,
        )

    asyncio.run(_run())



@celery_app.task(
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(TimeoutError, OSError, OperationalError),
    retry_backoff=True,
    rate_limit="2/s",
)
def process_user_daily_summary(user_id: str) -> None:
    from app.use_cases.request_daily_summary import RequestDailySummaryCase

    async def _run() -> None:
        async with get_celery_uow() as uow:
            event_service = get_event_service()
            use_case = RequestDailySummaryCase(uow, event_service)
            await use_case.execute(uuid.UUID(user_id))

    asyncio.run(_run())


@celery_app.task(max_retries=3,
                 default_retry_delay=60,
                 autoretry_for=(TimeoutError, OSError),
                 rate_limit="2/s",
                 retry_backoff=True)
def dispatch_daily_summaries() -> None:
    from app.use_cases.dispatch_daily_summaries import DispatchDailySummariesCase

    async def _run() -> None:
        async with get_celery_uow() as uow:
            use_case = DispatchDailySummariesCase(uow)
            await use_case.execute()

    asyncio.run(_run())


@celery_app.task(max_retries=3,
                 default_retry_delay=60,
                 autoretry_for=(TimeoutError, OSError, smtplib.SMTPException),
                 rate_limit="2/s",
                 retry_backoff=True)
def send_summary_email(email: str, username: str, summary_text: str) -> None:
    from app.use_cases.send_daily_summary_email import SendDailySummaryEmailCase
    async def _run() -> None:
        email_service = get_email_service()
        use_case = SendDailySummaryEmailCase(email_service)
        await use_case.execute(email, username, summary_text)

    asyncio.run(_run())
