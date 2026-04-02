"""
main.py

FastAPI application entry point.

Creates the app instance, mounts all routers, and sets up
Prometheus metrics instrumentation.

Run locally with:
    uvicorn main:app --reload --port 8000
"""

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from routers import allergens, dietary_tags, health, recipes

app = FastAPI(
    title="Recipe Allergen Tracker API",
    description=(
        "Query recipes scraped from BBC Good Food, "
        "filtered by allergens and dietary preferences."
    ),
    version="1.0.0",
)

# ---------------------------------------------------------------
# ROUTERS
# All route handlers live in the routers/ directory.
# Each router is mounted with a prefix so routes are grouped.
# ---------------------------------------------------------------

app.include_router(recipes.router,      prefix="/recipes",      tags=["Recipes"])
app.include_router(allergens.router,    prefix="/allergens",    tags=["Allergens"])
app.include_router(dietary_tags.router, prefix="/dietary-tags", tags=["Dietary Tags"])
app.include_router(health.router,                               tags=["Health"])

# ---------------------------------------------------------------
# PROMETHEUS METRICS
# Automatically instruments all routes and exposes /metrics.
# Prometheus scrapes this endpoint on a schedule.
# ---------------------------------------------------------------

Instrumentator().instrument(app).expose(app)