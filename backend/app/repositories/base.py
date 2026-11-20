from typing import Generic, TypeVar

from sqlalchemy.orm import Session

ModelT = TypeVar("ModelT")


class BaseRepository(Generic[ModelT]):
    """Thin data-access layer around a SQLAlchemy session.

    Services depend on repositories, never on the ORM session directly,
    so business logic can be unit tested against any backing store that
    implements the same repository interface.
    """

    model: type[ModelT]

    def __init__(self, db: Session):
        self.db = db

    def get(self, id_: int) -> ModelT | None:
        return self.db.get(self.model, id_)

    def add(self, instance: ModelT) -> ModelT:
        self.db.add(instance)
        self.db.flush()
        self.db.refresh(instance)
        return instance

    def delete(self, instance: ModelT) -> None:
        self.db.delete(instance)
        self.db.flush()
