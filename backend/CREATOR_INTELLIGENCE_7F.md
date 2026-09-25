# Phase 7F — Creator Intelligence & Learning Loop

## Evidence-backed Learning

`CreatorLearning` stores a reusable performance pattern. `CreatorLearningEvidence` stores the exact records that support or contradict it: Content, Opportunity, PublishingTask, AnalyticsRecord, ExperienceRecord, historical TrackingSnapshot IDs, observed metrics, and observation time.

Generation is deterministic-first. Only Published tasks with real Views are considered. The service calculates engagement, save, share, comment, follow-conversion, and completion/retention rates from Analytics and the latest append-only TrackingSnapshot. No model is allowed to invent performance values.

## Confidence and lifecycle

Confidence is transparent:

- sample size: up to 40 points
- consistency: 25%
- recency: 20%
- effect strength versus the relevant baseline: 15%

One sample is capped at 35 confidence and two samples at 48. A pattern needs at least three samples, confidence 60+, a non-neutral direction, and consistent evidence before it becomes `active`.

Statuses are `proposed`, `active`, `weakened`, and `archived`. Repeated generation validates the same `(workspace, pattern_key)` record. Contradictory direction, low consistency, or weak confidence can move an active Learning to `weakened`. Archived Learning remains historical but no longer influences new Opportunities.

## Feedback-loop protection

Active Learning may adjust an Opportunity by at most ±8 points. The score also carries an explicit exploration bonus: unseen directions get the largest bonus, while well-sampled known directions still retain a small exploration value. The Opportunity stores the matching Learning IDs and a human-readable explanation of every score change.

## Human-controlled strategy

Strong positive Learnings may create a `StrategySuggestion`, but they never edit Account Positioning, Content Pillars, Topics to Avoid, platform preferences, or format preferences directly. Only an explicit `accepted` decision updates the allowed Creator Memory list field. `rejected` and `ignored` decisions are retained for audit.

## Knowledge and Content integration

Every Learning is mirrored to Knowledge Brain as type `Learning` with confidence, sample size, metrics, evidence IDs, and validation time. It is never stored as `Fact`.

Opportunity analysis reads active same-workspace Learning through the service boundary. Develop copies only the relevant Learning IDs and guidance into the new Content context. Content Studio displays the guidance without automatically changing title, Hook, or body.

## Source of truth and fallback

PostgreSQL is authoritative when the backend is healthy. localStorage holds a cache/offline fallback plus pending recovery data. Settings migration imports fallback Learnings only when their Analytics evidence can be resolved, preserves terminal server decisions, and is idempotent.
