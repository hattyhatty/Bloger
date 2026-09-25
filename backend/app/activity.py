from sqlalchemy.orm import Session

from .models import ActivityLog


def log_activity(
    db: Session,
    action: str,
    entity_type: str,
    entity_id: str,
    details: dict | None = None,
    *,
    workspace_id: str = "default",
) -> None:
    db.add(ActivityLog(
        workspace_id=workspace_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details or {},
    ))
