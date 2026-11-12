"""Account: Google/Apple sign-in, profile settings."""

from urllib.parse import urlencode

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.routes import is_premium
from app.config import get_settings
from app.db import get_session
from app.models import Chat, Madhhab, ScholarQuestion, User
from app.oauth import VerifiedIdentity, verify_id_token
from app.schemas import Language, TokenResponse
from app.security import bearer, create_token, current_user, optional_user

router = APIRouter(prefix="/v1")


class SignInRequest(BaseModel):
    id_token: str
    name: str | None = None  # Apple only sends the name on first sign-in, from the app


class Profile(BaseModel):
    user_id: str
    email: str | None
    display_name: str | None
    signed_in_with: str | None
    preferred_language: str
    madhhab: Madhhab | None
    plan: str
    premium_active: bool


class ProfileUpdate(BaseModel):
    preferred_language: Language | None = None
    madhhab: Madhhab | None = None
    clear_madhhab: bool = False  # set true to go back to "show all schools side by side"


def _profile(u: User) -> Profile:
    return Profile(
        user_id=u.id, email=u.email, display_name=u.display_name, signed_in_with=u.auth_provider,
        preferred_language=u.preferred_language, madhhab=u.madhhab, plan=u.plan.value,
        premium_active=is_premium(u),
    )


async def link_identity(session: AsyncSession, ident: VerifiedIdentity, guest: User | None,
                        name: str | None = None) -> User:
    """Return the account for this identity, keeping the guest's history.

    - Identity already linked to an account: move the guest's chats there.
    - Otherwise: attach the identity to the guest account (or create one).
    """
    existing = (await session.execute(
        select(User).where(User.auth_provider == ident.provider, User.provider_subject == ident.subject)
    )).scalar_one_or_none()

    if existing is not None:
        if guest is not None and guest.id != existing.id and guest.auth_provider is None:
            await session.execute(update(Chat).where(Chat.user_id == guest.id).values(user_id=existing.id))
            await session.execute(
                update(ScholarQuestion).where(ScholarQuestion.user_id == guest.id).values(user_id=existing.id)
            )
        user = existing
    elif guest is not None and guest.auth_provider is None:
        user = guest
        user.auth_provider, user.provider_subject = ident.provider, ident.subject
    else:
        user = User(auth_provider=ident.provider, provider_subject=ident.subject)
        session.add(user)

    user.email = ident.email or user.email
    user.display_name = user.display_name or ident.name or name
    await session.commit()
    return user


ANDROID_PACKAGE = "com.islamicguru.islamic_guru"


@router.post("/auth/apple/callback", include_in_schema=False)
async def apple_android_callback(request: Request) -> RedirectResponse:
    """Apple sign-in on Android runs in a browser tab; Apple posts the result here and we
    hand it back to the app (the sign_in_with_apple package's documented redirect)."""
    form = await request.form()
    query = urlencode({k: v for k, v in form.items() if isinstance(v, str)})
    return RedirectResponse(
        f"intent://callback?{query}#Intent;package={ANDROID_PACKAGE};scheme=signinwithapple;end",
        status_code=307,
    )


@router.post("/auth/{provider}", response_model=TokenResponse)
async def sign_in(
    provider: str,
    req: SignInRequest,
    creds: HTTPAuthorizationCredentials | None = Depends(bearer),
    session: AsyncSession = Depends(get_session),
) -> TokenResponse:
    ident = verify_id_token(provider, req.id_token, get_settings())
    guest = await optional_user(creds, session)
    user = await link_identity(session, ident, guest, req.name)
    return TokenResponse(access_token=create_token(user.id), user_id=user.id)


@router.get("/me", response_model=Profile)
async def me(user: User = Depends(current_user)) -> Profile:
    return _profile(user)


@router.patch("/me", response_model=Profile)
async def update_me(
    req: ProfileUpdate, user: User = Depends(current_user), session: AsyncSession = Depends(get_session)
) -> Profile:
    if req.preferred_language is not None:
        user.preferred_language = req.preferred_language.value
    if req.clear_madhhab:
        user.madhhab = None
    elif req.madhhab is not None:
        user.madhhab = req.madhhab
    await session.commit()
    return _profile(user)
