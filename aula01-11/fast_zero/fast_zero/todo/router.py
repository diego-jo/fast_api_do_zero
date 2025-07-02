from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.exceptions import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fast_zero.auth.security import get_current_user
from fast_zero.database.config import get_session
from fast_zero.todo.models import Todo
from fast_zero.todo.schemas import (
    FilterTodo,
    TodoList,
    TodoRequest,
    TodoResponse,
    TodoUpdate,
)
from fast_zero.user.models import User

router = APIRouter(prefix='/todos', tags=['todos'])

Session = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]
Filter = Annotated[FilterTodo, Query()]


@router.post('/', status_code=HTTPStatus.CREATED, response_model=TodoResponse)
async def create_todo(
    todo: TodoRequest,
    user: CurrentUser,
    session: Session,
):
    db_todo = Todo(
        title=todo.title,
        description=todo.description,
        state=todo.state,
        user_id=user.id,
    )

    session.add(db_todo)
    await session.commit()
    await session.refresh(db_todo)

    return db_todo


@router.get('/', status_code=HTTPStatus.OK, response_model=TodoList)
async def list_todos(filter: Filter, user: CurrentUser, session: Session):
    query = (
        select(Todo)
        .where(Todo.user_id == user.id)
        .offset(filter.offset)
        .limit(filter.limit)
    )

    if filter.title:
        query = query.filter(Todo.title.contains(filter.title))
    if filter.description:
        query = query.filter(Todo.description.contains(filter.description))
    if filter.state:
        query = query.filter(Todo.state == filter.state)

    todos = await session.scalars(query)

    return TodoList(todos=todos.all())


@router.patch(
    '/{todo_id}', status_code=HTTPStatus.OK, response_model=TodoResponse
)
async def update_todo(
    todo_id: int, todo: TodoUpdate, user: CurrentUser, session: Session
):
    db_todo = await session.scalar(
        select(Todo).where((Todo.id == todo_id) & (Todo.user_id == user.id))
    )

    if not db_todo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='todo not found'
        )

    for key, value in todo.model_dump(exclude_unset=True).items():
        setattr(db_todo, key, value)

    await session.commit()
    await session.refresh(db_todo)

    return db_todo


@router.delete('/{todo_id}', status_code=HTTPStatus.NO_CONTENT)
async def delete_todo(todo_id: int, user: CurrentUser, session: Session):
    db_todo = await session.scalar(
        select(Todo).where(Todo.id == todo_id, Todo.user_id == user.id)
    )

    if not db_todo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='todo not found'
        )

    await session.delete(db_todo)
    await session.commit()
