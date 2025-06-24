from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from fast_zero.enums.todo import TodoState


class TodoRequest(BaseModel):
    title: str
    description: str
    state: TodoState = 'todo'


class TodoUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    state: TodoState | None = None


class TodoResponse(TodoRequest):
    id: int
    created_at: datetime = Field(alias='createdAt')
    updated_at: datetime = Field(alias='updatedAt')
    model_config = ConfigDict(
        from_attributes=True,
        validate_by_name=True,
        validate_by_alias=True,
    )


class TodoList(BaseModel):
    todos: list[TodoResponse]
