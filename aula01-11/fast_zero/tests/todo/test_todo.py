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


def test_create_todo_with_invalid_state(client, token):
    response = client.post(
        '/todos',
        json={
            'title': 'my task',
            'description': 'first task',
            'state': 'fazer',
        },
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


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


@pytest.mark.asyncio
async def test_list_todos_with_offset_and_limit_filters(
    client, token, user, session
):
    expected_value = 3
    todos = TodoFactory.create_batch(10, user_id=user.id)

    session.add_all(todos)
    await session.commit()
    await session.refresh(user)

    response = client.get(
        '/todos',
        headers={'Authorization': f'Bearer {token}'},
        params={'offset': 7, 'limit': 10}
    )

    assert response.status_code == HTTPStatus.OK
    assert len(response.json().get('todos')) == expected_value


@pytest.mark.asyncio
async def test_list_todos_with_title_filter(client, token, user, session):
    expected_value = 5
    session.add_all(TodoFactory.create_batch(5, user_id=user.id))
    session.add_all(
        TodoFactory.create_batch(5, user_id=user.id, title='python')
    )

    await session.commit()
    await session.refresh(user)

    response = client.get(
        '/todos',
        headers={'Authorization': f'Bearer {token}'},
        params={'title': 'pyt'}
    )

    assert response.status_code == HTTPStatus.OK
    assert len(response.json().get('todos')) == expected_value


@pytest.mark.asyncio
async def test_list_todos_with_description_filter(
    client, token, user, session
):
    expected_value = 3
    session.add_all(TodoFactory.create_batch(5, user_id=user.id))
    session.add_all(
        TodoFactory.create_batch(3, user_id=user.id, description='tarefa')
    )

    await session.commit()
    await session.refresh(user)

    response = client.get(
        '/todos',
        headers={'Authorization': f'Bearer {token}'},
        params={'description': 'tarefa'}
    )

    assert response.status_code == HTTPStatus.OK
    assert len(response.json().get('todos')) == expected_value


@pytest.mark.asyncio
async def test_list_todos_with_state_filter(
    client, token, user, session
):
    expected_value = 5
    session.add_all(TodoFactory.create_batch(3, user_id=user.id, state='todo'))
    session.add_all(
        TodoFactory.create_batch(5, user_id=user.id, state='doing')
    )

    await session.commit()
    await session.refresh(user)

    response = client.get(
        '/todos',
        headers={'Authorization': f'Bearer {token}'},
        params={'state': 'doing'}
    )

    assert response.status_code == HTTPStatus.OK
    assert len(response.json().get('todos')) == expected_value


@pytest.mark.asyncio
async def test_list_todos_with_all_filters(
    client, token, user, session
):
    expected_value = 5
    session.add_all(TodoFactory.create_batch(5, user_id=user.id, state='todo'))
    session.add_all(
        TodoFactory.create_batch(
            5,
            user_id=user.id,
            state='doing',
            title='first task',
            description='this is first task'
        )
    )

    await session.commit()
    await session.refresh(user)

    response = client.get(
        '/todos',
        headers={'Authorization': f'Bearer {token}'},
        params={'title': 'first', 'description': 'first', 'state': 'doing'}
    )

    assert response.status_code == HTTPStatus.OK
    assert len(response.json().get('todos')) == expected_value


def test_list_todos_with_invalid_state_filter(client, token, todo):
    response = client.get(
        '/todos',
        headers={'Authorization': f'Bearer {token}'},
        params={'state': 'dong'},
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_update_todo(client, token, todo):
    response = client.patch(
        f'/todos/{todo.id}',
        json={'title': 'new title', 'state': 'done'},
        headers={'Authorization': f'Bearer {token}'},
    )
    data = response.json()

    assert response.status_code == HTTPStatus.OK
    assert data.get('title') == 'new title'
    assert data.get('state') == 'done'


def test_update_todo_with_invalid_state(client, token, todo):
    response = client.patch(
        f'/todos/{todo.id}',
        json={'state': 'wrong'},
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_update_todo_not_found(client, token, todo):
    response = client.patch(
        '/todos/123',
        json={},
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'todo not found'}


def test_delete_todo(client, token, todo):
    response = client.delete(
        f'/todos/{todo.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    response_get = client.get(
        '/todos',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NO_CONTENT
    assert not len(response_get.json().get('todos'))


def test_delete_todo_not_found(client, token, todo):
    response = client.delete(
        '/todos/123',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'todo not found'}
