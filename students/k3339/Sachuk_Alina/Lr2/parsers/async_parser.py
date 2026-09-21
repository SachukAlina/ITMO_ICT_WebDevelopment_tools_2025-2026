import asyncio
import json
from time import perf_counter

import aiohttp

from parsers.common import BenchmarkResult, BookRecord, parse_book_html, split_items
from parsers.database import save_book
from parsers.urls import BOOK_URLS

WORKERS = 4
REQUEST_TIMEOUT = aiohttp.ClientTimeout(total=20)
HEADERS = {"User-Agent": "ITMO-WebDevelopment-Lab/1.0"}


async def parse_and_save(
    url: str, session: aiohttp.ClientSession | None = None
) -> BookRecord:
    if session is None:
        async with aiohttp.ClientSession(
            timeout=REQUEST_TIMEOUT, headers=HEADERS
        ) as owned_session:
            return await parse_and_save(url, owned_session)

    async with session.get(url) as response:
        response.raise_for_status()
        html = await response.text()
    record = parse_book_html(url, html)
    book_id = await asyncio.to_thread(save_book, record)
    print(
        json.dumps(
            {"id": book_id, "title": record.title, "source_url": record.source_url},
            ensure_ascii=False,
        )
    )
    return record


async def parse_chunk(
    urls: list[str], session: aiohttp.ClientSession
) -> list[BookRecord]:
    return [await parse_and_save(url, session) for url in urls]


async def run(urls: list[str] | None = None, workers: int = WORKERS) -> BenchmarkResult:
    target_urls = urls or BOOK_URLS
    chunks = split_items(target_urls, workers)
    started_at = perf_counter()
    async with aiohttp.ClientSession(
        timeout=REQUEST_TIMEOUT, headers=HEADERS
    ) as session:
        groups = await asyncio.gather(
            *(parse_chunk(chunk, session) for chunk in chunks)
        )
    return BenchmarkResult(
        "asyncio",
        sum(len(group) for group in groups),
        len(chunks),
        perf_counter() - started_at,
    )


if __name__ == "__main__":
    print(asyncio.run(run()))
