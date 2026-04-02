"""
database.py

Sets up the SQLAlchemy engine and session factory.

Includes a wait_for_db() function that retries the database
connection on startup — important in Docker where the API
container may start before Postgres is fully ready to accept
connections. Without this the API crashes immediately and
Docker has to restart it.
"""

import logging
import os
import time

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker

load_dotenv()

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
) if DATABASE_URL else None

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
) if engine else None


def wait_for_db(retries: int = 10, delay: int = 3) -> None:
    """
    Attempts to connect to the database, retrying on failure.

    Called once at API startup before the app begins serving
    traffic. If the database isn't ready yet — which happens
    in Docker when the API container starts before Postgres
    has finished initialising — this function waits and retries
    rather than crashing.

    retries — how many times to attempt the connection
    delay   — seconds to wait between each attempt

    Raises RuntimeError if all retries are exhausted.
    """
    if not engine:
        raise RuntimeError("DATABASE_URL is not configured")

    for attempt in range(1, retries + 1):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Database connection established")
            return
        except OperationalError as e:
            logger.warning(
                f"Database not ready (attempt {attempt}/{retries}): {e}"
            )
            if attempt < retries:
                time.sleep(delay)

    raise RuntimeError(
        f"Could not connect to database after {retries} attempts"
    )