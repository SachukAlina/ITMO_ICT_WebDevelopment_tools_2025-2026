# Лабораторная работа №2 — потоки, процессы и асинхронность

## Задача 1

Три реализации вычисляют сумму чисел от 1 до `10_000_000_000_000`, деля
диапазон на четыре части:

- `task1/threading_sum.py` — `ThreadPoolExecutor`;
- `task1/multiprocessing_sum.py` — `ProcessPoolExecutor`;
- `task1/async_sum.py` — `asyncio` и `async/await`.

Каждая подзадача использует формулу арифметической прогрессии. Наивный перебор
десяти триллионов чисел не завершился бы за приемлемое для лабораторной время.
Из-за постоянной сложности вычисления накладные расходы на создание процессов
ожидаемо больше полезной работы; benchmark это демонстрирует.

```bash
python -m task1.benchmark
```

Результат записывается в `results/sum_timings.csv`.

## Задача 2

Три реализации загружают страницы учебного сайта Books to Scrape, извлекают
название, описание, обложку, цену, наличие и рейтинг. Название, описание,
обложка и исходный URL сохраняются в таблицу `books` из ЛР1. Повторный запуск
обновляет существующую книгу по `source_url`, а не создаёт дубликат.

- `parsers/threading_parser.py` — потоки и `requests`;
- `parsers/multiprocessing_parser.py` — процессы и `requests`;
- `parsers/async_parser.py` — `asyncio` и `aiohttp`.

Список URL делится на четыре сбалансированные части. Каждая реализация содержит
функцию `parse_and_save(url)` и выводит сохранённые данные на экран.

```bash
export DATABASE_URL=postgresql+psycopg://bookcrossing:bookcrossing@localhost:5432/bookcrossing
python -m parsers.benchmark
```

Результат записывается в `results/parser_timings.csv`.

Последний интеграционный замер на 12 страницах:

| Подход | Время, с |
|---|---:|
| threading | 2.430716 |
| multiprocessing | 2.571006 |
| asyncio | 1.265441 |

## Установка и проверка

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pytest
ruff check .
```
