# Setup Instructions

## Quick Start

### 1. Environment Setup
```bash
cp .env.example .env
```

Edit `.env` if needed (default creds are safe for local dev):
- `DEFAULT_ADMIN_EMAIL=admin@company.local`
- `DEFAULT_ADMIN_PASSWORD=ChangeMe123!`

### 2. Start the Stack
```bash
docker compose up --build
```

This starts:
- PostgreSQL on `5432`
- Redis on `6379`
- Backend (FastAPI) on `8000`
- Frontend (React/Nginx) on `3000`

### 3. Seed the Admin Agent
```bash
docker compose exec backend python scripts/seed.py
```

### 4. Access the App
- **Dashboard:** http://localhost:3000
- **API Docs:** http://localhost:8000/docs
- **Health check:** http://localhost:8000/health

### Login
```
Email: admin@company.local
Password: ChangeMe123!
```

## Project Structure

```
.
├── backend/                    # FastAPI application
│   ├── app/
│   │   ├── api/routes/         # API endpoints (auth, agents, tickets, dashboard)
│   │   ├── models/             # SQLAlchemy ORM models + enums
│   │   ├── schemas/            # Pydantic request/response schemas
│   │   ├── core/               # Config, security, dependencies
│   │   ├── db/                 # Database session and base
│   │   ├── services/           # Redis notification publisher
│   │   ├── workers/            # Background notification listener
│   │   └── main.py             # FastAPI app entry point
│   ├── scripts/
│   │   └── seed.py             # Admin agent seed script
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                   # React + Vite application
│   ├── src/
│   │   ├── components/         # LoginForm, TicketForm, TicketDetail, SummaryCards
│   │   ├── context/            # AuthContext for JWT token management
│   │   ├── styles/             # Plain CSS (no Tailwind)
│   │   ├── api.js              # Fetch wrapper with auth headers
│   │   ├── App.jsx             # Main dashboard
│   │   └── main.jsx            # React entry point
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── Dockerfile
│   └── nginx.conf
├── docker-compose.yml          # Full stack orchestration
├── .env.example                # Environment variable template
├── .gitignore
├── README.md                   # API documentation
└── SETUP.md                    # This file
```

## Phase 1 Features (Implemented)

✅ **Ticket Management**
- Create tickets manually (agent intake)
- Assign to available agents
- Update status (Open → In Progress → Resolved → Closed)
- View audit trail (all changes logged)

✅ **Agent Management**
- Login with JWT
- Toggle availability (Available/Busy/Offline)
- List available agents for assignment

✅ **Dashboard**
- Ticket list with filters (status, priority, assigned agent)
- Summary cards (open count, by priority, per agent)
- Agent availability display

✅ **Notifications**
- Redis pub/sub for assignment events
- Logged to console (ready for Slack/email integration)

✅ **Security**
- JWT auth (no raw SQL, bcrypt passwords)
- CORS configured
- Input validation on all endpoints
- Parameterized queries (SQLAlchemy ORM)

## Phase 2 (Future - Schema Ready)

- Asset inventory module (tickets have optional `asset_id` field)
- Auto-assignment logic (round-robin, least-busy)
- Self-service customer portal
- Email/Slack notifications
- SLA tracking

## Stopping the Stack
```bash
docker compose down
```

Remove volumes (reset DB):
```bash
docker compose down -v
```

## Troubleshooting

**Port already in use:**
```bash
docker compose down
docker compose up --build
```

**Seed script fails:**
Make sure postgres is ready:
```bash
docker compose exec db psql -U helpdesk -d helpdesk -c "SELECT 1;"
# Then retry seed.py
```

**Frontend can't reach backend:**
Check CORS origins in `.env` — default is `http://localhost:8000/api/v1`.

**Redis connection issues:**
Verify Redis is running:
```bash
docker compose exec redis redis-cli PING
```
Should return `PONG`.
