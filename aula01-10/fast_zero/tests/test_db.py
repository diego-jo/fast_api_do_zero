from dataclasses import asdict

import pytest
from sqlalchemy import select

from fast_zero.models.todo import Todo
from fast_zero.models.user import User


@pytest.mark.asyncio
async def test_create_user_to_validate_db(session, mock_db_time):
    user = User(username='diego', email='diego@email.com', password='1234')

    with mock_db_time(model=User) as time:
        session.add(user)
        await session.commit()

    db_user = await session.scalar(
        select(User).where(User.username == user.username)
    )

    assert asdict(db_user) == {
        'id': user.id,
        'username': 'diego',
        'email': 'diego@email.com',
        'password': user.password,
        'created_at': time,
        'updated_at': time,
        'todos': [],
    }


@pytest.mark.asyncio
async def test_create_todo(session, user, mock_db_time):
    todo = Todo(
        title='teste',
        description='somente um teste',
        state='draft',
        user_id=user.id,
    )

    with mock_db_time(model=Todo) as time:
        session.add(todo)
        await session.commit()

    todo_db = await session.scalar(
        select(Todo).where(Todo.title == todo.title)
    )

    assert asdict(todo_db) == {
        'id': 1,
        'title': 'teste',
        'description': 'somente um teste',
        'state': 'draft',
        'user_id': 1,
        'created_at': time,
        'updated_at': time,
    }


@pytest.mark.asyncio
async def test_create_todo_with_invalid_state(session, user):
    invalid_state = 'invalid'
    error_message = f"'{invalid_state}' is not among the defined enum values"
    todo = Todo(
        title='teste',
        description='somente um teste',
        state=invalid_state,
        user_id=user.id,
    )

    session.add(todo)
    await session.commit()

    with pytest.raises(LookupError, match=error_message):
        await session.refresh(todo)


@pytest.mark.asyncio
async def test_user_todo_relationship(session, user):
    todo = Todo(
        title='teste',
        description='somente um teste',
        state='draft',
        user_id=user.id,
    )

    session.add(todo)
    await session.commit()
    await session.refresh(user)

    # NOTA: busca comentada pois não é mais necessária. Mas será mantida para
    # fins de aprendizado, a linha `session.refresh(user)` já faz
    # automaticamente um novo select na tabela de usuarios para atualizar o
    # estado do objeto `user`.

    # db_user = await session.scalar(select(User).where(User.id == user.id))

    assert user.todos == [todo]
