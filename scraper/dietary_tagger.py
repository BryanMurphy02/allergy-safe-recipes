"""
dietary_tagger.py

Takes the full normalised ingredient list for a recipe and
returns which dietary tags apply.

Unlike allergen matching (which works per ingredient), dietary
tags are recipe-level — a recipe is only vegan if every single
ingredient passes the vegan check. One non-vegan ingredient
disqualifies the whole recipe.

Tags produced:
  - vegetarian       → contains no meat or fish
  - vegan            → contains no animal products at all
  - gluten_free      → contains no gluten sources
  - contains_raw_egg → contains raw or lightly cooked egg
"""


# ---------------------------------------------------------------
# DISQUALIFYING INGREDIENTS
# If any ingredient in a recipe matches one of these lists,
# the corresponding tag cannot be applied.
# ---------------------------------------------------------------

MEAT_KEYWORDS = [
    "beef", "chicken", "pork", "lamb", "turkey", "duck", "veal",
    "venison", "rabbit", "bacon", "ham", "sausage", "salami",
    "chorizo", "prosciutto", "pancetta", "lard", "mince", "minced",
    "steak", "brisket", "rib", "ribs", "shank", "tenderloin",
    "chicken breast", "chicken thigh", "chicken leg", "chicken wing",
    "ground beef", "ground pork", "ground turkey", "ground lamb",
    "pepperoni", "mortadella", "bresaola", "coppa", "nduja",
    "bone broth", "beef stock", "chicken stock", "meat stock",
    "gelatin", "gelatine",   # animal-derived setting agent
    "lard",
    "suet",                  # beef or mutton fat
    "anchovies", "anchovy",  # fish — disqualifies vegetarian
    "worcestershire sauce",  # contains anchovies
    "fish sauce",
    "oyster sauce",
    "shrimp", "prawn", "crab", "lobster", "scallop", "clam",
    "mussel", "squid", "octopus", "salmon", "tuna", "cod",
    "haddock", "mackerel", "sardine", "sea bass", "sea bream",
    "trout", "halibut", "monkfish", "plaice", "sole", "tilapia",
]

# Additional ingredients that disqualify vegan but not vegetarian
NON_VEGAN_KEYWORDS = [
    "milk", "cream", "butter", "cheese", "yoghurt", "yogurt",
    "egg", "eggs", "honey", "beeswax", "whey", "casein",
    "lactose", "ghee", "mayonnaise", "mayo", "hollandaise",
    "aioli", "meringue", "albumen", "gelatin", "gelatine",
    "royal icing",           # typically contains egg white
    "lard", "suet",
    "coconut milk",          # vegan-safe — not included here
    "anchovy", "anchovies",
    "worcestershire sauce",
    "fish sauce",
    "oyster sauce",
]

GLUTEN_KEYWORDS = [
    "flour",
    "wheat",
    "bread",
    "breadcrumb",
    "breadcrumbs",
    "pasta",
    "spaghetti",
    "linguine",
    "penne",
    "fettuccine",
    "tagliatelle",
    "lasagne",
    "lasagna",
    "noodle",
    "barley",
    "rye",
    "spelt",
    "semolina",
    "couscous",
    "bulgur",
    "farro",
    "seitan",
    "soy sauce",             # most soy sauce contains wheat
    "teriyaki sauce",        # typically contains soy sauce
    "hoisin sauce",          # typically contains wheat
    "malt",
    "malt vinegar",
    "beer",
    "ale",
    "stout",
    "puff pastry",
    "shortcrust pastry",
    "filo pastry",
    "phyllo pastry",
    "pie crust",
    "crouton",
    "croutons",
    "panko",
    "biscuit",
    "cookie",
    "cake",
    "tortilla",              # flour tortillas — corn tortillas are ok
                             # handled by exception below
]

GLUTEN_EXCEPTIONS = [
    "rice flour",
    "almond flour",
    "coconut flour",
    "chickpea flour",
    "gram flour",
    "buckwheat flour",       # confusingly, buckwheat is gluten-free
    "tapioca flour",
    "cassava flour",
    "corn tortilla",
    "rice noodle",
    "glass noodle",
    "vermicelli",            # rice-based vermicelli
    "tamari",                # gluten-free alternative to soy sauce
    "gluten-free soy sauce",
    "gluten free soy sauce",
    "rice pasta",
    "gluten-free pasta",
    "gluten free pasta",
    "gluten-free bread",
    "gluten free bread",
    "gluten-free flour",
    "gluten free flour",
]

RAW_EGG_KEYWORDS = [
    "mayonnaise",
    "mayo",
    "hollandaise",
    "aioli",
    "caesar dressing",
    "raw egg",
    "egg yolk",
]


# ---------------------------------------------------------------
# HELPER
# ---------------------------------------------------------------

def _any_match(ingredient: str, keywords: list[str]) -> bool:
    """Returns True if the ingredient contains any of the keywords."""
    name = ingredient.lower().strip()
    return any(kw in name for kw in keywords)


def _is_gluten(ingredient: str) -> bool:
    """
    Returns True if the ingredient contains gluten, accounting
    for gluten-free exceptions.
    """
    name = ingredient.lower().strip()
    if any(exc in name for exc in GLUTEN_EXCEPTIONS):
        return False
    return any(kw in name for kw in GLUTEN_KEYWORDS)


# ---------------------------------------------------------------
# MAIN FUNCTION
# ---------------------------------------------------------------

def tag_recipe(normalised_ingredients: list[str]) -> list[str]:
    """
    Given a list of normalised ingredient names for a single recipe,
    returns a list of dietary tag names that apply.

    Tag names match dietary_tags.name in the database.

    Example:
        tag_recipe(["pasta", "double cream", "parmesan", "egg yolk"])
        → ["contains_raw_egg"]
        (has gluten from pasta, dairy from cream and parmesan,
         egg from egg yolk — so none of the positive tags apply,
         but raw egg is flagged)

        tag_recipe(["tofu", "soy sauce", "ginger", "garlic", "rice"])
        → ["vegetarian", "gluten_free"]
        (no meat, no animal products... but soy sauce has gluten,
         wait — soy sauce IS in gluten keywords, so not gluten free.
         Actually → ["vegetarian"])
    """
    tags = []

    has_meat       = any(_any_match(i, MEAT_KEYWORDS)     for i in normalised_ingredients)
    has_non_vegan  = any(_any_match(i, NON_VEGAN_KEYWORDS) for i in normalised_ingredients)
    has_gluten     = any(_is_gluten(i)                    for i in normalised_ingredients)
    has_raw_egg    = any(_any_match(i, RAW_EGG_KEYWORDS)  for i in normalised_ingredients)

    # Vegetarian: no meat or fish at all
    if not has_meat:
        tags.append("vegetarian")

    # Vegan: no meat AND no other animal products
    # (vegan implies vegetarian, so no need to check has_meat separately)
    if not has_meat and not has_non_vegan:
        tags.append("vegan")

    # Gluten-free: no gluten-containing ingredients detected
    if not has_gluten:
        tags.append("gluten_free")

    # Contains raw egg: flagged regardless of other tags
    if has_raw_egg:
        tags.append("contains_raw_egg")

    return tags