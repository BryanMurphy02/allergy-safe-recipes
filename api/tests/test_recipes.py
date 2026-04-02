"""
tests/test_recipes.py

Tests for all recipe endpoints:
  GET /recipes
  GET /recipes?exclude_allergens=...
  GET /recipes?dietary_tags=...
  GET /recipes?cuisine=...
  GET /recipes?max_total_time=...
  GET /recipes/{id}
  GET /recipes/{id}/allergens
  GET /recipes/{id}/dietary-tags
  GET /recipes/meta/cuisines
"""

import pytest

from tests.conftest import (
    add_allergen_to_recipe,
    add_dietary_tag_to_recipe,
    make_recipe,
)


# ---------------------------------------------------------------
# GET /recipes — basic
# ---------------------------------------------------------------

class TestGetRecipes:
    def test_returns_200_empty_db(self, client):
        response = client.get("/recipes")
        assert response.status_code == 200

    def test_returns_paginated_shape(self, client):
        response = client.get("/recipes")
        data = response.json()
        assert "total" in data
        assert "page" in data
        assert "size" in data
        assert "results" in data

    def test_empty_db_returns_zero_total(self, client):
        response = client.get("/recipes")
        assert response.json()["total"] == 0

    def test_returns_recipe_in_results(self, client, db_session):
        make_recipe(db_session, title="Pasta Carbonara")
        response = client.get("/recipes")
        assert response.json()["total"] == 1
        assert response.json()["results"][0]["title"] == "Pasta Carbonara"

    def test_pagination_page_default_is_1(self, client):
        response = client.get("/recipes")
        assert response.json()["page"] == 1

    def test_pagination_size_default_is_20(self, client):
        response = client.get("/recipes")
        assert response.json()["size"] == 20

    def test_pagination_limits_results(self, client, db_session):
        for i in range(5):
            make_recipe(
                db_session,
                title=f"Recipe {i}",
                url=f"https://www.bbcgoodfood.com/recipes/recipe-{i}"
            )
        response = client.get("/recipes?size=2")
        assert len(response.json()["results"]) == 2
        assert response.json()["total"] == 5

    def test_recipe_summary_has_expected_fields(self, client, db_session):
        make_recipe(db_session)
        response = client.get("/recipes")
        recipe = response.json()["results"][0]
        for field in ["id", "title", "url", "cuisine", "prep_time",
                      "cook_time", "total_time", "servings", "allergens", "dietary_tags"]:
            assert field in recipe


# ---------------------------------------------------------------
# GET /recipes — filtering by allergen exclusion
# ---------------------------------------------------------------

class TestExcludeAllergens:
    def test_excludes_recipe_with_dairy(self, client, db_session):
        dairy_recipe = make_recipe(db_session, title="Creamy Pasta",
                                   url="https://www.bbcgoodfood.com/recipes/creamy-pasta")
        safe_recipe  = make_recipe(db_session, title="Tomato Salad",
                                   url="https://www.bbcgoodfood.com/recipes/tomato-salad")

        add_allergen_to_recipe(db_session, dairy_recipe, "dairy")

        response = client.get("/recipes?exclude_allergens=dairy")
        titles = [r["title"] for r in response.json()["results"]]

        assert "Creamy Pasta" not in titles
        assert "Tomato Salad" in titles

    def test_excludes_multiple_allergens(self, client, db_session):
        peanut_recipe = make_recipe(db_session, title="Satay Chicken",
                                    url="https://www.bbcgoodfood.com/recipes/satay")
        egg_recipe    = make_recipe(db_session, title="Omelette",
                                    url="https://www.bbcgoodfood.com/recipes/omelette")
        safe_recipe   = make_recipe(db_session, title="Tomato Soup",
                                    url="https://www.bbcgoodfood.com/recipes/tomato-soup")

        add_allergen_to_recipe(db_session, peanut_recipe, "peanuts")
        add_allergen_to_recipe(db_session, egg_recipe, "egg")

        response = client.get("/recipes?exclude_allergens=peanuts,egg")
        titles = [r["title"] for r in response.json()["results"]]

        assert "Satay Chicken" not in titles
        assert "Omelette" not in titles
        assert "Tomato Soup" in titles

    def test_unknown_allergen_returns_all_recipes(self, client, db_session):
        make_recipe(db_session)
        response = client.get("/recipes?exclude_allergens=shellfish")
        assert response.json()["total"] == 1


