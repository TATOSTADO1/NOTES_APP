import base64
import hashlib
import hmac
import json
from datetime import datetime, timedelta, timezone
from uuid import UUID

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError

from CORE.config import settings


password_hasher = PasswordHasher()


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


def create_access_token(user_id: UUID) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = _encode(
        json.dumps({"sub": str(user_id), "exp": int(expires_at.timestamp())}).encode()
    )
    signature = _encode(
        hmac.new(settings.SECRET_KEY.encode(), payload.encode(), hashlib.sha256).digest()
    )
    return f"{payload}.{signature}"


def decode_access_token(token: str) -> UUID | None:
    try:
        payload, signature = token.split(".", 1)
        expected = _encode(
            hmac.new(settings.SECRET_KEY.encode(), payload.encode(), hashlib.sha256).digest()
        )
        if not hmac.compare_digest(signature, expected):
            return None
        data = json.loads(_decode(payload))
        if int(data["exp"]) <= int(datetime.now(timezone.utc).timestamp()):
            return None
        return UUID(data["sub"])
    except (ValueError, TypeError, KeyError, json.JSONDecodeError):
        return None
