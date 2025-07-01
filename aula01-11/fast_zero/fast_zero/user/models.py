from datetime import datetime

from pwdlib import PasswordHash
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fast_zero.database.tables import table_registry
from fast_zero.todo.models import Todo

passwd_context = PasswordHash.recommended()


@table_registry.mapped_as_dataclass
class User:
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    todos: Mapped[list[Todo]] = relationship(
        init=False,
        cascade='all, delete-orphan',
        lazy='selectin',
    )

    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now(), onupdate=func.now()
    )
