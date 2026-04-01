"""
tests/test_helpers.py

Unit tests for helper functions in main.py and the source parsers.

Covers:
  - normalise_ingredient() in main.py
  - _parse_duration() in bbc_good_food.py
  - _parse_servings() in bbc_good_food.py
  - _extract_cuisine() in bbc_good_food.py

These are all pure functions — no database or network needed.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from main import normalise_ingredient
from sources.bbc_good_food import (
    _parse_duration,
    _parse_servings,
    _extract_cuisine,
    _extract_image,
)


# ---------------------------------------------------------------
# normalise_ingredient
# ---------------------------------------------------------------

class TestNormaliseIngredient:
    def test_strips_leading_quantity(self):
        assert "spaghetti" in normalise_ingredient("200g dried spaghetti")

    def test_strips_count_and_size(self):
        result = normalise_ingredient("2 large eggs")
        assert "egg" in result
        assert "2" not in result
        assert "large" not in result

    def test_strips_tablespoon(self):
        result = normalise_ingredient("3 tbsp olive oil")
        assert "olive oil" in result
        assert "tbsp" not in result
        assert "3" not in result

    def test_strips_fraction(self):
        result = normalise_ingredient("1/2 tsp fine sea salt")
        assert "salt" in result
        assert "1/2" not in result
        assert "tsp" not in result

    def test_strips_preparation_notes(self):
        result = normalise_ingredient("100g parmesan, finely grated")
        assert "parmesan" in result
        assert "finely" not in result
        assert "grated" not in result

    def test_handles_plain_ingredient(self):
        """an ingredient with no quantity should pass through cleanly"""
        result = normalise_ingredient("garlic")
        assert result == "garlic"

    def test_handles_multiword_ingredient(self):
        result = normalise_ingredient("olive oil")
        assert "olive oil" in result

    def test_lowercase_output(self):
        result = normalise_ingredient("200g Parmesan")
        assert result == result.lower()

    def test_no_double_spaces(self):
        result = normalise_ingredient("2 large free-range eggs")
        assert "  " not in result

    def test_strips_ml_unit(self):
        result = normalise_ingredient("100ml double cream")
        assert "double cream" in result
        assert "ml" not in result
        assert "100" not in result


# ---------------------------------------------------------------
# _parse_duration
# ---------------------------------------------------------------

class TestParseDuration:
    def test_minutes_only(self):
        assert _parse_duration("PT30M") == 30

    def test_hours_only(self):
        assert _parse_duration("PT1H") == 60

    def test_hours_and_minutes(self):
        assert _parse_duration("PT1H30M") == 90

    def test_two_hours(self):
        assert _parse_duration("PT2H") == 120

    def test_two_hours_fifteen_minutes(self):
        assert _parse_duration("PT2H15M") == 135

    def test_zero_duration(self):
        assert _parse_duration("PT0M") == 0

    def test_none_returns_none(self):
        assert _parse_duration(None) is None

    def test_empty_string_returns_none(self):
        assert _parse_duration("") is None

    def test_malformed_string_returns_none(self):
        assert _parse_duration("30 minutes") is None


# ---------------------------------------------------------------
# _parse_servings
# ---------------------------------------------------------------

class TestParseServings:
    def test_plain_number(self):
        assert _parse_servings("4") == 4

    def test_servings_suffix(self):
        assert _parse_servings("4 servings") == 4

    def test_serves_prefix(self):
        assert _parse_servings("Serves 6") == 6

    def test_list_input(self):
        assert _parse_servings(["4 servings"]) == 4

    def test_none_returns_none(self):
        assert _parse_servings(None) is None

    def test_empty_list_returns_none(self):
        assert _parse_servings([]) is None

    def test_makes_prefix(self):
        assert _parse_servings("Makes 12") == 12


# ---------------------------------------------------------------
# _extract_cuisine
# ---------------------------------------------------------------

class TestExtractCuisine:
    def test_simple_string(self):
        assert _extract_cuisine("Italian") == "Italian"

    def test_list_takes_first(self):
        assert _extract_cuisine(["Italian", "Mediterranean"]) == "Italian"

    def test_title_case_applied(self):
        assert _extract_cuisine("italian") == "Italian"

    def test_none_returns_none(self):
        assert _extract_cuisine(None) is None

    def test_empty_string_returns_none(self):
        assert _extract_cuisine("") is None

    def test_empty_list_returns_none(self):
        assert _extract_cuisine([]) is None


# ---------------------------------------------------------------
# _extract_image
# ---------------------------------------------------------------

class TestExtractImage:
    def test_string_url(self):
        assert _extract_image("https://example.com/img.jpg") == "https://example.com/img.jpg"

    def test_dict_with_url_key(self):
        assert _extract_image({"url": "https://example.com/img.jpg"}) == "https://example.com/img.jpg"

    def test_list_takes_first(self):
        assert _extract_image(["https://example.com/img.jpg", "https://example.com/img2.jpg"]) == "https://example.com/img.jpg"

    def test_none_returns_none(self):
        assert _extract_image(None) is None

    def test_empty_list_returns_none(self):
        assert _extract_image([]) is None