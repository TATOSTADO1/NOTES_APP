from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    String,
    UniqueConstraint,
    Uuid,
    func,
)

from sqlalchemy.orm import Mapped, mapped_column

from CORE.database import Base

'''en table_args se define una restricción de clave única que asegura que la combinación de id_folder e id_user sea única en la tabla folders. Esto significa que un usuario no puede tener dos carpetas con el mismo id_folder.'''
class Folder(Base):
    __tablename__ = "folders"
    __table_args__ = (
        UniqueConstraint(
            "id_folder",
            "id_user",
            name="uq_folder_user"
        ),

        ForeignKeyConstraint(
            ["parent_folder_id", "id_user"],
            ["folders.id_folder", "folders.id_user"],
            name="fk_parent_folder_same_user"
        ),
    )

    id_folder: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid4
    )

    id_user: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey(
            "users.id_user",
            name="fk_folder_user"
        ),
        nullable=False
    )

    parent_folder_id: Mapped[UUID | None] = mapped_column(
        Uuid,
        nullable=True
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    color: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    icon: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
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
