# AI Content OS Backend — Phase 8C

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
- VideoProductionPlan / VideoScript / VideoStoryboard / VideoShot / VideoGenerationPrompt
- VideoReferenceAsset / VideoShotReferenceLink / VideoGenerationResult

Runway Dev is the first real video generation adapter. Real publishing APIs,
multi-user SaaS, schedulers, vector databases, and cloud deployment remain out of scope.

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
# separate terminal; the API process never executes durable jobs
python -m app.worker
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
- `GET/POST/PUT /api/video-plans`
- `PATCH /api/video-plans/{plan_id}/status`
- `GET /api/video-plans/{plan_id}/workspace`
- `GET /api/video-plans/{plan_id}/context`
- `PUT /api/video-plans/{plan_id}/script`
- `PUT /api/video-plans/{plan_id}/storyboard`
- `POST /api/video-plans/{plan_id}/storyboard/generate`
- `POST /api/video-storyboards/{storyboard_id}/shots`
- `POST /api/video-storyboards/{storyboard_id}/shots/reorder`
- `PUT/DELETE /api/video-shots/{shot_id}`
- `PUT /api/video-shots/{shot_id}/prompt`
- `GET /api/video-reference-assets`
- `POST /api/video-shots/{shot_id}/references`
- `GET/POST /api/video-shots/{shot_id}/results`
- `PUT /api/video-results/{result_id}`
- `PATCH /api/video-results/{result_id}/status`
- `GET /api/video-providers`
- `POST /api/video-providers/runway/test` (read-only, non-billable probe)
- `POST/GET /api/execution/generation-requests`
- `POST /api/execution/generation-requests/{id}/enqueue`
- `GET /api/execution/generation-requests/{id}/execution-state`
- `POST /api/execution/generation-requests/{id}/cancel`
- `POST /api/execution/generation-requests/{id}/reconcile`
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

When the API is healthy, PostgreSQL is authoritative for Topic, Content, Knowledge, Creator Memory, Opportunity, Approval, Publishing, Tracking, Analytics, Experience, Creator Learning, Strategy Suggestion, and Video Production Planner data. The frontend keeps localStorage only as:

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

## Video Production Planner and result integrity

- every Video Plan binds an immutable Content revision, hash, and snapshot; later Content edits only mark the Plan as changed
- Script, Storyboard, ordered Shots, and per-target Prompts are independent relational records rather than a Content JSON blob
- plan status advancement is validated server-side: Script → Storyboard/Shots → at least one Prompt per Shot
- Shot order is unique inside one Storyboard and reorder requests must include every Shot exactly once
- each Shot has at most one Prompt per target (`Generic`, `Seedance`, `Kling`, `Veo`, `Runway`); regeneration updates only that target
- Prompt source hashes preserve traceability to structured Shot and consistency inputs
- Reference Assets are reusable across Shots through workspace-scoped link records
- each Generation Result stores immutable Shot and Prompt snapshots plus Plan, Storyboard, Prompt, and Content revisions
- a partial unique index and transactional status service guarantee at most one Selected Result per Shot
- Shots with Generation Results cannot be deleted, preserving production history
- Manual Result remains available alongside durable provider execution

## Runway Dev adapter (Phase 8C)

Set `RUNWAYML_API_SECRET` in `backend/.env` or the backend process environment.
The key is never returned by an API, persisted in a GenerationRequest/Job/Receipt,
or sent to the browser. `GET /api/video-providers` returns only `configured`.

The adapter currently supports Runway Gen-4.5 text-to-video through
`/v1/text_to_video` and first-frame image-to-video through `/v1/image_to_video`,
2–10 second output, the documented
720p aspect ratios, asynchronous task polling, cancellation and task-ID
reconciliation. A reference must already be a public HTTPS URL; local files are
rejected because this phase intentionally has no upload/object-storage pipeline.
Negative prompts and webhooks are not advertised because this vertical slice
does not implement unsupported or unnecessary capabilities.

Submission uses the immutable GenerationRequest snapshot. A Provider task ID is
saved before a poll job is scheduled. Polling performs one GET per worker job;
unfinished tasks schedule another durable job at least five seconds later.
Successful output creates exactly one candidate VideoGenerationResult. Runway
delivery URLs are temporary, so durable media storage remains technical debt.

