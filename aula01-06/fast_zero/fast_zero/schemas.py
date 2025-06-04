from pydantic import BaseModel, ConfigDict, EmailStr


class UserRequest(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    # TODO: entender melhor esta linha
    model_config = ConfigDict(from_attributes=True)


class ListUsers(BaseModel):
    users: list[UserResponse]
