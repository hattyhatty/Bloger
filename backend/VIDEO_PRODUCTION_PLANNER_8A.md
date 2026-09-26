# Phase 8A — AI Video Production Planner

Phase 8A adds a planning-only workflow:

`Content revision → Concept → Script → Storyboard → ordered Shot List → per-Shot Prompt`

It does not call Seedance, Kling, Veo, Runway, image generation, TTS, storage, editing, publishing, or scheduler APIs.

## Relational model

- `video_production_plans` binds one exact `Content.revision`, content hash, and immutable snapshot.
- `video_scripts` stores the reviewed Hook, narration/dialogue, information flow, CTA, estimated duration, and read-only upstream context IDs.
- `video_storyboards` stores cross-shot character and visual consistency constraints.
- `video_shots` stores ordered, editable production instructions with a unique `(storyboard_id, shot_number)` constraint.
- `video_generation_prompts` stores independent target adaptations with a unique `(shot_id, prompt_target)` constraint and a hash of the structured source Shot.

All records carry the existing Workspace ownership boundary.

## Human review boundaries

The UI exposes each step separately. It never runs Content through to final prompts with one click:

1. Create and edit the Concept.
2. Generate or manually edit and save the Script.
3. Generate or save Storyboard consistency information.
4. Add, edit, remove, and reorder Shots.
5. Generate or manually edit one target Prompt for one Shot.

An existing Storyboard with Shots cannot be regenerated as a batch. This avoids silently replacing manual edits.

## Status validation

- `draft`: no prerequisites.
- `planned`: requires a Script.
- `in_production`: requires a Storyboard with at least one Shot.
- `ready_for_review`: requires at least one Generation Prompt for every Shot.

The backend enforces these prerequisites independently of the browser.

## Version behavior

Editing upstream Content does not rewrite an existing Plan. The old Plan remains bound to its original revision and snapshot and reports `content_changed=true`. A new Plan can be created for the new Content revision. Repeated creation for the same Workspace, Content, and revision is idempotent.

## Fallback behavior

PostgreSQL is authoritative while the backend is healthy. The frontend mirrors Planner records into localStorage for cache/offline use. If the backend is unavailable, edits remain usable locally and mark pending recovery; Settings → Migrate Business Data uploads Planner records in dependency order before an authoritative pull.
