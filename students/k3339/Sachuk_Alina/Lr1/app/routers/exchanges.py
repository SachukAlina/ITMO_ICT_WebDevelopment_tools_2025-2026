from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import or_
from sqlmodel import select

from app.models import EntryStatus, ExchangeRequest, ExchangeStatus, LibraryEntry
from app.presenters import present_exchange
from app.schemas import ExchangeCreate, ExchangeRead, ExchangeStatusUpdate
from app.security import CurrentUser, SessionDep

router = APIRouter(prefix="/exchanges", tags=["exchanges"])


@router.get("", response_model=list[ExchangeRead])
def list_my_exchanges(
    session: SessionDep, current_user: CurrentUser
) -> list[ExchangeRead]:
    owned_entry_ids = select(LibraryEntry.id).where(
        LibraryEntry.owner_id == current_user.id
    )
    exchanges = session.exec(
        select(ExchangeRequest)
        .where(
            or_(
                ExchangeRequest.requester_id == current_user.id,
                ExchangeRequest.requested_entry_id.in_(owned_entry_ids),
            )
        )
        .order_by(ExchangeRequest.created_at.desc())
    ).all()
    return [present_exchange(session, exchange) for exchange in exchanges]


@router.get("/{exchange_id}", response_model=ExchangeRead)
def get_exchange(
    exchange_id: int, session: SessionDep, current_user: CurrentUser
) -> ExchangeRead:
    exchange = _get_visible_exchange(exchange_id, session, current_user.id)
    return present_exchange(session, exchange)


@router.post("", response_model=ExchangeRead, status_code=status.HTTP_201_CREATED)
def create_exchange(
    payload: ExchangeCreate, session: SessionDep, current_user: CurrentUser
) -> ExchangeRead:
    requested = session.get(LibraryEntry, payload.requested_entry_id)
    if requested is None:
        raise HTTPException(status_code=404, detail="Requested library entry not found")
    if requested.owner_id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot request your own book")
    if requested.status != EntryStatus.available:
        raise HTTPException(status_code=409, detail="Requested book is not available")
    if payload.offered_entry_id is not None:
        offered = session.get(LibraryEntry, payload.offered_entry_id)
        if offered is None:
            raise HTTPException(
                status_code=404, detail="Offered library entry not found"
            )
        if offered.owner_id != current_user.id:
            raise HTTPException(
                status_code=403, detail="You can only offer your own book"
            )
        if offered.status != EntryStatus.available:
            raise HTTPException(status_code=409, detail="Offered book is not available")

    exchange = ExchangeRequest(requester_id=current_user.id, **payload.model_dump())
    session.add(exchange)
    session.commit()
    session.refresh(exchange)
    return present_exchange(session, exchange)


@router.patch("/{exchange_id}", response_model=ExchangeRead)
def update_exchange_status(
    exchange_id: int,
    payload: ExchangeStatusUpdate,
    session: SessionDep,
    current_user: CurrentUser,
) -> ExchangeRead:
    exchange = session.get(ExchangeRequest, exchange_id)
    if exchange is None:
        raise HTTPException(status_code=404, detail="Exchange request not found")
    requested = session.get(LibraryEntry, exchange.requested_entry_id)
    if requested is None:
        raise HTTPException(status_code=500, detail="Broken exchange relation")
    if exchange.status != ExchangeStatus.pending:
        raise HTTPException(
            status_code=409, detail="Exchange request is already closed"
        )

    if payload.status == ExchangeStatus.cancelled:
        if exchange.requester_id != current_user.id:
            raise HTTPException(status_code=403, detail="Only requester can cancel")
    elif payload.status in {ExchangeStatus.accepted, ExchangeStatus.rejected}:
        if requested.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Only book owner can respond")
    else:
        raise HTTPException(status_code=400, detail="Unsupported status transition")

    exchange.status = payload.status
    exchange.updated_at = datetime.now(timezone.utc)
    if payload.status == ExchangeStatus.accepted:
        requested.status = EntryStatus.reserved
        session.add(requested)
        if exchange.offered_entry_id is not None:
            offered = session.get(LibraryEntry, exchange.offered_entry_id)
            if offered:
                offered.status = EntryStatus.reserved
                session.add(offered)
    session.add(exchange)
    session.commit()
    session.refresh(exchange)
    return present_exchange(session, exchange)


@router.delete("/{exchange_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_exchange(
    exchange_id: int, session: SessionDep, current_user: CurrentUser
) -> None:
    exchange = session.get(ExchangeRequest, exchange_id)
    if exchange is None:
        raise HTTPException(status_code=404, detail="Exchange request not found")
    if exchange.requester_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only requester can delete")
    if exchange.status == ExchangeStatus.accepted:
        raise HTTPException(
            status_code=409, detail="Accepted exchange cannot be deleted"
        )
    session.delete(exchange)
    session.commit()


def _get_visible_exchange(
    exchange_id: int, session: SessionDep, user_id: int
) -> ExchangeRequest:
    exchange = session.get(ExchangeRequest, exchange_id)
    if exchange is None:
        raise HTTPException(status_code=404, detail="Exchange request not found")
    requested = session.get(LibraryEntry, exchange.requested_entry_id)
    if requested is None:
        raise HTTPException(status_code=500, detail="Broken exchange relation")
    if exchange.requester_id != user_id and requested.owner_id != user_id:
        raise HTTPException(status_code=403, detail="Exchange request is private")
    return exchange
