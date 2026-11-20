from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.project_member import ProjectRole
from app.schemas.user import UserOut


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=5000)


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=5000)


class MemberAdd(BaseModel):
    email: EmailStr


class MemberOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user: UserOut
    role: ProjectRole


class ProjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    owner_id: int
    created_at: datetime


class ProjectDetailOut(ProjectOut):
    members: list[MemberOut] = []
