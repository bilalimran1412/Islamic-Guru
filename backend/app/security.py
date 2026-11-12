"""Bearer-token auth.

MVP: the app creates a guest account on first launch and stores the token.
Google / Apple sign-in will attach an email to that same user later, so chat
history carries over.
"""

from datetime import UTC, datetime, timedelta

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db import get_session
from app.models import User

bearer = HTTPBearer(auto_error=False)
_ALGO = "HS256"


def create_token(user_id: str) -> str:
    s = get_settings()
    payload = {"sub": user_id, "exp": datetime.now(UTC) + timedelta(days=s.jwt_expiry_days)}
    return jwt.encode(payload, s.jwt_secret, algorithm=_ALGO)


async def current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer),
    session: AsyncSession = Depends(get_session),
) -> User:
    if creds is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing token")
    try:
        payload = jwt.decode(creds.credentials, get_settings().jwt_secret, algorithms=[_ALGO])
    except jwt.PyJWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token") from None
    user = await session.get(User, payload.get("sub"))
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Unknown user")
    return user


async def optional_user(creds: HTTPAuthorizationCredentials | None, session: AsyncSession) -> User | None:
    """The signed-in user if a valid token was sent, else None."""
    if creds is None:
        return None
    try:
        return await current_user(creds, session)
    except HTTPException:
        return None