# ---------------------------------------------------------------
# GET /recipes — filtering by dietary tags
# ---------------------------------------------------------------

class TestDietaryTagFilter:
    def test_filters_to_vegan_recipes(self, client, db_session):
        vegan_recipe = make_recipe(db_session, title="Lentil Soup",
                                   url="https://www.bbcgoodfood.com/recipes/lentil-soup")
        non_vegan    = make_recipe(db_session, title="Chicken Soup",
                                   url="https://www.bbcgoodfood.com/recipes/chicken-soup")

        add_dietary_tag_to_recipe(db_session, vegan_recipe, "vegan")

        response = client.get("/recipes?dietary_tags=vegan")
        titles = [r["title"] for r in response.json()["results"]]

        assert "Lentil Soup" in titles
        assert "Chicken Soup" not in titles

    def test_filters_by_multiple_tags(self, client, db_session):
        both_tags = make_recipe(db_session, title="Chickpea Salad",
                                url="https://www.bbcgoodfood.com/recipes/chickpea-salad")
        one_tag   = make_recipe(db_session, title="Rice Bowl",
                                url="https://www.bbcgoodfood.com/recipes/rice-bowl")

        add_dietary_tag_to_recipe(db_session, both_tags, "vegan")
        add_dietary_tag_to_recipe(db_session, both_tags, "gluten_free")
        add_dietary_tag_to_recipe(db_session, one_tag, "vegan")

        response = client.get("/recipes?dietary_tags=vegan,gluten_free")
        titles = [r["title"] for r in response.json()["results"]]

        assert "Chickpea Salad" in titles
        assert "Rice Bowl" not in titles


# ---------------------------------------------------------------
# GET /recipes — filtering by cuisine
# ---------------------------------------------------------------

class TestCuisineFilter:
    def test_filters_by_cuisine(self, client, db_session):
        make_recipe(db_session, title="Pasta",   cuisine="Italian",
                    url="https://www.bbcgoodfood.com/recipes/pasta")
        make_recipe(db_session, title="Curry",   cuisine="Indian",
                    url="https://www.bbcgoodfood.com/recipes/curry")

        response = client.get("/recipes?cuisine=Italian")
        titles = [r["title"] for r in response.json()["results"]]

        assert "Pasta" in titles
        assert "Curry" not in titles

    def test_cuisine_filter_is_case_insensitive(self, client, db_session):
        make_recipe(db_session, title="Pasta", cuisine="Italian",
                    url="https://www.bbcgoodfood.com/recipes/pasta2")

        response = client.get("/recipes?cuisine=italian")
        assert response.json()["total"] == 1


# ---------------------------------------------------------------
# GET /recipes — filtering by max total time
# ---------------------------------------------------------------

class TestMaxTotalTime:
    def test_filters_by_max_total_time(self, client, db_session):
        make_recipe(db_session, title="Quick Meal", total_time=15,
                    url="https://www.bbcgoodfood.com/recipes/quick")
        make_recipe(db_session, title="Slow Roast", total_time=180,
                    url="https://www.bbcgoodfood.com/recipes/slow")

        response = client.get("/recipes?max_total_time=30")
        titles = [r["title"] for r in response.json()["results"]]

        assert "Quick Meal" in titles
        assert "Slow Roast" not in titles


# ---------------------------------------------------------------
# GET /recipes/{id}
# ---------------------------------------------------------------

class TestGetRecipeById:
    def test_returns_200_for_existing_recipe(self, client, db_session):
        recipe = make_recipe(db_session)
        response = client.get(f"/recipes/{recipe.id}")
        assert response.status_code == 200

    def test_returns_404_for_missing_recipe(self, client):
        response = client.get("/recipes/99999")
        assert response.status_code == 404

    def test_returns_full_detail_fields(self, client, db_session):
        recipe = make_recipe(db_session)
        response = client.get(f"/recipes/{recipe.id}")
        data = response.json()
        for field in ["id", "title", "url", "description", "cuisine",
                      "prep_time", "cook_time", "total_time", "servings",
                      "allergens", "dietary_tags", "ingredients"]:
            assert field in data

    def test_returns_correct_title(self, client, db_session):
        recipe = make_recipe(db_session, title="Spaghetti Bolognese")
        response = client.get(f"/recipes/{recipe.id}")
        assert response.json()["title"] == "Spaghetti Bolognese"

    def test_includes_allergens_in_detail(self, client, db_session):
        recipe = make_recipe(db_session)
        add_allergen_to_recipe(db_session, recipe, "dairy")
        response = client.get(f"/recipes/{recipe.id}")
        allergen_names = [a["name"] for a in response.json()["allergens"]]
        assert "dairy" in allergen_names

    def test_includes_dietary_tags_in_detail(self, client, db_session):
        recipe = make_recipe(db_session)
        add_dietary_tag_to_recipe(db_session, recipe, "vegetarian")
        response = client.get(f"/recipes/{recipe.id}")
        tag_names = [t["name"] for t in response.json()["dietary_tags"]]
        assert "vegetarian" in tag_names


