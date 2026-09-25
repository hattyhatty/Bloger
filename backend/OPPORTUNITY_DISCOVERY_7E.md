# Phase 7E — Opportunity Discovery Engine

## Data design

`ContentOpportunity` is a first-class workspace-owned record. One Topic may have many Opportunities, and each Opportunity represents one independently actionable content angle. Relevant Knowledge uses the `opportunity_knowledge_links` association table. A developed Opportunity points to exactly one Content record.

The record stores audience and human-need reasoning, recommended format/platforms, eight score dimensions, the server-computed overall score, status, Creator Profile, analysis batch, and the eventual developed Content.

## Transparent scoring

The backend owns the final score:

| Dimension | Weight |
| --- | ---: |
| Novelty | 15% |
| Timeliness | 15% |
| Audience Fit | 15% |
| Creator Fit | 15% |
| Human Need Strength | 15% |
| Platform Fit | 10% |
| Visual Potential | 10% |
| Production Ease (`100 - difficulty`) | 5% |

AI may suggest dimension values, but a submitted overall score is ignored and recalculated by `app/opportunity.py`.

## Knowledge and Creator Memory

`GET /api/topics/{id}/opportunity-context` retrieves only active Knowledge from the same Workspace. It preserves the existing Knowledge type, source, confidence, Topic/Content relation, and Creator Profile. The frontend prompt explicitly separates verified Facts from Inferences; Inferences are labeled as unverified and cannot be presented as facts.

The ranking considers Account Positioning, Target Audience, Content Pillars, Preferred Formats, Topics to Avoid, and Platform Preferences. The current product still uses one Creator Profile per Workspace.

## Workflow and idempotency

Allowed states are `candidate`, `saved`, `rejected`, and `developed`. A developed record is terminal. Rejected records must be restored before Develop.

The analysis batch has a unique `(workspace, topic, batch, angle_key)` constraint. Candidate IDs and angle keys must be unique. Develop locks the Opportunity row in PostgreSQL, uses a deterministic Content ID, stores the resulting link, and returns the existing Content on retry.

## Frontend fallback

When PostgreSQL is available it remains authoritative. The frontend writes Opportunities through `ApiClient` and replaces the Opportunity cache during backend pull. If the backend is unavailable, the same workflow continues in localStorage and marks backend recovery as pending; the Settings migration safely imports those records later.

The fallback analysis uses Topic scores, relevant Knowledge, and Creator Memory. It does not fabricate platform metrics, and it keeps the same transparent scoring formula.
