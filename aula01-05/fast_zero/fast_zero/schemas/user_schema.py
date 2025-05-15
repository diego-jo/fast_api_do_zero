from pydantic import BaseModel, EmailStr


class UserRequest(BaseModel):
    username: str
    password: str
    email: EmailStr


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr


class UserEntity(UserRequest):
    id: int


class UserList(BaseModel):
    users: list[UserResponse]
