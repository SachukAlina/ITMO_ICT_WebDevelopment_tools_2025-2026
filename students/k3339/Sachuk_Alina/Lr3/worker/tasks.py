import requests

from parser_service.service import parse_book
from worker.celery_app import celery_app


@celery_app.task(
    name="parse_book",
    autoretry_for=(requests.RequestException,),
    retry_backoff=True,
    retry_jitter=True,
    max_retries=3,
)
def parse_book_task(url: str) -> dict[str, str | int | None]:
    return parse_book(url)
