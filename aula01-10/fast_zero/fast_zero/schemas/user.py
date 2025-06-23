from pydantic import BaseModel, ConfigDict, EmailStr


class UserRequest(BaseModel):
    username: str
    email: EmailStr
    password: str


# TODO: entender como a serialização funciona para nomes de campos diferentes
# commo created_at -> createdAt, e como a serialização de datas funciona.
class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    model_config = ConfigDict(from_attributes=True)


class UserList(BaseModel):
    users: list[UserResponse]
