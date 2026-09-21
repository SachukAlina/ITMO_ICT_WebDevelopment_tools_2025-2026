# Лабораторная работа №3 — Docker, источники данных и очереди

Выполнена полная версия работы (подзадачи 1, 2 и 3). Приложение ЛР1 и парсер
ЛР2 объединены в контейнерную систему из пяти сервисов:

- `api` — BookCrossing FastAPI и HTTP-шлюз к парсеру;
- `parser` — отдельный FastAPI-сервис синхронного парсинга;
- `worker` — Celery worker для фоновых задач;
- `redis` — брокер Celery и backend результатов;
- `db` — PostgreSQL 17.

## Эндпоинты интеграции

Все маршруты основного API требуют JWT:

- `POST /parser/parse` — синхронно вызывает parser-service и возвращает книгу;
- `POST /parser/tasks` — ставит URL в очередь и возвращает `task_id`;
- `GET /parser/tasks/{task_id}` — возвращает состояние и результат задачи.

Parser-service предоставляет `POST /parse`. Для защиты от SSRF разрешены только
HTTPS-страницы книг на `books.toscrape.com`.

## Запуск

Команды выполняются из папки `Lr3`:

```bash
docker compose up --build -d
docker compose ps
```

Основной Swagger UI: <http://localhost:8000/docs>.
Parser-service: <http://localhost:8001/docs>.

Остановка без удаления данных:

```bash
docker compose down
```

Удаление вместе с тестовыми томами:

```bash
docker compose down -v
```

## Пример работы

Сначала зарегистрируйтесь через `/auth/register`, получите JWT через
`/auth/token`, затем передавайте заголовок `Authorization: Bearer <token>`.

```json
POST /parser/tasks
{
  "url": "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
}
```

Ответ:

```json
{
  "task_id": "<uuid>",
  "status": "queued"
}
```

Состояние и результат задачи можно получить запросом
`GET /parser/tasks/{task_id}`. Celery хранит результаты один час.

## Проверка кода

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pytest -q
ruff check .
docker compose config --quiet
```

При контрольном запуске все сервисы прошли healthcheck, синхронный запрос
вернул `HTTP 200`, фоновый — `HTTP 202`, а затем состояние `success`. Модульные
тесты: **12 passed**.
