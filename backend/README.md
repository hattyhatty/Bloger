# AI Content OS Backend — Phase 7F

FastAPI + PostgreSQL backend for the AI Content OS core workflow and Knowledge Brain, with server-side workflow validation, immutable published-version history, and idempotent business operations.

The database persists:

- Topic
- Content
- KnowledgeEntry
- CreatorProfile (single creator memory)
- ActivityLog
- PlatformVersion / ApprovalRecord / PublishingTask
- TrackingSnapshot / AnalyticsRecord / ExperienceRecord
- Workspace (the minimal ownership boundary; this phase still uses one default workspace)
- ContentOpportunity and its relevant Knowledge / Creator Learning links
- CreatorLearning / CreatorLearningEvidence / StrategySuggestion

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
- `GET /api/topics/{topic_id}/opportunity-context`
- `GET /api/opportunities`
- `POST /api/opportunities/analyze`
- `PATCH /api/opportunities/{opportunity_id}/status`
- `POST /api/opportunities/{opportunity_id}/develop`
- `GET /api/creator-intelligence`
- `POST /api/creator-intelligence/generate`
- `GET /api/creator-learnings`
- `POST /api/creator-learnings/{learning_id}/archive`
- `GET /api/strategy-suggestions`
- `PATCH /api/strategy-suggestions/{suggestion_id}`
- `GET /api/activity-logs`
- `GET/POST/PUT /api/platform-versions`
- `GET/POST/PUT /api/approvals`
- `GET/POST/PUT /api/publishing-tasks`
- `POST /api/publishing-tasks/{task_id}/tracking/start`
- `GET/POST/PUT /api/tracking-snapshots`
- `GET/POST/PUT /api/analytics-records`
- `GET/POST/PUT /api/experience-records`
- `POST /api/import/localstorage-core`
- `POST /api/import/localstorage-business`
- `GET /api/knowledge/{knowledge_id}/export.md`
- `POST /api/knowledge/export/markdown`

## localStorage import

The frontend Settings page can import existing localStorage Topic, Content, Knowledge, Creator Memory, Opportunity, business workflow, Creator Learning, and Strategy Suggestion data into PostgreSQL.

Import is idempotent by original ID:

- existing IDs are skipped/updated safely
- localStorage is never deleted before import
- the response reports added, skipped, and failed counts

## Source of truth and offline fallback

When the API is healthy, PostgreSQL is authoritative for Topic, Content, Knowledge, Creator Memory, Opportunity, Approval, Publishing, Tracking, Analytics, Experience, Creator Learning, and Strategy Suggestion data. The frontend keeps localStorage only as:

- a local cache for fast rendering
- a temporary offline fallback when the API is unavailable
- pending recovery data until the user runs the idempotent migration action

Normal frontend saves use entity-level write-through. They do not re-import the entire local database after every save. A successful backend bootstrap replaces server-backed cache collections with the database snapshot; it does not merge stale local records back into the authoritative result.

## Workflow integrity

The service layer in `app/workflow.py` enforces the business chain independently of the UI:

- approvals bind an exact content revision and immutable platform version
- publishing requires a matching active approval
- published records retain an immutable version snapshot
- tracking starts only for a published task with an actual timestamp and URL
- tracking snapshots are append-only history
- analytics and experience records must refer to the same publishing/content/version chain
- repeated approval, publishing, tracking, and experience requests resolve idempotently

## Opportunity Discovery integrity

- each Content angle is an independent `ContentOpportunity` row
- one analysis batch contains 3–5 unique angles for one workspace-owned Topic
- relevant Knowledge is linked through `opportunity_knowledge_links`; only active, same-workspace entries are accepted
- Fact and Inference types remain unchanged in retrieval context so AI prompts cannot silently treat an inference as verified fact
- Creator Memory is loaded through the service/API boundary and bound to the same workspace
- the server recalculates `overall_score` from fixed, inspectable weights; it never trusts a model-provided total
- Save, Reject, Restore, and Develop use controlled status transitions
- Develop creates one Content record and is idempotent; the Content keeps the source Opportunity, Topic, Knowledge IDs, score, and reasoning

## Creator Intelligence integrity

- Learnings are derived deterministically from published Analytics and historical TrackingSnapshot data; AI may explain evidence but cannot invent metrics
- each Learning links to its supporting Content, PublishingTask, AnalyticsRecord, ExperienceRecord, Opportunity, and tracking snapshot IDs
- confidence combines sample size, consistency, recency, and effect strength; one or two samples cannot become an active rule
- new consistent evidence validates a Learning, while contradictory evidence can weaken it; Archive removes it from future ranking
- Opportunity scoring shows a capped Learning adjustment (±8) plus an explicit exploration bonus, preventing historical winners from monopolizing future recommendations
- Develop carries relevant Learning IDs and guidance into Content, but Content Studio never overwrites the user's draft automatically
- Strategy Suggestions require Accept / Reject / Ignore; Creator Memory changes only after an explicit Accept
- Learning entries mirrored to Knowledge Brain always retain type `Learning`, evidence IDs, metrics, and confidence; they are never promoted to `Fact`

## Security

Do not commit `.env`.

API keys, platform tokens, and database credentials must stay in backend environment variables or backend-only storage. They must not be placed in frontend code.
