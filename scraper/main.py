"""
main.py

Entry point for the scraper service.

Orchestrates the full pipeline for each enabled source:
  1. Discover recipe URLs from the source index
  2. For each URL — check if already scraped, skip if so
  3. Fetch and parse the recipe page
  4. Normalise ingredient names
  5. Match allergens and dietary tags
  6. Write everything to Postgres
  7. Log the result to scrape_log

Run directly:
    python main.py

Or via the scheduler (called by scheduler.py on a cron interval).
"""

import logging
import os
import re

import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

from allergen_matcher import match_allergens, is_raw_egg
from dietary_tagger import tag_recipe
from sources import bbc_good_food, budget_bytes

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------
# DATABASE CONNECTION
# ---------------------------------------------------------------

def get_db_connection():
    """
    Returns a psycopg2 connection using DATABASE_URL from .env.
    Expected format:
        postgresql://user:password@host:port/dbname
    """
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise EnvironmentError("DATABASE_URL is not set in environment")
    return psycopg2.connect(database_url)


# ---------------------------------------------------------------
# INGREDIENT NORMALISATION
# ---------------------------------------------------------------

def normalise_ingredient(raw: str) -> str:
    """
    Strips quantities, units, preparation notes, and prices
    from a raw ingredient string to produce a clean name.

    Handles Budget Bytes price annotations e.g.:
        "2 cups flour ($0.45)"  → "flour"
        "4 Roma tomatoes ($1.35)" → "tomatoes"

    Examples:
        "200g dried spaghetti"         → "spaghetti"
        "2 large free-range eggs"      → "eggs"
        "3 tbsp olive oil"             → "olive oil"
        "1/2 tsp fine sea salt"        → "salt"
        "100ml double cream"           → "double cream"
    """
    text = raw.lower().strip()

    # Strip price annotations e.g. ($1.35) or ($0.45)
    text = re.sub(r'\(\$[\d.]+\)', '', text)

    # Remove leading quantities: "200g", "2", "1/2", "a handful of"
    text = re.sub(r"^\d[\d/\.\s]*", "", text)
    text = re.sub(r"^a\s+", "", text)
    text = re.sub(r"^an\s+", "", text)
    text = re.sub(r"^some\s+", "", text)

    # Remove common units
    units = [
        "tbsp", "tsp", "tablespoon", "teaspoon",
        "cup", "cups", "ml", "l", "litre", "liter",
        "g", "kg", "oz", "lb", "pound",
        "handful", "pinch", "sprig", "bunch",
        "slice", "slices", "piece", "pieces",
        "clove", "cloves", "rasher", "rashers",
        "fillet", "fillets", "sheet", "sheets",
        "can", "tin", "jar",
    ]
    unit_pattern = r"\b(" + "|".join(units) + r"s?)\b"
    text = re.sub(unit_pattern, "", text)

    # Remove common adjectives that don't affect allergen matching
    adjectives = [
        "large", "small", "medium", "big",
        "fresh", "frozen", "dried", "smoked",
        "fine", "coarse", "ground", "whole",
        "organic", "free-range", "free range",
        "roughly", "finely", "thinly", "thickly",
        "chopped", "sliced", "diced", "grated",
        "peeled", "pitted", "deseeded", "trimmed",
        "rinsed", "drained", "toasted", "roasted",
        "softened", "melted", "cooled", "warmed",
        "boneless", "skinless", "room temperature",
    ]
    for adj in adjectives:
        text = re.sub(r"\b" + adj + r"\b", "", text, flags=re.IGNORECASE)

    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()

    return text or raw.lower().strip()


# ---------------------------------------------------------------
# DATABASE WRITE HELPERS
# ---------------------------------------------------------------

def get_or_create_source(cur, name: str, base_url: str) -> int:
    """Returns the id of the source, inserting if not present."""
    cur.execute("SELECT id FROM sources WHERE base_url = %s", (base_url,))
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute(
        "INSERT INTO sources (name, base_url) VALUES (%s, %s) RETURNING id",
        (name, base_url)
    )
    return cur.fetchone()[0]


