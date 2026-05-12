"""
Tests for authentication endpoints
"""
import pytest
from httpx import AsyncClient

from app.services import verify_password


@pytest.mark.asyncio
async def test_user_registration(client: AsyncClient):
    """Test user registration"""
    response = await client.post(
        "/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "SecurePass123!",
            "full_name": "New User",
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["expires_in"] == 900  # 15 minutes


@pytest.mark.asyncio
async def test_duplicate_email_registration(client: AsyncClient, test_user):
    """Test registration with duplicate email fails"""
    response = await client.post(
        "/auth/register",
        json={
            "email": test_user.email,
            "password": "SecurePass123!",
            "full_name": "Another User",
        }
    )
    
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


@pytest.mark.asyncio
async def test_user_login_success(client: AsyncClient, test_user):
    """Test successful user login"""
    response = await client.post(
        "/auth/login",
        json={
            "email": test_user.email,
            "password": "Test@1234",  # The password we set in fixture
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_user_login_invalid_password(client: AsyncClient, test_user):
    """Test login with invalid password"""
    response = await client.post(
        "/auth/login",
        json={
            "email": test_user.email,
            "password": "WrongPassword123!",
        }
    )
    
    assert response.status_code == 401
    assert "Invalid credentials" in response.json()["detail"]


@pytest.mark.asyncio
async def test_user_login_nonexistent_email(client: AsyncClient):
    """Test login with non-existent email"""
    response = await client.post(
        "/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "AnyPassword123!",
        }
    )
    
    assert response.status_code == 401
    assert "Invalid credentials" in response.json()["detail"]


@pytest.mark.asyncio
async def test_token_refresh(client: AsyncClient, test_user):
    """Test token refresh"""
    # First, login to get tokens
    login_response = await client.post(
        "/auth/login",
        json={
            "email": test_user.email,
            "password": "Test@1234",
        }
    )
    
    refresh_token = login_response.json()["refresh_token"]
    
    # Now refresh the token
    response = await client.post(
        "/auth/refresh",
        json={
            "refresh_token": refresh_token,
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_token_refresh_invalid(client: AsyncClient):
    """Test refresh with invalid token"""
    response = await client.post(
        "/auth/refresh",
        json={
            "refresh_token": "invalid.token.here",
        }
    )
    
    assert response.status_code == 401
    assert "Invalid refresh token" in response.json()["detail"]
