from enum import Enum

from pydantic import BaseModel, Field


class BookCondition(str, Enum):
    new = "new"
    good = "good"
    worn = "worn"


class User(BaseModel):
    id: int
    username: str
    full_name: str


class Author(BaseModel):
    id: int
    name: str


class Book(BaseModel):
    id: int
    title: str
    authors: list[Author] = Field(default_factory=list)


class LibraryEntry(BaseModel):
    id: int
    owner: User
    book: Book
    condition: BookCondition = BookCondition.good
    notes: str | None = None
