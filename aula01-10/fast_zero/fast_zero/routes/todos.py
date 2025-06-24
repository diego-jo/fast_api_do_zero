from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.exceptions import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fast_zero.config.database import get_session
from fast_zero.models.todo import Todo
from fast_zero.models.user import User
from fast_zero.schemas.filters import FilterTodo
from fast_zero.schemas.todo import (
    TodoList,
    TodoRequest,
    TodoResponse,
    TodoUpdate,
)
from fast_zero.security.auth import get_current_user

router = APIRouter(prefix='/todos', tags=['todos'])

CurrentUser = Annotated[User, Depends(get_current_user)]
Session = Annotated[AsyncSession, Depends(get_session)]
Filter = Annotated[FilterTodo, Query()]


@router.post('/', status_code=HTTPStatus.CREATED, response_model=TodoResponse)
async def create_todo(
    todo: TodoRequest,
    user: CurrentUser,
    session: Session,
):
    new_todo = Todo(
        title=todo.title,
        description=todo.description,
        state=todo.state,
        user_id=user.id,
    )

    session.add(new_todo)
    await session.commit()
    await session.refresh(new_todo)

    return new_todo


@router.get('/', status_code=HTTPStatus.OK, response_model=TodoList)
async def list_todos(
    todo_filter: Filter,
    user: CurrentUser,
    session: Session,
):
    defined_filters = (
        select(Todo).offset(todo_filter.offset).limit(todo_filter.limit)
    )

    if todo_filter.title:
        defined_filters = defined_filters.filter(
            Todo.title.contains(todo_filter.title)
        )
    if todo_filter.description:
        defined_filters = defined_filters.filter(
            Todo.description.contains(todo_filter.description)
        )
    if todo_filter.state:
        defined_filters = defined_filters.filter(
            Todo.state == todo_filter.state
        )

    query = await session.scalars(
        defined_filters.where(Todo.user_id == user.id)
    )

    todos = query.all()
    return TodoList(todos=todos)


@router.patch(
    '/{todo_id}', status_code=HTTPStatus.OK, response_model=TodoResponse
)
async def update_todo(
    todo_id: int,
    todo: TodoUpdate,
    user: CurrentUser,
    session: Session,
):
    db_todo = await session.scalar(
        select(Todo).where((Todo.id == todo_id) & (Todo.user_id == user.id))
    )

    if not db_todo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='task not found',
        )

    for key, value in todo.model_dump(exclude_unset=True).items():
        setattr(db_todo, key, value)

    await session.commit()
    await session.refresh(db_todo)

    return db_todo


@router.delete('/{todo_id}', status_code=HTTPStatus.NO_CONTENT)
async def delete_todo(
    todo_id: int,
    user: CurrentUser,
    session: Session,
):
    db_todo = await session.scalar(
        select(Todo).where((Todo.id == todo_id) & (Todo.user_id == user.id))
    )

    if not db_todo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='task not found',
        )

    await session.delete(db_todo)
    await session.commit()
