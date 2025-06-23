from datetime import datetime

from pwdlib import PasswordHash
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, validates

from fast_zero.models.tables import table_registry

passwd_context = PasswordHash.recommended()


@table_registry.mapped_as_dataclass
class User:
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(
        init=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        init=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # TODO: validar tamanho minimo e complexidade do passwd
    @validates('password')
    def _hash_password(self, key, plain_password: str):  # noqa: PLR6301
        return passwd_context.hash(plain_password)
