# AI Content OS Backend — Phase 7C

FastAPI + PostgreSQL backend for the AI Content OS core workflow and Knowledge Brain.

The database persists:

- Topic
- Content
- KnowledgeEntry
- CreatorProfile (single creator memory)
- ActivityLog
- PlatformVersion / ApprovalRecord / PublishingTask
- TrackingSnapshot / AnalyticsRecord / ExperienceRecord

Real platform APIs, auth, multi-user SaaS, schedulers, vector databases, and cloud deployment remain intentionally out of scope.

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
- `POST /api/knowledge/{knowledge_id}/archive`
- `DELETE /api/knowledge/{knowledge_id}`
- `GET /api/creator-memory`
- `PUT /api/creator-memory`
- `GET /api/activity-logs`
- `POST /api/import/localstorage-core`
- `POST /api/import/localstorage-business`
- `GET /api/knowledge/{knowledge_id}/export.md`
- `POST /api/knowledge/export/markdown`

## localStorage import

The frontend Settings page can import existing localStorage Topic, Content, Knowledge, Creator Memory, and business workflow data into PostgreSQL.

Import is idempotent by original ID:

- existing IDs are skipped/updated safely
- localStorage is never deleted before import
- the response reports added, skipped, and failed counts

## Security

Do not commit `.env`.

API keys, platform tokens, and database credentials must stay in backend environment variables or backend-only storage. They must not be placed in frontend code.
