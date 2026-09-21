import os
from functools import lru_cache

from sqlalchemy import Engine, create_engine, text

from parsers.common import BookRecord

DEFAULT_DATABASE_URL = (
    "postgresql+psycopg://bookcrossing:bookcrossing@localhost:5432/bookcrossing"
)


@lru_cache(maxsize=None)
def get_engine(database_url: str) -> Engine:
    return create_engine(database_url, pool_pre_ping=True)


def save_book(record: BookRecord, database_url: str | None = None) -> int:
    """Insert a parsed book or update it when its source URL already exists."""
    url = database_url or os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)
    statement = text(
        """
        INSERT INTO books (title, description, cover_url, source_url)
        VALUES (:title, :description, :cover_url, :source_url)
        ON CONFLICT (source_url) DO UPDATE SET
            title = EXCLUDED.title,
            description = EXCLUDED.description,
            cover_url = EXCLUDED.cover_url
        RETURNING id
        """
    )
    with get_engine(url).begin() as connection:
        return int(
            connection.execute(
                statement,
                {
                    "title": record.title,
                    "description": record.description,
                    "cover_url": record.cover_url,
                    "source_url": record.source_url,
                },
            ).scalar_one()
        )
