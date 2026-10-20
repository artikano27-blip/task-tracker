import uuid
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Task
from app.schemas import TaskCreate, TaskUpdate


class TaskRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, task_id: uuid.UUID)-> Task | None:
        query = select(Task).where(Task.id == task_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_all_by_author(self,author_id:uuid.UUID) -> Sequence[Task]:
        query = select(Task).where(Task.author_id == author_id).order_by(Task.timestamp.desc())
        result = await self.db.execute(query)
        return result.scalars().all()

    async def create(self, author_id: uuid.UUID, task_in: TaskCreate) -> Task:
        task = Task(author_id=author_id, label_text=task_in.label_text, main_text=task_in.main_text)
        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def update(self, task: Task, task_in: TaskUpdate) -> Task:
        update_data = task_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)
        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def delete(self, task: Task) -> None:
        await self.db.delete(task)
        await self.db.commit()

