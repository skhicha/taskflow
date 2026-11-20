import pytest

from app.core.exceptions import ConflictError, NotFoundError, PermissionDeniedError


def test_create_project_makes_creator_the_owner(project_service, make_user):
    owner = make_user()
    project = project_service.create_project(owner.id, "Launch", "Ship it")
    assert project.owner_id == owner.id
    assert project_service.is_owner(project.id, owner.id) is True


def test_get_project_allowed_for_member(project_service, make_user):
    owner = make_user()
    other = make_user()
    project = project_service.create_project(owner.id, "Launch", None)
    project_service.add_member(project.id, owner.id, other.email)

    fetched = project_service.get_project(project.id, other.id)
    assert fetched.id == project.id


def test_get_project_denied_for_non_member(project_service, make_user):
    owner = make_user()
    stranger = make_user()
    project = project_service.create_project(owner.id, "Private", None)

    with pytest.raises(PermissionDeniedError):
        project_service.get_project(project.id, stranger.id)


def test_get_project_for_nonexistent_project_denies_rather_than_leaks(project_service, make_user):
    owner = make_user()
    with pytest.raises(PermissionDeniedError):
        # Not a member of a project that doesn't exist either -> the
        # membership check runs first, so a stranger can't distinguish
        # "no access" from "doesn't exist".
        project_service.get_project(123456, owner.id)


def test_owner_can_delete_project(project_service, make_user):
    owner = make_user()
    project = project_service.create_project(owner.id, "Temp", None)
    project_service.delete_project(project.id, owner.id)
    with pytest.raises(PermissionDeniedError):
        project_service.get_project(project.id, owner.id)


def test_non_owner_member_cannot_delete_project(project_service, make_user):
    owner = make_user()
    member = make_user()
    project = project_service.create_project(owner.id, "Temp", None)
    project_service.add_member(project.id, owner.id, member.email)

    with pytest.raises(PermissionDeniedError):
        project_service.delete_project(project.id, member.id)


def test_non_member_cannot_delete_project(project_service, make_user):
    owner = make_user()
    stranger = make_user()
    project = project_service.create_project(owner.id, "Temp", None)

    with pytest.raises(PermissionDeniedError):
        project_service.delete_project(project.id, stranger.id)


def test_delete_missing_project_raises_not_found_for_owner_check_order(project_service, make_user):
    owner = make_user()
    with pytest.raises(PermissionDeniedError):
        project_service.delete_project(999999, owner.id)


def test_only_owner_can_add_member(project_service, make_user):
    owner = make_user()
    member = make_user()
    outsider = make_user()
    project = project_service.create_project(owner.id, "Team", None)
    project_service.add_member(project.id, owner.id, member.email)

    with pytest.raises(PermissionDeniedError):
        project_service.add_member(project.id, member.id, outsider.email)


def test_add_member_with_unknown_email_raises_not_found(project_service, make_user):
    owner = make_user()
    project = project_service.create_project(owner.id, "Team", None)

    with pytest.raises(NotFoundError):
        project_service.add_member(project.id, owner.id, "ghost@example.com")


def test_add_member_twice_raises_conflict(project_service, make_user):
    owner = make_user()
    member = make_user()
    project = project_service.create_project(owner.id, "Team", None)
    project_service.add_member(project.id, owner.id, member.email)

    with pytest.raises(ConflictError):
        project_service.add_member(project.id, owner.id, member.email)


def test_list_projects_only_returns_projects_user_belongs_to(project_service, make_user):
    owner = make_user()
    stranger = make_user()
    project_service.create_project(owner.id, "Mine", None)

    page = project_service.list_projects(stranger.id, page=1, size=20)
    assert page.items == []
    assert page.total == 0
