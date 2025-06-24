from pydantic import BaseModel

from fast_zero.enums.todo import TodoState


class FilterPage(BaseModel):
    offset: int = 0
    limit: int = 20


class FilterTodo(FilterPage):
    title: str | None = None
    description: str | None = None
    state: TodoState | None = None
