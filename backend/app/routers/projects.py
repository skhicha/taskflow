from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.core.exceptions import ConflictError, NotFoundError, PermissionDeniedError
from app.database import get_db
from app.models.user import User
from app.schemas.common import Page
from app.schemas.project import MemberAdd, MemberOut, ProjectCreate, ProjectDetailOut, ProjectOut
from app.services.project_service import ProjectService

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.post("", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    project = ProjectService(db).create_project(current_user.id, payload.name, payload.description)
    return project


@router.get("", response_model=Page[ProjectOut])
def list_projects(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ProjectService(db).list_projects(current_user.id, page, size)


@router.get("/{project_id}", response_model=ProjectDetailOut)
def get_project(
    project_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    try:
        return ProjectService(db).get_project(project_id, current_user.id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    try:
        ProjectService(db).delete_project(project_id, current_user.id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc


@router.post("/{project_id}/members", response_model=MemberOut, status_code=status.HTTP_201_CREATED)
def add_member(
    project_id: int,
    payload: MemberAdd,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return ProjectService(db).add_member(project_id, current_user.id, payload.email)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except ConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
