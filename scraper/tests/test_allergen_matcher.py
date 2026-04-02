"""
tests/test_allergen_matcher.py

Unit tests for allergen_matcher.py

Tests are grouped into four sections:
  1. Positive matches  — ingredients that SHOULD trigger an allergen
  2. Negative matches  — ingredients that should NOT trigger anything
  3. Exception rules   — ingredients that look like an allergen but aren't
  4. Raw egg detection — is_raw_egg() specific tests

No database or network connection required — pure function testing.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from allergen_matcher import match_allergens, is_raw_egg


def allergen_names(ingredient: str) -> list[str]:
    """Helper — returns just the allergen name strings for an ingredient."""
    return [m.allergen_name for m in match_allergens(ingredient)]


# ---------------------------------------------------------------
# POSITIVE MATCHES — should detect the allergen
# ---------------------------------------------------------------

class TestPeanutDetection:
    def test_peanut_butter(self):
        assert "peanuts" in allergen_names("peanut butter")

    def test_peanut_oil(self):
        assert "peanuts" in allergen_names("peanut oil")

    def test_groundnut_oil(self):
        assert "peanuts" in allergen_names("groundnut oil")

    def test_satay_sauce(self):
        assert "peanuts" in allergen_names("satay sauce")

    def test_monkey_nuts(self):
        assert "peanuts" in allergen_names("monkey nuts")


class TestTreeNutDetection:
    def test_almond(self):
        assert "tree_nuts" in allergen_names("almond")

    def test_almond_flakes(self):
        assert "tree_nuts" in allergen_names("flaked almonds")

    def test_cashew(self):
        assert "tree_nuts" in allergen_names("cashew nuts")

    def test_walnut(self):
        assert "tree_nuts" in allergen_names("walnut")

    def test_pistachio(self):
        assert "tree_nuts" in allergen_names("pistachio")

    def test_hazelnut(self):
        assert "tree_nuts" in allergen_names("hazelnut")

    def test_marzipan(self):
        assert "tree_nuts" in allergen_names("marzipan")

    def test_frangipane(self):
        assert "tree_nuts" in allergen_names("frangipane")

    def test_coconut(self):
        assert "tree_nuts" in allergen_names("coconut")

    def test_praline(self):
        assert "tree_nuts" in allergen_names("praline")


class TestDairyDetection:
    def test_milk(self):
        assert "dairy" in allergen_names("whole milk")

    def test_double_cream(self):
        assert "dairy" in allergen_names("double cream")

    def test_butter(self):
        assert "dairy" in allergen_names("butter")

    def test_cheddar(self):
        assert "dairy" in allergen_names("cheddar cheese")

    def test_parmesan(self):
        assert "dairy" in allergen_names("parmesan")

    def test_yoghurt(self):
        assert "dairy" in allergen_names("greek yoghurt")

    def test_creme_fraiche(self):
        assert "dairy" in allergen_names("creme fraiche")

    def test_mozzarella(self):
        assert "dairy" in allergen_names("mozzarella")

    def test_ghee(self):
        assert "dairy" in allergen_names("ghee")

    def test_buttermilk(self):
        assert "dairy" in allergen_names("buttermilk")

    def test_condensed_milk(self):
        assert "dairy" in allergen_names("condensed milk")

    def test_whey(self):
        assert "dairy" in allergen_names("whey protein")

    def test_mascarpone(self):
        assert "dairy" in allergen_names("mascarpone")

    def test_feta(self):
        assert "dairy" in allergen_names("feta cheese")


class TestEggDetection:
    def test_egg(self):
        assert "egg" in allergen_names("egg")

    def test_eggs(self):
        assert "egg" in allergen_names("eggs")

    def test_free_range_eggs(self):
        assert "egg" in allergen_names("free range eggs")

    def test_egg_yolk(self):
        assert "egg" in allergen_names("egg yolk")

    def test_egg_white(self):
        assert "egg" in allergen_names("egg white")

    def test_mayonnaise(self):
        assert "egg" in allergen_names("mayonnaise")

    def test_hollandaise(self):
        assert "egg" in allergen_names("hollandaise sauce")

    def test_meringue(self):
        assert "egg" in allergen_names("meringue")

    def test_fresh_pasta(self):
        assert "egg" in allergen_names("fresh pasta")


# ---------------------------------------------------------------
# NEGATIVE MATCHES — should not trigger any allergen
# ---------------------------------------------------------------

class TestNoAllergenDetected:
    def test_olive_oil(self):
        assert allergen_names("olive oil") == []

    def test_garlic(self):
        assert allergen_names("garlic") == []

    def test_salt(self):
        assert allergen_names("salt") == []

    def test_tomato(self):
        assert allergen_names("tomato") == []

    def test_chicken(self):
        # chicken is not an allergen we track
        assert allergen_names("chicken breast") == []

    def test_rice(self):
        assert allergen_names("basmati rice") == []

    def test_lemon(self):
        assert allergen_names("lemon juice") == []

    def test_onion(self):
        assert allergen_names("onion") == []


# ---------------------------------------------------------------
# EXCEPTION RULES — look like allergens but aren't
# ---------------------------------------------------------------

class TestExceptionRules:
    def test_coconut_milk_not_dairy(self):
        """coconut milk contains 'milk' but is not dairy"""
        assert "dairy" not in allergen_names("coconut milk")

    def test_almond_milk_not_dairy(self):
        assert "dairy" not in allergen_names("almond milk")

    def test_oat_milk_not_dairy(self):
        assert "dairy" not in allergen_names("oat milk")

    def test_oat_cream_not_dairy(self):
        assert "dairy" not in allergen_names("oat cream")

    def test_coconut_cream_not_dairy(self):
        assert "dairy" not in allergen_names("coconut cream")

    def test_coconut_butter_not_dairy(self):
        assert "dairy" not in allergen_names("coconut butter")

    def test_cocoa_butter_not_dairy(self):
        assert "dairy" not in allergen_names("cocoa butter")

    def test_eggplant_not_egg(self):
        """eggplant contains 'egg' but is not an egg allergen"""
        assert "egg" not in allergen_names("eggplant")

    def test_water_chestnut_not_tree_nut(self):
        """water chestnut contains 'chestnut' but is not a tree nut"""
        assert "tree_nuts" not in allergen_names("water chestnut")

    def test_nutmeg_not_tree_nut(self):
        assert "tree_nuts" not in allergen_names("nutmeg")

    def test_peanut_butter_not_tree_nut(self):
        """peanut butter should flag peanuts but NOT tree_nuts"""
        names = allergen_names("peanut butter")
        assert "peanuts" in names
        assert "tree_nuts" not in names

    def test_doughnut_not_tree_nut(self):
        assert "tree_nuts" not in allergen_names("doughnut")


# ---------------------------------------------------------------
# CONFIDENCE LEVELS
# ---------------------------------------------------------------

class TestConfidenceLevels:
    def test_high_confidence_returned(self):
        matches = match_allergens("double cream")
        assert len(matches) == 1
        assert matches[0].confidence == "high"

    def test_multiple_allergens_same_ingredient(self):
        """fresh pasta contains both egg and potentially gluten
        but we only track egg — confirm just egg is returned"""
        names = allergen_names("fresh pasta")
        assert "egg" in names


# ---------------------------------------------------------------
# RAW EGG DETECTION
# ---------------------------------------------------------------

class TestRawEggDetection:
    def test_mayonnaise_is_raw_egg(self):
        assert is_raw_egg("mayonnaise") is True

    def test_hollandaise_is_raw_egg(self):
        assert is_raw_egg("hollandaise sauce") is True

    def test_aioli_is_raw_egg(self):
        assert is_raw_egg("aioli") is True

    def test_egg_yolk_is_raw_egg(self):
        assert is_raw_egg("egg yolk") is True

    def test_caesar_dressing_is_raw_egg(self):
        assert is_raw_egg("caesar dressing") is True

    def test_whole_egg_not_raw_egg(self):
        """a whole egg in a recipe is not necessarily raw"""
        assert is_raw_egg("egg") is False

    def test_scrambled_egg_not_raw_egg(self):
        assert is_raw_egg("scrambled egg") is False

    def test_olive_oil_not_raw_egg(self):
        assert is_raw_egg("olive oil") is False