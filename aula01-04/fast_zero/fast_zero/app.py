from http import HTTPStatus

from fastapi import FastAPI, HTTPException

from fast_zero.schemas import UserEntity, UserList, UserPublic, UserSchema

app = FastAPI()

database = []


@app.get('/users', status_code=HTTPStatus.OK, response_model=UserList)
def list_users():
    return {'users': database}


@app.get(
    '/users/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic
)
def list_user(user_id: int):
    if user_id < 1 or len(database) < user_id:
        raise HTTPException(HTTPStatus.NOT_FOUND, 'User not found')

    return database[user_id - 1]


@app.post('/users', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema):
    new_user = UserEntity(**user.model_dump(), id=len(database) + 1)
    database.append(new_user)

    return new_user


@app.put(
    '/users/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic
)
def update_user(user_id: int, user: UserSchema):
    if user_id < 1 or len(database) < user_id:
        raise HTTPException(HTTPStatus.NOT_FOUND, 'User not found')

    updated_user = UserEntity(**user.model_dump(), id=user_id)
    database[user_id - 1] = updated_user
    return updated_user


@app.delete('/users/{user_id}', status_code=HTTPStatus.NO_CONTENT)
def delete_user(user_id: int):
    if user_id < 1 or len(database) < user_id:
        raise HTTPException(HTTPStatus.NOT_FOUND, 'User not found')

    del database[user_id - 1]
