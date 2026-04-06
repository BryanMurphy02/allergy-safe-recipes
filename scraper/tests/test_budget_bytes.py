"""
tests/test_budget_bytes.py

Unit tests for:
  - Budget Bytes cuisine extraction
  - Price stripping in normalise_ingredient()
  - Non-recipe URL handling

No network calls — pure function testing.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import normalise_ingredient
from sources.budget_bytes import _extract_cuisine_budget_bytes


# ---------------------------------------------------------------
# PRICE STRIPPING IN normalise_ingredient()
# ---------------------------------------------------------------

class TestPriceStripping:
    def test_strips_price_annotation(self):
        result = normalise_ingredient("4 Roma tomatoes ($1.35)")
        assert "($1.35)" not in result
        assert "$" not in result

    def test_strips_price_from_oil(self):
        result = normalise_ingredient("2 Tbsp olive oil ($0.32)")
        assert "$" not in result
        assert "olive oil" in result

    def test_strips_price_from_butter(self):
        result = normalise_ingredient("2 Tbsp butter, room temperature ($0.36)")
        assert "$" not in result
        assert "butter" in result

    def test_strips_price_with_zero_cents(self):
        result = normalise_ingredient("1/2 tsp salt ($0.02)")
        assert "$" not in result

    def test_ingredient_without_price_unaffected(self):
        """Ingredients without prices should still normalise correctly."""
        result = normalise_ingredient("200g dried spaghetti")
        assert "spaghetti" in result
        assert "$" not in result

    def test_strips_price_and_quantity(self):
        """Both price and quantity should be stripped."""
        result = normalise_ingredient("1 cup couscous ($0.79)")
        assert "couscous" in result
        assert "$" not in result
        assert "cup" not in result


# ---------------------------------------------------------------
# CUISINE EXTRACTION
# ---------------------------------------------------------------

class TestExtractCuisineBudgetBytes:
    def test_strips_recipes_suffix(self):
        result = _extract_cuisine_budget_bytes({"recipeCategory": "Dinner Recipes"})
        assert result == "Dinner"

    def test_strips_recipe_singular_suffix(self):
        result = _extract_cuisine_budget_bytes({"recipeCategory": "Chicken Recipe"})
        assert "Recipe" not in result

    def test_strips_inspired_suffix(self):
        result = _extract_cuisine_budget_bytes({"recipeCategory": "Asian Inspired Recipes"})
        assert "Inspired" not in result
        assert "Recipes" not in result

    def test_uses_recipe_cuisine_first(self):
        """recipeCuisine takes priority over recipeCategory."""
        result = _extract_cuisine_budget_bytes({
            "recipeCuisine": "Italian",
            "recipeCategory": "Dinner Recipes",
        })
        assert result == "Italian"

    def test_falls_back_to_category(self):
        """Falls back to recipeCategory when recipeCuisine absent."""
        result = _extract_cuisine_budget_bytes({
            "recipeCategory": "Mexican Recipes",
        })
        assert result is not None
        assert "Mexican" in result

    def test_returns_none_when_no_cuisine_data(self):
        result = _extract_cuisine_budget_bytes({})
        assert result is None

    def test_handles_list_category(self):
        """recipeCategory can be a list — should take first value."""
        result = _extract_cuisine_budget_bytes({
            "recipeCategory": ["Dinner Recipes", "Meal Prep"],
        })
        assert result is not None

    def test_title_case_applied(self):
        result = _extract_cuisine_budget_bytes({"recipeCuisine": "italian"})
        assert result == "Italian"


# ---------------------------------------------------------------
# NON-RECIPE URL HANDLING
# ---------------------------------------------------------------

class TestNonRecipeHandling:
    def test_parse_recipe_returns_none_for_no_json_ld(self):
        """
        Simulates a non-recipe post by mocking the HTTP response
        to return HTML with no Recipe JSON-LD block.
        """
        from unittest.mock import patch, MagicMock
        from sources.budget_bytes import parse_recipe

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html><body><p>Not a recipe</p></body></html>"
        mock_response.raise_for_status = MagicMock()

        with patch("sources.budget_bytes.requests.get", return_value=mock_response):
            result = parse_recipe("https://www.budgetbytes.com/some-blog-post/")

        assert result is None

    def test_parse_recipe_returns_none_on_request_failure(self):
        """Confirms network errors return None rather than crashing."""
        from unittest.mock import patch
        from sources.budget_bytes import parse_recipe
        import requests

        with patch(
            "sources.budget_bytes.requests.get",
            side_effect=requests.RequestException("timeout")
        ):
            result = parse_recipe("https://www.budgetbytes.com/some-recipe/")

        assert result is None