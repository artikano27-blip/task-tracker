import uuid
from app.models.task import Task
from app.models.column import Column
from app.core.exceptions import (
    TaskNotFoundError,
    TaskAccessDeniedError,
    ColumnNotFoundError,
    ColumnAccessDeniedError,
)
from app.repositories.column_repository import ColumnRepository
from app.repositories.task_repository import TaskRepository


async def get_task_for_user(
        tasks_repo: TaskRepository,
        task_id: uuid.UUID,
        user_id: uuid.UUID
) -> Task:
    """Получает задачу и проверяет права автора."""
    task = await tasks_repo.get_by_id(task_id)
    if not task:
        raise TaskNotFoundError
    if task.author_id != user_id:
        raise TaskAccessDeniedError
    return task


async def get_column_for_user(
        columns_repo: ColumnRepository,
        column_id: uuid.UUID,
        user_id: uuid.UUID
) -> Column:
    """Получает колонку и проверяет права владельца."""
    column = await columns_repo.get_by_id(column_id)
    if not column:
        raise ColumnNotFoundError
    if column.user_id != user_id:
        raise ColumnAccessDeniedError
    return column
