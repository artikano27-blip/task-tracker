import uuid

from app.core.unit_of_work import SqlAlchemyUnitOfWork
from app.models import Task
from app.schemas.task import TaskCreate
from app.use_cases.queries import get_column_for_user


class CreateTaskCase:
    def __init__(self, unit: SqlAlchemyUnitOfWork):
        self.unit = unit

    async def execute(self, author_id: uuid.UUID, task_in: TaskCreate) -> Task:
        async with self.unit:
            await get_column_for_user(self.unit.columns, task_in.column_id, author_id)
            max_pos = await self.unit.tasks.get_max_position(task_in.column_id)
            if max_pos is None:
                position = 0
            else:
                position = max_pos + 1

            return await self.unit.tasks.create(author_id, position, task_in)
