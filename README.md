# TaskFlow

A full-stack project management platform: projects, tasks, and role-based
collaboration, built with a React frontend and a FastAPI backend on
PostgreSQL.

## Tech stack

- **Frontend:** React 19, React Router, Vite, Axios, plain CSS (design tokens,
  no UI framework)
- **Backend:** FastAPI, SQLAlchemy 2.0, Alembic, Pydantic v2, PyJWT, bcrypt
- **Database:** PostgreSQL 16
- **Infra:** Docker, docker-compose, Nginx (serves the frontend build and
  proxies `/api` to the backend)
- **Testing:** pytest (backend service/business-logic layer)

## What it does

- Sign up / log in with a JWT-based session.
- Create projects, and add other registered users to them as members.
- Create, assign, and track tasks on a per-project board (To do / In
  progress / Done), with priority, assignee, and due date.
- Role-based access control: the project **owner** can delete the project,
  delete tasks, and reassign/edit any task; **members** can create tasks and
  update the status/description of tasks assigned to them, but cannot delete
  tasks, reassign them, or delete the project.
- Paginated project and task listings.

## Architecture

### Repository pattern (backend)

The backend is split into three layers, each with a single responsibility:

```
app/routers/      HTTP layer: request/response, status codes, auth dependency
app/services/      Business logic: permission checks, validation, orchestration
app/repositories/   Data access: SQLAlchemy queries, nothing else
app/models/         SQLAlchemy ORM models (the schema)
app/schemas/         Pydantic request/response models
```

Routers never touch the database directly — they call a service. Services
never write raw queries — they call a repository. This keeps permission and
business-rule logic (e.g. "only the owner may delete a project", "a member
may only edit the status of a task assigned to them") in one testable place,
independent of FastAPI or HTTP. The `tests/` suite exercises the service
layer directly against an in-memory SQLite database, with no HTTP or web
server involved.

### Database schema

Normalized relational schema with foreign keys, managed by Alembic
migrations (`backend/alembic/versions`):

- `users` — account + hashed password
- `projects` — owned by a user
- `project_members` — join table (user ↔ project) carrying a `role`
  (`owner` / `member`), unique per (project, user)
- `tasks` — belongs to a project, optional assignee (a project member)

### JWT auth flow

1. `POST /api/auth/signup` hashes the password with bcrypt and stores the
   user.
2. `POST /api/auth/login` verifies the password and issues a signed JWT
   (`sub` = user id, `exp` = expiry) via `PyJWT`.
3. The frontend stores the token and sends `Authorization: Bearer <token>`
   on every request (Axios interceptor).
4. A FastAPI dependency (`get_current_user`) decodes and verifies the token
   on each protected request, returning 401 for a missing, invalid, or
   expired token, or one pointing at a deleted user.
5. Role checks (owner vs. member) happen inside the service layer, after
   authentication, using the `project_members.role` column.

## Running it

Requires Docker and Docker Compose.

```bash
docker-compose up -d --build
```

This starts three services:

| Service  | URL                     | Notes                                   |
|----------|-------------------------|------------------------------------------|
| frontend | http://localhost:8080   | Nginx serving the production React build |
| backend  | http://localhost:8010   | FastAPI, also reachable at `/api` behind the frontend's Nginx proxy |
| db       | internal only           | PostgreSQL 16, not published to the host  |

The backend container runs `alembic upgrade head` on startup before
launching Uvicorn, so the schema is always up to date. Open
http://localhost:8080 and sign up to get started.

To stop the stack: `docker-compose down` (add `-v` to also drop the
database volume).

### Local (non-Docker) development

Backend:

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # point DATABASE_URL at a local Postgres
alembic upgrade head
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev   # proxies /api to http://localhost:8000 (see vite.config.js)
```

## Running the tests

```bash
cd backend
source .venv/bin/activate   # after the local setup above
pytest
```

The suite covers the service layer: authentication (signup, login, password
hashing, valid/expired/malformed JWTs), project and task permission checks
(owner vs. member, non-member access, deleting/reassigning restrictions),
and pagination (first/middle/last page, page 0, page beyond the last page,
empty result sets).
