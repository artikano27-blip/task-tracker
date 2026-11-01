import uuid

from app.core.unit_of_work import SqlAlchemyUnitOfWork
from app.use_cases.queries import get_task_for_user


class DeleteTaskCase:
    def __init__(self, unit: SqlAlchemyUnitOfWork):
        self.unit = unit

    async def execute(self, task_id: uuid.UUID, user_id: uuid.UUID) -> None:
        async with self.unit:
            task = await get_task_for_user(self.unit.tasks,task_id,user_id)
            await self.unit.tasks.shift_from_position(task.column_id, task.position + 1, -1)
            await self.unit.tasks.delete(task)
