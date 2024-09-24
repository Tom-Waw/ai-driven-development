import pytest
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

user_id = 1


@pytest.fixture(scope="module")
def create_user():
    response = client.post("/users", data={"name": "John", "age": 30})
    return response.json()["user_id"]


# Test can_play endpoint


def test_can_play_pokebeasts():
    response = client.post("/can_play", data={"user_id": user_id, "game_name": "Pokebeasts"})
    assert response.status_code == 200
    assert response.json() == {"can_play": True}


def test_can_play_heat_age():
    response = client.post("/can_play", data={"user_id": user_id, "game_name": "Heat Age"})
    assert response.status_code == 200
    assert response.json() == {"can_play": True}


def test_can_play_call_of_war():
    response = client.post("/can_play", data={"user_id": user_id, "game_name": "Call of War"})
    assert response.status_code == 200
    assert response.json() == {"can_play": True}


def test_cannot_play_call_of_war_underage():
    response = client.post("/users", data={"name": "Jane", "age": 16})
    underage_user_id = response.json()["user_id"]
    response = client.post("/can_play", data={"user_id": underage_user_id, "game_name": "Call of War"})
    assert response.status_code == 200
    assert response.json() == {"can_play": False}
