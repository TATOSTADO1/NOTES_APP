import base64
import hashlib
import hmac
import json
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from uuid import UUID

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError

from CORE.config import settings


password_hasher = PasswordHasher()


@dataclass(frozen=True)
class AccessTokenData:
    user_id: UUID
    session_id: UUID


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(password: str, encoded: str) -> bool:
    try:
        return password_hasher.verify(encoded, password)
    except (InvalidHashError, VerificationError, VerifyMismatchError):
        return False


def _encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _decode(data: str) -> bytes:
    return base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))


def create_refresh_token() -> str:
    return secrets.token_urlsafe(64)


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def create_access_token(user_id: UUID, session_id: UUID) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = _encode(
        json.dumps(
            {
                "sub": str(user_id),
                "sid": str(session_id),
                "typ": "access",
                "exp": int(expires_at.timestamp()),
            }
        ).encode()
    )
    signature = _encode(
        hmac.new(settings.SECRET_KEY.encode(), payload.encode(), hashlib.sha256).digest()
    )
    return f"{payload}.{signature}"


def decode_access_token(token: str) -> AccessTokenData | None:
    try:
        payload, signature = token.split(".", 1)
        expected = _encode(
            hmac.new(settings.SECRET_KEY.encode(), payload.encode(), hashlib.sha256).digest()
        )
        if not hmac.compare_digest(signature, expected):
            return None
        data = json.loads(_decode(payload))
        if data.get("typ") != "access":
            return None
        if int(data["exp"]) <= int(datetime.now(timezone.utc).timestamp()):
            return None
        return AccessTokenData(
            user_id=UUID(data["sub"]),
            session_id=UUID(data["sid"]),
        )
    except (ValueError, TypeError, KeyError, json.JSONDecodeError):
        return None
