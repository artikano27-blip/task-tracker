import uuid

from app.core.unit_of_work import SqlAlchemyUnitOfWork
from app.use_cases.queries import get_column_for_user


class DeleteColumnCase:
    def __init__(self, unit: SqlAlchemyUnitOfWork):
        self.unit = unit

    async def execute(self, column_id: uuid.UUID, user_id: uuid.UUID) -> None:
        async with self.unit:
            column = await get_column_for_user(self.unit.columns, column_id, user_id)
            await self.unit.columns.shift_from_position(user_id, column.position + 1, -1)
            await self.unit.columns.delete(column)
