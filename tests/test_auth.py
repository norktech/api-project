import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_login_success():
    response = client.post("/auth/login", json={
        "username": "admin",
        "password": "norktech123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_fail():
    response = client.post("/auth/login", json={
        "username": "admin",
        "password": "wrongpassword"
    })
    assert response.status_code == 401

def test_books_without_token():
    response = client.get("/books")
    assert response.status_code == 401