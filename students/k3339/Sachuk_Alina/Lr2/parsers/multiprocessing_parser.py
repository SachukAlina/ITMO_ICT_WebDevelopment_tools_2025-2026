import json
from concurrent.futures import ProcessPoolExecutor
from time import perf_counter

import requests

from parsers.common import BenchmarkResult, BookRecord, parse_book_html, split_items
from parsers.database import save_book
from parsers.urls import BOOK_URLS

WORKERS = 4
REQUEST_TIMEOUT = 20
HEADERS = {"User-Agent": "ITMO-WebDevelopment-Lab/1.0"}


def parse_and_save(url: str) -> BookRecord:
    response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    response.encoding = "utf-8"
    record = parse_book_html(url, response.text)
    book_id = save_book(record)
    print(
        json.dumps(
            {"id": book_id, "title": record.title, "source_url": record.source_url},
            ensure_ascii=False,
        )
    )
    return record


def parse_chunk(urls: list[str]) -> list[BookRecord]:
    return [parse_and_save(url) for url in urls]


def run(urls: list[str] | None = None, workers: int = WORKERS) -> BenchmarkResult:
    target_urls = urls or BOOK_URLS
    chunks = split_items(target_urls, workers)
    started_at = perf_counter()
    with ProcessPoolExecutor(max_workers=len(chunks)) as executor:
        parsed_count = sum(
            len(records) for records in executor.map(parse_chunk, chunks)
        )
    return BenchmarkResult(
        "multiprocessing", parsed_count, len(chunks), perf_counter() - started_at
    )


if __name__ == "__main__":
    print(run())
