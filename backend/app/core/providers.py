from app.core.database import async_session_maker
from app.core.unit_of_work import SqlAlchemyUnitOfWork
from app.services.email_service import EmailService
from app.services.event_service import EventService


def get_uow() -> SqlAlchemyUnitOfWork:
    return SqlAlchemyUnitOfWork(async_session_maker)


def get_event_service() -> EventService:
    return EventService()


def get_email_service() -> EmailService:
    return EmailService()