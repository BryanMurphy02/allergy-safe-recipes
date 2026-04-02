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