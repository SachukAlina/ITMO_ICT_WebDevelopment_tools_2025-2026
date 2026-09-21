# Лабораторная работа №1

## Цель и вариант

Реализовать серверное FastAPI-приложение с PostgreSQL, ORM, миграциями и
типизированным CRUD. Выбран вариант «Веб-приложение для буккросинга» и полный
уровень на 15 баллов с регистрацией, JWT-аутентификацией и хешированием паролей.

## Структура проекта

```text
Lr1/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── security.py
│   ├── presenters.py
│   └── routers/
├── migrations/
├── practices/
│   ├── practice_1_1/
│   ├── practice_1_2/
│   └── practice_1_3/
└── tests/
```

Практика 1.1 содержит самостоятельное приложение с временной базой. Практики
1.2 и 1.3 указывают на итоговые ORM-модели, CRUD, миграции и конфигурацию.

## Модель данных

| Таблица | Основные поля | Назначение и связи |
|---|---|---|
| `users` | email, username, password_hash, is_active | Пользователь; one-to-many с экземплярами книг |
| `authors` | name, biography | Автор книги |
| `books` | title, isbn, description, published_year, source_url | Каталог книг; one-to-many с экземплярами |
| `book_authors` | book_id, author_id, **role, position** | Many-to-many книг и авторов; дополнительные поля характеризуют связь |
| `library_entries` | owner_id, book_id, **condition, status, notes** | Ассоциативная сущность пользователя и книги |
| `exchange_requests` | requester_id, requested_entry_id, offered_entry_id, status | Запросы на обмен экземплярами |

Таким образом выполнены требования к шести таблицам, one-to-many, many-to-many
и ассоциативной сущности с содержательными полями.

Полные определения находятся в
[`app/models.py`](https://github.com/SachukAlina/ITMO_ICT_WebDevelopment_tools_2025-2026/blob/main/students/k3339/Sachuk_Alina/Lr1/app/models.py).

## Соединение с базой данных

URL PostgreSQL читается из `DATABASE_URL`. Настоящий `.env` исключён из Git,
а безопасный шаблон находится в `.env.example`.

```python
def create_db_engine(database_url: str) -> Engine:
    connect_args = (
        {"check_same_thread": False}
        if database_url.startswith("sqlite")
        else {}
    )
    return create_engine(
        database_url,
        connect_args=connect_args,
        pool_pre_ping=True,
    )

engine = create_db_engine(settings.database_url)

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
```

Схема создаётся миграцией `0001_initial_schema.py`; Alembic также получает URL
из настроек приложения, поэтому пароль не хранится в `alembic.ini`.

## Эндпоинты

### Сервис и пользователи

| Метод | Путь | Назначение | JWT |
|---|---|---|---|
| GET | `/` | Информация о сервисе | нет |
| GET | `/health` | Проверка доступности | нет |
| POST | `/auth/register` | Регистрация | нет |
| POST | `/auth/token` | Получение JWT по OAuth2 Password form | нет |
| GET | `/users/me` | Текущий пользователь | да |
| GET | `/users` | Список пользователей без хешей паролей | да |
| POST | `/users/change-password` | Проверка старого и установка нового пароля | да |

### Авторы и книги

| Метод | Путь | Назначение | JWT |
|---|---|---|---|
| GET | `/authors` | Список авторов | нет |
| GET | `/authors/{id}` | Автор | нет |
| POST | `/authors` | Создать автора | да |
| PATCH | `/authors/{id}` | Изменить автора | да |
| DELETE | `/authors/{id}` | Удалить несвязанного автора | да |
| GET | `/books` | Книги с вложенными авторами | нет |
| GET | `/books/{id}` | Книга с вложенными авторами | нет |
| POST | `/books` | Создать книгу и связи с авторами | да |
| PATCH | `/books/{id}` | Изменить книгу | да |
| DELETE | `/books/{id}` | Удалить книгу | да |
| POST | `/books/{id}/authors` | Добавить связь с автором | да |
| DELETE | `/books/{id}/authors/{author_id}` | Удалить связь | да |

### Библиотека и обмены

| Метод | Путь | Назначение | JWT |
|---|---|---|---|
| GET | `/library` | Все экземпляры с вложенными книгой и владельцем | нет |
| GET | `/library/me` | Экземпляры текущего пользователя | да |
| GET | `/library/{id}` | Один экземпляр | нет |
| POST | `/library` | Добавить собственный экземпляр | да |
| PATCH | `/library/{id}` | Изменить собственный экземпляр | да |
| DELETE | `/library/{id}` | Удалить собственный экземпляр | да |
| GET | `/exchanges` | Входящие и исходящие заявки | да |
| GET | `/exchanges/{id}` | Заявка, доступная участникам | да |
| POST | `/exchanges` | Создать заявку | да |
| PATCH | `/exchanges/{id}` | Принять, отклонить или отменить | да |
| DELETE | `/exchanges/{id}` | Удалить непринятую заявку | да |

При принятии заявки экземпляры переводятся в состояние `reserved`. Изменять и
удалять экземпляр может только его владелец.

## Аутентификация

Функциональность реализована вручную поверх инструментов FastAPI:

- пароль хешируется Argon2 через `pwdlib`;
- JWT создаётся и проверяется через `PyJWT`;
- идентификатор пользователя записывается в claim `sub`;
- срок действия токена — 30 минут;
- Swagger UI использует `OAuth2PasswordBearer`;
- модели ответа никогда не содержат `password_hash`.

## Запуск

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

Документация OpenAPI: `http://127.0.0.1:8000/docs`.

## Проверка

```bash
pytest -q
ruff check .
```

Результат: **2 API-теста пройдены**. Дополнительно выполнена интеграционная
проверка с PostgreSQL 17: миграция, регистрация, получение JWT, создание автора
и книги, возврат вложенного автора — успешно.