Error handling preserves the execution certainty boundary: validation and missing
credentials fail before dispatch without inventing an Attempt; a definitive HTTP rejection fails the call; a
submit timeout or ambiguous 5xx becomes `unknown`; polling transport errors retry
only the Poll Job; and 429 honors `Retry-After` via `ExecutionJob.available_at`.
Runway credit cost is stored as structured usage/cost when the task response
provides it. No cost is estimated when Runway does not return billing data.

## Execution core (Phase 8B.5A)

The 8B.5A execution core separates business requests, logical calls, dispatch
attempts and production results. Provider transport remains behind an adapter.

- `ExternalCallReceipt`: one logical call, globally unique deterministic key,
  generic workspace-owned subject, template snapshot, input/config hashes,
  provider response, usage and optional cost/currency.
- `ExternalCallAttempt`: one dispatch attempt; numbered per Receipt. A partial
  unique index allows only one `running` attempt. Finished rows are never edited
  through the service/API. A received attempt records dispatch acceptance; later
  asynchronous completion changes the Receipt, not that finished Attempt.
- `GenerationRequest`: video business execution, linked to Plan/Shot/Prompt and
  Receipt, with immutable Content/Storyboard/Shot/Prompt/consistency input snapshot.
- `VideoGenerationResult.generation_request_id`: nullable unique relationship.
  Manual results remain supported. Execution-linked results require a succeeded
  request and use its original snapshots rather than today's edited Prompt.

`backend/prompts/` contains code-owned templates. Registry template versions are
SHA256 of UTF-8 template content (line endings normalized); they are independent
of `VideoGenerationPrompt.revision`. Receipt snapshots retain template content.

The logical key is SHA256 of canonical sorted JSON containing schema version,
Workspace, service/purpose/subject, input revision/hash, provider/model, template
key/version/hash, Prompt artifact revision and configuration hash. Changing any
generation input produces a distinct request; retrying the same logical call
keeps its Receipt and appends another Attempt. Subject/Shot locks and unique
constraints protect concurrent create; row locks serialize state mutations.

Receipt lifecycle:

- `pending` → `received` / `completed` / `failed` / `unknown`
- `received` → `completed` / `failed` / `unknown`
- confirmed `failed` → new Attempt (`pending`)
- `unknown` → explicit reconciliation only, requiring provider ID and evidence
- `completed` is terminal; duplicate outcomes do not overwrite stored data
- active Attempt ID is required for outcomes; stale callbacks are rejected
- a crash leaves a running Attempt that blocks retry until explicitly resolved

GenerationRequest transitions:

- `created` → `queued` / `submitting` / `cancelled`
- `queued` → `submitting` / pre-dispatch `failed` / `cancelled`
- `submitting` → `submitted` / `succeeded` / `failed` / `unknown`
- `submitted` → `polling` / `succeeded` / `failed` / `unknown` / provider-confirmed `cancelled`
- `polling` → `succeeded` / `failed` / `unknown` / provider-confirmed `cancelled`
- `failed` → `queued` / `cancelled`
- `unknown` → `submitted` / `succeeded` / `failed`, only after Receipt reconciliation
- `succeeded` / `cancelled` are terminal

Submission requires a running Attempt. Accepted/polling states require a provider
job ID and matching Receipt outcome; success requires a completed Receipt.
Provider job IDs cannot change within an attempt. A confirmed failed request
requeued for retry resets its current job metadata; the previous ID remains in
ActivityLog and the finished Attempt's provider request record.
Start Attempt is disallowed for cancelled or already submitted requests.
Moving into `queued` through the API now delegates to the transactional durable
queue service described below.

API routes (all mutations delegate to `app/execution.py`):

- `POST/GET /api/execution/receipts`
- `GET /api/execution/receipts/{id}` (Receipt + ordered Attempt history)
- `POST /api/execution/receipts/{id}/attempts`
- `PATCH /api/execution/receipts/{id}/outcome`
- `POST/GET /api/execution/generation-requests`
- `GET /api/execution/generation-requests/{id}`
- `PATCH /api/execution/generation-requests/{id}/status`

ActivityLog covers Receipt creation/reuse/outcomes, Attempt starts and Request
creation/state changes. Reads are not logged. Execution input config/summary
reject credential fields; API keys belong in backend provider configuration.

Validation:

```powershell
python -m pytest tests -q
python tests/validate_execution_postgres.py
python -m alembic upgrade head
python -m alembic check
```

