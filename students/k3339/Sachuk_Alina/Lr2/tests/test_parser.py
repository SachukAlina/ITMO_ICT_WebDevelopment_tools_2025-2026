from sqlalchemy import create_engine, text

from parsers.common import BookRecord, parse_book_html, split_items
from parsers.database import get_engine, save_book

SAMPLE_HTML = """
<html><body>
  <div id="product_gallery"><img src="../../media/cache/cover.jpg"></div>
  <div class="product_main">
    <h1>Test Book</h1>
    <p class="star-rating Four"></p>
    <p class="price_color">£12.50</p>
    <p class="availability">In stock (3 available)</p>
  </div>
  <div id="product_description"></div><p>A useful description.</p>
</body></html>
"""


def test_parse_book_html() -> None:
    url = "https://books.toscrape.com/catalogue/test_1/index.html"
    record = parse_book_html(url, SAMPLE_HTML)
    assert record.title == "Test Book"
    assert record.rating == "Four"
    assert record.price == "£12.50"
    assert record.description == "A useful description."
    assert record.cover_url == "https://books.toscrape.com/media/cache/cover.jpg"


def test_chunks_are_balanced() -> None:
    chunks = split_items([str(number) for number in range(10)], 3)
    assert [len(chunk) for chunk in chunks] == [4, 3, 3]


def test_save_book_upserts_by_source_url(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'books.db'}"
    engine = create_engine(database_url)
    with engine.begin() as connection:
        connection.execute(
            text(
                """
                CREATE TABLE books (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title VARCHAR NOT NULL,
                    description VARCHAR,
                    cover_url VARCHAR,
                    source_url VARCHAR UNIQUE
                )
                """
            )
        )

    first = BookRecord(
        "First title", None, None, "https://example.test/1", None, None, None
    )
    second = BookRecord(
        "Updated title", None, None, "https://example.test/1", None, None, None
    )
    first_id = save_book(first, database_url)
    second_id = save_book(second, database_url)

    assert first_id == second_id
    with get_engine(database_url).connect() as connection:
        assert (
            connection.execute(text("SELECT title FROM books")).scalar_one()
            == "Updated title"
        )
