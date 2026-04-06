"""
sources/budget_bytes.py

Scrapes recipes from Budget Bytes (https://www.budgetbytes.com).

Two responsibilities:
  1. discover_urls() — fetches both post sitemaps and returns
     all post URLs. Non-recipe posts are silently skipped
     during parsing since Budget Bytes has no recipe-specific
     sitemap.

  2. parse_recipe() — fetches a single page, extracts the
     schema.org Recipe JSON-LD from the @graph block, and
     returns a ParsedRecipe.

Key difference from BBC Good Food:
  - Recipe JSON-LD is nested inside a @graph array
  - Ingredient strings include prices e.g. "2 cups flour ($0.45)"
    — these are stripped in main.py's normalise_ingredient()
  - Both post sitemaps must be crawled for full coverage
"""

import logging
import re
import time
from typing import Optional

import requests
from bs4 import BeautifulSoup

from sources.bbc_good_food import (
    ParsedRecipe,
    _clean_text,
    _extract_image,
    _extract_json_ld,
    _parse_duration,
    _parse_servings,
    _extract_ingredients,
)

logger = logging.getLogger(__name__)

BASE_URL = "https://www.budgetbytes.com"
SITEMAPS = [
    "https://www.budgetbytes.com/post-sitemap.xml",
    "https://www.budgetbytes.com/post-sitemap2.xml",
]

REQUEST_DELAY = 2.0

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


# ---------------------------------------------------------------
# URL DISCOVERY
# ---------------------------------------------------------------

def discover_urls(max_sitemaps: int = 2) -> list[str]:
    """
    Fetches both Budget Bytes post sitemaps and returns all
    post URLs.

    max_sitemaps controls how many of the two sitemaps to
    process. Default of 2 processes both. Set to 1 when
    testing to limit to the first sitemap only (~977 URLs).

    Non-recipe posts are handled at parse time — if a URL
    has no Recipe JSON-LD it is silently skipped.

    Returns a deduplicated list of absolute URLs.
    """
    urls = []
    seen = set()

    for sitemap_url in SITEMAPS[:max_sitemaps]:
        logger.info(f"Fetching Budget Bytes sitemap: {sitemap_url}")

        try:
            response = requests.get(sitemap_url, headers=HEADERS, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch sitemap {sitemap_url}: {e}")
            continue

        soup = BeautifulSoup(response.text, "xml")

        for loc in soup.find_all("loc"):
            url = loc.text.strip()

            # Skip image URLs embedded in the sitemap
            if "wp-content" in url:
                continue

            if url not in seen:
                seen.add(url)
                urls.append(url)

        logger.info(f"Running total: {len(urls)} URLs discovered")
        time.sleep(REQUEST_DELAY)

    logger.info(f"Discovered {len(urls)} URLs from Budget Bytes")
    return urls


# ---------------------------------------------------------------
# PAGE PARSING
# ---------------------------------------------------------------

def parse_recipe(url: str) -> Optional[ParsedRecipe]:
    """
    Fetches a single Budget Bytes page and extracts recipe data
    from the schema.org JSON-LD @graph block.

    Returns None if:
      - The page cannot be fetched
      - No Recipe JSON-LD is found (non-recipe post)

    Non-recipe posts returning None are silently skipped by
    main.py's process_recipe() — this is expected behaviour.
    """
    logger.info(f"Parsing: {url}")

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Failed to fetch {url}: {e}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    json_ld = _extract_json_ld(soup)
    if not json_ld:
        # Non-recipe post — silently skip
        logger.debug(f"No Recipe JSON-LD found at {url}, skipping")
        return None

    return _parse_json_ld_budget_bytes(json_ld, url)


def _parse_json_ld_budget_bytes(data: dict, url: str) -> Optional[ParsedRecipe]:
    """
    Converts a raw schema.org Recipe dict into a ParsedRecipe.

    Budget Bytes specific handling:
      - cuisine comes from recipeCategory rather than recipeCuisine
      - recipeCategory values tend to be descriptive e.g.
        "Dinner Recipes", "Meal Prep" — we clean these up
    """
    title = data.get("name", "").strip()
    if not title:
        logger.warning(f"Recipe at {url} has no title, skipping")
        return None

    description = _clean_text(data.get("description"))
    image_url   = _extract_image(data.get("image"))
    cuisine     = _extract_cuisine_budget_bytes(data)
    prep_time   = _parse_duration(data.get("prepTime"))
    cook_time   = _parse_duration(data.get("cookTime"))
    total_time  = _parse_duration(data.get("totalTime"))
    servings    = _parse_servings(data.get("recipeYield"))
    ingredients = _extract_ingredients(data.get("recipeIngredient", []))

    return ParsedRecipe(
        title=title,
        url=url,
        description=description,
        cuisine=cuisine,
        prep_time=prep_time,
        cook_time=cook_time,
        total_time=total_time,
        servings=servings,
        image_url=image_url,
        ingredients=ingredients,
    )


def _extract_cuisine_budget_bytes(data: dict) -> Optional[str]:
    """
    Budget Bytes uses recipeCategory rather than recipeCuisine.

    Category values include things like:
        "Dinner Recipes", "Meal Prep", "Vegetarian Recipes",
        "Chicken Recipes", "Asian Inspired Recipes"

    We strip common generic suffixes to get a cleaner label.
    """
    # Try recipeCuisine first
    cuisine = data.get("recipeCuisine")
    if cuisine:
        if isinstance(cuisine, list):
            cuisine = cuisine[0] if cuisine else None
        if isinstance(cuisine, str) and cuisine.strip():
            return cuisine.strip().title()

    # Fall back to recipeCategory
    category = data.get("recipeCategory")
    if category:
        if isinstance(category, list):
            category = category[0] if category else None
        if isinstance(category, str) and category.strip():
            clean = re.sub(
                r"\b(recipes?|dishes?|mains?|meals?|food|cooking|inspired)\b",
                "",
                category,
                flags=re.IGNORECASE,
            ).strip().title()
            return clean or None

    return None