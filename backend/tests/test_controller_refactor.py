"""
Tests for controller extraction and route delegation.
"""
import pytest
from fastapi import HTTPException


@pytest.mark.asyncio
async def test_worker_controller_creates_and_rejects_duplicate_email(test_db):
    from app.controllers.workers import create_worker

    async with test_db() as db:
        worker = await create_worker(
            full_name="Controller User",
            email="controller@example.com",
            division_id=1,
            phone=None,
            skills=["python"],
            db=db,
        )

        assert worker.worker_id is not None
        assert worker.email == "controller@example.com"

        with pytest.raises(HTTPException) as excinfo:
            await create_worker(
                full_name="Duplicate User",
                email="controller@example.com",
                division_id=1,
                phone=None,
                skills=None,
                db=db,
            )

        assert excinfo.value.status_code == 400


@pytest.mark.asyncio
async def test_auth_login_route_delegates_to_controller(client, monkeypatch):
    from app.routes import auth as auth_routes

    called = {}

    async def fake_login_user(req, db, request=None):
        called["value"] = True
        return {
            "access_token": "access-token",
            "refresh_token": "refresh-token",
            "expires_in": 900,
            "user": {
                "user_id": 1,
                "email": req.email,
                "full_name": "Route Delegate",
                "is_active": True,
                "last_login": None,
            },
        }

    monkeypatch.setattr(auth_routes, "login_user", fake_login_user)

    response = await client.post(
        "/auth/login",
        json={
            "email": "delegate@example.com",
            "password": "Password123!",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert called.get("value") is True
    assert payload["status"] == "success"
    assert payload["data"]["user"]["email"] == "delegate@example.com"