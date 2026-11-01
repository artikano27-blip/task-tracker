import uuid
from typing import Sequence
from pydantic import TypeAdapter
from app.core.unit_of_work import SqlAlchemyUnitOfWork
from app.schemas.column import ColumnResponse


class GetColumnsCase:
    _columns_adapter = TypeAdapter(Sequence[ColumnResponse])

    def __init__(self, unit: SqlAlchemyUnitOfWork):
        self.unit = unit
    async def execute(self, user_id: uuid.UUID) -> Sequence[ColumnResponse]:
        async with self.unit:
            columns = await self.unit.columns.nested_load(user_id)
            return self._columns_adapter.validate_python(columns)