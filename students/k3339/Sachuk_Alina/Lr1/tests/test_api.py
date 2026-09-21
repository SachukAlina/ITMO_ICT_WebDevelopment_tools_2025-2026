from fastapi.testclient import TestClient


def register_and_login(client: TestClient, username: str, email: str) -> dict[str, str]:
    response = client.post(
        "/auth/register",
        json={
            "email": email,
            "username": username,
            "full_name": username.title(),
            "password": "strong-password",
        },
    )
    assert response.status_code == 201
    response = client.post(
        "/auth/token",
        data={"username": username, "password": "strong-password"},
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_registration_login_and_password_change(client: TestClient) -> None:
    headers = register_and_login(client, "alina", "alina@example.com")

    response = client.get("/users/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["username"] == "alina"
    assert "password_hash" not in response.json()

    response = client.post(
        "/users/change-password",
        headers=headers,
        json={
            "current_password": "strong-password",
            "new_password": "new-strong-password",
        },
    )
    assert response.status_code == 204
    assert (
        client.post(
            "/auth/token",
            data={"username": "alina", "password": "new-strong-password"},
        ).status_code
        == 200
    )


def test_nested_crud_and_exchange_workflow(client: TestClient) -> None:
    owner_headers = register_and_login(client, "owner", "owner@example.com")
    reader_headers = register_and_login(client, "reader", "reader@example.com")

    author_response = client.post(
        "/authors",
        headers=owner_headers,
        json={"name": "Jane Austen", "biography": "English novelist"},
    )
    assert author_response.status_code == 201
    author_id = author_response.json()["id"]

    book_response = client.post(
        "/books",
        headers=owner_headers,
        json={
            "title": "Pride and Prejudice",
            "published_year": 1813,
            "authors": [{"author_id": author_id, "role": "author", "position": 1}],
        },
    )
    assert book_response.status_code == 201
    assert book_response.json()["authors"][0]["author"]["name"] == "Jane Austen"
    book_id = book_response.json()["id"]

    entry_response = client.post(
        "/library",
        headers=owner_headers,
        json={"book_id": book_id, "condition": "good", "notes": "Paperback"},
    )
    assert entry_response.status_code == 201
    entry_id = entry_response.json()["id"]
    assert entry_response.json()["owner"]["username"] == "owner"

    forbidden_response = client.patch(
        f"/library/{entry_id}",
        headers=reader_headers,
        json={"condition": "worn"},
    )
    assert forbidden_response.status_code == 403

    exchange_response = client.post(
        "/exchanges",
        headers=reader_headers,
        json={"requested_entry_id": entry_id, "message": "May I borrow it?"},
    )
    assert exchange_response.status_code == 201
    exchange_id = exchange_response.json()["id"]

    accept_response = client.patch(
        f"/exchanges/{exchange_id}",
        headers=owner_headers,
        json={"status": "accepted"},
    )
    assert accept_response.status_code == 200
    assert accept_response.json()["status"] == "accepted"

    entry_after_accept = client.get(f"/library/{entry_id}")
    assert entry_after_accept.json()["status"] == "reserved"
