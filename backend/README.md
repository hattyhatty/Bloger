# AI Content OS Backend — Phase 7A

FastAPI + PostgreSQL backend skeleton for the first core database layer.

Phase 7A only persists:

- Topic
- Content
- KnowledgeEntry
- ActivityLog

Publishing, Analytics, Settings, real platform APIs, auth, and cloud deployment are intentionally out of scope for this step.

## Local setup

```powershell
cd backend
copy .env.example .env
docker compose up -d postgres
py -m venv .venv
.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

Open:

- Health: <http://localhost:8000/api/health>
- API docs: <http://localhost:8000/docs>

## API routes

- `GET /api/health`
- `GET /api/topics`
- `POST /api/topics`
- `PUT /api/topics/{topic_id}`
- `GET /api/contents`
- `POST /api/contents`
- `PUT /api/contents/{content_id}`
- `GET /api/knowledge`
- `POST /api/knowledge`
- `PUT /api/knowledge/{knowledge_id}`
- `DELETE /api/knowledge/{knowledge_id}`
- `GET /api/activity-logs`
- `POST /api/import/localstorage-core`
- `GET /api/knowledge/{knowledge_id}/export.md`
- `POST /api/knowledge/export/markdown`

## localStorage import

The frontend Settings page can import existing localStorage Topic, Content, and Knowledge data into PostgreSQL.

Import is idempotent by original ID:

- existing IDs are skipped/updated safely
- localStorage is never deleted before import
- the response reports added, skipped, and failed counts

## Security

Do not commit `.env`.

API keys, platform tokens, and database credentials must stay in backend environment variables or backend-only storage. They must not be placed in frontend code.
