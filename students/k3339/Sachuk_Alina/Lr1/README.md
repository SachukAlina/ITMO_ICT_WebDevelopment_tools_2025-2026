# Лабораторная работа №1 — BookCrossing API

Серверное приложение для учёта книг пользователей и управления запросами на
обмен. Выполнен вариант на 15 баллов: PostgreSQL, SQLModel, CRUD, вложенные
объекты, Alembic, регистрация, ручная JWT-аутентификация и хеширование паролей.

## Модель данных

- `users` — пользователи;
- `books` — каталог книг;
- `authors` — авторы;
- `book_authors` — ассоциативная сущность с ролью автора и порядком отображения;
- `library_entries` — ассоциативная сущность пользователя и книги с состоянием
  экземпляра, доступностью и примечанием;
- `exchange_requests` — заявки на обмен.

## Локальный запуск

Требуются Python 3.11+ и PostgreSQL.

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

Swagger UI доступен по адресу <http://127.0.0.1:8000/docs>.

## Проверка

```bash
pip install -r requirements-dev.txt
pytest
ruff check .
```

Срезы и пояснения практик 1.1–1.3 находятся в папке `practices`.
