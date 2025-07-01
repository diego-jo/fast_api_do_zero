from http import HTTPStatus

import pytest

from fast_zero.user.schemas import UserResponse
from tests.conftest import UserFactory


def test_create_user(client):
    response = client.post(
        '/users',
        json={
            'username': 'diego',
            'email': 'diego@email.com',
            'password': '123@asd',
        }
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'username': 'diego',
        'email': 'diego@email.com',
        'todos': []
    }


def test_create_user_with_already_in_use_username(client, user):
    response = client.post(
        '/users',
        json={
            'username': user.username,
            'email': 'diego@imail.com',
            'password': '123@asd',
        }
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'username or email already in use'}


def test_create_user_with_already_in_use_email(client, user):
    response = client.post(
        '/users',
        json={
            'username': 'any_username',
            'email': user.email,
            'password': '123@asd',
        }
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'username or email already in use'}


def test_list_users(client, user):
    user_schema = UserResponse.model_validate(user).model_dump()
    response = client.get('/users')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema]}


@pytest.mark.asyncio
async def test_list_users_with_offset_filter(client, session):
    expected_users = 5
    users = UserFactory.create_batch(10)

    session.add_all(users)
    await session.commit()

    response = client.get(
        '/users',
        params={'offset': 5}
    )

    assert response.status_code == HTTPStatus.OK
    assert len(response.json().get('users')) == expected_users


@pytest.mark.asyncio
async def test_list_users_with_limit_filter(client, session):
    expected_users = 3
    users = UserFactory.create_batch(10)

    session.add_all(users)
    await session.commit()

    response = client.get(
        '/users',
        params={'limit': 3}
    )

    assert response.status_code == HTTPStatus.OK
    assert len(response.json().get('users')) == expected_users


@pytest.mark.asyncio
async def test_list_users_with_offset_and_limit_filter(client, session):
    expected_users = 2
    users = UserFactory.create_batch(10)

    session.add_all(users)
    await session.commit()

    response = client.get(
        '/users',
        params={'offset': 6, 'limit': 2}
    )

    assert response.status_code == HTTPStatus.OK
    assert len(response.json().get('users')) == expected_users


def test_get_user_by_id(client, user, token):
    response = client.get(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json().get('id') == user.id


def test_get_user_by_id_with_no_permissions(client, token):
    response = client.get(
        '/users/23',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {
        'detail': 'not enough permissions to get user info'
    }


def test_update_user(client, user, token):
    response = client.put(
        f'/users/{user.id}',
        json={
            'username': 'updated_user',
            'email': 'updated_user@email.com',
            'password': '123@123',
        },
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
            'id': user.id,
            'username': 'updated_user',
            'email': 'updated_user@email.com',
        }


def test_update_user_with_no_permissions(client, token):
    response = client.put(
        '/users/12',
        json={
            'username': 'updated_user',
            'email': 'updated_user@email.com',
            'password': '123@123',
        },
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {
        'detail': 'not enough permissions to get user info'
    }


@pytest.mark.asyncio
async def test_update_user_with_already_in_use_username(
    client, user, token, session
):
    session.add(UserFactory.create(username='joao'))
    await session.commit()

    response = client.put(
        f'/users/{user.id}',
        json={
            'username': 'joao',
            'email': 'diego@email.com',
            'password': '123@123',
        },
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'username or email already in use'}


@pytest.mark.asyncio
async def test_update_user_with_already_in_use_email(
    client, user, token, session
):
    session.add(UserFactory.create(email='joao@email.com'))
    await session.commit()

    response = client.put(
        f'/users/{user.id}',
        json={
            'username': 'diego',
            'email': 'joao@email.com',
            'password': '123@123',
        },
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'username or email already in use'}


def test_delete_user(client, user, token):
    response = client.delete(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NO_CONTENT


def test_delete_user_with_no_permissions(client, token):
    response = client.delete(
        '/users/12',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {
        'detail': 'not enough permissions to get user info'
    }
