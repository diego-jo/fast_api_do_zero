from http import HTTPStatus

from fastapi import FastAPI, HTTPException

from fast_zero.schemas.user_schema import (
    UserEntity,
    UserList,
    UserRequest,
    UserResponse,
)

app = FastAPI()


database = []


@app.get('/users', status_code=HTTPStatus.OK, response_model=UserList)
def get_all_users():
    return {'users': database}


@app.get(
    '/users/{user_id}', status_code=HTTPStatus.OK, response_model=UserResponse
)
def user_by_id(user_id: int):
    if user_id < 1 or user_id > len(database):
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='user not found'
        )

    return database[user_id - 1]


@app.post(
    '/users', status_code=HTTPStatus.CREATED, response_model=UserResponse
)
def create_user(user: UserRequest):
    user_entity = UserEntity(**user.model_dump(), id=len(database) + 1)
    database.append(user_entity)

    return user_entity


@app.put(
    '/users/{user_id}', status_code=HTTPStatus.OK, response_model=UserResponse
)
# TODO: entender pq alterar o parametro user_id para id retorna 422
def update_user(user_id: int, user: UserRequest):
    if user_id < 1 or user_id > len(database):
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='user not found'
        )

    updated_user = UserEntity(**user.model_dump(), id=user_id)
    database[user_id - 1] = updated_user

    return updated_user


@app.delete('/users/{user_id}', status_code=HTTPStatus.NO_CONTENT)
def delete_user(user_id: int):
    if user_id < 1 or user_id > len(database):
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='user not found'
        )

    del database[user_id - 1]
