from fastapi.testclient import TestClient
from main import app, users_db, next_user_id

client = TestClient(app)

def setup_function():
    """Reset the in-memory database before each test."""
    global users_db, next_user_id
    users_db.clear() # Clear existing users
    next_user_id = 1 # Reset ID counter

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the User Management API!"}

def test_create_user():
    response = client.post(
        "/users/",
        json={"username": "testuser", "email": "test@example.com"}
    )
    assert response.status_code == 201
    assert response.json()["username"] == "testuser"
    assert response.json()["email"] == "test@example.com"
    assert response.json()["id"] == 1

def test_get_all_users():
    client.post("/users/", json={"username": "user1", "email": "user1@example.com"})
    client.post("/users/", json={"username": "user2", "email": "user2@example.com"})
    response = client.get("/users/")
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["username"] == "user1"
    assert response.json()[1]["username"] == "user2"

def test_get_user_by_id():
    create_response = client.post("/users/", json={"username": "specific", "email": "specific@example.com"})
    user_id = create_response.json()["id"]

    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["username"] == "specific"

def test_get_non_existent_user():
    response = client.get("/users/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}

def test_update_user():
    create_response = client.post("/users/", json={"username": "oldname", "email": "old@example.com"})
    user_id = create_response.json()["id"]

    update_response = client.put(
        f"/users/{user_id}",
        json={"username": "newname", "email": "new@example.com"}
    )
    assert update_response.status_code == 200
    assert update_response.json()["username"] == "newname"
    assert update_response.json()["email"] == "new@example.com"

    # Test partial update
    partial_update_response = client.put(
        f"/users/{user_id}",
        json={"username": "newername"}
    )
    assert partial_update_response.status_code == 200
    assert partial_update_response.json()["username"] == "newername"
    assert partial_update_response.json()["email"] == "new@example.com" # Email should remain unchanged

def test_update_non_existent_user():
    response = client.put(
        "/users/999",
        json={"username": "nonexistent", "email": "nonexistent@example.com"}
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}

def test_delete_user():
    create_response = client.post("/users/", json={"username": "todelete", "email": "todelete@example.com"})
    user_id = create_response.json()["id"]

    delete_response = client.delete(f"/users/{user_id}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/users/{user_id}")
    assert get_response.status_code == 404

def test_delete_non_existent_user():
    response = client.delete("/users/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}