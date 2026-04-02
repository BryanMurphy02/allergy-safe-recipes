"""
tests/test_dietary_tags.py

Tests for GET /dietary-tags.
"""


def test_get_dietary_tags_returns_200(client):
    response = client.get("/dietary-tags")
    assert response.status_code == 200


def test_get_dietary_tags_returns_list(client):
    response = client.get("/dietary-tags")
    assert isinstance(response.json(), list)


def test_get_dietary_tags_returns_all_four(client):
    response = client.get("/dietary-tags")
    assert len(response.json()) == 4


def test_get_dietary_tags_contains_expected_names(client):
    response = client.get("/dietary-tags")
    names = [t["name"] for t in response.json()]
    assert "vegetarian" in names
    assert "vegan" in names
    assert "gluten_free" in names
    assert "contains_raw_egg" in names


def test_get_dietary_tags_response_shape(client):
    """Each tag should have the expected fields."""
    response = client.get("/dietary-tags")
    tag = response.json()[0]
    assert "id" in tag
    assert "name" in tag
    assert "display_name" in tag
    assert "description" in tag