from collections.abc import AsyncGenerator

import httpx
from app.models import User
from app.security import get_current_user
from fastapi.testclient import TestClient
from kombu.exceptions import OperationalError
from redis.exceptions import ConnectionError as RedisConnectionError

from gateway.main import app
from gateway.parser_api import celery_client, get_parser_client

VALID_URL = "https://books.toscrape.com/catalogue/test-book_1/index.html"


def fake_current_user() -> User:
    return User(
        id=1,
        email="test@example.com",
        username="tester",
        full_name="Test User",
        password_hash="not-returned",
    )


def parser_handler(request: httpx.Request) -> httpx.Response:
    assert request.url.path == "/parse"
    return httpx.Response(
        200,
        json={
            "id": 7,
            "title": "Parsed Book",
            "description": None,
            "cover_url": None,
            "source_url": VALID_URL,
            "price": "£12.00",
            "availability": "In stock",
            "rating": "Five",
        },
    )


async def fake_parser_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    transport = httpx.MockTransport(parser_handler)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://parser.test"
    ) as client:
        yield client


def test_gateway_forwards_direct_parse_request() -> None:
    app.dependency_overrides[get_current_user] = fake_current_user
    app.dependency_overrides[get_parser_client] = fake_parser_client
    try:
        response = TestClient(app).post("/parser/parse", json={"url": VALID_URL})
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["id"] == 7


def test_gateway_enqueues_task(monkeypatch) -> None:
    class FakeTask:
        id = "task-123"

    monkeypatch.setattr(celery_client, "send_task", lambda *args, **kwargs: FakeTask())
    app.dependency_overrides[get_current_user] = fake_current_user
    try:
        response = TestClient(app).post("/parser/tasks", json={"url": VALID_URL})
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 202
    assert response.json() == {"task_id": "task-123", "status": "queued"}


def test_gateway_returns_503_when_queue_is_unavailable(monkeypatch) -> None:
    def unavailable_queue(*args, **kwargs):
        raise OperationalError("connection refused")

    monkeypatch.setattr(celery_client, "send_task", unavailable_queue)
    app.dependency_overrides[get_current_user] = fake_current_user
    try:
        response = TestClient(app).post("/parser/tasks", json={"url": VALID_URL})
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 503
    assert response.json() == {"detail": "Task queue is unavailable"}


def test_gateway_returns_completed_task(monkeypatch) -> None:
    class FakeResult:
        status = "SUCCESS"
        result = {
            "id": 8,
            "title": "Queued Book",
            "description": None,
            "cover_url": None,
            "source_url": VALID_URL,
            "price": None,
            "availability": None,
            "rating": None,
        }

        @staticmethod
        def successful() -> bool:
            return True

        @staticmethod
        def failed() -> bool:
            return False

    monkeypatch.setattr(celery_client, "AsyncResult", lambda task_id: FakeResult())
    app.dependency_overrides[get_current_user] = fake_current_user
    try:
        response = TestClient(app).get("/parser/tasks/task-123")
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["result"]["id"] == 8


def test_gateway_returns_503_when_result_backend_is_unavailable(monkeypatch) -> None:
    class UnavailableResult:
        @staticmethod
        def successful() -> bool:
            raise RedisConnectionError("connection refused")

    monkeypatch.setattr(
        celery_client, "AsyncResult", lambda task_id: UnavailableResult()
    )
    app.dependency_overrides[get_current_user] = fake_current_user
    try:
        response = TestClient(app).get("/parser/tasks/task-123")
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 503
    assert response.json() == {"detail": "Task result backend is unavailable"}
