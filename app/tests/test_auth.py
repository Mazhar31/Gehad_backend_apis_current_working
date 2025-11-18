import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import get_db, Base
from app.services.admin_service import AdminService
from app.schemas.admin import AdminCreate

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture
def test_admin():
    db = TestingSessionLocal()
    admin_data = AdminCreate(
        name="Test Admin",
        email="test@admin.com",
        password="testpassword123"
    )
    admin = AdminService.create_admin(db, admin_data)
    db.close()
    return admin


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["success"] is True


def test_admin_login_success(test_admin):
    response = client.post(
        "/api/auth/admin/login",
        json={"email": "test@admin.com", "password": "testpassword123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "access_token" in data["data"]


def test_admin_login_invalid_credentials():
    response = client.post(
        "/api/auth/admin/login",
        json={"email": "wrong@email.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401


def test_admin_login_invalid_password(test_admin):
    response = client.post(
        "/api/auth/admin/login",
        json={"email": "test@admin.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401


def test_get_current_user_without_token():
    response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_get_current_user_with_token(test_admin):
    # Login first
    login_response = client.post(
        "/api/auth/admin/login",
        json={"email": "test@admin.com", "password": "testpassword123"}
    )
    token = login_response.json()["data"]["access_token"]
    
    # Get user info
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["email"] == "test@admin.com"
    assert data["data"]["user_type"] == "admin"