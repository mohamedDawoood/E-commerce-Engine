import pytest
from fastapi import status
import io

def test_create_product(client, test_user):
    file_content = b"fake image content"
    file = io.BytesIO(file_content)
    
    data = {
        "name": "Gaming Mouse",
        "price": 25.5,
        "description": "High performance mouse",
        "stock": 10
    }
    
    response = client.post(
        "/products/",
        data=data,
        files={"file": ("mouse.jpg", file, "image/jpeg")}
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["product"]["name"] == "Gaming Mouse"
    assert "static/images/" in response.json()["product"]["image_url"]


def test_read_all_products(client, test_product):
    response = client.get("/products/")
    assert response.status_code == 200
    assert len(response.json()) >= 1
    assert response.json()[0]["name"] == test_product.name


def test_read_single_product(client, test_product):
    response = client.get(f"/products/{test_product.id}")
    assert response.status_code == 200
    assert response.json()["id"] == test_product.id


def test_search_products(client, test_product):
    response = client.get(f"/products/?search={test_product.name}")
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_update_product_success(client, test_product, test_user):
    update_data = {
        "name": "Updated Keyboard",
        "price": 50.0,
        "stock": 5,
        "description": "Updated desc"
    }
    response = client.put(f"/products/{test_product.id}", json=update_data)
    assert response.status_code == 202
    assert response.json()["name"] == "Updated Keyboard"


def test_delete_product_success(client, test_product, test_user):
    response = client.delete(f"/products/{test_product.id}")
    assert response.status_code == 200
    assert response.json()["message"] == "the product has been deleted"


def test_delete_product_unauthorized(client, test_product):
    from app.models.user import User
    from app.api.deps import get_current_user 

    hacker = User(id=999, username="hacker", role="user")

    client.app.dependency_overrides[get_current_user] = lambda: hacker

    response = client.delete(f"/products/{test_product.id}")
    
    client.app.dependency_overrides.clear()
    
    assert response.status_code == 403