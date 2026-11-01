from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from app.repositories.column_repository import ColumnRepository
from app.repositories.task_repository import TaskRepository
from app.repositories.user_repository import UserRepository


class SqlAlchemyUnitOfWork:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self.session_factory = session_factory

    async def __aenter__(self) -> SqlAlchemyUnitOfWork:
        self.session = self.session_factory()
        self.tasks = TaskRepository(self.session)
        self.columns = ColumnRepository(self.session)
        self.users = UserRepository(self.session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        try:
            if exc_type is None:
                await self.session.commit()
            else:
                await self.session.rollback()
        finally:
            await self.session.close()