import os

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app

RUN_DB_TESTS = os.getenv("RUN_DB_TESTS") == "1"
pytestmark = pytest.mark.skipif(not RUN_DB_TESTS, reason="set RUN_DB_TESTS=1 with docker compose running")


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as async_client:
        yield async_client


async def test_health(client):
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


async def test_job_filters_and_pagination(client):
    response = await client.get("/api/v1/jobs", params={"q": "python", "page": 1, "limit": 5})
    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"items", "total", "page", "limit", "has_more"}
    assert body["limit"] == 5


async def test_invalid_page_is_rejected(client):
    response = await client.get("/api/v1/jobs", params={"page": 0})
    assert response.status_code == 422


async def test_admin_requires_auth(client):
    response = await client.get("/api/v1/admin/overview")
    assert response.status_code == 401
