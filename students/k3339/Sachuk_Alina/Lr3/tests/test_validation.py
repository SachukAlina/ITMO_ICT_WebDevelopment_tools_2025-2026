import pytest

from shared.validation import validate_book_url


def test_allows_books_to_scrape_product_page() -> None:
    url = "https://books.toscrape.com/catalogue/test-book_1/index.html"
    assert validate_book_url(url) == url


@pytest.mark.parametrize(
    "url",
    [
        "http://books.toscrape.com/catalogue/test-book_1/index.html",
        "https://example.com/catalogue/test-book_1/index.html",
        "https://books.toscrape.com/catalogue/category/books_1/index.html",
        "https://books.toscrape.com/",
    ],
)
def test_rejects_unsafe_or_non_product_urls(url: str) -> None:
    with pytest.raises(ValueError):
        validate_book_url(url)
