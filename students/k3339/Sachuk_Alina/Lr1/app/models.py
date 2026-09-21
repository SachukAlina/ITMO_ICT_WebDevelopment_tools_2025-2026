from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import Column, DateTime, Index, String, UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class BookCondition(str, Enum):
    new = "new"
    good = "good"
    worn = "worn"


class EntryStatus(str, Enum):
    available = "available"
    reserved = "reserved"
    unavailable = "unavailable"


class ExchangeStatus(str, Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"
    cancelled = "cancelled"


class BookAuthorLink(SQLModel, table=True):
    __tablename__ = "book_authors"

    book_id: int = Field(foreign_key="books.id", primary_key=True, ondelete="CASCADE")
    author_id: int = Field(
        foreign_key="authors.id", primary_key=True, ondelete="CASCADE"
    )
    role: str = Field(default="author", max_length=50)
    position: int = Field(default=1, ge=1)

    book: "Book" = Relationship(back_populates="author_links")
    author: "Author" = Relationship(back_populates="book_links")


class User(SQLModel, table=True):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("email"),
        UniqueConstraint("username"),
        Index("ix_users_email", "email"),
        Index("ix_users_username", "username"),
    )

    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(sa_column=Column(String(320), nullable=False))
    username: str = Field(sa_column=Column(String(50), nullable=False))
    full_name: str = Field(max_length=120)
    password_hash: str
    is_active: bool = True
    created_at: datetime = Field(
        default_factory=utc_now, sa_type=DateTime(timezone=True)
    )

    library_entries: list["LibraryEntry"] = Relationship(back_populates="owner")


class Author(SQLModel, table=True):
    __tablename__ = "authors"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, max_length=160)
    biography: str | None = None

    book_links: list[BookAuthorLink] = Relationship(back_populates="author")


class Book(SQLModel, table=True):
    __tablename__ = "books"

    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(index=True, max_length=255)
    isbn: str | None = Field(default=None, index=True, max_length=20)
    description: str | None = None
    published_year: int | None = Field(default=None, ge=0, le=3000)
    cover_url: str | None = Field(default=None, max_length=1000)
    source_url: str | None = Field(
        default=None,
        sa_column=Column(String(1000), unique=True, nullable=True),
    )

    author_links: list[BookAuthorLink] = Relationship(back_populates="book")
    library_entries: list["LibraryEntry"] = Relationship(back_populates="book")


class LibraryEntry(SQLModel, table=True):
    __tablename__ = "library_entries"

    id: int | None = Field(default=None, primary_key=True)
    owner_id: int = Field(foreign_key="users.id", index=True)
    book_id: int = Field(foreign_key="books.id", index=True)
    condition: BookCondition = Field(default=BookCondition.good)
    status: EntryStatus = Field(default=EntryStatus.available)
    notes: str | None = Field(default=None, max_length=1000)
    added_at: datetime = Field(default_factory=utc_now, sa_type=DateTime(timezone=True))

    owner: User = Relationship(back_populates="library_entries")
    book: Book = Relationship(back_populates="library_entries")


class ExchangeRequest(SQLModel, table=True):
    __tablename__ = "exchange_requests"

    id: int | None = Field(default=None, primary_key=True)
    requester_id: int = Field(foreign_key="users.id", index=True)
    requested_entry_id: int = Field(foreign_key="library_entries.id", index=True)
    offered_entry_id: int | None = Field(
        default=None, foreign_key="library_entries.id", index=True
    )
    status: ExchangeStatus = Field(default=ExchangeStatus.pending)
    message: str | None = Field(default=None, max_length=1000)
    created_at: datetime = Field(
        default_factory=utc_now, sa_type=DateTime(timezone=True)
    )
    updated_at: datetime = Field(
        default_factory=utc_now, sa_type=DateTime(timezone=True)
    )
