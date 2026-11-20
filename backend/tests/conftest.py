import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.services.auth_service import AuthService
from app.services.project_service import ProjectService
from app.services.task_service import TaskService


@pytest.fixture()
def db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def _enable_fk(dbapi_connection, _):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = session_factory()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def auth_service(db):
    return AuthService(db)


@pytest.fixture()
def project_service(db):
    return ProjectService(db)


@pytest.fixture()
def task_service(db):
    return TaskService(db)


@pytest.fixture()
def make_user(auth_service):
    counter = {"n": 0}

    def _make(email: str | None = None, password: str = "correct-password-1"):
        counter["n"] += 1
        email = email or f"user{counter['n']}@example.com"
        return auth_service.signup(email, f"User {counter['n']}", password)

    return _make
