from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.project_member import ProjectMember, ProjectRole
from app.repositories.base import BaseRepository


class ProjectRepository(BaseRepository[Project]):
    model = Project

    def __init__(self, db: Session):
        super().__init__(db)

    def create(self, name: str, description: str | None, owner_id: int) -> Project:
        project = Project(name=name, description=description, owner_id=owner_id)
        project = self.add(project)
        self.add_member(project.id, owner_id, ProjectRole.OWNER)
        return project

    def add_member(self, project_id: int, user_id: int, role: ProjectRole) -> ProjectMember:
        member = ProjectMember(project_id=project_id, user_id=user_id, role=role)
        return self.add(member)

    def get_member(self, project_id: int, user_id: int) -> ProjectMember | None:
        stmt = select(ProjectMember).where(
            ProjectMember.project_id == project_id, ProjectMember.user_id == user_id
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def list_for_user(self, user_id: int, limit: int, offset: int) -> tuple[list[Project], int]:
        base = (
            select(Project)
            .join(ProjectMember, ProjectMember.project_id == Project.id)
            .where(ProjectMember.user_id == user_id)
        )
        total = self.db.execute(select(func.count()).select_from(base.subquery())).scalar_one()
        stmt = base.order_by(Project.created_at.desc()).limit(limit).offset(offset)
        items = list(self.db.execute(stmt).scalars().all())
        return items, total
