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

SECRET_KEY = 'segredo_bem_segredoso'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_SEC = 300
pwd_context = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


def create_access_token(data: dict):
    to_encode = data.copy()
    # TODO: como funciona essa soma do datetime com o timedelta?
    expire = datetime.now(tz=ZoneInfo('UTC')) + timedelta(
        seconds=ACCESS_TOKEN_EXPIRE_SEC
    )
    to_encode.update({'exp': expire})
    encoded_jwt = encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def get_password_hash(password: str):
    return pwd_context.hash(password)


def verify_password(plain_pass: str, hashed_pass: str):
    return pwd_context.verify(plain_pass, hashed_pass)


def get_current_user(
    session: Session = Depends(get_session),
    token: str = Depends(oauth2_scheme),
):
    credentials_exception = HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )

    try:
        payload = decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        sub_email = payload.get('sub')

        if not sub_email:
            raise credentials_exception

    except DecodeError:
        raise credentials_exception
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail='Expired token'
        )

    user = session.scalar(select(User).where(User.email == sub_email))

    if not user:
        raise credentials_exception

    return user
