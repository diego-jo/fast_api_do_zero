from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from fast_zero.config.database import get_session
from fast_zero.models.user import User
from fast_zero.schemas.filter import FilterPage
from fast_zero.schemas.user import UserList, UserRequest, UserResponse
from fast_zero.security.auth import get_current_user, hash_password

router = APIRouter(prefix='/users', tags=['users'])


FilterUser = Annotated[FilterPage, Query()]
InjectedSession = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('/', status_code=HTTPStatus.CREATED, response_model=UserResponse)
async def create_user(user: UserRequest, session: InjectedSession):
    db_user = User(
        username=user.username,
        email=user.email,
        password=hash_password(user.password),
    )

    try:
        session.add(db_user)
        await session.commit()
        await session.refresh(db_user)

        return db_user
    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='username or email already in use',
        )


@router.get('/', status_code=HTTPStatus.OK, response_model=UserList)
async def get_all_users(filter_user: FilterUser, session: InjectedSession):
    users_cor = await session.scalars(
        select(User).offset(filter_user.offset).limit(filter_user.limit)
    )

    users = users_cor.all()
    return {'users': users}


@router.get(
    '/{user_id}', status_code=HTTPStatus.OK, response_model=UserResponse
)
async def get_user_by_id(user_id: int, session: InjectedSession):
    db_user = await session.scalar(select(User).where(User.id == user_id))

    if not db_user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='user not found',
        )

    return db_user


@router.put(
    '/{user_id}', status_code=HTTPStatus.OK, response_model=UserResponse
)
async def update_user(
    user_id: int,
    user: UserRequest,
    session: InjectedSession,
    current_user: CurrentUser,
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='not enough permissions'
        )

    current_user.username = user.username
    current_user.email = user.email
    current_user.password = hash_password(user.password)

    try:
        await session.commit()
        await session.refresh(current_user)
    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='username or email already in use',
        )

    return current_user


@router.delete('/{user_id}', status_code=HTTPStatus.NO_CONTENT)
async def delete_user(
    user_id: int, session: InjectedSession, current_user: CurrentUser
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='not enough permissions'
        )

    await session.delete(current_user)
    await session.commit()
