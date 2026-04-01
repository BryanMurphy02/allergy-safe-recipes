"""
sources/bbc_good_food.py

Scrapes recipes from BBC Good Food.

Two responsibilities:
  1. discover_urls() — crawls the BBC Good Food recipe index
     and returns a list of recipe URLs to scrape.
  2. parse_recipe() — takes a single recipe URL, fetches the
     page, extracts the schema.org JSON-LD block, and returns
     a structured dict ready to be inserted into the database.

BBC Good Food embeds structured recipe data as a JSON-LD block
inside a <script type="application/ld+json"> tag. This is far
more reliable than CSS selectors, which break on site redesigns.
"""

import json
import logging
import re
import time
from dataclasses import dataclass, field
from typing import Optional

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

BASE_URL = "https://www.bbcgoodfood.com"
SITEMAP_INDEX_URL = "https://www.bbcgoodfood.com/sitemap.xml"

# Polite delay between requests — BBC Good Food will rate-limit
# aggressive scrapers. 2 seconds is conservative and safe.
REQUEST_DELAY = 2.0

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


@dataclass
class ParsedRecipe:
    """
    Structured recipe data extracted from a single page.
    All fields map directly to columns in the recipes table,
    except ingredients which feed into recipe_ingredients.
    """
    title:       str
    url:         str
    description: Optional[str]
    cuisine:     Optional[str]
    prep_time:   Optional[int]   # minutes
    cook_time:   Optional[int]   # minutes
    total_time:  Optional[int]   # minutes
    servings:    Optional[int]
    image_url:   Optional[str]
    ingredients: list[str] = field(default_factory=list)  # raw strings


# ---------------------------------------------------------------
# URL DISCOVERY
# ---------------------------------------------------------------

