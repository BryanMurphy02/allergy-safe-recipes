"""
sources/serious_eats.py

Scrapes recipes from Serious Eats.

Structure mirrors bbc_good_food.py — same two responsibilities:
  1. discover_urls() — crawls the Serious Eats recipe index
  2. parse_recipe()  — parses a single recipe page

Serious Eats also uses schema.org/Recipe JSON-LD, but with a few
differences from BBC Good Food:
  - cuisine is less consistently populated
  - recipeYield formatting varies more
  - Some pages have multiple JSON-LD blocks nested in @graph
  - They use "recipeCategory" more than "recipeCuisine"
"""

import json
import logging
import re
import time
from dataclasses import dataclass, field
from typing import Optional

import requests
from bs4 import BeautifulSoup

# Reuse the ParsedRecipe dataclass from the BBC module — the
# output format is identical regardless of source.
from sources.bbc_good_food import (
    ParsedRecipe,
    _clean_text,
    _extract_image,
    _parse_duration,
    _parse_servings,
    _extract_ingredients,
    _extract_json_ld,
)

logger = logging.getLogger(__name__)

BASE_URL = "https://www.seriouseats.com"
RECIPE_INDEX_URLS = [
    "https://www.seriouseats.com/recipes",
    "https://www.seriouseats.com/dinner-recipes",
    "https://www.seriouseats.com/breakfast-brunch-recipes",
    "https://www.seriouseats.com/lunch-recipes",
    "https://www.seriouseats.com/dessert-recipes",
]

REQUEST_DELAY = 2.0

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; RecipeAllergenBot/1.0; "
        "educational project)"
    )
}


# ---------------------------------------------------------------
# URL DISCOVERY
# ---------------------------------------------------------------

def discover_urls(max_pages: int = 5) -> list[str]:
    """
    Crawls multiple Serious Eats category index pages and returns
    a list of recipe page URLs.

    Serious Eats does not have a single paginated recipe index
    like BBC Good Food, so we crawl several category pages instead.

    max_pages applies per category page, not total.
    """
    urls = []
    seen = set()

    for index_url in RECIPE_INDEX_URLS:
        for page_num in range(1, max_pages + 1):
            paginated_url = f"{index_url}?page={page_num}" if page_num > 1 else index_url
            logger.info(f"Crawling Serious Eats: {paginated_url}")

            try:
                response = requests.get(
                    paginated_url,
                    headers=HEADERS,
                    timeout=10
                )
                response.raise_for_status()
            except requests.RequestException as e:
                logger.error(f"Failed to fetch {paginated_url}: {e}")
                break

            soup = BeautifulSoup(response.text, "html.parser")
            found_on_page = 0

            for link in soup.find_all("a", href=True):
                href = link["href"]

                # Serious Eats recipe URLs end in a numeric ID slug
                # e.g. /the-best-chocolate-chip-cookies-recipe-988877
                # We match any path that looks like a recipe.
                full_url = _normalise_url(href)
                if full_url and _is_recipe_url(full_url) and full_url not in seen:
                    seen.add(full_url)
                    urls.append(full_url)
                    found_on_page += 1

            # If we got no new URLs from this page, stop paginating
            # this category — we've likely hit the end.
            if found_on_page == 0:
                logger.info(f"No new URLs found on page {page_num}, stopping pagination")
                break

            time.sleep(REQUEST_DELAY)

    logger.info(f"Discovered {len(urls)} recipe URLs from Serious Eats")
    return urls


def _normalise_url(href: str) -> Optional[str]:
    """Converts relative or absolute hrefs to a clean absolute URL."""
    if not href:
        return None
    href = href.split("?")[0].split("#")[0]  # strip query params and anchors
    if href.startswith("http"):
        if "seriouseats.com" in href:
            return href
        return None
    if href.startswith("/"):
        return BASE_URL + href
    return None


def _is_recipe_url(url: str) -> bool:
    """
    Heuristic to identify recipe URLs vs category/article pages.
    Serious Eats recipe URLs typically end in a numeric ID:
        /the-food-lab-ultimate-chocolate-chip-cookies-recipe-278866
    We also exclude known non-recipe paths.
    """
    exclude_patterns = [
        "/author/", "/about", "/contact", "/tag/",
        "/search", "/newsletter", "/privacy", "/terms",
    ]
    if any(pattern in url for pattern in exclude_patterns):
        return False

    # Recipe URLs on Serious Eats always end in a 6-digit number
    return bool(re.search(r"-\d{6,}$", url))


# ---------------------------------------------------------------
# PAGE PARSING
# ---------------------------------------------------------------

def parse_recipe(url: str) -> Optional[ParsedRecipe]:
    """
    Fetches a single Serious Eats recipe page and extracts
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

    json_ld = _extract_json_ld(soup)
    if not json_ld:
        logger.warning(f"No schema.org Recipe data found at {url}")
        return None

    return _parse_json_ld_serious_eats(json_ld, url)


def _parse_json_ld_serious_eats(data: dict, url: str) -> Optional[ParsedRecipe]:
    """
    Converts a raw schema.org Recipe dict into a ParsedRecipe,
    with Serious Eats-specific field handling.

    Key difference from BBC: Serious Eats uses recipeCategory
    more consistently than recipeCuisine, so we check both.
    """
    title = data.get("name", "").strip()
    if not title:
        logger.warning(f"Recipe at {url} has no title, skipping")
        return None

    description = _clean_text(data.get("description"))
    image_url   = _extract_image(data.get("image"))
    cuisine     = _extract_cuisine_serious_eats(data)
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


def _extract_cuisine_serious_eats(data: dict) -> Optional[str]:
    """
    Serious Eats populates recipeCategory more reliably than
    recipeCuisine. We check recipeCuisine first, then fall back
    to recipeCategory.

    Examples of what Serious Eats puts in recipeCategory:
        "American Mains", "Italian", "Quick Dinners"

    We take the first value and clean it up.
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
            # Strip common suffixes like "Mains", "Recipes", "Dishes"
            # to get a cleaner cuisine label
            clean = re.sub(
                r"\b(mains|recipes|dishes|food|cooking)\b",
                "",
                category,
                flags=re.IGNORECASE
            ).strip().title()
            return clean or None

    return None