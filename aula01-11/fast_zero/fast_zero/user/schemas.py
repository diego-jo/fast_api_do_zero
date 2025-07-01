from pydantic import BaseModel, ConfigDict, EmailStr

from fast_zero.todo.schemas import TodoResponse


class UserRequest(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    todos: list[TodoResponse]

    model_config = ConfigDict(from_attributes=True)


# TODO: entender ser é melhor assim com 2 schemas ou trabalhar a resposta do
# user.todos condicionalmente
class UpdatedUserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


class UserList(BaseModel):
    users: list[UserResponse]
