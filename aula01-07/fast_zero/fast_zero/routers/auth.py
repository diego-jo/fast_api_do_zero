from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.schemas import Token
from fast_zero.security import (
    create_jwt_token,
    verify_password,
)

router = APIRouter(prefix='/auth', tags=['auth'])

OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]
InjectedSession = Annotated[Session, Depends(get_session)]


@router.post('/token', status_code=HTTPStatus.OK, response_model=Token)
def create_token(
    form_data: OAuth2Form,
    session: InjectedSession,
):
    user = session.scalar(select(User).where(User.email == form_data.username))

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='invalid username or password',
        )

    token = create_jwt_token(data={'sub': form_data.username})

    return Token(access_token=token, token_type='bearer')
