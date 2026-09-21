# Sachuk Alina, K3339

Лабораторные работы по дисциплине «Средства Web-программирования».

- `Lr1` — серверное приложение BookCrossing на FastAPI;
- `Lr2` — сравнение threading, multiprocessing и asyncio;
- `Lr3` — Docker Compose, отдельный parser-service и очередь Celery/Redis;
- `docs` и `mkdocs.yml` — отчётный сайт.

Локальный просмотр отчёта:

```bash
python3.11 -m venv .venv-docs
source .venv-docs/bin/activate
pip install -r requirements-docs.txt
mkdocs serve
```
