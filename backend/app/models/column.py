from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models import User, Task
import uuid
from sqlalchemy import UUID, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Column(Base):
    __tablename__ = "columns"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column()
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    position: Mapped[int] = mapped_column(default=0, server_default="0")

    user: Mapped["User"] = relationship(back_populates="columns")
    tasks: Mapped[list["Task"]] = relationship(
        "Task",
        back_populates="column",
        order_by="Task.position",
        cascade="all, delete-orphan",
        passive_deletes=True
    )