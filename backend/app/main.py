from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine
from app.routers import auth, projects, tasks

app = FastAPI(title="TaskFlow API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(tasks.router)


@app.on_event("startup")
def on_startup() -> None:
    # Dev/CI convenience: in production, schema changes should go through
    # Alembic migrations (see backend/alembic). create_all is a no-op for
    # tables that already exist, so this is safe alongside migrations.
    Base.metadata.create_all(bind=engine)


@app.get("/api/health", tags=["health"])
def health_check():
    return {"status": "ok"}
