"""
models.py

SQLAlchemy ORM models — one class per database table.

These map directly to the tables defined in db/schema.sql.
SQLAlchemy uses them to generate queries rather than us
writing raw SQL in every route handler.

Note: we are using SQLAlchemy 2.0 style with mapped_column()
and Mapped[] type annotations — this is the modern approach
and gives better type checking than the older Column() style.
"""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import (
    Boolean,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """
    Base class all models inherit from.
    SQLAlchemy uses this to track all table definitions.
    """
    pass


# ---------------------------------------------------------------
# SOURCES
# ---------------------------------------------------------------

class Source(Base):
    __tablename__ = "sources"

    id:         Mapped[int]          = mapped_column(Integer, primary_key=True)
    name:       Mapped[str]          = mapped_column(String(100), nullable=False)
    base_url:   Mapped[str]          = mapped_column(String(255), nullable=False, unique=True)
    enabled:    Mapped[bool]         = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime]     = mapped_column(nullable=False, default=lambda: datetime.now(timezone.utc))

    recipes:    Mapped[list["Recipe"]]    = relationship("Recipe", back_populates="source")
    scrape_logs: Mapped[list["ScrapeLog"]] = relationship("ScrapeLog", back_populates="source")


# ---------------------------------------------------------------
# RECIPES
# ---------------------------------------------------------------

