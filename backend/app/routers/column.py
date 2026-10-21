import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.core.dependencies import get_task_service, get_current_user
from app.models import User
from app.schemas import TaskResponse, TaskCreate, TaskUpdate
from app.services.task_service import TaskService

router = APIRouter(prefix="/columns", tags=["Columns"])

@router.get("/{task_id}", response_model=TaskResponse, status_code=200)
async def get_task(
        current_user: Annotated[User, Depends(get_current_user)],
        task_id: uuid.UUID,
        task_service: Annotated[TaskService, Depends(get_task_service)],
):
    return await task_service.get_task(task_id, current_user.id)