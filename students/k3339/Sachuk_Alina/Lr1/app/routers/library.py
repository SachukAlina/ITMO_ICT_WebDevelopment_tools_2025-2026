from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from app.models import Book, LibraryEntry
from app.presenters import present_library_entry
from app.schemas import LibraryEntryCreate, LibraryEntryRead, LibraryEntryUpdate
from app.security import CurrentUser, SessionDep

router = APIRouter(prefix="/library", tags=["library"])


@router.get("", response_model=list[LibraryEntryRead])
def list_available_entries(session: SessionDep) -> list[LibraryEntryRead]:
    entries = session.exec(select(LibraryEntry).order_by(LibraryEntry.added_at)).all()
    return [present_library_entry(session, entry) for entry in entries]


@router.get("/me", response_model=list[LibraryEntryRead])
def list_my_entries(
    session: SessionDep, current_user: CurrentUser
) -> list[LibraryEntryRead]:
    entries = session.exec(
        select(LibraryEntry).where(LibraryEntry.owner_id == current_user.id)
    ).all()
    return [present_library_entry(session, entry) for entry in entries]


@router.get("/{entry_id}", response_model=LibraryEntryRead)
def get_entry(entry_id: int, session: SessionDep) -> LibraryEntryRead:
    entry = session.get(LibraryEntry, entry_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Library entry not found")
    return present_library_entry(session, entry)


@router.post("", response_model=LibraryEntryRead, status_code=status.HTTP_201_CREATED)
def create_entry(
    payload: LibraryEntryCreate, session: SessionDep, current_user: CurrentUser
) -> LibraryEntryRead:
    if session.get(Book, payload.book_id) is None:
        raise HTTPException(status_code=404, detail="Book not found")
    entry = LibraryEntry(owner_id=current_user.id, **payload.model_dump())
    session.add(entry)
    session.commit()
    session.refresh(entry)
    return present_library_entry(session, entry)


@router.patch("/{entry_id}", response_model=LibraryEntryRead)
def update_entry(
    entry_id: int,
    payload: LibraryEntryUpdate,
    session: SessionDep,
    current_user: CurrentUser,
) -> LibraryEntryRead:
    entry = session.get(LibraryEntry, entry_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Library entry not found")
    if entry.owner_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Only the owner can edit this entry"
        )
    entry.sqlmodel_update(payload.model_dump(exclude_unset=True))
    session.add(entry)
    session.commit()
    session.refresh(entry)
    return present_library_entry(session, entry)


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_entry(entry_id: int, session: SessionDep, current_user: CurrentUser) -> None:
    entry = session.get(LibraryEntry, entry_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Library entry not found")
    if entry.owner_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Only the owner can delete this entry"
        )
    session.delete(entry)
    session.commit()
