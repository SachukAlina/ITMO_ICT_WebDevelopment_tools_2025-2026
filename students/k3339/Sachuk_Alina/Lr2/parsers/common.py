from dataclasses import asdict, dataclass
from urllib.parse import urljoin

from bs4 import BeautifulSoup


@dataclass(frozen=True)
class BookRecord:
    title: str
    description: str | None
    cover_url: str | None
    source_url: str
    price: str | None
    availability: str | None
    rating: str | None

    def as_dict(self) -> dict[str, str | None]:
        return asdict(self)


@dataclass(frozen=True)
class BenchmarkResult:
    approach: str
    parsed_count: int
    workers: int
    elapsed_seconds: float


def parse_book_html(url: str, html: str) -> BookRecord:
    soup = BeautifulSoup(html, "html.parser")
    title_node = soup.select_one(".product_main h1")
    if title_node is None:
        raise ValueError(f"Book title not found at {url}")

    description_node = soup.select_one("#product_description + p")
    cover_node = soup.select_one("#product_gallery img")
    price_node = soup.select_one(".product_main .price_color")
    availability_node = soup.select_one(".product_main .availability")
    rating_node = soup.select_one(".product_main .star-rating")
    rating = None
    if rating_node:
        rating = next(
            (
                class_name
                for class_name in rating_node.get("class", [])
                if class_name != "star-rating"
            ),
            None,
        )

    cover_url = None
    if cover_node and cover_node.get("src"):
        cover_url = urljoin(url, str(cover_node["src"]))

    return BookRecord(
        title=title_node.get_text(strip=True),
        description=(
            description_node.get_text(" ", strip=True) if description_node else None
        ),
        cover_url=cover_url,
        source_url=url,
        price=price_node.get_text(strip=True) if price_node else None,
        availability=(
            availability_node.get_text(" ", strip=True) if availability_node else None
        ),
        rating=rating,
    )


def split_items(items: list[str], workers: int) -> list[list[str]]:
    if workers < 1:
        raise ValueError("workers must be positive")
    if not items:
        return []
    workers = min(workers, len(items))
    size, remainder = divmod(len(items), workers)
    chunks: list[list[str]] = []
    offset = 0
    for index in range(workers):
        chunk_size = size + (1 if index < remainder else 0)
        chunks.append(items[offset : offset + chunk_size])
        offset += chunk_size
    return chunks
