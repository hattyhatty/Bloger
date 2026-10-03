"""Run real migrations + persistence checks in a disposable PostgreSQL database.

Run from backend: python tests/validate_execution_postgres.py
Uses backend configuration without printing credentials; never clears application data.
"""
import os
import sys
import subprocess
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.config import get_settings
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url


def main():
    url = make_url(get_settings().database_url)
    if url.get_backend_name() != "postgresql":
        raise RuntimeError("PostgreSQL configuration required")
    name = "execution_validation_" + uuid.uuid4().hex
    admin = create_engine(url.set(database="postgres"), isolation_level="AUTOCOMMIT")
    with admin.connect() as connection:
        connection.execute(text(f'CREATE DATABASE "{name}"'))
    env = os.environ.copy()
    env["DATABASE_URL"] = url.set(database=name).render_as_string(hide_password=False)
    try:
        for args in (("upgrade", "head"), ("check",), ("downgrade", "0009_execution_core"), ("upgrade", "head"), ("check",)):
            subprocess.run([sys.executable, "-m", "alembic", *args], env=env, check=True)
        subprocess.run([sys.executable, __file__, "--persistence"], env=env, check=True)
        env["TEST_DATABASE_URL"] = env["DATABASE_URL"]
        subprocess.run([sys.executable, "-m", "pytest", "tests", "-q"], env=env, check=True)
        print("PostgreSQL clean migration, downgrade/upgrade, API persistence and regression checks passed")
    finally:
        with admin.connect() as connection:
            connection.execute(text(f'DROP DATABASE "{name}" WITH (FORCE)'))
        admin.dispose()


def persistence():
    from fastapi.testclient import TestClient
    from app.main import app
    from app.database import engine, SessionLocal
    from app.queue import claim_next_job
    from app.models import ExecutionJob
    from app.workflow import utcnow
    from datetime import timedelta
    from test_execution import setup_prompt, create, start, outcome, transition
    from test_queue import create_request, enqueue
    with TestClient(app) as client:
        _, _, shot, prompt = setup_prompt(client, "real_pg")
        request = create(client, prompt)
        attempt = start(client, request)
        assert transition(client, request, "submitting").status_code == 200
        assert outcome(client, request, "completed", attempt_id=attempt["id"], provider_request_id="manual-fixture", response_payload={"url": "https://example.com/fixture"}).status_code == 200
        assert transition(client, request, "succeeded").status_code == 200
        result = client.post(f"/api/video-shots/{shot['id']}/results", json={"prompt_id": prompt["id"], "generation_request_id": request["id"], "result_url": "https://example.com/fixture", "status": "selected"})
        assert result.status_code == 200, result.text
        _, _, recovery_request = create_request(client, "real_pg_recovery")
        recovery_job = enqueue(client, recovery_request)
        with SessionLocal() as db:
            claimed = claim_next_job(db, "crash-fixture")
            assert claimed.id == recovery_job["id"]
            claimed = db.get(ExecutionJob, claimed.id)
            claimed.lease_expires_at = utcnow() - timedelta(seconds=1)
            db.commit()
        subprocess.run([sys.executable, "-m", "app.worker", "--recover-only"], check=True)
        recovered = client.get(f"/api/execution/generation-requests/{recovery_request['id']}/execution-state").json()
        assert recovered["jobs"][0]["status"] == "queued"
        assert client.post(f"/api/execution/generation-requests/{recovery_request['id']}/cancel", json={}).status_code == 200
        queue_shot, _, queue_request = create_request(client, "real_pg_queue", "async_success",
            ready_after_polls=1, poll_interval_seconds=0)
        enqueue(client, queue_request)
    engine.dispose()  # Read through fresh database connections, not an ORM cache.
    subprocess.run([sys.executable, "-m", "app.worker", "--once", "--worker-id", "persistence-submit"], check=True)
    subprocess.run([sys.executable, "-m", "app.worker", "--once", "--worker-id", "persistence-poll"], check=True)
    engine.dispose()
    with TestClient(app) as client:
        restored = client.get(f"/api/execution/generation-requests/{request['id']}").json()
        assert restored["status"] == "succeeded"
        assert restored["input_snapshot"]["prompt"]["genericVideoPrompt"] == "Creator in studio"
        history = client.get(f"/api/execution/receipts/{request['receipt_id']}").json()
        assert history["attempts"][0]["status"] == "completed"
        assert client.get(f"/api/video-shots/{shot['id']}/results").json()[0]["generation_request_id"] == request["id"]
        queue_state = client.get(f"/api/execution/generation-requests/{queue_request['id']}/execution-state").json()
        assert queue_state["request"]["status"] == "succeeded"
        assert len(queue_state["jobs"]) == 2
        queue_results = client.get(f"/api/video-shots/{queue_shot['id']}/results").json()
        assert queue_results[0]["status"] == "candidate"
    engine.dispose()
    print("Migrated PostgreSQL API persistence passed")


if __name__ == "__main__":
    persistence() if "--persistence" in sys.argv else main()
