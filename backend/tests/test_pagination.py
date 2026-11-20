import pytest

from app.models.task import TaskPriority
from app.schemas.common import paginate_params, total_pages


@pytest.mark.parametrize(
    "page,size,expected_offset",
    [
        (1, 20, 0),
        (2, 20, 20),
        (3, 10, 20),
    ],
)
def test_paginate_params_computes_offset(page, size, expected_offset):
    limit, offset = paginate_params(0, page, size)
    assert limit == size
    assert offset == expected_offset


def test_paginate_params_treats_page_zero_as_page_one():
    limit, offset = paginate_params(0, 0, 20)
    assert offset == 0


def test_paginate_params_treats_negative_page_as_page_one():
    limit, offset = paginate_params(0, -5, 20)
    assert offset == 0


def test_paginate_params_clamps_oversized_page_size():
    limit, _ = paginate_params(0, 1, 10_000)
    assert limit == 100


def test_paginate_params_clamps_zero_page_size_to_one():
    limit, _ = paginate_params(0, 1, 0)
    assert limit == 1


def test_total_pages_of_empty_result_set_is_zero():
    assert total_pages(0, 20) == 0


def test_total_pages_rounds_up_for_partial_last_page():
    assert total_pages(41, 20) == 3


def test_total_pages_exact_multiple():
    assert total_pages(40, 20) == 2


def test_list_projects_page_beyond_last_returns_empty_items(project_service, make_user):
    owner = make_user()
    project_service.create_project(owner.id, "Only Project", None)

    page = project_service.list_projects(owner.id, page=5, size=20)
    assert page.items == []
    assert page.total == 1
    assert page.pages == 1


def test_list_projects_empty_result_set(project_service, make_user):
    owner = make_user()
    page = project_service.list_projects(owner.id, page=1, size=20)
    assert page.items == []
    assert page.total == 0
    assert page.pages == 0


def test_list_tasks_pagination_across_pages(task_service, project_service, make_user):
    owner = make_user()
    project = project_service.create_project(owner.id, "Big Project", None)
    for i in range(25):
        task_service.create_task(
            project.id, owner.id, f"Task {i}", None, TaskPriority.LOW, None, None
        )

    first_page = task_service.list_tasks(project.id, owner.id, page=1, size=10)
    second_page = task_service.list_tasks(project.id, owner.id, page=2, size=10)
    third_page = task_service.list_tasks(project.id, owner.id, page=3, size=10)

    assert first_page.total == 25
    assert len(first_page.items) == 10
    assert len(second_page.items) == 10
    assert len(third_page.items) == 5
    assert first_page.pages == 3

    first_ids = {t.id for t in first_page.items}
    second_ids = {t.id for t in second_page.items}
    assert first_ids.isdisjoint(second_ids)


def test_list_tasks_page_zero_behaves_like_page_one(task_service, project_service, make_user):
    owner = make_user()
    project = project_service.create_project(owner.id, "Project", None)
    task_service.create_task(project.id, owner.id, "Only task", None, TaskPriority.LOW, None, None)

    page_zero = task_service.list_tasks(project.id, owner.id, page=0, size=20)
    page_one = task_service.list_tasks(project.id, owner.id, page=1, size=20)
    assert [t.id for t in page_zero.items] == [t.id for t in page_one.items]
