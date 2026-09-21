import requests
from parsers.common import parse_book_html
from parsers.database import save_book

from shared.validation import validate_book_url

REQUEST_TIMEOUT = 20
HEADERS = {"User-Agent": "ITMO-WebDevelopment-Lab/1.0"}


def parse_book(url: str) -> dict[str, str | int | None]:
    safe_url = validate_book_url(url)
    response = requests.get(safe_url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    response.encoding = "utf-8"
    record = parse_book_html(safe_url, response.text)
    book_id = save_book(record)
    return {"id": book_id, **record.as_dict()}
