# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Group class (拼课) enrollment system prototype. A Chinese-language education platform where parents browse group classes, enroll students or join waitlists, and admins manage classes through a review workflow. The backend is FastAPI + uvicorn with uv-managed dependencies, the frontend is vanilla HTML/CSS/JS.

## Commands

### Run locally (Windows)

```powershell
powershell -ExecutionPolicy Bypass -File scripts/start-local.ps1   # starts backend :18000 + frontend :5173
powershell -ExecutionPolicy Bypass -File scripts/stop-local.ps1    # kills both
```

### Run locally (macOS/Linux)

```bash
./scripts/start-local.sh        # starts backend :18000 + frontend :5173
./scripts/stop-local.sh         # kills both
```

Override with env vars: `PYTHON_BIN=python3 FRONTEND_PORT=5173 BACKEND_PORT=18000`

### Run backend directly

```bash
uv run uvicorn apps.group_class_backend.app:app --host 0.0.0.0 --port 18000 --reload
```

### Run tests

```bash
uv run pytest tests/ -q
```

Single test file:

```bash
uv run pytest tests/group_class_backend/classes/test_create_class_draft.py -q
```

API integration tests:

```bash
uv run pytest tests/test_api/ -v
```

### Frontend syntax checks

```bash
node --check apps/group_class_frontend/js/api.js
node --check apps/group_class_frontend/js/app.js
```

### Docker

```bash
docker compose up -d --build    # frontend :5173, backend :18000
docker compose down
```

## Architecture

### Backend (`apps/group_class_backend/`)

FastAPI application served by uvicorn. Entry point: `apps/group_class_backend/app.py`. All state is in-memory by default (`InMemoryClassRepository`, `InMemoryRegistrationRepository`); SQLite repositories exist but are not wired into the server yet.

**Layering**: `app.py` (FastAPI app + lifespan state + seed data) -> `routers/*.py` (HTTP routing, dependency parsing, status-code mapping) -> `{domain}/controller.py` (business logic, validation, audit events) -> `{domain}/repository.py` (persistence). Controllers are pure functions that take repositories and return dicts; they never touch HTTP directly.

Two domains:
- **classes** — CRUD + review workflow for group classes. Implemented workflow: `DRAFT -> PENDING_REVIEW -> OPEN_FOR_ENROLLMENT | REJECTED`. The model also supports lifecycle/display states such as `ALMOST_CONFIRMED`, `CONFIRMED`, `FULL`, `WAITLIST_OPEN`, `IN_PROGRESS`, `ENDED`, and `CANCELLED`, but the server does not expose a full transition API for all of them yet.
- **registrations** — enrollment/waitlist/trial submissions from public users, plus admin status updates and notes.

**Key patterns**:
- Domain models are `@dataclass(slots=True)` in `models/`. Construction via `ClassName.create_draft()` / `Registration.create()` factory classmethods that enforce invariants.
- Mutations use `dataclasses.replace()` to produce new instances; repositories bump `version` on update (optimistic concurrency via version field in payloads).
- API field names are camelCase (JSON contract), model fields are snake_case. Field mapping dicts (`_MUTABLE_FIELD_MAP`, `_COPYABLE_CREATE_FIELDS`) in controllers handle the translation.
- All API responses follow `{requestId, code, data}` (success) or `{requestId, code, details}` (error) via `common/responses.py`.
- Role-based access: `CLASS_ADMIN`/`SUPER_ADMIN` can approve/reject reviews; `INITIATOR` can only edit own classes. `ActorContext` is parsed in `deps.py` from `X-Actor-Id` and `X-Actor-Roles` headers.
- `AuditWriter` protocol in `audit/interface.py`; currently only `NullAuditWriter` is used.

### API routes

Implemented in `apps/group_class_backend/routers/classes.py` and `apps/group_class_backend/routers/registrations.py`:

- `GET /api/v1/public/classes`
- `GET /api/v1/public/classes/{classId}`
- `POST /api/v1/public/registrations`
- `GET /api/v1/admin/classes`
- `GET /api/v1/admin/classes/{classId}`
- `POST /api/v1/admin/classes`
- `POST /api/v1/admin/classes/{classId}/update`
- `POST /api/v1/admin/classes/{classId}/submit-review`
- `POST /api/v1/admin/classes/{classId}/approve`
- `POST /api/v1/admin/classes/{classId}/reject`
- `GET /api/v1/admin/registrations`
- `GET /api/v1/admin/registrations/{registrationId}`
- `POST /api/v1/admin/registrations/{registrationId}/notes`
- `POST /api/v1/admin/registrations/{registrationId}/status`

### Frontend (`apps/group_class_frontend/`)

Vanilla JS SPA (no build step). `api.js` contains `ApiClient` with a mock-data mode (`localStorage GROUP_CLASS_USE_MOCK_DATA=true`) and a live-API mode (`localStorage GROUP_CLASS_API_BASE_URL`). `app.js` handles routing and rendering.

Frontend is served as static files via Python's `http.server` in dev, or nginx in Docker.

### Tests (`tests/group_class_backend/`)

Runtime dependencies are managed by `uv` in `pyproject.toml`. Existing backend tests call controller functions directly with in-memory repositories; `tests/test_api/` covers FastAPI HTTP routes via `TestClient`. Some tests use SQLite `:memory:` to verify persistence layer compatibility.

### Persistence (`persistence/schema.py`)

SQLite schema DDL with CHECK constraints mirroring the model validation. `apply_schema()` creates tables + indexes. Three tables: `classes`, `registrations`, `class_templates`.

## Engineering Notes

- This is a prototype, not a production server. Permissive CORS, request-supplied actor headers, and in-memory repositories are intentional simplifications.
- Server state is seeded on process start and lost on restart. SQLite repositories exist, but `app.py` is still wired to in-memory repositories.
- When changing API fields, update the model, controller field maps, serializers, schema, tests, and frontend `ApiClient` together. API JSON is camelCase; Python model fields are snake_case.
- Preserve the frozen response contract: success is `{requestId, code, data}` and error is `{requestId, code, details}`.
- Run `uv run pytest tests/ -q` after backend changes and `node --check` after frontend JavaScript changes.
- For work that changes scope, acceptance criteria, startup behavior, or delivery status, also review/update `README.md`, `docs/development-and-deployment.md`, and the relevant `docs/plans/` document.
