# IT Helpdesk Ticketing System

Internal ticketing tool for desk-based IT support intake, assignment, and tracking.

## Architecture

- **Backend:** FastAPI + SQLAlchemy + PostgreSQL
- **Notifications:** Redis pub/sub for ticket assignment events
- **Frontend:** React + Vite + plain CSS
- **Auth:** JWT for agents and admins only

The backend exposes OpenAPI docs at `http://localhost:8000/docs`.

## Local run with Docker

1. Copy `.env.example` to `.env`.
2. Start the stack:

```bash
docker compose up --build
```

3. Seed the default admin agent:

```bash
docker compose exec backend python scripts/seed.py
```

4. Open:

- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`

## Default login

Use the admin credentials from `.env`:

- Email: `DEFAULT_ADMIN_EMAIL`
- Password: `DEFAULT_ADMIN_PASSWORD`

## API endpoints

### Auth
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`

### Agents
- `GET /api/v1/agents`
- `GET /api/v1/agents/available`
- `GET /api/v1/agents/availability`
- `PATCH /api/v1/agents/me/availability`

### Tickets
- `GET /api/v1/tickets`
- `POST /api/v1/tickets`
- `GET /api/v1/tickets/{ticket_id}`
- `PATCH /api/v1/tickets/{ticket_id}/status`
- `PATCH /api/v1/tickets/{ticket_id}/assignment`

### Dashboard
- `GET /api/v1/dashboard/summary`

## Phase 1 schema notes

Tickets already include an optional `asset_id` field so a future asset inventory module can attach assets without rewriting the ticket model.
