from datetime import datetime

from pydantic import EmailStr
from sqlmodel import Field, SQLModel

from app.models import BookCondition, EntryStatus, ExchangeStatus


class UserCreate(SQLModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=50)
    full_name: str = Field(min_length=1, max_length=120)
    password: str = Field(min_length=8, max_length=128)


class UserRead(SQLModel):
    id: int
    email: EmailStr
    username: str
    full_name: str
    is_active: bool
    created_at: datetime


class PasswordChange(SQLModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=128)


class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


class AuthorCreate(SQLModel):
    name: str = Field(min_length=1, max_length=160)
    biography: str | None = None


class AuthorUpdate(SQLModel):
    name: str | None = Field(default=None, min_length=1, max_length=160)
    biography: str | None = None


class AuthorRead(SQLModel):
    id: int
    name: str
    biography: str | None = None


class BookAuthorCreate(SQLModel):
    author_id: int
    role: str = Field(default="author", min_length=1, max_length=50)
    position: int = Field(default=1, ge=1)


class BookAuthorRead(SQLModel):
    author: AuthorRead
    role: str
    position: int


class BookCreate(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    isbn: str | None = Field(default=None, max_length=20)
    description: str | None = None
    published_year: int | None = Field(default=None, ge=0, le=3000)
    cover_url: str | None = Field(default=None, max_length=1000)
    source_url: str | None = Field(default=None, max_length=1000)
    authors: list[BookAuthorCreate] = Field(default_factory=list)


class BookUpdate(SQLModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    isbn: str | None = Field(default=None, max_length=20)
    description: str | None = None
    published_year: int | None = Field(default=None, ge=0, le=3000)
    cover_url: str | None = Field(default=None, max_length=1000)
    source_url: str | None = Field(default=None, max_length=1000)


class BookRead(SQLModel):
    id: int
    title: str
    isbn: str | None = None
    description: str | None = None
    published_year: int | None = None
    cover_url: str | None = None
    source_url: str | None = None
    authors: list[BookAuthorRead] = Field(default_factory=list)


class LibraryEntryCreate(SQLModel):
    book_id: int
    condition: BookCondition = BookCondition.good
    status: EntryStatus = EntryStatus.available
    notes: str | None = Field(default=None, max_length=1000)


class LibraryEntryUpdate(SQLModel):
    condition: BookCondition | None = None
    status: EntryStatus | None = None
    notes: str | None = Field(default=None, max_length=1000)


class LibraryEntryRead(SQLModel):
    id: int
    owner: UserRead
    book: BookRead
    condition: BookCondition
    status: EntryStatus
    notes: str | None = None
    added_at: datetime


class ExchangeCreate(SQLModel):
    requested_entry_id: int
    offered_entry_id: int | None = None
    message: str | None = Field(default=None, max_length=1000)


class ExchangeStatusUpdate(SQLModel):
    status: ExchangeStatus


class ExchangeRead(SQLModel):
    id: int
    requester: UserRead
    requested_entry: LibraryEntryRead
    offered_entry: LibraryEntryRead | None = None
    status: ExchangeStatus
    message: str | None = None
    created_at: datetime
    updated_at: datetime
