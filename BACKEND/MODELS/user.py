from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import String, DateTime, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from CORE.database import Base
from sqlalchemy import func

'''mapped es un tipo de dato que se utiliza para mapear una columna de la base de datos a un atributo de una clase en SQLAlchemy.'''
'''mapped_column es una función que se utiliza para definir una columna en una tabla de la base de datos y mapearla a un atributo de una clase en SQLAlchemy.'''
class User(Base):

    __tablename__ = "users"

    id_user: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid4
    )

    username: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False
    )

    password_hash: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    server_default=func.now(),
    nullable=False
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
