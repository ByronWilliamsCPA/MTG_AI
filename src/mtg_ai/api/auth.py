"""Authentication API: login and the current-user dependency.

User provisioning is intentionally not exposed as an open endpoint. For a
self-hosted, few-user deployment, accounts are created out of band via the CLI
(``mtg_ai user create``), so there is no unauthenticated account-creation
surface.
"""

from __future__ import annotations

import datetime  # noqa: TC003 - Pydantic resolves field annotations at runtime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

# Runtime import: FastAPI resolves dependency annotations at runtime, so this
# must not be moved into a TYPE_CHECKING block.
from sqlalchemy.orm import Session as DBSession  # noqa: TC002

from mtg_ai.auth.service import authenticate_user, get_user_for_token, issue_session
from mtg_ai.db.engine import get_session
from mtg_ai.schema.app_models import User

router = APIRouter(prefix="/auth", tags=["auth"])

_bearer = HTTPBearer(auto_error=False)


class LoginRequest(BaseModel):
    """Login credentials."""

    username: str = Field(..., min_length=1, max_length=64)
    password: str = Field(..., min_length=1)


class LoginResponse(BaseModel):
    """A newly issued session token."""

    token: str = Field(..., description="Opaque session token; store securely.")
    token_type: str = Field(default="bearer")
    expires_at: datetime.datetime = Field(..., description="Token expiry (UTC).")


class UserResponse(BaseModel):
    """Public view of a user."""

    id: str
    username: str


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
    session: Annotated[DBSession, Depends(get_session)],
) -> User:
    """Resolve the bearer token to the owning user or raise 401.

    This dependency is the basis for per-user scoping: every protected route
    derives its identity here and must filter all data by this user's id.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = get_user_for_token(session, credentials.credentials)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post("/login", response_model=LoginResponse)
def login(
    payload: LoginRequest,
    session: Annotated[DBSession, Depends(get_session)],
) -> LoginResponse:
    """Authenticate credentials and return a session token."""
    user = authenticate_user(session, payload.username, payload.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    session_row, raw_token = issue_session(session, user)
    session.commit()
    return LoginResponse(token=raw_token, expires_at=session_row.expires_at)


@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: CurrentUser) -> UserResponse:
    """Return the authenticated user. Demonstrates per-user scoping."""
    return UserResponse(id=str(current_user.id), username=current_user.username)
