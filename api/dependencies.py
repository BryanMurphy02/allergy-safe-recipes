"""
dependencies.py

Shared FastAPI dependencies injected into route handlers.

FastAPI's dependency injection system works by declaring a
function as a parameter type in a route handler. FastAPI
calls the function automatically and passes the result in.

Example usage in a route:
    @router.get("/recipes")
    def get_recipes(db: Session = Depends(get_db)):
        ...

get_db() opens a database session, yields it to the route
handler, then closes it cleanly when the request is done —
whether it succeeded or raised an exception. This pattern
ensures we never leak database connections.
"""

from collections.abc import Generator

from sqlalchemy.orm import Session

from database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    if SessionLocal is None:
        raise RuntimeError("DATABASE_URL is not configured")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()