"""
schemas/dietary_tag.py

Pydantic models defining the shape of dietary tag data
returned by the API.
"""

from pydantic import BaseModel


class DietaryTagResponse(BaseModel):
    id:           int
    name:         str
    display_name: str
    description:  str | None

    model_config = {"from_attributes": True}