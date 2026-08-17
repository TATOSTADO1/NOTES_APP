from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from CORE.database import Base


class AuthSession(Base):
    __tablename__ = "auth_sessions"

    id_session: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    id_user: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id_user", name="fk_auth_session_user"),
        nullable=False,
        index=True,
    )
    device_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    last_used_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
    )


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id_refresh_token: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    id_session: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("auth_sessions.id_session", name="fk_refresh_token_session"),
        nullable=False,
        index=True,
    )
    token_hash: Mapped[str] = mapped_column(
        String(64), unique=True, nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    replaced_by_id: Mapped[UUID | None] = mapped_column(
        Uuid,
        ForeignKey("refresh_tokens.id_refresh_token", name="fk_refresh_token_replacement"),
        nullable=True,
    )

    session: Mapped[AuthSession] = relationship(back_populates="refresh_tokens")