# ---------------------------------------------------------------
# GET /recipes/{id}/allergens
# ---------------------------------------------------------------

class TestGetRecipeAllergens:
    def test_returns_200(self, client, db_session):
        recipe = make_recipe(db_session)
        response = client.get(f"/recipes/{recipe.id}/allergens")
        assert response.status_code == 200

    def test_returns_empty_list_for_recipe_with_no_allergens(self, client, db_session):
        recipe = make_recipe(db_session)
        response = client.get(f"/recipes/{recipe.id}/allergens")
        assert response.json() == []

    def test_returns_allergens_for_recipe(self, client, db_session):
        recipe = make_recipe(db_session)
        add_allergen_to_recipe(db_session, recipe, "egg")
        response = client.get(f"/recipes/{recipe.id}/allergens")
        names = [a["name"] for a in response.json()]
        assert "egg" in names

    def test_returns_404_for_missing_recipe(self, client):
        response = client.get("/recipes/99999/allergens")
        assert response.status_code == 404


# ---------------------------------------------------------------
# GET /recipes/{id}/dietary-tags
# ---------------------------------------------------------------

class TestGetRecipeDietaryTags:
    def test_returns_200(self, client, db_session):
        recipe = make_recipe(db_session)
        response = client.get(f"/recipes/{recipe.id}/dietary-tags")
        assert response.status_code == 200

    def test_returns_empty_list_for_untagged_recipe(self, client, db_session):
        recipe = make_recipe(db_session)
        response = client.get(f"/recipes/{recipe.id}/dietary-tags")
        assert response.json() == []

    def test_returns_tags_for_recipe(self, client, db_session):
        recipe = make_recipe(db_session)
        add_dietary_tag_to_recipe(db_session, recipe, "vegan")
        response = client.get(f"/recipes/{recipe.id}/dietary-tags")
        names = [t["name"] for t in response.json()]
        assert "vegan" in names

    def test_returns_404_for_missing_recipe(self, client):
        response = client.get("/recipes/99999/dietary-tags")
        assert response.status_code == 404


# ---------------------------------------------------------------
# GET /recipes/meta/cuisines
# ---------------------------------------------------------------

class TestGetCuisines:
    def test_returns_200(self, client):
        response = client.get("/recipes/meta/cuisines")
        assert response.status_code == 200

    def test_returns_list(self, client):
        response = client.get("/recipes/meta/cuisines")
        assert isinstance(response.json(), list)

    def test_returns_empty_list_when_no_recipes(self, client):
        response = client.get("/recipes/meta/cuisines")
        assert response.json() == []

    def test_returns_distinct_cuisines(self, client, db_session):
        make_recipe(db_session, cuisine="Italian",
                    url="https://www.bbcgoodfood.com/recipes/pasta-1")
        make_recipe(db_session, cuisine="Italian",
                    url="https://www.bbcgoodfood.com/recipes/pasta-2")
        make_recipe(db_session, cuisine="Indian",
                    url="https://www.bbcgoodfood.com/recipes/curry-1")

        response = client.get("/recipes/meta/cuisines")
        cuisines = response.json()

        assert cuisines.count("Italian") == 1
        assert "Indian" in cuisines

    def test_returns_sorted_cuisines(self, client, db_session):
        make_recipe(db_session, cuisine="Italian",
                    url="https://www.bbcgoodfood.com/recipes/pasta-3")
        make_recipe(db_session, cuisine="British",
                    url="https://www.bbcgoodfood.com/recipes/pie-1")

        response = client.get("/recipes/meta/cuisines")
        cuisines = response.json()
        assert cuisines == sorted(cuisines)