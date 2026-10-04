from enum import Enum
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models import User
import uuid
from datetime import datetime
from sqlalchemy import UUID, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class TaskStatus(str,Enum):
    COMPLETED = "ВЫПОЛНЕНА"
    UNCOMPLETED = "НЕ ВЫПОЛНЕНА"


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    label_text: Mapped[str] = mapped_column()
    main_text: Mapped[str] = mapped_column()
    status: Mapped[TaskStatus] = mapped_column(default=TaskStatus.UNCOMPLETED)
    author_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now())

    author: Mapped["User"] = relationship(back_populates="tasks")
