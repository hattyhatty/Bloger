# Phase 7D Architecture Audit & Hardening

## Audit findings

The audit confirmed these structural risks:

1. The frontend wrote localStorage first and then bulk-imported it after every save, while backend bootstrap merged rather than replaced server-backed collections. PostgreSQL and localStorage could therefore behave as parallel primary stores.
2. A platform version was mutable and reused for a content/platform pair. Approval and publishing records did not identify the exact approved revision.
3. Business workflow rules were mostly enforced by the UI. Generic API writes could publish an unapproved content item or start tracking against an invalid task.
4. Critical retry paths relied on caller-provided IDs without database business-key constraints or transaction-level idempotency.
5. Tracking checkpoint updates overwrote the same record instead of retaining a historical sequence.
6. Knowledge types were already separated correctly, but Knowledge, Creator Memory, and business records had no minimal ownership boundary. Knowledge deletion could remove an audit-relevant record.

## Hardening changes

- PostgreSQL is authoritative whenever the backend is healthy. localStorage is now a cache, offline fallback, and pending-recovery source only.
- Normal saves use entity-level write-through. Full imports are explicit, idempotent recovery/migration operations.
- If an online optimistic Topic/Content write is rejected by workflow validation, the frontend immediately restores the PostgreSQL snapshot instead of retaining a divergent local record.
- Added a default Workspace ownership boundary without introducing authentication or multi-user UI.
- Added Content revision/hash metadata and immutable, sequential PlatformVersion revisions.
- Approval binds the exact PlatformVersion, content revision, snapshot, and hash.
- Publishing binds the Approval and PlatformVersion and stores the approved snapshot. A later content edit cannot alter published history.
- Re-saving published metadata preserves the original approval, content revision, and platform snapshot; an existing PlatformVersion cannot be rebound to another Content.
- Added a centralized workflow service for approval, publishing, tracking, analytics, and experience validation.
- Added unique constraints and idempotent resolution for publishing, analytics, tracking history, experience, and creator memory.
- TrackingSnapshot is append-only by checkpoint and sequence; Analytics remains a traceable summary.
- Knowledge delete now archives. Fact entries require a source, and cross-workspace Topic/Content references are rejected.
- ActivityLog covers approval invalidation/approval/revocation, publishing creation/status changes, tracking, analytics, experience review, Knowledge changes, and Creator Memory changes.

## Already correct and retained

- Fact, Inference, Learning, Creator Preference, and Playbook were already distinct Knowledge types.
- Knowledge retrieval already kept verified facts separate from inference results.
- Research Save to Knowledge already used the Knowledge service path.
- Creator Memory already used the API/client abstraction.
- Frontend approval invalidation and local tracking guards were already present; backend validation was added without replacing those UX checks.
- AI-capable business modules already call the AI Router rather than a specific provider. No provider-specific dependency was added.
- The localStorage fallback remains available when the backend is unavailable.

## Remaining technical debt

- Offline edits use explicit recovery/migration rather than automatic conflict resolution. A future phase should add a visible per-entity outbox and conflict UI before multi-device editing.
- The default workspace boundary is ready for future ownership, but authentication and authorization are intentionally absent.
- Existing legacy rows are backfilled to one current immutable revision. The migration cannot reconstruct historical revisions that were never stored.
- PostgreSQL advisory locks or explicit idempotency keys may be appropriate when background workers and concurrent Agents are introduced.
- Analytics summaries are updated transactionally from snapshots, but a dedicated rebuild command would improve disaster recovery at larger scale.
- Legacy AI Settings still support a browser-local provider key and direct provider calls. Before production credentials are used, this configuration and invocation path must move behind a backend AI capability endpoint.

## Phase 7E readiness

The current architecture is suitable for Opportunity Discovery as a single-workspace system, provided Phase 7E uses the existing service/API boundaries and does not bypass workflow validation or the authoritative-source policy.

## Validation completed

- PostgreSQL migration `0004_architecture_hardening` upgraded, downgraded to `0003_knowledge_brain`, and upgraded again on an isolated database.
- `alembic current` reports `0004_architecture_hardening (head)` and `alembic check` reports no pending schema operations.
- Backend test suite: 8 passed.
- Real HTTP/PostgreSQL flow: Topic → Content → PlatformVersion → Approval → Publishing → TrackingSnapshot → Analytics → Experience/ActivityLog passed.
- Invalid pre-approval publishing, pre-publication tracking, immutable snapshot changes, and PlatformVersion rebinding returned HTTP 409.
- Core and business localStorage imports were each executed twice; the first pass added records and the second pass skipped all duplicates.
- Knowledge Fact save, filtered retrieval, archive rules, source requirement, and workspace relationship validation passed.
- Frontend JavaScript syntax, Python compile, whitespace, static file serving, and relative GitHub Pages asset paths passed.
