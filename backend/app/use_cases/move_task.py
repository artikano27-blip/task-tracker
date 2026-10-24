import uuid

from app.models import Task
from app.schemas.task import TaskMove
from app.services.column_service import ColumnService
from app.services.task_service import TaskService


class MoveTaskCase:
    def __init__(self, task_service: TaskService, column_service: ColumnService):
        self.task_service = task_service
        self.column_service = column_service

    async def execute(self, task_id: uuid.UUID, user_id: uuid.UUID, task_in: TaskMove) -> Task:
        await self.column_service.get_column_for_user(task_in.target_column_id, user_id)
        return await self.task_service.move_task(task_id, user_id, task_in)