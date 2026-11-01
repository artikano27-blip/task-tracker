import uuid

from app.core.unit_of_work import SqlAlchemyUnitOfWork
from app.models import Task
from app.use_cases.queries import get_task_for_user


class GetTaskCase:
    def __init__(self, unit: SqlAlchemyUnitOfWork):
        self.unit = unit

    async def execute(self, task_id: uuid.UUID, user_id: uuid.UUID) -> Task:
        async with self.unit:
            return await get_task_for_user(self.unit.tasks, task_id, user_id)


