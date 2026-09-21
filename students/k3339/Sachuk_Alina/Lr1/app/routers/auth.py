from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from app.models import User
from app.presenters import present_user
from app.schemas import PasswordChange, Token, UserCreate, UserRead
from app.security import (
    CurrentUser,
    SessionDep,
    create_access_token,
    hash_password,
    verify_password,
)

router = APIRouter(tags=["authentication"])


@router.post(
    "/auth/register", response_model=UserRead, status_code=status.HTTP_201_CREATED
)
def register(payload: UserCreate, session: SessionDep) -> UserRead:
    normalized_email = str(payload.email).lower()
    duplicate = session.exec(
        select(User).where(
            (User.email == normalized_email) | (User.username == payload.username)
        )
    ).first()
    if duplicate:
        raise HTTPException(
            status_code=409, detail="Email or username already registered"
        )

    user = User(
        email=normalized_email,
        username=payload.username,
        full_name=payload.full_name,
        password_hash=hash_password(payload.password),
    )
    session.add(user)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=409, detail="Email or username already registered"
        ) from None
    session.refresh(user)
    return present_user(user)


@router.post("/auth/token", response_model=Token)
def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep
) -> Token:
    user = session.exec(select(User).where(User.username == form.username)).first()
    if user is None or not verify_password(form.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Inactive user")
    return Token(access_token=create_access_token(user.id))


@router.get("/users/me", response_model=UserRead)
def read_current_user(current_user: CurrentUser) -> UserRead:
    return present_user(current_user)


@router.get("/users", response_model=list[UserRead])
def read_users(session: SessionDep, _: CurrentUser) -> list[UserRead]:
    return [present_user(user) for user in session.exec(select(User)).all()]


@router.post("/users/change-password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    payload: PasswordChange, current_user: CurrentUser, session: SessionDep
) -> None:
    if not verify_password(payload.current_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    current_user.password_hash = hash_password(payload.new_password)
    session.add(current_user)
    session.commit()
