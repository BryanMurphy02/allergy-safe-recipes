"""
allergen_matcher.py

Takes a normalised ingredient name and returns which of the
4 tracked allergens it contains, along with a confidence level.

Matching works in two passes:
  1. Exact / substring match against a known lookup table (high confidence)
  2. If nothing found, returns an empty list (no guess)

The lookup table is intentionally conservative — it is better to
miss an allergen than to falsely flag a safe recipe.
"""

from dataclasses import dataclass


@dataclass
class AllergenMatch:
    allergen_name: str   # matches allergens.name in the DB
    confidence: str      # 'high', 'medium', or 'low'


# ---------------------------------------------------------------
# LOOKUP TABLE
# Keys are allergen names matching allergens.name in the DB.
# Values are lists of substrings — if any appear in the
# normalised ingredient name, the allergen is flagged.
# Order within each list does not matter.
# ---------------------------------------------------------------

ALLERGEN_KEYWORDS: dict[str, list[str]] = {

    "peanuts": [
        "peanut",
        "groundnut",
        "monkey nut",
        "arachis",          # arachis oil = peanut oil
        "satay",            # satay sauce is almost always peanut-based
        "peanut butter",
        "peanut oil",
    ],

    "tree_nuts": [
        "almond",
        "cashew",
        "walnut",
        "pecan",
        "pistachio",
        "hazelnut",
        "macadamia",
        "brazil nut",
        "pine nut",
        "chestnut",
        "coconut",          # classified as tree nut by FDA
        "praline",          # typically hazelnut or almond based
        "marzipan",         # almond based
        "frangipane",       # almond based
        "nougat",           # typically contains almonds
        "nut oil",
        "nut butter",
    ],

    "dairy": [
        "milk",
        "cream",
        "butter",
        "cheese",
        "yoghurt",
        "yogurt",
        "creme fraiche",
        "crème fraîche",
        "sour cream",
        "whipping cream",
        "double cream",
        "single cream",
        "clotted cream",
        "half and half",
        "ghee",
        "buttermilk",
        "condensed milk",
        "evaporated milk",
        "skimmed milk",
        "whole milk",
        "full fat milk",
        "milk powder",
        "whey",
        "casein",
        "lactose",
        "mascarpone",
        "ricotta",
        "mozzarella",
        "parmesan",
        "parmigiano",
        "pecorino",
        "brie",
        "camembert",
        "cheddar",
        "gruyere",
        "gruyère",
        "feta",
        "halloumi",
        "quark",
        "fromage frais",
    ],

    "egg": [
        "egg",
        "eggs",
        "egg yolk",
        "egg white",
        "egg wash",
        "beaten egg",
        "whole egg",
        "free range egg",
        "mayonnaise",       # contains raw egg
        "mayo",
        "hollandaise",      # egg yolk based
        "aioli",            # egg yolk based
        "meringue",         # egg white based
        "albumen",          # egg white protein
        "egg noodle",
        "egg pasta",
        "fresh pasta",      # typically contains egg
    ],

}

# Ingredients that look like they contain an allergen but don't.
# Checked before the main lookup — if matched here, the allergen
# is NOT flagged regardless of keyword matches.
EXCEPTIONS: dict[str, list[str]] = {
    "dairy": [
        "coconut milk",     # not dairy despite "milk"
        "almond milk",
        "oat milk",
        "soy milk",
        "rice milk",
        "oat cream",
        "coconut cream",
        "coconut butter",   # not dairy butter
        "peanut butter",    # not dairy butter
        "nut butter",       # not dairy butter
        "cocoa butter",     # not dairy butter
        "shea butter",
    ],
    "egg": [
        "eggplant",         # not an egg
        "egg fruit",
    ],
    "tree_nuts": [
        "water chestnut",   # not a tree nut
        "nutmeg",           # not a tree nut allergen
        "doughnut",
        "donut",
        "peanut",           # peanut is its own allergen, not tree nut
    ],
}


def match_allergens(normalised_name: str) -> list[AllergenMatch]:
    """
    Given a normalised ingredient name, return a list of
    AllergenMatch objects for any allergens detected.

    Example:
        match_allergens("double cream")
        → [AllergenMatch(allergen_name='dairy', confidence='high')]

        match_allergens("coconut milk")
        → []   ← exception rule prevents dairy being flagged
    """
    name = normalised_name.lower().strip()
    results = []

    for allergen, keywords in ALLERGEN_KEYWORDS.items():

        # Check exceptions first — if the ingredient is in the
        # exception list for this allergen, skip it entirely.
        exceptions = EXCEPTIONS.get(allergen, [])
        if any(exc in name for exc in exceptions):
            continue

        # Check keywords — if any keyword appears in the ingredient
        # name, flag this allergen with high confidence.
        if any(keyword in name for keyword in keywords):
            results.append(
                AllergenMatch(
                    allergen_name=allergen,
                    confidence="high",
                )
            )

    return results


def is_raw_egg(normalised_name: str) -> bool:
    """
    Returns True if the ingredient suggests raw or very lightly
    cooked egg — used for the contains_raw_egg dietary tag.

    Distinct from the egg allergen check: all these recipes
    contain egg, but only some use it raw.
    """
    name = normalised_name.lower().strip()
    raw_egg_indicators = [
        "mayonnaise",
        "mayo",
        "hollandaise",
        "aioli",
        "caesar dressing",
        "raw egg",
        "egg yolk",     # often used raw in dressings, pasta, desserts
    ]
    return any(indicator in name for indicator in raw_egg_indicators)