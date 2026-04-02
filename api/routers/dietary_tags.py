"""
routers/dietary_tags.py

GET /dietary-tags — returns the full list of dietary tags.

Same pattern as allergens — reference data that never
changes at runtime. Used by frontend filter UIs.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from dependencies import get_db
from models import DietaryTag
from schemas.dietary_tag import DietaryTagResponse

router = APIRouter()


@router.get("", response_model=list[DietaryTagResponse])
def get_dietary_tags(db: Session = Depends(get_db)):
    """
    Returns all dietary tags.

    Example response:
        [
            {"id": 1, "name": "vegetarian", "display_name": "Vegetarian", "description": "..."},
            {"id": 2, "name": "vegan", "display_name": "Vegan", "description": "..."},
            ...
        ]
    """
    return db.query(DietaryTag).order_by(DietaryTag.display_name).all()