import uuid

from app.core.unit_of_work import SqlAlchemyUnitOfWork
from app.schemas.column import ColumnCreate, ColumnResponse


class CreateColumnCase:
    def __init__(self, unit: SqlAlchemyUnitOfWork):
        self.unit = unit

    async def execute(self, user_id: uuid.UUID, column_in: ColumnCreate) -> ColumnResponse:
        async with self.unit:
            max_pos = await self.unit.columns.get_max_position(user_id)
            if max_pos is None:
                position = 0
            else:
                position = max_pos + 1

            column = await self.unit.columns.create(user_id, position, column_in)
            return ColumnResponse.model_validate(column)