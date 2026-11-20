from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.task import Task, TaskStatus
from app.repositories.base import BaseRepository


class TaskRepository(BaseRepository[Task]):
    model = Task

    def __init__(self, db: Session):
        super().__init__(db)

    def create(self, **fields) -> Task:
        task = Task(**fields)
        return self.add(task)

    def list_for_project(
        self,
        project_id: int,
        limit: int,
        offset: int,
        status: TaskStatus | None = None,
    ) -> tuple[list[Task], int]:
        base = select(Task).where(Task.project_id == project_id)
        if status is not None:
            base = base.where(Task.status == status)
        total = self.db.execute(select(func.count()).select_from(base.subquery())).scalar_one()
        stmt = base.order_by(Task.created_at.desc()).limit(limit).offset(offset)
        items = list(self.db.execute(stmt).scalars().all())
        return items, total

    def update(self, task: Task, **fields) -> Task:
        for key, value in fields.items():
            setattr(task, key, value)
        self.db.flush()
        self.db.refresh(task)
        return task
