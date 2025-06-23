from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fast_zero.config.database import get_session
from fast_zero.models.user import User
from fast_zero.schemas.token import Token
from fast_zero.security.auth import (
    create_jwt_token,
    get_current_user,
    verify_password,
)

router = APIRouter(prefix='/auth', tags=['auth'])

Session = Annotated[AsyncSession, Depends(get_session)]
Oauth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('/token', status_code=HTTPStatus.OK, response_model=Token)
async def login(session: Session, form_data: Oauth2Form):
    email = form_data.username
    user = await session.scalar(select(User).where(User.email == email))

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail='invalid credentials'
        )

    token = create_jwt_token(data={'sub': user.email})

    return Token(access_token=token, token_type='Bearer')


@router.post('/refresh_token', status_code=HTTPStatus.OK, response_model=Token)
def refresh(current_user: CurrentUser):
    token = create_jwt_token(data={'sub': current_user.email})

    return Token(access_token=token, token_type='Bearer')
