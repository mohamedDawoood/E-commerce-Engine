import pytest
from fastapi import status



def test_signup(client):
    payload = {
        "username": "new_user",
        "email": "new@example.com",
        "password": "strongpassword123",
        "first_name": "Mohamed",
        "last_name": "Dawood",
        "phone_number": "0123456789"
    }
    response = client.post("/users/signup", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["username"] == "new_user"
    assert "id" in data

def test_login_success(client, test_user):

    login_data = {
        "username": test_user.username,
        "password": "testpassword123" 
    }
    response = client.post("/users/login", data=login_data)
    

    assert response.status_code == 200
    assert "access_token" in response.json()

def test_read_all_users_as_admin(client, test_user):

    response = client.get("/users/admin")
    assert response.status_code == 200
    assert len(response.json()) >= 1

def test_read_single_user(client, test_user):
    response = client.get(f"/users/{test_user.id}")
    assert response.status_code == 200
    assert response.json()["username"] == test_user.username

def test_update_own_profile(client, test_user):
    update_payload = {
        "username": "updated_name",
        "email": "updated@example.com",
        "password": "newpassword123",
        "first_name": "Updated",
        "last_name": "User",
        "phone_number": "0987654321"
    }
    response = client.put(f"/users/{test_user.id}", json=update_payload)
    assert response.status_code == 200
    assert "updated" in response.json()["message"]

def test_admin_delete_user(client, db, test_user):

    from app.models.user import User
    other_user = User(username="victim", email="v@v.com", hashed_password="..", role="user")
    db.add(other_user)
    db.commit()
    db.refresh(other_user)

    response = client.delete(f"/users/admin_delete_user/{other_user.id}")
    assert response.status_code == 200
    assert "deleted" in response.json()["message"]

def test_delete_user_self(client, test_user):

    response = client.delete(f"/users/admin_delete_user/{test_user.id}")
    assert response.status_code == 400
    assert "can't delete your self" in response.json()["detail"]