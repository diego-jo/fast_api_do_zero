from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.exceptions import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from fast_zero.auth.security import hash_password, permission_validation
from fast_zero.commons.filters import FilterPage
from fast_zero.database.config import get_session
from fast_zero.user.models import User
from fast_zero.user.schemas import (
    UpdatedUserResponse,
    UserList,
    UserRequest,
    UserResponse,
)

router = APIRouter(prefix='/users', tags=['users'])

Session = Annotated[AsyncSession, Depends(get_session)]
FilterUser = Annotated[FilterPage, Query()]
PermissionValidation = Annotated[User, Depends(permission_validation)]


@router.post('/', status_code=HTTPStatus.CREATED, response_model=UserResponse)
async def create_user(user: UserRequest, session: Session):
    try:
        db_user = User(
            username=user.username,
            email=user.email,
            password=hash_password(user.password),
        )

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
async def list_users(session: Session, filter_user: FilterUser):
    query = await session.scalars(
        select(User).offset(filter_user.offset).limit(filter_user.limit)
    )

    users = query.all()
    return UserList(users=users)


@router.get(
    '/{user_id}', status_code=HTTPStatus.OK, response_model=UserResponse
)
async def get_user_by_id(user_id: int, user: PermissionValidation):
    return user


@router.put(
    '/{user_id}', status_code=HTTPStatus.OK, response_model=UpdatedUserResponse
)
async def update_user(
    user_id: int,
    user: UserRequest,
    db_user: PermissionValidation,
    session: Session,
):
    try:
        db_user.username = user.username
        db_user.email = user.email
        db_user.password = hash_password(user.password)

        await session.commit()
        await session.refresh(db_user)

        return UpdatedUserResponse(
            id=db_user.id,
            username=db_user.username,
            email=db_user.email,
        )

    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='username or email already in use',
        )


@router.delete('/{user_id}', status_code=HTTPStatus.NO_CONTENT)
async def delete_user(
    user_id: int,
    user: PermissionValidation,
    session: Session,
):
    await session.delete(user)
    await session.commit()
