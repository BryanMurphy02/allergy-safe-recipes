"""
database.py

Sets up the SQLAlchemy engine and session factory.

The engine is the low-level connection to Postgres.
The SessionLocal factory creates individual database sessions —
one per request, opened at the start and closed at the end.

This module is imported by dependencies.py which exposes
get_db() to the route handlers via FastAPI's dependency injection.
"""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise EnvironmentError("DATABASE_URL is not set in environment")

# The engine manages the actual connection pool to Postgres.
# pool_pre_ping=True checks connections are alive before using them
# — important for long-running services where connections can drop.
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

# SessionLocal is a factory — calling SessionLocal() creates a
# new session. We never use it directly in route handlers,
# instead get_db() in dependencies.py handles that cleanly.
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)