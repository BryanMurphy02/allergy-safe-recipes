"""
routers/health.py

Health and readiness endpoints.

GET /health  — liveness probe. Docker and Kubernetes use this
               to know if the container is alive. Returns 200
               if the app is running, regardless of DB state.

GET /ready   — readiness probe. Returns 200 only if the database
               is reachable. Use this to know if the API can
               actually serve traffic.

/metrics is handled automatically by the Prometheus
instrumentator mounted in main.py — no code needed here.
"""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from dependencies import get_db

router = APIRouter()


@router.get("/health")
def health():
    """
    Liveness probe — is the API process running?
    Always returns 200 if the app is up.
    """
    return {"status": "ok"}


@router.get("/ready")
def ready(db: Session = Depends(get_db)):
    """
    Readiness probe — can the API reach the database?
    Returns 200 if the DB connection works, 503 if not.
    """
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ready", "database": "connected"}
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail=f"Database unavailable: {e}")