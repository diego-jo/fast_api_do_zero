from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from fast_zero.commons.filters import FilterPage
from fast_zero.todo.enums import TodoState


class FilterTodo(FilterPage):
    title: str | None = None
    description: str | None = None
    state: TodoState | None = None


class TodoRequest(BaseModel):
    title: str
    description: str
    state: TodoState


class TodoResponse(TodoRequest):
    id: int
    created_at: datetime = Field(alias='createdAt')
    updated_at: datetime = Field(alias='updatedAt')

    model_config = ConfigDict(
        from_attributes=True,
        validate_by_alias=True,
        validate_by_name=True,
    )


class TodoList(BaseModel):
    todos: list[TodoResponse]
