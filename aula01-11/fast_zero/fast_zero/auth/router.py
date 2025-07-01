from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fast_zero.auth.schemas import Token
from fast_zero.auth.security import (
    create_access_token,
    get_current_user,
    verify_password,
)
from fast_zero.database.config import get_session
from fast_zero.user.models import User

router = APIRouter(prefix='/auth', tags=['auth'])

OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]
Session = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('/token', status_code=HTTPStatus.OK, response_model=Token)
async def login(form_data: OAuth2Form, session: Session):
    user = await session.scalar(
        select(User).where(User.email == form_data.username)
    )

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Invalid username or password',
        )

    token, expires_in = create_access_token(data={'sub': user.email})

    return Token(
        access_token=token,
        token_type='Bearer',
        expires_in=expires_in,
    )


@router.post('/refresh_token', status_code=HTTPStatus.OK, response_model=Token)
def refresh_token(user: CurrentUser):
    token, expires_in = create_access_token(data={'sub': user.email})

    return Token(
        access_token=token, token_type='Bearer', expires_in=expires_in
    )
