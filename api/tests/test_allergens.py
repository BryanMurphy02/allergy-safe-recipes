"""
tests/test_allergens.py

Tests for GET /allergens.
"""


def test_get_allergens_returns_200(client):
    response = client.get("/allergens")
    assert response.status_code == 200


def test_get_allergens_returns_list(client):
    response = client.get("/allergens")
    assert isinstance(response.json(), list)


def test_get_allergens_returns_all_four(client):
    response = client.get("/allergens")
    assert len(response.json()) == 4


def test_get_allergens_contains_expected_names(client):
    response = client.get("/allergens")
    names = [a["name"] for a in response.json()]
    assert "peanuts" in names
    assert "tree_nuts" in names
    assert "dairy" in names
    assert "egg" in names


def test_get_allergens_response_shape(client):
    """Each allergen should have the expected fields."""
    response = client.get("/allergens")
    allergen = response.json()[0]
    assert "id" in allergen
    assert "name" in allergen
    assert "display_name" in allergen
    assert "description" in allergen