from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from fast_zero.config.database import get_session
from fast_zero.models.user import User
from fast_zero.schemas.filters import FilterPage
from fast_zero.schemas.user import UserList, UserRequest, UserResponse
from fast_zero.security.auth import get_current_user

router = APIRouter(prefix='/users', tags=['users'])

CurrentUser = Annotated[User, Depends(get_current_user)]
Session = Annotated[AsyncSession, Depends(get_session)]
FilterUser = Annotated[FilterPage, Query()]


@router.post('/', status_code=HTTPStatus.CREATED, response_model=UserResponse)
async def create_user(user: UserRequest, session: Session):
    db_user = User(
        username=user.username, email=user.email, password=user.password
    )

    try:
        session.add(db_user)
        await session.commit()
        await session.refresh(db_user)
    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='username or email already in use',
        )

    return db_user


@router.get('/', status_code=HTTPStatus.OK, response_model=UserList)
async def get_all_users(
    filter_user: FilterUser,
    session: Session,
):
    query = await session.scalars(
        select(User).offset(filter_user.offset).limit(filter_user.limit)
    )
    users = query.all()

    return UserList(users=users)


@router.get(
    '/{user_id}', status_code=HTTPStatus.OK, response_model=UserResponse
)
def get_user_by_id(user_id: int, current_user: CurrentUser):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='not enough permissions to get user info',
        )

    return current_user


@router.put(
    '/{user_id}', status_code=HTTPStatus.OK, response_model=UserResponse
)
async def update_user(
    user_id: int,
    user: UserRequest,
    session: Session,
    current_user: CurrentUser,
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='not enough permissions to update user',
        )

    current_user.username = user.username
    current_user.email = user.email
    current_user.password = user.password

    try:
        await session.commit()
        await session.refresh(current_user)

        return current_user
    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='username or email already in use',
        )


@router.delete('/{user_id}', status_code=HTTPStatus.NO_CONTENT)
async def delete_user(
    user_id: int, session: Session, current_user: CurrentUser
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='not enough permissions to delete user',
        )

    await session.delete(current_user)
    await session.commit()
