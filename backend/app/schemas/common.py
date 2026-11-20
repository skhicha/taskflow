from dataclasses import dataclass, field
from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    """Pydantic response schema used by routers for JSON serialization."""

    items: list[T]
    total: int
    page: int
    size: int
    pages: int


@dataclass
class PageResult(Generic[T]):
    """Plain container returned by the service layer.

    Kept separate from the pydantic `Page` schema above: services return
    lists of SQLAlchemy ORM objects, and building a pydantic generic model
    parameterized directly with an ORM class raises a schema-generation
    error. Routers convert a PageResult into Page[<OutSchema>] for the
    HTTP response.
    """

    items: list[T] = field(default_factory=list)
    total: int = 0
    page: int = 1
    size: int = 20
    pages: int = 0


def paginate_params(total: int, page: int, size: int) -> tuple[int, int]:
    """Clamp page/size to sane bounds and return (limit, offset).

    page is 1-indexed. page < 1 is treated as page 1. A page beyond the
    last available page yields an offset past `total`, which callers'
    repositories will naturally resolve to an empty item list.
    """
    page = max(page, 1)
    size = max(min(size, 100), 1)
    offset = (page - 1) * size
    return size, offset


def total_pages(total: int, size: int) -> int:
    if total == 0:
        return 0
    size = max(size, 1)
    return (total + size - 1) // size
