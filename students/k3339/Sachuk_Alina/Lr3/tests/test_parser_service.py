from fastapi.testclient import TestClient

from parser_service.main import app

VALID_URL = "https://books.toscrape.com/catalogue/test-book_1/index.html"


def test_parse_endpoint_returns_saved_book(monkeypatch) -> None:
    monkeypatch.setattr(
        "parser_service.main.parse_book",
        lambda url: {
            "id": 42,
            "title": "Test Book",
            "description": "Description",
            "cover_url": None,
            "source_url": url,
            "price": "£10.00",
            "availability": "In stock",
            "rating": "Four",
        },
    )
    response = TestClient(app).post("/parse", json={"url": VALID_URL})
    assert response.status_code == 200
    assert response.json()["id"] == 42
    assert response.json()["source_url"] == VALID_URL


def test_parse_endpoint_rejects_external_host() -> None:
    response = TestClient(app).post(
        "/parse",
        json={"url": "https://example.com/catalogue/test-book_1/index.html"},
    )
    assert response.status_code == 400
