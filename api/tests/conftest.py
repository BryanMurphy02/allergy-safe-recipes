"""
tests/conftest.py

Shared pytest fixtures for the API test suite.

Two key fixtures:

  db_session — creates a fresh in-memory SQLite database for
               each test, applies the schema, and seeds reference
               data (allergens, dietary tags). Torn down after
               each test so tests are fully isolated.

  client     — a FastAPI TestClient wired to use the test db_session
               instead of the real Postgres database. Every test
               that uses client gets a clean database.

Why SQLite for testing?
  We don't want tests to need a running Postgres container.
  SQLite runs entirely in memory, needs no setup, and is fast.
  The trade-off is minor dialect differences — but for the queries
  we're running, SQLite behaves identically to Postgres.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from unittest.mock import patch

from dependencies import get_db
from main import app
from models import Allergen, Base, DietaryTag, Recipe, RecipeAllergen, RecipeDietaryTag

SQLITE_URL = "sqlite://"


@pytest.fixture(autouse=True)
def mock_wait_for_db():
    """
    Prevents wait_for_db() from trying to connect to a real
    Postgres database when the TestClient starts up during tests.
    Applied automatically to every test via autouse=True.
    """
    with patch("main.wait_for_db"):
        yield


@pytest.fixture()
def db_session():
    """
    Creates a fresh in-memory SQLite database for a single test.
    Seeds allergens and dietary tags to mirror schema.sql.
    Drops all tables after the test completes.
    """
    engine = create_engine(
        SQLITE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()

    session.add_all([
        Allergen(id=1, name="peanuts",   display_name="Peanuts",   description="Peanut-derived ingredients"),
        Allergen(id=2, name="tree_nuts", display_name="Tree Nuts", description="Almonds, cashews, walnuts etc."),
        Allergen(id=3, name="dairy",     display_name="Dairy",     description="Milk-derived ingredients"),
        Allergen(id=4, name="egg",       display_name="Egg",       description="Egg-derived ingredients"),
    ])

    session.add_all([
        DietaryTag(id=1, name="vegetarian",       display_name="Vegetarian",       description="No meat or fish"),
        DietaryTag(id=2, name="vegan",            display_name="Vegan",            description="No animal products"),
        DietaryTag(id=3, name="gluten_free",      display_name="Gluten-Free",      description="No gluten"),
        DietaryTag(id=4, name="contains_raw_egg", display_name="Contains Raw Egg", description="Raw egg present"),
    ])

    session.commit()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session):
    """
    Returns a FastAPI TestClient wired to the test database.
    FastAPI's dependency override replaces get_db() with
    a function that returns the test session instead.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


# ---------------------------------------------------------------
# DATA FACTORIES
# ---------------------------------------------------------------

def make_recipe(db_session, **kwargs) -> Recipe:
    """Creates and commits a Recipe with sensible defaults."""
    from models import Source
    source = db_session.query(Source).first()
    if not source:
        source = Source(id=1, name="BBC Good Food", base_url="https://www.bbcgoodfood.com")
        db_session.add(source)
        db_session.commit()

    defaults = {
        "source_id":  source.id,
        "title":      "Test Recipe",
        "url":        "https://www.bbcgoodfood.com/recipes/test-recipe",
        "cuisine":    "British",
        "prep_time":  10,
        "cook_time":  20,
        "total_time": 30,
        "servings":   4,
    }
    defaults.update(kwargs)

    recipe = Recipe(**defaults)
    db_session.add(recipe)
    db_session.commit()
    db_session.refresh(recipe)
    return recipe


def add_allergen_to_recipe(db_session, recipe: Recipe, allergen_name: str):
    """Links a named allergen to a recipe in recipe_allergens."""
    allergen = db_session.query(Allergen).filter(Allergen.name == allergen_name).first()
    if allergen:
        db_session.add(RecipeAllergen(recipe_id=recipe.id, allergen_id=allergen.id))
        db_session.commit()


def add_dietary_tag_to_recipe(db_session, recipe: Recipe, tag_name: str):
    """Links a named dietary tag to a recipe in recipe_dietary_tags."""
    tag = db_session.query(DietaryTag).filter(DietaryTag.name == tag_name).first()
    if tag:
        db_session.add(RecipeDietaryTag(recipe_id=recipe.id, dietary_tag_id=tag.id))
        db_session.commit()