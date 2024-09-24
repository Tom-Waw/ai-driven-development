import pytest
from app.data_store import clear_users
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


@pytest.fixture(autouse=True)
def run_around_tests():
    clear_users()
    yield


def test_create_user():
    response = client.post("/users", json={"name": "John", "age": 30})
    assert response.status_code == 200
    assert "user_id" in response.json()


def test_get_user():
    response = client.post("/users", json={"name": "John", "age": 30})
    user_id = response.json()["user_id"]
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    assert response.json() == {"name": "John", "age": 30}


def test_update_user():
    response = client.post("/users", json={"name": "John", "age": 30})
    user_id = response.json()["user_id"]
    response = client.put(f"/users/{user_id}", json={"name": "Jane", "age": 25})
    assert response.status_code == 200
    assert response.json() == {"name": "Jane", "age": 25}


def test_delete_user():
    response = client.post("/users", json={"name": "John", "age": 30})
    user_id = response.json()["user_id"]
    response = client.delete(f"/users/{user_id}")
    assert response.status_code == 200
    assert response.json() == {"message": "User deleted successfully"}
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 404
    assert response.json() == {"error": "User not found"}
