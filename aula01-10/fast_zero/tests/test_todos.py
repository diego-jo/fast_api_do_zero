from http import HTTPStatus

import factory.fuzzy
import pytest

from fast_zero.enums.todo import TodoState
from fast_zero.models.todo import Todo
from fast_zero.schemas.todo import TodoResponse

from .conftest import TodoFactory


def test_create_todo(client, token, mock_db_time):
    with mock_db_time(model=Todo) as time:
        response = client.post(
            '/todos',
            json={
                'title': 'unit test',
                'description': 'todo for unit test',
                'state': 'todo',
            },
            headers={'Authorization': f'Bearer {token}'},
        )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'title': 'unit test',
        'description': 'todo for unit test',
        'state': 'todo',
        'createdAt': time.isoformat(),
        'updatedAt': time.isoformat(),
    }


def test_create_todo_with_no_title(client, token):
    response = client.post(
        '/todos',
        json={
            'description': 'todo for unit test',
            'state': 'todo',
        },
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_create_todo_with_wrong_state_value(client, token):
    response = client.post(
        '/todos',
        json={
            'title': 'unit test',
            'description': 'todo for unit test',
            'state': 'wrong',
        },
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_list_todos(client, session, token, user):
    size_list = 10
    expected_length = size_list
    todos = TodoFactory.create_batch(size_list, user_id=user.id)

    session.add_all(todos)
    await session.commit()

    response = client.get(
        '/todos',
        headers={'Authorization': f'Bearer {token}'},
    )
    data = response.json()

    assert response.status_code == HTTPStatus.OK
    assert len(data.get('todos')) == expected_length


def test_list_todos_schema_validation(client, token, todo):
    todo_schema = TodoResponse.model_validate(todo).model_dump(
        by_alias=True, mode='json'
    )
    response = client.get(
        '/todos',
        headers={'Authorization': f'Bearer {token}'},
    )
    todo_response = response.json().get('todos')[0]

    assert response.status_code == HTTPStatus.OK
    assert todo_response == todo_schema


@pytest.mark.asyncio
async def test_list_todos_offset_and_limit(client, session, token, user):
    todo_id = 4
    size_list = 10
    expected_length = 3
    todos = TodoFactory.create_batch(size_list, user_id=user.id)

    session.add_all(todos)
    await session.commit()

    response = client.get(
        '/todos',
        headers={'Authorization': f'Bearer {token}'},
        params={'offset': 3, 'limit': 3},
    )
    data = response.json()

    assert response.status_code == HTTPStatus.OK
    assert len(data.get('todos')) == expected_length
    assert data.get('todos')[0].get('id') == todo_id


@pytest.mark.asyncio
async def test_list_todos_filter_by_title(client, session, token, user):
    size_list = 5
    expected_length = 5
    random_todos = TodoFactory.create_batch(size=size_list, user_id=user.id)
    defined_todos = TodoFactory.create_batch(
        size=size_list,
        title=factory.fuzzy.FuzzyText('estudar ', 20),
        user_id=user.id,
    )

    session.add_all([*random_todos, *defined_todos])
    await session.commit()

    response = client.get(
        '/todos',
        headers={'Authorization': f'Bearer {token}'},
        params={'title': 'estudar'},
    )
    data = response.json()

    assert response.status_code == HTTPStatus.OK
    assert len(data.get('todos')) == expected_length


@pytest.mark.asyncio
async def test_list_todos_filter_by_description(client, session, token, user):
    size_list = 5
    expected_length = 5
    random_todos = TodoFactory.create_batch(size=size_list, user_id=user.id)
    defined_todos = TodoFactory.create_batch(
        size=size_list,
        description=factory.fuzzy.FuzzyText('estudar', 50),
        user_id=user.id,
    )

    session.add_all([*random_todos, *defined_todos])
    await session.commit()

    response = client.get(
        '/todos',
        headers={'Authorization': f'Bearer {token}'},
        params={'description': 'estudar'},
    )
    data = response.json()

    assert response.status_code == HTTPStatus.OK
    assert len(data.get('todos')) == expected_length


@pytest.mark.asyncio
async def test_list_todos_filter_by_state(client, session, token, user):
    size_list = 5
    expected_length = 5
    random_todos = TodoFactory.create_batch(
        size=size_list, state=TodoState.todo, user_id=user.id
    )

    defined_todos = TodoFactory.create_batch(
        size=size_list,
        state=TodoState.draft,
        user_id=user.id,
    )

    session.add_all([*random_todos, *defined_todos])
    await session.commit()

    response = client.get(
        '/todos',
        headers={'Authorization': f'Bearer {token}'},
        params={'state': 'draft'},
    )
    data = response.json()

    assert response.status_code == HTTPStatus.OK
    assert len(data.get('todos')) == expected_length


@pytest.mark.asyncio
async def test_list_todos_all_filters(client, session, token, user):
    size_list = 5
    expected_length = 1
    todos = TodoFactory.create_batch(
        size=size_list,
        title=factory.declarations.Sequence(lambda n: f'task{n}'),
        description=factory.declarations.Sequence(lambda n: f'description{n}'),
        state=TodoState.todo,
        user_id=user.id,
    )

    todos.append(
        TodoFactory(
            title='first done',
            description='my first task finished',
            state=TodoState.done,
            user_id=user.id,
        )
    )

    session.add_all(todos)
    await session.commit()

    response = client.get(
        '/todos',
        headers={'Authorization': f'Bearer {token}'},
        params={'state': 'done', 'title': 'first', 'description': 'my'},
    )
    data = response.json()

    assert response.status_code == HTTPStatus.OK
    assert len(data.get('todos')) == expected_length


def test_update_todo(client, token, todo):
    response = client.patch(
        f'/todos/{todo.id}',
        json={
            'title': 'todo novo titulo',
        },
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json().get('title') == 'todo novo titulo'


def test_update_todo_not_found(client, token, todo):
    response = client.patch(
        '/todos/123',
        json={
            'title': 'todo novo titulo',
            'description': 'nova descrição',
            'state': 'done',
        },
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'task not found'}


def test_delete_todo(client, token, todo):
    response = client.delete(
        f'/todos/{todo.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NO_CONTENT


def test_delete_todo_not_found(client, token, todo):
    response = client.delete(
        '/todos/123',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'task not found'}