def recipe_already_scraped(cur, url: str) -> bool:
    """Returns True if this URL already exists in the recipes table."""
    cur.execute("SELECT id FROM recipes WHERE url = %s", (url,))
    return cur.fetchone() is not None


def insert_recipe(cur, source_id: int, recipe) -> int:
    """Inserts a recipe row and returns its new id."""
    cur.execute(
        """
        INSERT INTO recipes
            (source_id, title, url, description, cuisine,
             prep_time, cook_time, total_time, servings, image_url)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """,
        (
            source_id,
            recipe.title,
            recipe.url,
            recipe.description,
            recipe.cuisine,
            recipe.prep_time,
            recipe.cook_time,
            recipe.total_time,
            recipe.servings,
            recipe.image_url,
        )
    )
    return cur.fetchone()[0]


def get_or_create_ingredient(cur, raw_name: str, normalised_name: str) -> int:
    """Returns the id of the ingredient, inserting if not present."""
    cur.execute(
        "SELECT id FROM ingredients WHERE raw_name = %s",
        (raw_name,)
    )
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute(
        """
        INSERT INTO ingredients (raw_name, normalised_name)
        VALUES (%s, %s)
        RETURNING id
        """,
        (raw_name, normalised_name)
    )
    return cur.fetchone()[0]


def get_allergen_id(cur, allergen_name: str) -> int | None:
    """Looks up an allergen by name and returns its id."""
    cur.execute(
        "SELECT id FROM allergens WHERE name = %s",
        (allergen_name,)
    )
    row = cur.fetchone()
    return row[0] if row else None


def get_dietary_tag_id(cur, tag_name: str) -> int | None:
    """Looks up a dietary tag by name and returns its id."""
    cur.execute(
        "SELECT id FROM dietary_tags WHERE name = %s",
        (tag_name,)
    )
    row = cur.fetchone()
    return row[0] if row else None


def log_scrape(cur, source_id: int, url: str, status: str, error: str = None):
    """Appends a row to scrape_log."""
    cur.execute(
        """
        INSERT INTO scrape_log (source_id, url, status, error_message)
        VALUES (%s, %s, %s, %s)
        """,
        (source_id, url, status, error)
    )


# ---------------------------------------------------------------
# CORE PIPELINE — ONE RECIPE
# ---------------------------------------------------------------