The PostgreSQL validator creates a disposable database, runs all migrations,
checks downgrade/upgrade, verifies API persistence through fresh connections,
runs the regression suite with isolated schemas, and removes only its own test
database. It does not clear the application's database. Set `TEST_DATABASE_URL`
to opt into PostgreSQL pytest fixtures; default tests use SQLite.

## Durable execution worker (Phase 8B.5B)

`ExecutionJob` is separate from `GenerationRequest`. PostgreSQL stores every job,
schedule, attempt count, lease, heartbeat, error and completion state. Supported
job types are `generation.submit`, `generation.poll`, `generation.cancel` and
`generation.reconcile`; queue states are `queued`, `running`, `succeeded`,
`failed`, `dead` and `cancelled`. Provider uncertainty remains exclusively on the
Receipt and GenerationRequest.

Enqueue strategy and idempotency:

- `GenerationRequest → queued` and the submit Job insert share one transaction.
- stable keys are `generation.submit:{request}`, `generation.poll:{request}:{sequence}`,
  `generation.cancel:{request}` and `generation.reconcile:{request}`.
- a database unique constraint plus a locked GenerationRequest makes repeated and
  concurrent enqueue safe; Job IDs are derived from those keys, not random IDs.
- each pending provider poll is one future `ExecutionJob.available_at`; workers do
  not wait in a provider polling loop.

Claim and lease algorithm:

- workers claim in a short transaction using `FOR UPDATE SKIP LOCKED`, ordered by
  priority then availability, and atomically set owner, expiry and attempt count.
- a separate heartbeat connection renews long adapter calls every lease/3; only
  the active, unexpired owner can renew or finalize a Job.
- worker startup runs idempotent expired-lease recovery before claiming work.
- pre-dispatch crashes requeue with backoff. A running ExternalCallAttempt proves
  the uncertainty boundary was crossed, so recovery marks Receipt and Request
  `unknown` and never redispatches automatically.
- accepted submissions recovered after a crash are completed as submit Jobs and
  receive exactly one active poll Job. Poll and reconciliation lookups are safe
  to reschedule because they do not create a new generation.

Retry policy uses `min(300, 2 ** attempt_count)` seconds, overridden by a
provider `Retry-After` value up to the same cap. Only pre-dispatch or
otherwise side-effect-free technical errors retry automatically. Exhausted jobs
become `dead`; definitive provider rejection becomes `failed`; timeout after
dispatch becomes provider `unknown`. Manual retry rejects succeeded, cancelled or
unknown generation calls, except that an unknown reconciliation lookup itself may
be safely retried.

`FakeVideoProvider` is deterministic, offline and implements the same
`submit/poll/cancel/reconcile` contract required of future real adapters. It can
simulate immediate success, asynchronous completion, not-ready polls, definitive
failure, pre-dispatch transient errors, timeout/unknown, supported/unsupported
cancellation and reconciliation success/failure. Successful metadata creates one
idempotent `candidate` VideoGenerationResult from the immutable request snapshot;
it is never auto-selected.

Run the independent worker:

```powershell
python -m app.worker
python -m app.worker --once --worker-id local-smoke
python -m app.worker --recover-only
```

Minimal operations API:

- `POST /api/execution/generation-requests/{id}/enqueue`
- `GET /api/execution/generation-requests/{id}/execution-state`
- `GET /api/execution/jobs`
- `POST /api/execution/jobs/{id}/retry`
- `POST /api/execution/generation-requests/{id}/cancel`
- `POST /api/execution/generation-requests/{id}/reconcile`

Jobs and payloads reject credential-shaped fields and contain no provider secrets.
Worker credentials remain backend-only. ActivityLog records enqueue, claim,
retry, success/failure/dead, recovery, dispatch, polling schedule and unknown
outcomes; heartbeat writes only to the Job row.

Known 8C boundaries: Runway output URLs are temporary and no S3/R2 ingest exists;
there is no webhook ingestion, distributed metrics/alerts or operator dashboard.
Reconciliation requires a known Runway task ID, otherwise the request correctly
remains `unknown` for manual handling. This is a database queue, not a distributed
scheduler or autoscaler. Attempt immutability is service-enforced, not protected
against privileged direct SQL changes. Existing single-Creator Workspace
ownership and no-auth development API remain unchanged.

## Security requirements

Do not commit `.env`.

API keys, platform tokens, and database credentials must stay in backend environment variables or backend-only storage. They must not be placed in frontend code.
