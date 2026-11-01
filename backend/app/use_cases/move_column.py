import uuid

from app.core.unit_of_work import SqlAlchemyUnitOfWork
from app.schemas.column import ColumnMove, ColumnResponse, ColumnUpdate
from app.use_cases.queries import  get_column_for_user


class MoveColumnCase:
    def __init__(self, unit: SqlAlchemyUnitOfWork):
        self.unit = unit

    async def execute(self, column_id: uuid.UUID, user_id: uuid.UUID, column_in: ColumnMove) -> ColumnResponse:
        async with self.unit:
            column = await get_column_for_user(self.unit.columns, column_id, user_id)
            if column.position == column_in.new_position:
                return ColumnResponse.model_validate(column)

            if column.position < column_in.new_position:
                await self.unit.columns.shift_range(
                    user_id=user_id,
                    start_pos=column.position + 1,
                    end_pos=column_in.new_position,
                    step=-1
                )

            elif column.position > column_in.new_position:
                await self.unit.columns.shift_range(
                    user_id=user_id,
                    start_pos=column_in.new_position,
                    end_pos=column.position - 1,
                    step=1
                )

            column_update = ColumnUpdate(position=column_in.new_position)
            return ColumnResponse.model_validate(await self.unit.columns.update(column, column_update))