def process_recipe(cur, source_id: int, url: str, parse_fn) -> bool:
    """
    Full pipeline for a single recipe URL:
      1. Skip if already in the database
      2. Parse the page
      3. Insert recipe row
      4. For each ingredient: normalise, get/create, match allergens
      5. Roll up allergens to recipe level
      6. Apply dietary tags
      7. Log the result

    Returns True on success, False on any failure.
    None returned from parse_fn (non-recipe post) is treated
    as a skip rather than a failure.
    """
    if recipe_already_scraped(cur, url):
        logger.info(f"Already scraped, skipping: {url}")
        log_scrape(cur, source_id, url, "skipped")
        return True

    # Parse the page
    recipe = parse_fn(url)
    if not recipe:
        # Silently skip non-recipe posts from Budget Bytes
        log_scrape(cur, source_id, url, "skipped")
        return True

    try:
        # Insert the recipe
        recipe_id = insert_recipe(cur, source_id, recipe)

        # Track which allergens appear in this recipe (for roll-up)
        recipe_allergen_ids = set()
        # Track all normalised ingredients (for dietary tagging)
        all_normalised = []

        for raw_ingredient in recipe.ingredients:
            normalised = normalise_ingredient(raw_ingredient)
            all_normalised.append(normalised)

            # Get or create ingredient record
            ingredient_id = get_or_create_ingredient(
                cur, raw_ingredient, normalised
            )

            # Link ingredient to recipe
            cur.execute(
                """
                INSERT INTO recipe_ingredients (recipe_id, ingredient_id)
                VALUES (%s, %s)
                ON CONFLICT (recipe_id, ingredient_id) DO NOTHING
                """,
                (recipe_id, ingredient_id)
            )

            # Match allergens for this ingredient
            matches = match_allergens(normalised)
            for match in matches:
                allergen_id = get_allergen_id(cur, match.allergen_name)
                if not allergen_id:
                    continue

                # Store ingredient → allergen link
                cur.execute(
                    """
                    INSERT INTO ingredient_allergens
                        (ingredient_id, allergen_id, confidence)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (ingredient_id, allergen_id) DO NOTHING
                    """,
                    (ingredient_id, allergen_id, match.confidence)
                )
                recipe_allergen_ids.add(allergen_id)

        # Roll up allergens to recipe level
        for allergen_id in recipe_allergen_ids:
            cur.execute(
                """
                INSERT INTO recipe_allergens (recipe_id, allergen_id)
                VALUES (%s, %s)
                ON CONFLICT (recipe_id, allergen_id) DO NOTHING
                """,
                (recipe_id, allergen_id)
            )

        # Apply dietary tags
        applicable_tags = tag_recipe(all_normalised)

        # Also check for raw egg specifically
        if any(is_raw_egg(i) for i in all_normalised):
            if "contains_raw_egg" not in applicable_tags:
                applicable_tags.append("contains_raw_egg")

        for tag_name in applicable_tags:
            tag_id = get_dietary_tag_id(cur, tag_name)
            if not tag_id:
                continue
            cur.execute(
                """
                INSERT INTO recipe_dietary_tags (recipe_id, dietary_tag_id)
                VALUES (%s, %s)
                ON CONFLICT (recipe_id, dietary_tag_id) DO NOTHING
                """,
                (recipe_id, tag_id)
            )

        log_scrape(cur, source_id, url, "success")
        logger.info(f"Successfully processed: {recipe.title}")
        return True

    except Exception as e:
        logger.error(f"Error processing {url}: {e}")
        log_scrape(cur, source_id, url, "failed", str(e))
        return False


# ---------------------------------------------------------------
# MAIN — RUNS ALL ENABLED SOURCES
# ---------------------------------------------------------------

def run_scraper():
    """
    Main entry point. Runs the full scrape pipeline for all
    enabled sources defined in the .env file.
    """
    bbc_enabled    = os.getenv("BBC_ENABLED", "true").lower() == "true"
    bb_enabled     = os.getenv("BUDGET_BYTES_ENABLED", "true").lower() == "true"
    max_sitemaps   = int(os.getenv("MAX_SITEMAPS", "2"))

    sources_to_run = []
    if bbc_enabled:
        sources_to_run.append({
            "name":     "BBC Good Food",
            "base_url": "https://www.bbcgoodfood.com",
            "discover": lambda: bbc_good_food.discover_urls(max_sitemaps),
            "parse":    bbc_good_food.parse_recipe,
        })
    if bb_enabled:
        sources_to_run.append({
            "name":     "Budget Bytes",
            "base_url": "https://www.budgetbytes.com",
            "discover": lambda: budget_bytes.discover_urls(max_sitemaps),
            "parse":    budget_bytes.parse_recipe,
        })

    if not sources_to_run:
        logger.warning("No sources enabled. Set BBC_ENABLED or BUDGET_BYTES_ENABLED in .env")
        return

    conn = get_db_connection()

    try:
        for source in sources_to_run:
            logger.info(f"Starting scrape: {source['name']}")

            with conn.cursor() as cur:
                source_id = get_or_create_source(
                    cur, source["name"], source["base_url"]
                )
                conn.commit()

            urls = source["discover"]()
            logger.info(f"Found {len(urls)} URLs to process for {source['name']}")

            success_count = 0
            fail_count    = 0

            for url in urls:
                with conn.cursor() as cur:
                    ok = process_recipe(cur, source_id, url, source["parse"])
                    conn.commit()

                if ok:
                    success_count += 1
                else:
                    fail_count += 1

            logger.info(
                f"Finished {source['name']}: "
                f"{success_count} succeeded, {fail_count} failed"
            )

    finally:
        conn.close()

    logger.info("Scrape run complete")


if __name__ == "__main__":
    run_scraper()