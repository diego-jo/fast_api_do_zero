from http import HTTPStatus

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from fast_zero.schemas import Message, UserDB, UserList, UserPublic, UserSchema

app = FastAPI()

database = []


@app.post('/users', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema):
    user_with_id = UserDB(**user.model_dump(), id=len(database) + 1)
    database.append(user_with_id)

    return user_with_id


@app.get('/users', status_code=HTTPStatus.OK, response_model=UserList)
def read_users():
    return {'users': database}


@app.put(
    '/users/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic
)
def update_user(user_id: int, user: UserSchema):
    if user_id > len(database) or user_id < 1:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )

    updated_user = UserDB(**user.model_dump(), id=user_id)
    database[user_id - 1] = updated_user
    return updated_user


@app.delete('/users/{user_id}', status_code=HTTPStatus.NO_CONTENT)
def delete_user(user_id: int):
    if user_id > len(database) or user_id < 1:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )

    del database[user_id - 1]


@app.get(path='/', status_code=200, response_model=Message)
def read_root():
    return {'message': 'aula01-02'}


@app.get('/html', response_class=HTMLResponse)
def read_html():
    return """
    <body>
        Teste de api com html!
    <body/>
    """