class Recipe(Base):
    __tablename__ = "recipes"

    id:          Mapped[int]           = mapped_column(Integer, primary_key=True)
    source_id:   Mapped[int]           = mapped_column(ForeignKey("sources.id"), nullable=False)
    title:       Mapped[str]           = mapped_column(String(255), nullable=False)
    url:         Mapped[str]           = mapped_column(String(500), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    cuisine:     Mapped[Optional[str]] = mapped_column(String(100))
    prep_time:   Mapped[Optional[int]] = mapped_column(Integer)
    cook_time:   Mapped[Optional[int]] = mapped_column(Integer)
    total_time:  Mapped[Optional[int]] = mapped_column(Integer)
    servings:    Mapped[Optional[int]] = mapped_column(Integer)
    image_url:   Mapped[Optional[str]] = mapped_column(String(500))
    scraped_at:  Mapped[datetime]      = mapped_column(nullable=False, default=lambda: datetime.now(timezone.utc))

    source:           Mapped["Source"]               = relationship("Source", back_populates="recipes")
    recipe_ingredients: Mapped[list["RecipeIngredient"]] = relationship("RecipeIngredient", back_populates="recipe", cascade="all, delete-orphan")
    recipe_allergens:   Mapped[list["RecipeAllergen"]]   = relationship("RecipeAllergen", back_populates="recipe", cascade="all, delete-orphan")
    recipe_dietary_tags: Mapped[list["RecipeDietaryTag"]] = relationship("RecipeDietaryTag", back_populates="recipe", cascade="all, delete-orphan")


# ---------------------------------------------------------------
# INGREDIENTS
# ---------------------------------------------------------------

class Ingredient(Base):
    __tablename__ = "ingredients"

    id:               Mapped[int]      = mapped_column(Integer, primary_key=True)
    raw_name:         Mapped[str]      = mapped_column(String(255), nullable=False, unique=True)
    normalised_name:  Mapped[str]      = mapped_column(String(255), nullable=False)
    created_at:       Mapped[datetime] = mapped_column(nullable=False, default=lambda: datetime.now(timezone.utc))

    recipe_ingredients:   Mapped[list["RecipeIngredient"]]   = relationship("RecipeIngredient", back_populates="ingredient")
    ingredient_allergens: Mapped[list["IngredientAllergen"]] = relationship("IngredientAllergen", back_populates="ingredient", cascade="all, delete-orphan")


# ---------------------------------------------------------------
# RECIPE_INGREDIENTS
# ---------------------------------------------------------------

class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredients"
    __table_args__ = (UniqueConstraint("recipe_id", "ingredient_id"),)

    id:            Mapped[int]           = mapped_column(Integer, primary_key=True)
    recipe_id:     Mapped[int]           = mapped_column(ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False)
    ingredient_id: Mapped[int]           = mapped_column(ForeignKey("ingredients.id"), nullable=False)
    quantity:      Mapped[Optional[str]] = mapped_column(String(50))
    unit:          Mapped[Optional[str]] = mapped_column(String(50))
    preparation:   Mapped[Optional[str]] = mapped_column(String(100))

    recipe:     Mapped["Recipe"]     = relationship("Recipe", back_populates="recipe_ingredients")
    ingredient: Mapped["Ingredient"] = relationship("Ingredient", back_populates="recipe_ingredients")


# ---------------------------------------------------------------
# ALLERGENS
# ---------------------------------------------------------------

class Allergen(Base):
    __tablename__ = "allergens"

    id:           Mapped[int]           = mapped_column(Integer, primary_key=True)
    name:         Mapped[str]           = mapped_column(String(100), nullable=False, unique=True)
    display_name: Mapped[str]           = mapped_column(String(100), nullable=False)
    description:  Mapped[Optional[str]] = mapped_column(Text)

    ingredient_allergens: Mapped[list["IngredientAllergen"]] = relationship("IngredientAllergen", back_populates="allergen")
    recipe_allergens:     Mapped[list["RecipeAllergen"]]     = relationship("RecipeAllergen", back_populates="allergen")


# ---------------------------------------------------------------
# INGREDIENT_ALLERGENS
# ---------------------------------------------------------------

class IngredientAllergen(Base):
    __tablename__ = "ingredient_allergens"
    __table_args__ = (UniqueConstraint("ingredient_id", "allergen_id"),)

    id:            Mapped[int] = mapped_column(Integer, primary_key=True)
    ingredient_id: Mapped[int] = mapped_column(ForeignKey("ingredients.id", ondelete="CASCADE"), nullable=False)
    allergen_id:   Mapped[int] = mapped_column(ForeignKey("allergens.id"), nullable=False)
    confidence:    Mapped[str] = mapped_column(String(20), nullable=False, default="high")

    ingredient: Mapped["Ingredient"] = relationship("Ingredient", back_populates="ingredient_allergens")
    allergen:   Mapped["Allergen"]   = relationship("Allergen", back_populates="ingredient_allergens")


# ---------------------------------------------------------------
# RECIPE_ALLERGENS
# ---------------------------------------------------------------

class RecipeAllergen(Base):
    __tablename__ = "recipe_allergens"
    __table_args__ = (UniqueConstraint("recipe_id", "allergen_id"),)

    id:          Mapped[int] = mapped_column(Integer, primary_key=True)
    recipe_id:   Mapped[int] = mapped_column(ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False)
    allergen_id: Mapped[int] = mapped_column(ForeignKey("allergens.id"), nullable=False)

    recipe:  Mapped["Recipe"]  = relationship("Recipe", back_populates="recipe_allergens")
    allergen: Mapped["Allergen"] = relationship("Allergen", back_populates="recipe_allergens")


# ---------------------------------------------------------------
# DIETARY TAGS
# ---------------------------------------------------------------

class DietaryTag(Base):
    __tablename__ = "dietary_tags"

    id:           Mapped[int]           = mapped_column(Integer, primary_key=True)
    name:         Mapped[str]           = mapped_column(String(100), nullable=False, unique=True)
    display_name: Mapped[str]           = mapped_column(String(100), nullable=False)
    description:  Mapped[Optional[str]] = mapped_column(Text)

    recipe_dietary_tags: Mapped[list["RecipeDietaryTag"]] = relationship("RecipeDietaryTag", back_populates="dietary_tag")


# ---------------------------------------------------------------
# RECIPE_DIETARY_TAGS
# ---------------------------------------------------------------

class RecipeDietaryTag(Base):
    __tablename__ = "recipe_dietary_tags"
    __table_args__ = (UniqueConstraint("recipe_id", "dietary_tag_id"),)

    id:             Mapped[int] = mapped_column(Integer, primary_key=True)
    recipe_id:      Mapped[int] = mapped_column(ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False)
    dietary_tag_id: Mapped[int] = mapped_column(ForeignKey("dietary_tags.id"), nullable=False)

    recipe:      Mapped["Recipe"]     = relationship("Recipe", back_populates="recipe_dietary_tags")
    dietary_tag: Mapped["DietaryTag"] = relationship("DietaryTag", back_populates="recipe_dietary_tags")


# ---------------------------------------------------------------
# SCRAPE LOG
# ---------------------------------------------------------------

class ScrapeLog(Base):
    __tablename__ = "scrape_log"

    id:            Mapped[int]           = mapped_column(Integer, primary_key=True)
    source_id:     Mapped[int]           = mapped_column(ForeignKey("sources.id"), nullable=False)
    url:           Mapped[str]           = mapped_column(String(500), nullable=False)
    status:        Mapped[str]           = mapped_column(String(20), nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    scraped_at:    Mapped[datetime]      = mapped_column(nullable=False, default=lambda: datetime.now(timezone.utc))

    source: Mapped["Source"] = relationship("Source", back_populates="scrape_logs")