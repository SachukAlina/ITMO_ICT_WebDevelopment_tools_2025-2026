from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from app.models import Author, BookAuthorLink
from app.schemas import AuthorCreate, AuthorRead, AuthorUpdate
from app.security import CurrentUser, SessionDep

router = APIRouter(prefix="/authors", tags=["authors"])


@router.get("", response_model=list[AuthorRead])
def list_authors(session: SessionDep) -> list[Author]:
    return list(session.exec(select(Author).order_by(Author.name)).all())


@router.get("/{author_id}", response_model=AuthorRead)
def get_author(author_id: int, session: SessionDep) -> Author:
    author = session.get(Author, author_id)
    if author is None:
        raise HTTPException(status_code=404, detail="Author not found")
    return author


@router.post("", response_model=AuthorRead, status_code=status.HTTP_201_CREATED)
def create_author(payload: AuthorCreate, session: SessionDep, _: CurrentUser) -> Author:
    author = Author.model_validate(payload)
    session.add(author)
    session.commit()
    session.refresh(author)
    return author


@router.patch("/{author_id}", response_model=AuthorRead)
def update_author(
    author_id: int, payload: AuthorUpdate, session: SessionDep, _: CurrentUser
) -> Author:
    author = session.get(Author, author_id)
    if author is None:
        raise HTTPException(status_code=404, detail="Author not found")
    author.sqlmodel_update(payload.model_dump(exclude_unset=True))
    session.add(author)
    session.commit()
    session.refresh(author)
    return author


@router.delete("/{author_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_author(author_id: int, session: SessionDep, _: CurrentUser) -> None:
    author = session.get(Author, author_id)
    if author is None:
        raise HTTPException(status_code=404, detail="Author not found")
    link = session.exec(
        select(BookAuthorLink).where(BookAuthorLink.author_id == author_id)
    ).first()
    if link:
        raise HTTPException(status_code=409, detail="Author is linked to books")
    session.delete(author)
    session.commit()
