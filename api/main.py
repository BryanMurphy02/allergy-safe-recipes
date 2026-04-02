"""
main.py

FastAPI application entry point.

Creates the app instance, mounts all routers, sets up
Prometheus metrics, and calls wait_for_db() on startup
to ensure the database is ready before serving traffic.

Run locally with:
    uvicorn main:app --reload --port 8000
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from database import wait_for_db
from routers import allergens, dietary_tags, health, recipes


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Runs once when the app starts up.
    wait_for_db() blocks until Postgres is reachable,
    then the app starts serving traffic.
    """
    wait_for_db()
    yield


app = FastAPI(
    title="Recipe Allergen Tracker API",
    description=(
        "Query recipes scraped from BBC Good Food, "
        "filtered by allergens and dietary preferences."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(recipes.router,      prefix="/recipes",      tags=["Recipes"])
app.include_router(allergens.router,    prefix="/allergens",    tags=["Allergens"])
app.include_router(dietary_tags.router, prefix="/dietary-tags", tags=["Dietary Tags"])
app.include_router(health.router,                               tags=["Health"])

Instrumentator().instrument(app).expose(app)