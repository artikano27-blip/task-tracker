import uuid
from typing import Sequence
from app.core.config import settings
from app.core.exceptions import ColumnNotFoundError, ColumnAccessDeniedError
from app.repositories.column_repository import ColumnRepository
from app.models import Column
from app.schemas.column import ColumnCreate, ColumnUpdate


class ColumnService:
    def __init__(self, column_repo: ColumnRepository):
        self.column_repo = column_repo

    async def get_column_for_user(self, column_id: uuid.UUID, user_id: uuid.UUID) -> Column:
        column = await self.column_repo.get_by_id(column_id)
        if not column:
            raise ColumnNotFoundError
        if column.user_id != user_id:
            raise ColumnAccessDeniedError
        return column

    async def get_board(self, user_id: uuid.UUID) -> Sequence[Column]:
        columns = await self.column_repo.nested_load(user_id)
        return columns

    async def create_default_columns(self, user_id: uuid.UUID) -> Sequence[Column]:
        columns = [
            Column(title=title, position=idx, user_id=user_id)
            for idx, title in enumerate(settings.DEFAULT_COLUMNS)
        ]
        return await self.column_repo.create_many(columns)

    async def create_column(self, user_id: uuid.UUID, column_in: ColumnCreate) -> Column:
        max_pos = await self.column_repo.get_max_position(user_id)
        if max_pos is None:
            position = 0
        else:
            position = max_pos + 1

        return await self.column_repo.create(user_id, position, column_in)

    async def update_column(self, column_id: uuid.UUID, user_id: uuid.UUID, column_in: ColumnUpdate) -> Column:
        column = await self.get_column_for_user(column_id, user_id)
        return await self.column_repo.update(column, column_in)

    async def delete_column(self, column_id: uuid.UUID, user_id:uuid.UUID) -> None:
        column = await self.get_column_for_user(column_id, user_id)
        await self.column_repo.delete(column)

