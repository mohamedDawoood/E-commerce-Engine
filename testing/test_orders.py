import pytest
from fastapi import status

def test_place_order_success(client, test_user, test_product):

    order_data = {
        "product_id": test_product.id,
        "quantity": 2
    }
    response = client.post("/orders/", json=order_data)
    
    assert response.status_code == 200 
    data = response.json()
    assert data["total_price"] == test_product.price * 2

    assert "8 items left" in data["remaining_stock"]

def test_place_order_insufficient_stock(client, test_user, test_product):

    order_data = {
        "product_id": test_product.id,
        "quantity": 50 
    }
    response = client.post("/orders/", json=order_data)
    
    assert response.status_code == 400
    assert response.json()["detail"] == f"We have just {test_product.stock}"

def test_place_order_insufficient_stock(client, test_user, test_product):
    order_data = {
        "product_id": test_product.id,
        "quantity": 999999
    }
    response = client.post("/orders/", json=order_data)
    assert response.status_code == 400

    assert "We have just" in response.json()["detail"]

def test_get_my_orders(client, test_user, test_product):

    client.post("/orders/", json={"product_id": test_product.id, "quantity": 1})
    

    response = client.get("/orders/me")
    assert response.status_code == 200
    assert len(response.json()) >= 1
    assert response.json()[0]["total_price"] > 0