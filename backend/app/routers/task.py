import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.core.dependencies import get_task_service, get_current_user
from app.models import User
from app.schemas import TaskResponse, TaskCreate, TaskUpdate
from app.services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("/", response_model=TaskResponse, status_code=201)
async def create_task(
        current_user: Annotated[User, Depends(get_current_user)],
        task_in: TaskCreate,
        task_service: Annotated[TaskService, Depends(get_task_service)],
):
    return await task_service.create_task(current_user.id, task_in)


@router.get("/{task_id}", response_model=TaskResponse, status_code=200)
async def get_task(
        current_user: Annotated[User, Depends(get_current_user)],
        task_id: uuid.UUID,
        task_service: Annotated[TaskService, Depends(get_task_service)],
):
    return await task_service.get_task(task_id, current_user.id)


@router.get("/", response_model=list[TaskResponse], status_code=200)
async def get_tasks(
        current_user: Annotated[User, Depends(get_current_user)],
        task_service: Annotated[TaskService, Depends(get_task_service)],
):
    return await task_service.get_all_tasks(current_user.id)


@router.patch("/{task_id}", response_model=TaskResponse, status_code=200)
async def update_task(
        current_user: Annotated[User, Depends(get_current_user)],
        task_in: TaskUpdate,
        task_id: uuid.UUID,
        task_service: Annotated[TaskService, Depends(get_task_service)],
):
    return await task_service.update_task(task_id, current_user.id, task_in)


@router.delete("/{task_id}", status_code=204)
async def delete_task(
        current_user: Annotated[User, Depends(get_current_user)],
        task_id: uuid.UUID,
        task_service: Annotated[TaskService, Depends(get_task_service)],
):
    return await task_service.delete_task(task_id, current_user.id)