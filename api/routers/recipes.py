"""
routers/recipes.py

The core recipe endpoints:

GET /recipes                              — paginated list, filterable
GET /recipes?exclude_allergens=dairy,egg  — exclude recipes containing allergens
GET /recipes?dietary_tags=vegan           — filter by dietary tag
GET /recipes?cuisine=Italian              — filter by cuisine
GET /recipes/{id}                         — full recipe detail
GET /recipes/{id}/allergens               — allergen summary for one recipe
GET /recipes/{id}/dietary-tags            — dietary tag summary for one recipe
GET /cuisines                             — list all distinct cuisines in the DB
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from dependencies import get_db
from models import Allergen, DietaryTag, Recipe, RecipeAllergen, RecipeDietaryTag
from schemas.allergen import AllergenResponse
from schemas.dietary_tag import DietaryTagResponse
from schemas.recipe import PaginatedRecipes, RecipeDetail, RecipeSummary

router = APIRouter()


# ---------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------

def _get_recipe_or_404(recipe_id: int, db: Session) -> Recipe:
    """Fetches a recipe by id or raises a 404."""
    recipe = (
        db.query(Recipe)
        .options(
            joinedload(Recipe.recipe_allergens).joinedload(RecipeAllergen.allergen),
            joinedload(Recipe.recipe_dietary_tags).joinedload(RecipeDietaryTag.dietary_tag),
            joinedload(Recipe.recipe_ingredients),
        )
        .filter(Recipe.id == recipe_id)
        .first()
    )
    if not recipe:
        raise HTTPException(status_code=404, detail=f"Recipe {recipe_id} not found")
    return recipe


def _build_recipe_summary(recipe: Recipe) -> RecipeSummary:
    """Converts a Recipe ORM object into a RecipeSummary schema."""
    return RecipeSummary(
        id=recipe.id,
        title=recipe.title,
        url=recipe.url,
        cuisine=recipe.cuisine,
        prep_time=recipe.prep_time,
        cook_time=recipe.cook_time,
        total_time=recipe.total_time,
        servings=recipe.servings,
        image_url=recipe.image_url,
        allergens=[
            AllergenResponse(
                id=ra.allergen.id,
                name=ra.allergen.name,
                display_name=ra.allergen.display_name,
                description=ra.allergen.description,
            )
            for ra in recipe.recipe_allergens
        ],
        dietary_tags=[
            DietaryTagResponse(
                id=rdt.dietary_tag.id,
                name=rdt.dietary_tag.name,
                display_name=rdt.dietary_tag.display_name,
                description=rdt.dietary_tag.description,
            )
            for rdt in recipe.recipe_dietary_tags
        ],
    )


# ---------------------------------------------------------------
# GET /recipes
# ---------------------------------------------------------------

@router.get("", response_model=PaginatedRecipes)
def get_recipes(
    db:               Session = Depends(get_db),
    page:             int     = Query(default=1, ge=1, description="Page number"),
    size:             int     = Query(default=20, ge=1, le=100, description="Results per page"),
    cuisine:          str     | None = Query(default=None, description="Filter by cuisine"),
    exclude_allergens: str    | None = Query(default=None, description="Comma-separated allergen names to exclude"),
    dietary_tags:     str     | None = Query(default=None, description="Comma-separated dietary tags to filter by"),
    max_total_time:   int     | None = Query(default=None, description="Maximum total cook time in minutes"),
):
    """
    Returns a paginated list of recipes with optional filtering.

    Examples:
        GET /recipes
        GET /recipes?cuisine=Italian
        GET /recipes?exclude_allergens=dairy,egg
        GET /recipes?dietary_tags=vegan
        GET /recipes?exclude_allergens=peanuts&dietary_tags=vegetarian
        GET /recipes?max_total_time=30
    """
    query = (
        db.query(Recipe)
        .options(
            joinedload(Recipe.recipe_allergens).joinedload(RecipeAllergen.allergen),
            joinedload(Recipe.recipe_dietary_tags).joinedload(RecipeDietaryTag.dietary_tag),
        )
    )

    # Filter by cuisine (case-insensitive)
    if cuisine:
        query = query.filter(Recipe.cuisine.ilike(f"%{cuisine}%"))

    # Filter by max total time
    if max_total_time:
        query = query.filter(Recipe.total_time <= max_total_time)

    # Exclude recipes containing specified allergens
    if exclude_allergens:
        allergen_names = [a.strip().lower() for a in exclude_allergens.split(",")]
        allergen_ids = (
            db.query(Allergen.id)
            .filter(Allergen.name.in_(allergen_names))
            .scalar_subquery()
        )
        excluded_recipe_ids = (
            db.query(RecipeAllergen.recipe_id)
            .filter(RecipeAllergen.allergen_id.in_(allergen_ids))
            .scalar_subquery()
        )
        query = query.filter(Recipe.id.notin_(excluded_recipe_ids))

    # Filter to only recipes that have ALL specified dietary tags
    if dietary_tags:
        tag_names = [t.strip().lower() for t in dietary_tags.split(",")]
        for tag_name in tag_names:
            tag = db.query(DietaryTag).filter(DietaryTag.name == tag_name).first()
            if tag:
                tagged_recipe_ids = (
                    db.query(RecipeDietaryTag.recipe_id)
                    .filter(RecipeDietaryTag.dietary_tag_id == tag.id)
                    .scalar_subquery()
                )
                query = query.filter(Recipe.id.in_(tagged_recipe_ids))

    total = query.count()
    recipes = query.offset((page - 1) * size).limit(size).all()

    return PaginatedRecipes(
        total=total,
        page=page,
        size=size,
        results=[_build_recipe_summary(r) for r in recipes],
    )


# ---------------------------------------------------------------
# GET /recipes/{id}
# ---------------------------------------------------------------

@router.get("/{recipe_id}", response_model=RecipeDetail)
def get_recipe(recipe_id: int, db: Session = Depends(get_db)):
    """
    Returns full detail for a single recipe including
    ingredients, allergens, and dietary tags.
    """
    recipe = _get_recipe_or_404(recipe_id, db)

    return RecipeDetail(
        id=recipe.id,
        title=recipe.title,
        url=recipe.url,
        description=recipe.description,
        cuisine=recipe.cuisine,
        prep_time=recipe.prep_time,
        cook_time=recipe.cook_time,
        total_time=recipe.total_time,
        servings=recipe.servings,
        image_url=recipe.image_url,
        allergens=[
            AllergenResponse(
                id=ra.allergen.id,
                name=ra.allergen.name,
                display_name=ra.allergen.display_name,
                description=ra.allergen.description,
            )
            for ra in recipe.recipe_allergens
        ],
        dietary_tags=[
            DietaryTagResponse(
                id=rdt.dietary_tag.id,
                name=rdt.dietary_tag.name,
                display_name=rdt.dietary_tag.display_name,
                description=rdt.dietary_tag.description,
            )
            for rdt in recipe.recipe_dietary_tags
        ],
        ingredients=[
            {
                "ingredient": {
                    "id": ri.ingredient.id,
                    "raw_name": ri.ingredient.raw_name,
                    "normalised_name": ri.ingredient.normalised_name,
                },
                "quantity": ri.quantity,
                "unit": ri.unit,
                "preparation": ri.preparation,
            }
            for ri in recipe.recipe_ingredients
        ],
    )


# ---------------------------------------------------------------
# GET /recipes/{id}/allergens
# ---------------------------------------------------------------

@router.get("/{recipe_id}/allergens", response_model=list[AllergenResponse])
def get_recipe_allergens(recipe_id: int, db: Session = Depends(get_db)):
    """Returns just the allergens for a single recipe."""
    recipe = _get_recipe_or_404(recipe_id, db)
    return [
        AllergenResponse(
            id=ra.allergen.id,
            name=ra.allergen.name,
            display_name=ra.allergen.display_name,
            description=ra.allergen.description,
        )
        for ra in recipe.recipe_allergens
    ]


# ---------------------------------------------------------------
# GET /recipes/{id}/dietary-tags
# ---------------------------------------------------------------

@router.get("/{recipe_id}/dietary-tags", response_model=list[DietaryTagResponse])
def get_recipe_dietary_tags(recipe_id: int, db: Session = Depends(get_db)):
    """Returns just the dietary tags for a single recipe."""
    recipe = _get_recipe_or_404(recipe_id, db)
    return [
        DietaryTagResponse(
            id=rdt.dietary_tag.id,
            name=rdt.dietary_tag.name,
            display_name=rdt.dietary_tag.display_name,
            description=rdt.dietary_tag.description,
        )
        for rdt in recipe.recipe_dietary_tags
    ]


# ---------------------------------------------------------------
# GET /cuisines
# ---------------------------------------------------------------

@router.get("/meta/cuisines", response_model=list[str])
def get_cuisines(db: Session = Depends(get_db)):
    """
    Returns a sorted list of all distinct cuisines in the database.
    Useful for building filter dropdowns in a frontend.
    """
    results = (
        db.query(Recipe.cuisine)
        .filter(Recipe.cuisine.isnot(None))
        .distinct()
        .order_by(Recipe.cuisine)
        .all()
    )
    return [r.cuisine for r in results]