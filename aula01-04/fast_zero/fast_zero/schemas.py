from pydantic import BaseModel, EmailStr


class UserSchema(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserPublic(BaseModel):
    id: int
    username: str
    email: EmailStr


class UserEntity(UserSchema):
    id: int


class UserList(BaseModel):
    users: list[UserPublic]