def discover_urls(max_sitemaps: int = 2) -> list[str]:
    """
    Discovers recipe URLs by parsing BBC Good Food's sitemap index.

    BBC Good Food publishes a sitemap index at /sitemap.xml which
    contains child sitemaps organised by quarter and content type:
        2026-Q1-recipe.xml
        2025-Q4-recipe.xml
        ...

    We fetch the index, filter to only the -recipe.xml sitemaps,
    then extract all /recipes/ URLs from each one — skipping
    /premium/ URLs which are behind a paywall.

    max_sitemaps controls how many quarterly recipe sitemaps to
    process. Each contains ~200-400 recipes. Default of 2 gives
    a good starting dataset without being excessive.
    Set to 1 when testing.

    Returns a deduplicated list of absolute URLs.
    """
    urls = []
    seen = set()

    # Step 1 — fetch the sitemap index
    logger.info(f"Fetching sitemap index: {SITEMAP_INDEX_URL}")
    try:
        response = requests.get(SITEMAP_INDEX_URL, headers=HEADERS, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Failed to fetch sitemap index: {e}")
        return []

    soup = BeautifulSoup(response.text, "xml")

    # Step 2 — find all child sitemaps that are recipe sitemaps
    recipe_sitemaps = [
        loc.text.strip()
        for loc in soup.find_all("loc")
        if "-recipe.xml" in loc.text
    ]

    logger.info(f"Found {len(recipe_sitemaps)} recipe sitemaps in index")

    # Step 3 — fetch each recipe sitemap and extract /recipes/ URLs
    for sitemap_url in recipe_sitemaps[:max_sitemaps]:
        logger.info(f"Fetching recipe sitemap: {sitemap_url}")

        try:
            response = requests.get(sitemap_url, headers=HEADERS, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch sitemap {sitemap_url}: {e}")
            continue

        sitemap_soup = BeautifulSoup(response.text, "xml")

        for loc in sitemap_soup.find_all("loc"):
            url = loc.text.strip()

            # Only take free /recipes/ URLs — skip /premium/
            if "/recipes/" in url and "/premium/" not in url:
                if url not in seen:
                    seen.add(url)
                    urls.append(url)

        logger.info(f"Running total: {len(urls)} recipe URLs discovered")
        time.sleep(REQUEST_DELAY)

    logger.info(f"Discovered {len(urls)} recipe URLs from BBC Good Food")
    return urls


# ---------------------------------------------------------------
# PAGE PARSING
# ---------------------------------------------------------------

def parse_recipe(url: str) -> Optional[ParsedRecipe]:
    """
    Fetches a single BBC Good Food recipe page and extracts
    structured data from the schema.org JSON-LD block.

    Returns a ParsedRecipe on success, None on failure.
    """
    logger.info(f"Parsing: {url}")

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Failed to fetch {url}: {e}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    # Find the JSON-LD block containing Recipe data
    json_ld = _extract_json_ld(soup)
    if not json_ld:
        logger.warning(f"No schema.org Recipe data found at {url}")
        return None

    return _parse_json_ld(json_ld, url)


def _extract_json_ld(soup: BeautifulSoup) -> Optional[dict]:
    """
    Finds the <script type="application/ld+json"> block that
    contains a schema.org Recipe object.

    A page may have multiple JSON-LD blocks (for breadcrumbs,
    organisation info, etc.) so we iterate until we find one
    with "@type": "Recipe".
    """
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string)
        except (json.JSONDecodeError, TypeError):
            continue

        # Handle both a single object and an array of objects
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and item.get("@type") == "Recipe":
                    return item
        elif isinstance(data, dict):
            if data.get("@type") == "Recipe":
                return data
            # Some sites nest Recipe inside a @graph array
            if "@graph" in data:
                for item in data["@graph"]:
                    if isinstance(item, dict) and item.get("@type") == "Recipe":
                        return item

    return None


def _parse_json_ld(data: dict, url: str) -> Optional[ParsedRecipe]:
    """
    Converts a raw schema.org Recipe dict into a ParsedRecipe.
    Handles missing or malformed fields gracefully.
    """
    title = data.get("name", "").strip()
    if not title:
        logger.warning(f"Recipe at {url} has no title, skipping")
        return None

    description = _clean_text(data.get("description"))
    image_url   = _extract_image(data.get("image"))
    cuisine     = _extract_cuisine(data.get("recipeCuisine"))
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


# ---------------------------------------------------------------
# FIELD PARSERS
# ---------------------------------------------------------------

def _clean_text(value) -> Optional[str]:
    """Strips HTML tags and whitespace from a text field."""
    if not value:
        return None
    # Remove any HTML tags that sometimes appear in descriptions
    clean = re.sub(r"<[^>]+>", "", str(value))
    return clean.strip() or None


def _extract_image(image_field) -> Optional[str]:
    """
    schema.org image can be a string URL, a dict with a 'url'
    key, or a list of either. We just want the first URL.
    """
    if not image_field:
        return None
    if isinstance(image_field, str):
        return image_field
    if isinstance(image_field, dict):
        return image_field.get("url")
    if isinstance(image_field, list) and image_field:
        return _extract_image(image_field[0])
    return None


def _extract_cuisine(cuisine_field) -> Optional[str]:
    """
    recipeCuisine can be a string or a list. Take the first
    value and capitalise it.
    """
    if not cuisine_field:
        return None
    if isinstance(cuisine_field, list):
        cuisine_field = cuisine_field[0] if cuisine_field else None
    if isinstance(cuisine_field, str):
        return cuisine_field.strip().title() or None
    return None


def _parse_duration(iso_duration: Optional[str]) -> Optional[int]:
    """
    Converts ISO 8601 duration strings to integer minutes.

    Examples:
        "PT30M"      → 30
        "PT1H30M"    → 90
        "PT1H"       → 60
        "P0D"        → 0
        None         → None
    """
    if not iso_duration:
        return None
    try:
        hours   = int(re.search(r"(\d+)H", iso_duration).group(1)) if "H" in iso_duration else 0
        minutes = int(re.search(r"(\d+)M", iso_duration).group(1)) if "M" in iso_duration else 0
        return hours * 60 + minutes
    except (AttributeError, ValueError):
        return None


def _parse_servings(yield_field) -> Optional[int]:
    """
    recipeYield can be "4", "4 servings", "Serves 4", or a list.
    We extract the first integer found.
    """
    if not yield_field:
        return None
    if isinstance(yield_field, list):
        yield_field = yield_field[0] if yield_field else None
    if not yield_field:
        return None
    numbers = re.findall(r"\d+", str(yield_field))
    return int(numbers[0]) if numbers else None


def _extract_ingredients(ingredient_list) -> list[str]:
    """
    recipeIngredient is a list of raw strings like:
        ["200g spaghetti", "2 large eggs", "100g pancetta"]

    We return them as-is. Normalisation happens in main.py
    before they are passed to the allergen matcher.
    """
    if not isinstance(ingredient_list, list):
        return []
    return [str(i).strip() for i in ingredient_list if i]