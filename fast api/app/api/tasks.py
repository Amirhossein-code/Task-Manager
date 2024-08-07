import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..dependencies.get_active_user import get_current_active_user_db_dependency
from ..models import User
from ..schemas import tasks as task_schemas
from ..utils.db import tasks as task_crud

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
)


@router.post("/", response_model=task_schemas.Task, status_code=status.HTTP_201_CREATED)
def create_task(
    request: task_schemas.TaskCreate,
    user: User = Depends(get_current_active_user_db_dependency),
    db: Session = Depends(get_db),
):
    new_task = task_crud.create_new_task(
        request=request,
        user=user,
        db=db,
    )
    return new_task


@router.get(
    "/", response_model=List[task_schemas.Task], status_code=status.HTTP_200_OK
)
def get_users_tasks(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user_db_dependency),
):
    tasks = task_crud.get_user_tasks_or_404(
        user=user,
        db=db,
    )
    return tasks


@router.get(
    "/{task_id}", response_model=task_schemas.Task, status_code=status.HTTP_200_OK
)
def get_task_by_id(
    task_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user_db_dependency),
):
    task = task_crud.get_task_by_id_or_404(task_id=task_id, db=db)

    if task.owner_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
        )

    return task


@router.put(
    "/{task_id}", response_model=task_schemas.Task, status_code=status.HTTP_200_OK
)
def update_task(
    task_id: int,
    request: task_schemas.TaskUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user_db_dependency),
):
    task = task_crud.get_task_by_id_or_404(task_id=task_id, db=db)

    if task.owner_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this task",
        )

    updated_task = task_crud.update_task(task=task, request=request, db=db)

    return updated_task
