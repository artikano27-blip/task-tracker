import uuid
from typing import Sequence

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Column
from app.schemas.column import ColumnCreate, ColumnUpdate


class ColumnRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def nested_load(self, user_id: uuid.UUID) -> Sequence[Column]:
        query = (select(Column)
                 .options(selectinload(Column.tasks))
                 .where(Column.user_id == user_id).
                 order_by(Column.position))
        result = await self.db.execute(query)
        return result.scalars().all()

    async def create_many(self, columns: list[Column]) -> Sequence[Column]:
        self.db.add_all(columns)
        await self.db.commit()
        return columns

    async def create(self, user_id: uuid.UUID, position: int, column_in: ColumnCreate) -> Column:
        column = Column(title=column_in.title,user_id=user_id,position=position)
        self.db.add(column)
        await self.db.commit()
        await self.db.refresh(column)
        return column

    async def get_max_position(self,user_id: uuid.UUID) -> int | None:
        query = select(func.max(Column.position)).where(Column.user_id == user_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_id(self, column_id: uuid.UUID) -> Column | None:
        query = select(Column).where(Column.id == column_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def update(self, column: Column, column_in: ColumnUpdate) -> Column:
        update_data = column_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(column, field, value)
        await self.db.commit()
        await self.db.refresh(column)
        return column

    async def delete(self, column: Column) -> None:
        await self.db.delete(column)
        await self.db.commit()