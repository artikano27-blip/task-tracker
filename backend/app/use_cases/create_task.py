import uuid

from app.models import Task
from app.schemas import TaskCreate
from app.services.column_service import ColumnService
from app.services.task_service import TaskService


class CreateTaskCase:
    def __init__(self, task_service: TaskService, column_service: ColumnService):
        self.task_service = task_service
        self.column_service = column_service

    async def execute(self, author_id: uuid.UUID, task_in: TaskCreate) -> Task:
        await self.column_service.get_column_for_user(task_in.column_id, author_id)
        return await self.task_service.create_task(author_id, task_in)
