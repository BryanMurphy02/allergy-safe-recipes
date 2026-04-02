"""
routers/allergens.py

GET /allergens — returns the full list of tracked allergens.

This is a reference endpoint — the data never changes at
runtime since allergens are seeded at schema creation time.
Useful for frontend filter UIs that need to know what
allergen options exist.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from dependencies import get_db
from models import Allergen
from schemas.allergen import AllergenResponse

router = APIRouter()


@router.get("", response_model=list[AllergenResponse])
def get_allergens(db: Session = Depends(get_db)):
    """
    Returns all 4 tracked allergens.

    Example response:
        [
            {"id": 1, "name": "peanuts", "display_name": "Peanuts", "description": "..."},
            {"id": 2, "name": "tree_nuts", "display_name": "Tree Nuts", "description": "..."},
            ...
        ]
    """
    return db.query(Allergen).order_by(Allergen.display_name).all()