import uuid

from app.core.unit_of_work import SqlAlchemyUnitOfWork
from app.schemas.column import ColumnUpdate, ColumnResponse
from app.use_cases.queries import get_column_for_user


class UpdateColumnCase:
    def __init__(self, unit: SqlAlchemyUnitOfWork):
        self.unit = unit

    async def execute(self, column_id: uuid.UUID, user_id: uuid.UUID, column_in: ColumnUpdate) -> ColumnResponse:
        async with self.unit:
            raw_column = await get_column_for_user(self.unit.columns,column_id, user_id)
            edited_column = await self.unit.columns.update(raw_column, column_in)
            return ColumnResponse.model_validate(edited_column)