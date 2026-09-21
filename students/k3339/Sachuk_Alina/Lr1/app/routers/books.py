from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from app.models import Author, Book, BookAuthorLink, LibraryEntry
from app.presenters import present_book
from app.schemas import BookAuthorCreate, BookCreate, BookRead, BookUpdate
from app.security import CurrentUser, SessionDep

router = APIRouter(prefix="/books", tags=["books"])


@router.get("", response_model=list[BookRead])
def list_books(session: SessionDep) -> list[BookRead]:
    books = session.exec(select(Book).order_by(Book.title)).all()
    return [present_book(session, book) for book in books]


@router.get("/{book_id}", response_model=BookRead)
def get_book(book_id: int, session: SessionDep) -> BookRead:
    book = session.get(Book, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return present_book(session, book)


@router.post("", response_model=BookRead, status_code=status.HTTP_201_CREATED)
def create_book(payload: BookCreate, session: SessionDep, _: CurrentUser) -> BookRead:
    book_data = payload.model_dump(exclude={"authors"})
    book = Book.model_validate(book_data)
    session.add(book)
    try:
        session.flush()
        for author_data in payload.authors:
            if session.get(Author, author_data.author_id) is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"Author {author_data.author_id} not found",
                )
            session.add(BookAuthorLink(book_id=book.id, **author_data.model_dump()))
        session.commit()
    except HTTPException:
        session.rollback()
        raise
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=409, detail="Book or author link already exists"
        ) from None
    session.refresh(book)
    return present_book(session, book)


@router.patch("/{book_id}", response_model=BookRead)
def update_book(
    book_id: int, payload: BookUpdate, session: SessionDep, _: CurrentUser
) -> BookRead:
    book = session.get(Book, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    book.sqlmodel_update(payload.model_dump(exclude_unset=True))
    session.add(book)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=409, detail="Book identifier already exists"
        ) from None
    session.refresh(book)
    return present_book(session, book)


@router.post("/{book_id}/authors", response_model=BookRead)
def add_book_author(
    book_id: int,
    payload: BookAuthorCreate,
    session: SessionDep,
    _: CurrentUser,
) -> BookRead:
    book = session.get(Book, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    if session.get(Author, payload.author_id) is None:
        raise HTTPException(status_code=404, detail="Author not found")
    session.add(BookAuthorLink(book_id=book_id, **payload.model_dump()))
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=409, detail="Author already linked to this book"
        ) from None
    return present_book(session, book)


@router.delete("/{book_id}/authors/{author_id}", response_model=BookRead)
def remove_book_author(
    book_id: int, author_id: int, session: SessionDep, _: CurrentUser
) -> BookRead:
    book = session.get(Book, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    link = session.get(BookAuthorLink, (book_id, author_id))
    if link is None:
        raise HTTPException(status_code=404, detail="Author link not found")
    session.delete(link)
    session.commit()
    return present_book(session, book)


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int, session: SessionDep, _: CurrentUser) -> None:
    book = session.get(Book, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    entry = session.exec(
        select(LibraryEntry).where(LibraryEntry.book_id == book_id)
    ).first()
    if entry:
        raise HTTPException(status_code=409, detail="Book is present in user libraries")
    links = session.exec(
        select(BookAuthorLink).where(BookAuthorLink.book_id == book_id)
    ).all()
    for link in links:
        session.delete(link)
    session.delete(book)
    session.commit()
