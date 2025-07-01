from datetime import datetime, timedelta
from http import HTTPStatus
from typing import Annotated
from zoneinfo import ZoneInfo

from fastapi import Depends
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import decode, encode
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fast_zero.database.config import get_session
from fast_zero.user.models import User
from settings import settings

passwd_context = PasswordHash.recommended()
oauth2_schema = OAuth2PasswordBearer(
    tokenUrl='/auth/token', refreshUrl='/auth/refresh_token'
)

Session = Annotated[AsyncSession, Depends(get_session)]


def hash_password(plain_password: str):
    return passwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str):
    return passwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict):
    to_encode = data.copy()
    expiration_time = datetime.now(tz=ZoneInfo('UTC')) + timedelta(
        seconds=settings.TOKEN_TIME_EXPIRATION_SECS
    )

    to_encode.update({'exp': expiration_time})
    token = encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )

    return token, int(expiration_time.timestamp())


async def get_current_user(
    session: Session,
    token: str = Depends(oauth2_schema),
):
    credential_exception = HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authentication': 'Bearer'},
    )

    try:
        decoded_token = decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email = decoded_token.get('sub')

        if not email:
            raise credential_exception

    except InvalidTokenError:
        raise credential_exception

    user = await session.scalar(select(User).where(User.email == email))

    if not user:
        raise credential_exception

    return user


# TODO: mover para o contexto de users??
def permission_validation(
    user_id: int,
    user: Annotated[User, Depends(get_current_user)],
):
    if user_id != user.id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='not enough permissions to get user info',
        )

    return user
