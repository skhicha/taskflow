"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-11-20

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

task_status_enum = sa.Enum("todo", "in_progress", "done", name="taskstatus")
task_priority_enum = sa.Enum("low", "medium", "high", name="taskpriority")
project_role_enum = sa.Enum("owner", "member", name="projectrole")


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "projects",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "owner_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "project_members",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "project_id", sa.Integer(), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role", project_role_enum, nullable=False, server_default="member"),
        sa.Column("joined_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("project_id", "user_id", name="uq_project_user"),
    )

    op.create_table(
        "tasks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "project_id", sa.Integer(), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", task_status_enum, nullable=False, server_default="todo"),
        sa.Column("priority", task_priority_enum, nullable=False, server_default="medium"),
        sa.Column(
            "assignee_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True
        ),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_tasks_project_id", "tasks", ["project_id"])


def downgrade() -> None:
    op.drop_index("ix_tasks_project_id", table_name="tasks")
    op.drop_table("tasks")
    op.drop_table("project_members")
    op.drop_table("projects")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
    task_status_enum.drop(op.get_bind(), checkfirst=True)
    task_priority_enum.drop(op.get_bind(), checkfirst=True)
    project_role_enum.drop(op.get_bind(), checkfirst=True)
