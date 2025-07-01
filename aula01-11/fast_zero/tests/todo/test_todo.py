from http import HTTPStatus

import pytest

from fast_zero.todo.models import Todo
from tests.conftest import TodoFactory


def test_create_todo(client, token, mock_db_time):
    with mock_db_time(model=Todo) as time:
        response = client.post(
            '/todos',
            json={
                'title': 'my task',
                'description': 'first task',
                'state': 'todo',
            },
            headers={'Authorization': f'Bearer {token}'},
        )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
                'id': 1,
                'title': 'my task',
                'description': 'first task',
                'state': 'todo',
                'createdAt': time.isoformat(),
                'updatedAt': time.isoformat(),
            }


@pytest.mark.asyncio
async def test_list_todos(client, token, user, session):
    expected_value = 5
    todos = TodoFactory.create_batch(5, user_id=user.id)

    session.add_all(todos)
    await session.commit()
    await session.refresh(user)

    response = client.get(
        '/todos',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert len(response.json().get('todos')) == expected_value
