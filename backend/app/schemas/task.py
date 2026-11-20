from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.task import TaskPriority, TaskStatus


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    description: str | None = Field(default=None, max_length=10000)
    priority: TaskPriority = TaskPriority.MEDIUM
    assignee_id: int | None = None
    due_date: date | None = None


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=500)
    description: str | None = Field(default=None, max_length=10000)
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    assignee_id: int | None = None
    due_date: date | None = None


class TaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    title: str
    description: str | None
    status: TaskStatus
    priority: TaskPriority
    assignee_id: int | None
    due_date: date | None
    created_at: datetime
    updated_at: datetime
