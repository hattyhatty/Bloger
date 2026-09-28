# Phase 8B — Shot Asset & Result Tracking

Phase 8B extends the human-reviewed Video Planner without calling a video provider API.

## Data model

- `video_reference_assets` stores lightweight external references classified as character, clothing, environment, style, or other.
- `video_shot_reference_links` allows one Reference Asset to be reused by multiple Shots while preserving the bound Video Plan and Content revision.
- `video_generation_results` records an external result, provider/model, URL or file reference, note, and lifecycle status.

Every Generation Result stores immutable copies of the Shot and Prompt used at creation, together with `plan_content_revision`, `storyboard_revision`, and `prompt_revision`. Later Shot, Storyboard, Prompt, or Content edits cannot rewrite this history.

## Integrity rules

- a Prompt must belong to the same Shot as its Result
- a Result requires a URL or external file reference
- only one Result per Shot can be `selected`; selecting another returns the previous selection to `candidate`
- `rejected` and `archived` records remain queryable
- a Shot with any Result cannot be deleted
- all writes enforce the existing Workspace boundary and emit ActivityLog entries

## Manual workflow

Copy Prompt → generate externally in Seedance/Kling/Veo/Runway → add Result → Select, Reject, or Archive.

No generation queue, worker, object storage, upload pipeline, video editor, or real video provider integration is included.
