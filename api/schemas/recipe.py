"""
schemas/recipe.py

Pydantic models defining the shape of recipe data
returned by the API.

Two levels of detail:
  - RecipeSummary  — used in list responses (GET /recipes)
                     lightweight, no nested ingredients
  - RecipeDetail   — used in single recipe responses (GET /recipes/{id})
                     full detail with allergens, dietary tags, ingredients
"""

from pydantic import BaseModel

from schemas.allergen import AllergenResponse
from schemas.dietary_tag import DietaryTagResponse


# ---------------------------------------------------------------
# INGREDIENT — nested inside RecipeDetail
# ---------------------------------------------------------------

class IngredientResponse(BaseModel):
    id:              int
    raw_name:        str
    normalised_name: str

    model_config = {"from_attributes": True}


class RecipeIngredientResponse(BaseModel):
    ingredient:  IngredientResponse
    quantity:    str | None
    unit:        str | None
    preparation: str | None

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------
# RECIPE SUMMARY — returned in list endpoints
# Lightweight — no nested ingredients to keep responses fast
# ---------------------------------------------------------------

class RecipeSummary(BaseModel):
    id:          int
    title:       str
    url:         str
    cuisine:     str | None
    prep_time:   int | None
    cook_time:   int | None
    total_time:  int | None
    servings:    int | None
    image_url:   str | None
    allergens:   list[AllergenResponse]
    dietary_tags: list[DietaryTagResponse]

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------
# RECIPE DETAIL — returned for single recipe endpoints
# Full detail including ingredients
# ---------------------------------------------------------------

class RecipeDetail(BaseModel):
    id:           int
    title:        str
    url:          str
    description:  str | None
    cuisine:      str | None
    prep_time:    int | None
    cook_time:    int | None
    total_time:   int | None
    servings:     int | None
    image_url:    str | None
    allergens:    list[AllergenResponse]
    dietary_tags: list[DietaryTagResponse]
    ingredients:  list[RecipeIngredientResponse]

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------
# PAGINATED RECIPE LIST — wraps RecipeSummary for list endpoints
# ---------------------------------------------------------------

class PaginatedRecipes(BaseModel):
    total:   int
    page:    int
    size:    int
    results: list[RecipeSummary]