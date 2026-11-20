from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, PermissionDeniedError
from app.models.project_member import ProjectRole
from app.models.task import Task, TaskStatus
from app.repositories.project_repository import ProjectRepository
from app.repositories.task_repository import TaskRepository
from app.schemas.common import PageResult, paginate_params, total_pages

# Fields a regular (non-owner) member may change, and only on a task
# assigned to themselves. Owners may change any field on any task.
MEMBER_EDITABLE_FIELDS = {"status", "description"}


class TaskService:
    def __init__(self, db: Session):
        self.db = db
        self.tasks = TaskRepository(db)
        self.projects = ProjectRepository(db)

    def _member_or_raise(self, project_id: int, user_id: int):
        member = self.projects.get_member(project_id, user_id)
        if member is None:
            raise PermissionDeniedError("you are not a member of this project")
        return member

    def create_task(
        self,
        project_id: int,
        user_id: int,
        title: str,
        description: str | None,
        priority,
        assignee_id: int | None,
        due_date,
    ) -> Task:
        self._member_or_raise(project_id, user_id)
        if assignee_id is not None and self.projects.get_member(project_id, assignee_id) is None:
            raise PermissionDeniedError("assignee must be a member of the project")
        task = self.tasks.create(
            project_id=project_id,
            title=title,
            description=description,
            priority=priority,
            assignee_id=assignee_id,
            due_date=due_date,
            status=TaskStatus.TODO,
        )
        self.db.commit()
        return task

    def get_task(self, task_id: int, user_id: int) -> Task:
        task = self.tasks.get(task_id)
        if task is None:
            raise NotFoundError("task not found")
        self._member_or_raise(task.project_id, user_id)
        return task

    def list_tasks(
        self, project_id: int, user_id: int, page: int, size: int, status: TaskStatus | None = None
    ) -> PageResult[Task]:
        self._member_or_raise(project_id, user_id)
        limit, offset = paginate_params(0, page, size)
        items, total = self.tasks.list_for_project(project_id, limit, offset, status=status)
        return PageResult(
            items=items, total=total, page=max(page, 1), size=limit, pages=total_pages(total, limit)
        )

    def update_task(self, task_id: int, user_id: int, changes: dict) -> Task:
        task = self.tasks.get(task_id)
        if task is None:
            raise NotFoundError("task not found")
        member = self._member_or_raise(task.project_id, user_id)

        changes = {k: v for k, v in changes.items() if v is not None}

        if member.role != ProjectRole.OWNER:
            if task.assignee_id != user_id:
                raise PermissionDeniedError("members may only update tasks assigned to them")
            disallowed = set(changes) - MEMBER_EDITABLE_FIELDS
            if disallowed:
                raise PermissionDeniedError(
                    f"members may not change: {', '.join(sorted(disallowed))}"
                )
        else:
            if "assignee_id" in changes and changes["assignee_id"] is not None:
                if self.projects.get_member(task.project_id, changes["assignee_id"]) is None:
                    raise PermissionDeniedError("assignee must be a member of the project")

        if not changes:
            return task

        task = self.tasks.update(task, **changes)
        self.db.commit()
        return task

    def delete_task(self, task_id: int, user_id: int) -> None:
        task = self.tasks.get(task_id)
        if task is None:
            raise NotFoundError("task not found")
        member = self._member_or_raise(task.project_id, user_id)
        if member.role != ProjectRole.OWNER:
            raise PermissionDeniedError("only the project owner can delete tasks")
        self.tasks.delete(task)
        self.db.commit()
