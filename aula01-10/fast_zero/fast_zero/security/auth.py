from datetime import datetime, timedelta
from http import HTTPStatus
from typing import Annotated
from zoneinfo import ZoneInfo

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import decode, encode
from jwt.exceptions import DecodeError, ExpiredSignatureError
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fast_zero.config.database import get_session
from fast_zero.models.user import User
from settings import Settings

Session = Annotated[AsyncSession, Depends(get_session)]

oauth2_schema = OAuth2PasswordBearer(tokenUrl='/auth/token')
env = Settings()
passwd_context = PasswordHash.recommended()


def verify_password(plain_password: str, hashed_password: str):
    return passwd_context.verify(plain_password, hashed_password)


def create_jwt_token(data: dict):
    to_encode = data.copy()
    expiration_time = datetime.now(tz=ZoneInfo('UTC')) + timedelta(
        seconds=env.TOKEN_TIME_EXPIRATION_SECS
    )

    to_encode.update({'exp': expiration_time})
    token = encode(to_encode, env.SECRET_KEY, algorithm=env.ALGORITHM)

    return token


async def get_current_user(
    session: Session, token: str = Depends(oauth2_schema)
):
    unauthorized_exception = HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED, detail='invalid credentials'
    )

    try:
        d_token = decode(token, env.SECRET_KEY, algorithms=[env.ALGORITHM])
        email = d_token.get('sub')

        if not email:
            raise unauthorized_exception

    except DecodeError:
        raise unauthorized_exception
    except ExpiredSignatureError:
        raise unauthorized_exception

    user = await session.scalar(select(User).where(User.email == email))

    if not user:
        raise unauthorized_exception

    return user
