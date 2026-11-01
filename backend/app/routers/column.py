import uuid
from typing import Annotated, Sequence

from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user, get_create_column_use_case, get_columns_use_case, \
    get_update_column_use_case, get_delete_column_use_case, get_move_column_use_case
from app.models import User

from app.schemas.column import ColumnResponse, ColumnCreate, ColumnUpdate, ColumnMove
from app.use_cases.create_column import CreateColumnCase
from app.use_cases.delete_column import DeleteColumnCase
from app.use_cases.get_columns import GetColumnsCase
from app.use_cases.move_column import MoveColumnCase
from app.use_cases.update_column import UpdateColumnCase

router = APIRouter(prefix="/columns", tags=["Columns"])

@router.post("/", response_model=ColumnResponse, status_code=201)
async def create_column(
        current_user: Annotated[User, Depends(get_current_user)],
        create_column_case: Annotated[CreateColumnCase, Depends(get_create_column_use_case)],
        column_in: ColumnCreate,
):
    return await create_column_case.execute(current_user.id, column_in)


@router.get("/", response_model=Sequence[ColumnResponse], status_code=200)
async def get_columns(
        current_user: Annotated[User, Depends(get_current_user)],
        get_columns_case: Annotated[GetColumnsCase, Depends(get_columns_use_case)],
):
    return await get_columns_case.execute(current_user.id)


@router.patch("/{column_id}", response_model=ColumnResponse, status_code=200)
async def update_column(
        current_user: Annotated[User, Depends(get_current_user)],
        update_column_case: Annotated[UpdateColumnCase, Depends(get_update_column_use_case)],
        column_in: ColumnUpdate,
        column_id: uuid.UUID,
):
    return await update_column_case.execute(column_id, current_user.id, column_in)


@router.delete("/{column_id}", status_code=204)
async def delete_column(
        current_user: Annotated[User, Depends(get_current_user)],
        column_id: uuid.UUID,
        delete_column_case: Annotated[DeleteColumnCase, Depends(get_delete_column_use_case)]
):
    return await delete_column_case.execute(column_id,current_user.id)


@router.patch("/{column_id}/move", response_model=ColumnResponse, status_code=200)
async def move_column(
        current_user: Annotated[User, Depends(get_current_user)],
        move_column_case: Annotated[MoveColumnCase, Depends(get_move_column_use_case)],
        column_in: ColumnMove,
        column_id: uuid.UUID,
):
    return await move_column_case.execute(column_id,current_user.id,column_in)