from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.schemas import ListUsers, Token, UserRequest, UserResponse
from fast_zero.security import (
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
)

app = FastAPI()


@app.post(
    '/users', status_code=HTTPStatus.CREATED, response_model=UserResponse
)
def create_user(user: UserRequest, session: Session = Depends(get_session)):
    db_user = session.scalar(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )

    if db_user:
        if db_user.username == user.username:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='username already in use',
            )
        elif db_user.email == user.email:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT, detail='email already in use'
            )

    db_user = User(
        username=user.username,
        email=user.email,
        password=get_password_hash(user.password),
    )

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


@app.get('/users', status_code=HTTPStatus.OK, response_model=ListUsers)
def get_all_users(
    skip: int = 0, limit: int = 20, session: Session = Depends(get_session)
):
    users = session.scalars(select(User).offset(skip).limit(limit)).all()

    return {'users': users}


@app.get('/users/{id}', status_code=HTTPStatus.OK, response_model=UserResponse)
def get_user_by_id(id: int, session: Session = Depends(get_session)):
    db_user = session.scalar(select(User).where(User.id == id))

    if not db_user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )

    return db_user


@app.put('/users/{id}', status_code=HTTPStatus.OK, response_model=UserResponse)
def update_user(
    id: int,
    user: UserRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user.id != id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='not enough permissions'
        )

    # TODO: removido pois o usuário já é buscando na função get_current_user
    # como seria em caso de permissões mais abrangentes que apenas com o
    # usuário atual? ex: permissões de admin

    # db_user = session.scalar(select(User).where(User.id == id))
    # if not db_user:
    #     raise HTTPException(
    #         status_code=HTTPStatus.NOT_FOUND, detail='User not found'
    #     )

    try:
        current_user.username = user.username
        current_user.email = user.email
        current_user.password = get_password_hash(user.password)

        session.commit()
        session.refresh(current_user)

        return current_user
    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='username or email already in use',
        )


@app.delete('/users/{id}', status_code=HTTPStatus.NO_CONTENT)
def delete_user(
    id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user.id != id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='not enough permissions'
        )

    session.delete(current_user)
    session.commit()


@app.post('/token', response_model=Token)
def create_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    user = session.scalar(select(User).where(User.email == form_data.username))

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect email or password',
        )

    if not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect email or password',
        )

    access_token = create_access_token(data={'sub': user.email})

    return Token(access_token=access_token, token_type='bearer')
