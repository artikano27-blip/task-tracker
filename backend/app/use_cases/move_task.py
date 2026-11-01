import uuid

from app.core.unit_of_work import SqlAlchemyUnitOfWork
from app.models import Task
from app.schemas.task import TaskMove, TaskUpdate
from app.use_cases.queries import get_task_for_user, get_column_for_user


class MoveTaskCase:
    def __init__(self, unit: SqlAlchemyUnitOfWork):
        self.unit = unit

    async def execute(self, task_id: uuid.UUID, user_id: uuid.UUID, task_in: TaskMove) -> Task:
        async with self.unit:
            task = await get_task_for_user(self.unit.tasks, task_id, user_id)
            if task.column_id == task_in.target_column_id and task.position == task_in.new_position:
                return task

            if task.column_id != task_in.target_column_id:
                await get_column_for_user(self.unit.columns,task_in.target_column_id,user_id)
                await self.unit.tasks.shift_from_position(task_in.target_column_id, task_in.new_position, 1)
                await self.unit.tasks.shift_from_position(task.column_id, task.position + 1, - 1)

            elif task.position < task_in.new_position:
                await self.unit.tasks.shift_range(
                    column_id=task_in.target_column_id,
                    start_pos=task.position + 1,
                    end_pos=task_in.new_position,
                    step=-1,
                )

            elif task.position > task_in.new_position:
                await self.unit.tasks.shift_range(
                    column_id=task_in.target_column_id,
                    start_pos=task_in.new_position,
                    end_pos=task.position - 1,
                    step=1,
                )

            task_update = TaskUpdate(column_id=task_in.target_column_id, position=task_in.new_position)
            return await self.unit.tasks.update(task, task_update)