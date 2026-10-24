import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.core.dependencies import get_task_service, get_current_user, get_create_task_use_case, get_move_task_use_case
from app.models import User
from app.schemas import TaskResponse, TaskCreate, TaskUpdate
from app.schemas.task import TaskMove
from app.services.task_service import TaskService
from app.use_cases.create_task import CreateTaskCase
from app.use_cases.move_task import MoveTaskCase

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("/", response_model=TaskResponse, status_code=201)
async def create_task(
        current_user: Annotated[User, Depends(get_current_user)],
        create_task_case: Annotated[CreateTaskCase, Depends(get_create_task_use_case)],
        task_in: TaskCreate,
):
    return await create_task_case.execute(current_user.id, task_in)


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

@router.patch("/{task_id}/move", response_model=TaskResponse, status_code=200)
async def move_task(
        current_user: Annotated[User, Depends(get_current_user)],
        move_task_case: Annotated[MoveTaskCase, Depends(get_move_task_use_case)],
        task_in: TaskMove,
        task_id: uuid.UUID,
):
    return await move_task_case.execute(task_id,current_user.id,task_in)


@router.delete("/{task_id}", status_code=204)
async def delete_task(
        current_user: Annotated[User, Depends(get_current_user)],
        task_id: uuid.UUID,
        task_service: Annotated[TaskService, Depends(get_task_service)],
):
    return await task_service.delete_task(task_id, current_user.id)