from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.core.exceptions import NotFoundError, PermissionDeniedError
from app.database import get_db
from app.models.task import TaskStatus
from app.models.user import User
from app.schemas.common import Page
from app.schemas.task import TaskCreate, TaskOut, TaskUpdate
from app.services.task_service import TaskService

router = APIRouter(tags=["tasks"])


@router.post("/api/projects/{project_id}/tasks", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(
    project_id: int,
    payload: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return TaskService(db).create_task(
            project_id,
            current_user.id,
            payload.title,
            payload.description,
            payload.priority,
            payload.assignee_id,
            payload.due_date,
        )
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc


@router.get("/api/projects/{project_id}/tasks", response_model=Page[TaskOut])
def list_tasks(
    project_id: int,
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    status_filter: TaskStatus | None = Query(default=None, alias="status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return TaskService(db).list_tasks(project_id, current_user.id, page, size, status_filter)
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc


@router.get("/api/tasks/{task_id}", response_model=TaskOut)
def get_task(task_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        return TaskService(db).get_task(task_id, current_user.id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc


@router.patch("/api/tasks/{task_id}", response_model=TaskOut)
def update_task(
    task_id: int,
    payload: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return TaskService(db).update_task(task_id, current_user.id, payload.model_dump())
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc


@router.delete("/api/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        TaskService(db).delete_task(task_id, current_user.id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
