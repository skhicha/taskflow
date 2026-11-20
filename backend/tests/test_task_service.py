import pytest

from app.core.exceptions import NotFoundError, PermissionDeniedError
from app.models.task import TaskPriority, TaskStatus


def _project_with_member(project_service, make_user):
    owner = make_user()
    member = make_user()
    project = project_service.create_project(owner.id, "Sprint", None)
    project_service.add_member(project.id, owner.id, member.email)
    return owner, member, project


def test_member_can_create_task_in_own_project(task_service, project_service, make_user):
    owner, member, project = _project_with_member(project_service, make_user)
    task = task_service.create_task(project.id, member.id, "Write docs", None, TaskPriority.LOW, None, None)
    assert task.status == TaskStatus.TODO
    assert task.project_id == project.id


def test_non_member_cannot_create_task(task_service, project_service, make_user):
    owner = make_user()
    stranger = make_user()
    project = project_service.create_project(owner.id, "Sprint", None)

    with pytest.raises(PermissionDeniedError):
        task_service.create_task(project.id, stranger.id, "Sneaky", None, TaskPriority.LOW, None, None)


def test_create_task_rejects_assignee_outside_project(task_service, project_service, make_user):
    owner, member, project = _project_with_member(project_service, make_user)
    outsider = make_user()

    with pytest.raises(PermissionDeniedError):
        task_service.create_task(
            project.id, owner.id, "Task", None, TaskPriority.LOW, outsider.id, None
        )


def test_owner_can_update_any_field_on_any_task(task_service, project_service, make_user):
    owner, member, project = _project_with_member(project_service, make_user)
    task = task_service.create_task(project.id, owner.id, "Task", None, TaskPriority.LOW, None, None)

    updated = task_service.update_task(
        task.id, owner.id, {"title": "Renamed", "priority": TaskPriority.HIGH, "assignee_id": member.id}
    )
    assert updated.title == "Renamed"
    assert updated.priority == TaskPriority.HIGH
    assert updated.assignee_id == member.id


def test_member_can_update_status_of_own_assigned_task(task_service, project_service, make_user):
    owner, member, project = _project_with_member(project_service, make_user)
    task = task_service.create_task(
        project.id, owner.id, "Task", None, TaskPriority.LOW, member.id, None
    )

    updated = task_service.update_task(task.id, member.id, {"status": TaskStatus.IN_PROGRESS})
    assert updated.status == TaskStatus.IN_PROGRESS


def test_member_cannot_update_task_not_assigned_to_them(task_service, project_service, make_user):
    owner, member, project = _project_with_member(project_service, make_user)
    task = task_service.create_task(project.id, owner.id, "Task", None, TaskPriority.LOW, None, None)

    with pytest.raises(PermissionDeniedError):
        task_service.update_task(task.id, member.id, {"status": TaskStatus.DONE})


def test_member_cannot_reassign_task_even_if_assigned_to_them(task_service, project_service, make_user):
    owner, member, project = _project_with_member(project_service, make_user)
    task = task_service.create_task(
        project.id, owner.id, "Task", None, TaskPriority.LOW, member.id, None
    )

    with pytest.raises(PermissionDeniedError):
        task_service.update_task(task.id, member.id, {"assignee_id": owner.id})


def test_update_nonexistent_task_raises_not_found(task_service, project_service, make_user):
    owner = make_user()
    with pytest.raises(NotFoundError):
        task_service.update_task(999999, owner.id, {"status": TaskStatus.DONE})


def test_owner_can_delete_task(task_service, project_service, make_user):
    owner, member, project = _project_with_member(project_service, make_user)
    task = task_service.create_task(project.id, owner.id, "Task", None, TaskPriority.LOW, None, None)

    task_service.delete_task(task.id, owner.id)
    with pytest.raises(NotFoundError):
        task_service.get_task(task.id, owner.id)


def test_member_cannot_delete_task(task_service, project_service, make_user):
    owner, member, project = _project_with_member(project_service, make_user)
    task = task_service.create_task(
        project.id, owner.id, "Task", None, TaskPriority.LOW, member.id, None
    )

    with pytest.raises(PermissionDeniedError):
        task_service.delete_task(task.id, member.id)


def test_delete_nonexistent_task_raises_not_found(task_service, make_user):
    owner = make_user()
    with pytest.raises(NotFoundError):
        task_service.delete_task(999999, owner.id)


def test_status_transition_todo_to_in_progress_to_done(task_service, project_service, make_user):
    owner, member, project = _project_with_member(project_service, make_user)
    task = task_service.create_task(project.id, owner.id, "Task", None, TaskPriority.LOW, None, None)
    assert task.status == TaskStatus.TODO

    task = task_service.update_task(task.id, owner.id, {"status": TaskStatus.IN_PROGRESS})
    assert task.status == TaskStatus.IN_PROGRESS

    task = task_service.update_task(task.id, owner.id, {"status": TaskStatus.DONE})
    assert task.status == TaskStatus.DONE
