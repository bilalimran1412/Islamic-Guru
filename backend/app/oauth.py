"""Verify Google and Apple ID tokens sent by the app after native sign-in."""

from dataclasses import dataclass

import jwt
from fastapi import HTTPException, status

from app.config import Settings


@dataclass(frozen=True)
class ProviderConfig:
    jwks_url: str
    issuers: tuple[str, ...]


PROVIDERS = {
    "google": ProviderConfig(
        "https://www.googleapis.com/oauth2/v3/certs",
        ("https://accounts.google.com", "accounts.google.com"),
    ),
    "apple": ProviderConfig("https://appleid.apple.com/auth/keys", ("https://appleid.apple.com",)),
}

_jwks_clients: dict[str, jwt.PyJWKClient] = {}


@dataclass
class VerifiedIdentity:
    provider: str
    subject: str
    email: str | None
    name: str | None


def _audiences(provider: str, settings: Settings) -> list[str]:
    raw = settings.google_client_ids if provider == "google" else settings.apple_client_ids
    return [a.strip() for a in raw.split(",") if a.strip()]


def verify_id_token(provider: str, token: str, settings: Settings) -> VerifiedIdentity:
    cfg = PROVIDERS.get(provider)
    if cfg is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Unknown provider")
    audiences = _audiences(provider, settings)
    if not audiences:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, f"{provider} sign-in is not configured")

    client = _jwks_clients.setdefault(provider, jwt.PyJWKClient(cfg.jwks_url, cache_keys=True))
    try:
        key = client.get_signing_key_from_jwt(token)
        claims = jwt.decode(
            token, key.key, algorithms=["RS256"], audience=audiences, issuer=list(cfg.issuers),
            options={"require": ["sub", "exp", "iss", "aud"]},
        )
    except (jwt.PyJWTError, jwt.PyJWKClientError):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid sign-in token") from None

    return VerifiedIdentity(provider=provider, subject=claims["sub"], email=claims.get("email"),
                            name=claims.get("name"))
