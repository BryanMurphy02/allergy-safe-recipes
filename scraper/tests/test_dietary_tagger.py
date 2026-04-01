"""
tests/test_dietary_tagger.py

Unit tests for dietary_tagger.py

Tests cover all four dietary tags:
  - vegetarian
  - vegan
  - gluten_free
  - contains_raw_egg

Each test passes a list of normalised ingredient names — exactly
what main.py would pass after running normalise_ingredient().
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from dietary_tagger import tag_recipe


# ---------------------------------------------------------------
# VEGETARIAN
# ---------------------------------------------------------------

class TestVegetarian:
    def test_simple_vegetarian_recipe(self):
        ingredients = ["pasta", "tomato", "garlic", "olive oil", "basil"]
        assert "vegetarian" in tag_recipe(ingredients)

    def test_recipe_with_chicken_not_vegetarian(self):
        ingredients = ["chicken breast", "lemon", "garlic", "olive oil"]
        assert "vegetarian" not in tag_recipe(ingredients)

    def test_recipe_with_beef_not_vegetarian(self):
        ingredients = ["beef mince", "onion", "tomato", "garlic"]
        assert "vegetarian" not in tag_recipe(ingredients)

    def test_recipe_with_bacon_not_vegetarian(self):
        ingredients = ["pasta", "bacon", "egg", "parmesan"]
        assert "vegetarian" not in tag_recipe(ingredients)

    def test_recipe_with_fish_not_vegetarian(self):
        """fish disqualifies vegetarian"""
        ingredients = ["salmon fillet", "lemon", "dill", "butter"]
        assert "vegetarian" not in tag_recipe(ingredients)

    def test_recipe_with_anchovies_not_vegetarian(self):
        ingredients = ["pizza dough", "tomato", "anchovies", "mozzarella"]
        assert "vegetarian" not in tag_recipe(ingredients)

    def test_recipe_with_worcestershire_not_vegetarian(self):
        """worcestershire sauce contains anchovies"""
        ingredients = ["steak", "worcestershire sauce", "butter"]
        assert "vegetarian" not in tag_recipe(ingredients)

    def test_dairy_recipe_is_vegetarian(self):
        """dairy is fine for vegetarian"""
        ingredients = ["pasta", "double cream", "parmesan", "garlic"]
        assert "vegetarian" in tag_recipe(ingredients)

    def test_egg_recipe_is_vegetarian(self):
        """eggs are fine for vegetarian"""
        ingredients = ["eggs", "butter", "salt", "chives"]
        assert "vegetarian" in tag_recipe(ingredients)


# ---------------------------------------------------------------
# VEGAN
# ---------------------------------------------------------------

class TestVegan:
    def test_simple_vegan_recipe(self):
        ingredients = ["chickpeas", "tomato", "garlic", "olive oil", "cumin"]
        assert "vegan" in tag_recipe(ingredients)

    def test_vegan_implies_vegetarian(self):
        """if vegan, must also be vegetarian"""
        ingredients = ["chickpeas", "tomato", "garlic", "olive oil"]
        tags = tag_recipe(ingredients)
        assert "vegan" in tags
        assert "vegetarian" in tags

    def test_recipe_with_dairy_not_vegan(self):
        ingredients = ["pasta", "double cream", "parmesan"]
        assert "vegan" not in tag_recipe(ingredients)

    def test_recipe_with_egg_not_vegan(self):
        ingredients = ["flour", "eggs", "sugar", "vanilla"]
        assert "vegan" not in tag_recipe(ingredients)

    def test_recipe_with_honey_not_vegan(self):
        ingredients = ["oats", "honey", "nuts", "dried fruit"]
        assert "vegan" not in tag_recipe(ingredients)

    def test_recipe_with_butter_not_vegan(self):
        ingredients = ["toast", "butter", "jam"]
        assert "vegan" not in tag_recipe(ingredients)

    def test_recipe_with_chicken_not_vegan(self):
        ingredients = ["chicken", "garlic", "olive oil"]
        assert "vegan" not in tag_recipe(ingredients)

    def test_coconut_milk_is_vegan(self):
        """coconut milk should not disqualify vegan"""
        ingredients = ["coconut milk", "chickpeas", "spinach", "garlic"]
        assert "vegan" in tag_recipe(ingredients)


# ---------------------------------------------------------------
# GLUTEN FREE
# ---------------------------------------------------------------

class TestGlutenFree:
    def test_simple_gluten_free_recipe(self):
        ingredients = ["chicken", "lemon", "garlic", "olive oil", "rosemary"]
        assert "gluten_free" in tag_recipe(ingredients)

    def test_recipe_with_flour_not_gluten_free(self):
        ingredients = ["flour", "butter", "sugar", "eggs"]
        assert "gluten_free" not in tag_recipe(ingredients)

    def test_recipe_with_pasta_not_gluten_free(self):
        ingredients = ["spaghetti", "eggs", "pancetta", "parmesan"]
        assert "gluten_free" not in tag_recipe(ingredients)

    def test_recipe_with_bread_not_gluten_free(self):
        ingredients = ["bread", "butter", "cheese"]
        assert "gluten_free" not in tag_recipe(ingredients)

    def test_recipe_with_soy_sauce_not_gluten_free(self):
        """most soy sauce contains wheat"""
        ingredients = ["tofu", "soy sauce", "ginger", "garlic"]
        assert "gluten_free" not in tag_recipe(ingredients)

    def test_recipe_with_couscous_not_gluten_free(self):
        ingredients = ["couscous", "chickpeas", "tomato", "cucumber"]
        assert "gluten_free" not in tag_recipe(ingredients)

    def test_rice_flour_is_gluten_free(self):
        """rice flour is a gluten-free exception"""
        ingredients = ["rice flour", "coconut milk", "sugar", "eggs"]
        assert "gluten_free" in tag_recipe(ingredients)

    def test_tamari_is_gluten_free(self):
        """tamari is gluten-free soy sauce"""
        ingredients = ["tofu", "tamari", "ginger", "sesame oil"]
        assert "gluten_free" in tag_recipe(ingredients)

    def test_buckwheat_is_gluten_free(self):
        """buckwheat is confusingly gluten-free despite the name"""
        ingredients = ["buckwheat flour", "eggs", "milk"]
        assert "gluten_free" in tag_recipe(ingredients)

    def test_corn_tortilla_is_gluten_free(self):
        ingredients = ["corn tortilla", "black beans", "avocado", "lime"]
        assert "gluten_free" in tag_recipe(ingredients)

    def test_rice_pasta_is_gluten_free(self):
        ingredients = ["rice pasta", "tomato", "garlic", "olive oil"]
        assert "gluten_free" in tag_recipe(ingredients)


# ---------------------------------------------------------------
# CONTAINS RAW EGG
# ---------------------------------------------------------------

class TestContainsRawEgg:
    def test_mayonnaise_flags_raw_egg(self):
        ingredients = ["chicken", "mayonnaise", "lettuce", "bread"]
        assert "contains_raw_egg" in tag_recipe(ingredients)

    def test_hollandaise_flags_raw_egg(self):
        ingredients = ["eggs benedict", "hollandaise sauce", "ham"]
        assert "contains_raw_egg" in tag_recipe(ingredients)

    def test_aioli_flags_raw_egg(self):
        ingredients = ["chips", "aioli", "lemon"]
        assert "contains_raw_egg" in tag_recipe(ingredients)

    def test_egg_yolk_flags_raw_egg(self):
        ingredients = ["spaghetti", "egg yolk", "pancetta", "parmesan"]
        assert "contains_raw_egg" in tag_recipe(ingredients)

    def test_scrambled_eggs_no_raw_egg_flag(self):
        """cooked egg should not flag contains_raw_egg"""
        ingredients = ["eggs", "butter", "salt", "chives"]
        assert "contains_raw_egg" not in tag_recipe(ingredients)

    def test_raw_egg_independent_of_other_tags(self):
        """contains_raw_egg can appear alongside other tags"""
        ingredients = ["spaghetti", "egg yolk", "parmesan", "black pepper"]
        tags = tag_recipe(ingredients)
        assert "contains_raw_egg" in tags
        assert "vegetarian" in tags      # no meat
        assert "vegan" not in tags       # has egg and dairy


# ---------------------------------------------------------------
# COMBINED TAG SCENARIOS
# ---------------------------------------------------------------

class TestCombinedScenarios:
    def test_carbonara_tags(self):
        """carbonara: vegetarian, contains raw egg, not vegan, not gluten free"""
        ingredients = ["spaghetti", "egg yolk", "pancetta", "parmesan", "black pepper"]
        tags = tag_recipe(ingredients)
        assert "vegetarian" not in tags     # pancetta is meat
        assert "vegan" not in tags
        assert "gluten_free" not in tags    # spaghetti has gluten
        assert "contains_raw_egg" in tags

    def test_lentil_soup_tags(self):
        """lentil soup: vegetarian, vegan, gluten free"""
        ingredients = ["lentils", "tomato", "onion", "garlic", "cumin", "olive oil"]
        tags = tag_recipe(ingredients)
        assert "vegetarian" in tags
        assert "vegan" in tags
        assert "gluten_free" in tags
        assert "contains_raw_egg" not in tags

    def test_empty_ingredients_returns_all_positive_tags(self):
        """a recipe with no ingredients is technically vegan and gluten free"""
        tags = tag_recipe([])
        assert "vegetarian" in tags
        assert "vegan" in tags
        assert "gluten_free" in tags