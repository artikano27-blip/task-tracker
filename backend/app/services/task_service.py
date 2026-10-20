import uuid
from typing import Sequence
from uuid import UUID

from app.core.exceptions import TaskNotFoundError, TaskAccessDeniedError
from app.repositories.task_repository import TaskRepository
from app.models import Task
from app.schemas.task import TaskCreate, TaskUpdate


class TaskService:
    def __init__(self, task_repo: TaskRepository):
        self.task_repo = task_repo

    async def _get_task_for_user(self, task_id: UUID, user_id: UUID) -> Task:
        task = await self.task_repo.get_by_id(task_id)
        if not task:
            raise TaskNotFoundError
        if task.author_id != user_id:
            raise TaskAccessDeniedError
        return task

    async def update_task(self,task_id:uuid.UUID, user_id:uuid.UUID, task_in: TaskUpdate) -> Task:
        task = await self._get_task_for_user(task_id, user_id)
        return await self.task_repo.update(task, task_in)

    async def delete_task(self, task_id:uuid.UUID, user_id:uuid.UUID) -> None:
        task = await self._get_task_for_user(task_id, user_id)
        await self.task_repo.delete(task)

    async def get_task(self,task_id: UUID, user_id: UUID) -> Task:
       return await self._get_task_for_user(task_id, user_id)

    async def get_all_tasks(self, author_id: uuid.UUID) -> Sequence[Task]:
        return await self.task_repo.get_all_by_author(author_id)

    async def create_task(self,author_id: uuid.UUID, task_in:TaskCreate) -> Task:
        return await self.task_repo.create(author_id, task_in)
