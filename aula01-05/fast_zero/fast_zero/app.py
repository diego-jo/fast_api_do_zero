from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from fast_zero.database import get_session
from fast_zero.models.user_model import User
from fast_zero.schemas.user_schema import (
    UserList,
    UserRequest,
    UserResponse,
)

app = FastAPI()


database = []


# TODO: pq os comentários estão sendo setados com ctrl+;????????/
@app.post(
    '/users', status_code=HTTPStatus.CREATED, response_model=UserResponse
)
# TODO: validar se nas outras funções o id do objeto session é o mesmo sempre.
def create_user(user: UserRequest, session: Session = Depends(get_session)):
    # TODO: entender se é uma opção deixar a regra de `unique` no db e esperar
    # a exceção ser lançada para tratar.
    db_user = session.scalar(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )

    if db_user:
        if db_user.username == user.username:
            message = f'Username {user.username}'
        else:
            message = f'Email {user.email}'

        raise HTTPException(
            detail=f'{message} already exists',
            status_code=HTTPStatus.CONFLICT,
        )

    db_user = User(**user.model_dump())

    session.add(db_user)
    session.commit()
    session.flush(db_user)

    return db_user


@app.get('/users', status_code=HTTPStatus.OK, response_model=UserList)
def get_all_users(
    skip: int = 0, limit: int = 20, session: Session = Depends(get_session)
):
    users = session.scalars(select(User).offset(skip).limit(limit)).all()
    return {'users': users}


# TODO entender se é seguro o casting altomatico do Pydantic
# User -> UserResponse. ou se o correto seria criar um novo objeto manualmente
# UserResponse(username=db_user.username, ...) ????
@app.get(
    '/users/{user_id}', status_code=HTTPStatus.OK, response_model=UserResponse
)
def user_by_id(user_id: int, session: Session = Depends(get_session)):
    db_user = session.scalar(select(User).where(User.id == user_id))

    if not db_user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='user not found'
        )

    return db_user


@app.put(
    '/users/{user_id}', status_code=HTTPStatus.OK, response_model=UserResponse
)
# TODO: entender pq alterar o parametro user_id para id retorna 422
def update_user(
    user_id: int, user: UserRequest, session: Session = Depends(get_session)
):
    db_user = session.scalar(select(User).where(User.id == user_id))

    if not db_user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='user not found'
        )

    try:
        db_user.username = user.username
        db_user.email = user.email
        db_user.password = user.password

        session.commit()
        # TODO: qual a diferença entre o flush e o refresh
        session.refresh(db_user)

        return db_user
    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='username or email already in use',
        )


@app.delete('/users/{user_id}', status_code=HTTPStatus.NO_CONTENT)
def delete_user(user_id: int, session: Session = Depends(get_session)):
    db_user = session.scalar(select(User).where(User.id == user_id))

    if not db_user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='user not found'
        )

    session.delete(db_user)
    session.commit()
