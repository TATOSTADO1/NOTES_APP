from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    String,
    Text,
    Uuid,
    false,
    func,
)

from sqlalchemy.orm import Mapped, mapped_column

from CORE.database import Base


class Note(Base):
    __tablename__ = "notes"

    __table_args__ = (
        ForeignKeyConstraint(
            ["id_folder", "id_user"],
            ["folders.id_folder", "folders.id_user"],
            name="fk_note_folder_same_user"
        ),
    )

    id_note: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid4
    )

    id_user: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey(
            "users.id_user",
            name="fk_note_user"
        ),
        nullable=False
    )

    id_folder: Mapped[UUID | None] = mapped_column(
        Uuid,
        nullable=True
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    content: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    favorite: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=false()
    )

    deleted: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=false()
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )
