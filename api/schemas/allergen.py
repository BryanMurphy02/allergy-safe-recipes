"""
schemas/allergen.py

Pydantic models defining the shape of allergen data
returned by the API.

Pydantic validates and serialises the data — if a field
is missing or the wrong type, FastAPI returns a clear
error rather than crashing or returning malformed JSON.
"""

from pydantic import BaseModel


class AllergenResponse(BaseModel):
    id:           int
    name:         str
    display_name: str
    description:  str | None

    model_config = {"from_attributes": True}