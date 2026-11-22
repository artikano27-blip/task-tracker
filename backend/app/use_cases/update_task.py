import uuid
from datetime import datetime, timezone

from app.core.unit_of_work import SqlAlchemyUnitOfWork
from app.models import Task
from app.schemas.task import TaskUpdate
from app.use_cases.queries import get_task_for_user, get_column_for_user


class UpdateTaskCase:
    def __init__(self, unit: SqlAlchemyUnitOfWork):
        self.unit = unit

    async def execute(self, task_id: uuid.UUID, user_id: uuid.UUID, task_in: TaskUpdate) -> Task:
        async with self.unit:
            task = await get_task_for_user(self.unit.tasks, task_id, user_id)
            if task_in.column_id:
                await get_column_for_user(self.unit.columns, task_in.column_id, user_id)

            if task_in.is_completed is not None:
                if task_in.is_completed:
                    task.completed_at = datetime.now(timezone.utc)
                else:
                    task.completed_at = None

            return await self.unit.tasks.update(task, task_in)
