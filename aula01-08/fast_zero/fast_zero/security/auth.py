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

InjectedSession = Annotated[AsyncSession, Depends(get_session)]

oauth2_schema = OAuth2PasswordBearer(tokenUrl='/auth/token')
passwd_context = PasswordHash.recommended()
env = Settings()


def hash_password(plain_password: str):
    return passwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str):
    return passwd_context.verify(plain_password, hashed_password)


def create_jwt_token(data: dict):
    to_encode = data.copy()
    expiration_time = datetime.now(tz=ZoneInfo('UTC')) + timedelta(
        seconds=env.TOKEN_EXPIRATION_TIME_SECONDS
    )
    to_encode.update({'exp': expiration_time})
    token = encode(to_encode, env.SECRET_KEY, algorithm=env.ALGORITHM)

    return token


# TODO: centralizar lançamento de exceções do tipo HTTP em um handler??!!!
# para evitar qem em todo lugar no código tenham espalhadas chamadas a classe
# HTTPException do fastapi.
async def get_current_user(
    session: InjectedSession, token: str = Depends(oauth2_schema)
):
    forbiden_exception = HTTPException(
        status_code=HTTPStatus.FORBIDDEN, detail='not enough permissions'
    )

    try:
        decoded_token = decode(
            token, env.SECRET_KEY, algorithms=[env.ALGORITHM]
        )
        email = decoded_token.get('sub')

        if not email:
            raise forbiden_exception

    except DecodeError:
        raise forbiden_exception
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail='expired token'
        )

    db_user = await session.scalar(select(User).where(User.email == email))

    if not db_user:
        raise forbiden_exception

    return db_user
