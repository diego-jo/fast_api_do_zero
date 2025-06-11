from datetime import datetime, timedelta
from http import HTTPStatus
from zoneinfo import ZoneInfo

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import decode, encode
from jwt.exceptions import DecodeError, ExpiredSignatureError
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session

from fast_zero.database import get_session
from fast_zero.models import User
from settings import Settings

pass_context = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/token')
env = Settings()


def hash_password(plain_password: str):
    return pass_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str):
    return pass_context.verify(plain_password, hashed_password)


def create_jwt_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(tz=ZoneInfo('UTC')) + timedelta(
        seconds=env.TOKEN_EXPIRATION_TIME_SECONDS
    )
    to_encode.update({'exp': expire})
    token_jwt = encode(to_encode, env.SECRET_KEY, algorithm=env.ALGORITHM)

    return token_jwt


def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session),
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
            status_code=HTTPStatus.UNAUTHORIZED, detail='Expired token'
        )

    user = session.scalar(select(User).where(User.email == email))

    if not user:
        raise forbiden_exception

    return user
