from dataclasses import asdict

import pytest
from sqlalchemy import select
from sqlalchemy.exc import DataError

from fast_zero.todo.models import Todo
from fast_zero.user.models import User


@pytest.mark.asyncio
async def test_create_user(session, mock_db_time):
    plain_password = '123@asd'
    user = User(
        username='diego',
        email='diego@email.com',
        password=plain_password,
    )

    with mock_db_time(model=User) as time:
        session.add(user)
        await session.commit()
        await session.refresh(user)

    db_user = await session.scalar(select(User).where(User.id == user.id))

    assert asdict(db_user) == {
        'id': 1,
        'username': 'diego',
        'email': 'diego@email.com',
        'password': plain_password,
        'created_at': time,
        'updated_at': time,
        'todos': [],
    }


@pytest.mark.asyncio
async def test_create_todo(session, user, mock_db_time):
    todo = Todo(
        title='first task',
        description='my first task',
        state='todo',
        user_id=user.id,
    )

    with mock_db_time(model=Todo) as time:
        session.add(todo)
        await session.commit()
        await session.refresh(todo)

    db_todo = await session.scalar(select(Todo).where(Todo.id == todo.id))

    assert asdict(db_todo) == {
        'id': todo.id,
        'title': 'first task',
        'description': 'my first task',
        'state': 'todo',
        'user_id': 1,
        'created_at': time,
        'updated_at': time,
    }


@pytest.mark.asyncio
async def test_create_todo_with_invalid_state(session, user):
    todo = Todo(
        title='task',
        description='my task',
        state='invalid',
        user_id=user.id,
    )

    session.add(todo)

    with pytest.raises(DataError):
        await session.commit()


@pytest.mark.asyncio
async def test_created_user_with_todos(session, user):
    todo = Todo(
        title='task 1',
        description='my task',
        state='draft',
        user_id=user.id,
    )

    session.add(todo)
    await session.commit()
    await session.refresh(user)

    assert len(user.todos) == 1
    assert user.todos[0].title == 'task 1'
