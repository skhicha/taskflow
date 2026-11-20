from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError, PermissionDeniedError
from app.models.project import Project
from app.models.project_member import ProjectMember, ProjectRole
from app.repositories.project_repository import ProjectRepository
from app.repositories.user_repository import UserRepository
from app.schemas.common import PageResult, paginate_params, total_pages


class ProjectService:
    def __init__(self, db: Session):
        self.db = db
        self.projects = ProjectRepository(db)
        self.users = UserRepository(db)

    def _require_membership(self, project_id: int, user_id: int) -> ProjectMember:
        member = self.projects.get_member(project_id, user_id)
        if member is None:
            raise PermissionDeniedError("you are not a member of this project")
        return member

    def _require_owner(self, project_id: int, user_id: int) -> ProjectMember:
        member = self._require_membership(project_id, user_id)
        if member.role != ProjectRole.OWNER:
            raise PermissionDeniedError("only the project owner can perform this action")
        return member

    def create_project(self, owner_id: int, name: str, description: str | None) -> Project:
        project = self.projects.create(name=name, description=description, owner_id=owner_id)
        self.db.commit()
        return project

    def get_project(self, project_id: int, user_id: int) -> Project:
        self._require_membership(project_id, user_id)
        project = self.projects.get(project_id)
        if project is None:
            raise NotFoundError("project not found")
        return project

    def list_projects(self, user_id: int, page: int, size: int) -> PageResult[Project]:
        limit, offset = paginate_params(0, page, size)
        items, total = self.projects.list_for_user(user_id, limit, offset)
        return PageResult(
            items=items, total=total, page=max(page, 1), size=limit, pages=total_pages(total, limit)
        )

    def delete_project(self, project_id: int, user_id: int) -> None:
        self._require_owner(project_id, user_id)
        project = self.projects.get(project_id)
        if project is None:
            raise NotFoundError("project not found")
        self.projects.delete(project)
        self.db.commit()

    def add_member(self, project_id: int, requester_id: int, member_email: str) -> ProjectMember:
        self._require_owner(project_id, requester_id)
        user = self.users.get_by_email(member_email)
        if user is None:
            raise NotFoundError(f"no user found with email '{member_email}'")
        if self.projects.get_member(project_id, user.id) is not None:
            raise ConflictError("user is already a member of this project")
        member = self.projects.add_member(project_id, user.id, ProjectRole.MEMBER)
        self.db.commit()
        return member

    def is_owner(self, project_id: int, user_id: int) -> bool:
        member = self.projects.get_member(project_id, user_id)
        return member is not None and member.role == ProjectRole.OWNER
