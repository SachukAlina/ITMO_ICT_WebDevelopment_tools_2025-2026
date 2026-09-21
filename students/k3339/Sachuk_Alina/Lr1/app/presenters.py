from fastapi import HTTPException
from sqlmodel import Session, select

from app.models import Author, Book, BookAuthorLink, ExchangeRequest, LibraryEntry, User
from app.schemas import (
    AuthorRead,
    BookAuthorRead,
    BookRead,
    ExchangeRead,
    LibraryEntryRead,
    UserRead,
)


def present_user(user: User) -> UserRead:
    return UserRead.model_validate(user)


def present_book(session: Session, book: Book) -> BookRead:
    links = session.exec(
        select(BookAuthorLink)
        .where(BookAuthorLink.book_id == book.id)
        .order_by(BookAuthorLink.position)
    ).all()
    authors: list[BookAuthorRead] = []
    for link in links:
        author = session.get(Author, link.author_id)
        if author is not None:
            authors.append(
                BookAuthorRead(
                    author=AuthorRead.model_validate(author),
                    role=link.role,
                    position=link.position,
                )
            )
    return BookRead(**book.model_dump(), authors=authors)


def present_library_entry(session: Session, entry: LibraryEntry) -> LibraryEntryRead:
    owner = session.get(User, entry.owner_id)
    book = session.get(Book, entry.book_id)
    if owner is None or book is None:
        raise HTTPException(status_code=500, detail="Broken library entry relation")
    return LibraryEntryRead(
        id=entry.id,
        owner=present_user(owner),
        book=present_book(session, book),
        condition=entry.condition,
        status=entry.status,
        notes=entry.notes,
        added_at=entry.added_at,
    )


def present_exchange(session: Session, exchange: ExchangeRequest) -> ExchangeRead:
    requester = session.get(User, exchange.requester_id)
    requested_entry = session.get(LibraryEntry, exchange.requested_entry_id)
    offered_entry = (
        session.get(LibraryEntry, exchange.offered_entry_id)
        if exchange.offered_entry_id is not None
        else None
    )
    if requester is None or requested_entry is None:
        raise HTTPException(status_code=500, detail="Broken exchange relation")
    return ExchangeRead(
        id=exchange.id,
        requester=present_user(requester),
        requested_entry=present_library_entry(session, requested_entry),
        offered_entry=(
            present_library_entry(session, offered_entry) if offered_entry else None
        ),
        status=exchange.status,
        message=exchange.message,
        created_at=exchange.created_at,
        updated_at=exchange.updated_at,
    )
