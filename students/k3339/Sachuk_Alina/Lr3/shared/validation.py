from urllib.parse import urlsplit

ALLOWED_HOSTS = {"books.toscrape.com", "www.books.toscrape.com"}


def validate_book_url(url: str) -> str:
    parsed = urlsplit(url)
    if parsed.scheme != "https" or parsed.hostname not in ALLOWED_HOSTS:
        raise ValueError("Only HTTPS pages from books.toscrape.com are allowed")
    if (
        not parsed.path.startswith("/catalogue/")
        or "/category/" in parsed.path
        or not parsed.path.endswith("/index.html")
    ):
        raise ValueError("URL must point to a book page")
    return url
