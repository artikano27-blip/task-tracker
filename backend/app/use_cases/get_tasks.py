import uuid
from typing import Sequence

from app.core.unit_of_work import SqlAlchemyUnitOfWork
from app.models import Task


class GetTasksCase:
    def __init__(self, unit: SqlAlchemyUnitOfWork):
        self.unit = unit

    async def execute(self, author_id: uuid.UUID) -> Sequence[Task]:
        return await self.unit.tasks.get_all_by_author(author_id)