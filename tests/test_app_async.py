import copy

import pytest
import httpx

from src.app import app, activities


@pytest.mark.asyncio
async def test_root_redirect():
    # Arrange
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        # Act
        response = await client.get("/")

        # Assert
        assert response.status_code in (302, 307)
        assert response.headers.get("location") == "/static/index.html"


@pytest.mark.asyncio
async def test_get_activities():
    # Arrange
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        # Act
        response = await client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) >= 1


@pytest.mark.asyncio
async def test_signup_and_unregister():
    # Arrange: snapshot current activities state
    original = copy.deepcopy(activities)
    activity_name = next(iter(activities.keys()))
    test_email = "ci-test+user@example.com"

    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        # Act: sign up the test email
        resp_post = await client.post(f"/activities/{activity_name}/signup", params={"email": test_email})

        # Assert: signup succeeded and participant added
        assert resp_post.status_code == 200
        assert test_email in activities[activity_name]["participants"]

        # Act: unregister the test email
        resp_del = await client.delete(f"/activities/{activity_name}/signup", params={"email": test_email})

        # Assert: unregister succeeded and participant removed
        assert resp_del.status_code == 200
        assert test_email not in activities[activity_name]["participants"]

    # Teardown: restore original activities state
    activities.clear()
    activities.update(original)
