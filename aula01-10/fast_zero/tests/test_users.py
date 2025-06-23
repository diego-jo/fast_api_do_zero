from http import HTTPStatus

import pytest

from fast_zero.schemas.user import UserResponse


def test_create_user(client):
    response = client.post(
        '/users',
        json={
            'username': 'diego',
            'email': 'diego@email.com',
            'password': '123&123',
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'username': 'diego',
        'email': 'diego@email.com',
    }


def test_create_user_with_already_in_use_email(client, user):
    response = client.post(
        '/users',
        json={
            'username': 'djol',
            'email': user.email,
            'password': '123&123',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'username or email already in use'}


def test_create_user_with_already_in_use_username(client, user):
    response = client.post(
        '/users',
        json={
            'username': user.username,
            'email': 'djol@email.com',
            'password': '123&123',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'username or email already in use'}


def test_create_user_without_required_property(client):
    response = client.post(
        '/users',
        json={'username': 'djol', 'email': 'diego@email.com'},
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


# TODO: ao usar factory-boy implementar criacão de mais usuários para validar
# filtros
def test_get_all_users(client, user):
    user_schema = UserResponse.model_validate(user).model_dump()
    response = client.get(
        '/users',
        params={'offset': 0, 'limit': 10},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema]}


def test_get_user_by_id(client, user, token):
    user_schema = UserResponse.model_validate(user).model_dump()
    response = client.get(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == user_schema


@pytest.mark.asyncio
async def test_get_user_by_id_when_user_deleted_after_token_issuance(
    client, token, user, session
):
    user_id = user.id
    await session.delete(user)
    await session.commit()

    response = client.get(
        f'/users/{user_id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'invalid credentials'}


def test_get_user_by_id_with_diferente_user_ids(client, token):
    response = client.get(
        '/users/12',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {
        'detail': 'not enough permissions to get user info'
    }


def test_update_user(client, token, user):
    response = client.put(
        f'/users/{user.id}',
        json={
            'username': 'jose',
            'email': 'diego@email.com',
            'password': '123',
        },
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': user.id,
        'username': 'jose',
        'email': 'diego@email.com',
    }


def test_update_user_with_different_ids(client, token):
    response = client.put(
        '/users/12',
        json={
            'username': 'jose',
            'email': 'diego@email.com',
            'password': '123',
        },
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {
        'detail': 'not enough permissions to update user'
    }


def test_update_user_with_already_in_use_username(
    client, token, user, other_user
):
    response = client.put(
        f'/users/{user.id}',
        json={
            'username': other_user.username,
            'email': 'other@email.com',
            'password': '123',
        },
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'username or email already in use'}


def test_update_user_with_already_in_use_email(
    client, token, user, other_user
):
    response = client.put(
        f'/users/{user.id}',
        json={
            'username': 'asd',
            'email': other_user.email,
            'password': '123',
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


def test_delete_user_with_different_ids(client, token):
    response = client.delete(
        '/users/12',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {
        'detail': 'not enough permissions to delete user'
    }
