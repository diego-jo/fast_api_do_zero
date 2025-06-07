from http import HTTPStatus

import pytest

from fast_zero.schemas import UserResponse


def test_positive_create_user(client):
    response = client.post(
        '/users',
        json={
            'username': 'diego',
            'email': 'diego@email.com',
            'password': '1234',
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'username': 'diego',
        'email': 'diego@email.com',
    }


def test_create_user_without_username(client):
    response = client.post(
        '/users', json={'email': 'diego@email.com', 'password': '1234'}
    )

    # TODO: alterar retorno referente ao payload para 400 bad request
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_create_user_with_existent_email(client, user):
    response = client.post(
        '/users',
        json={
            'username': 'diego11',
            'email': 'diego@email.com',
            'password': '1234',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'email already in use'}


def test_create_user_with_existent_username(client, user):
    response = client.post(
        '/users',
        json={
            'username': 'diego',
            'email': 'djo@email.com',
            'password': '1234',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'username already in use'}


def test_positive_get_all_users(client, user):
    user_schema = UserResponse.model_validate(user).model_dump()
    response = client.get('/users')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema]}


def test_positive_get_by_id(client, user):
    response = client.get(f'users/{user.id}')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'username': 'diego',
        'email': 'diego@email.com',
    }


def test_get_user_by_id_not_found(client):
    response = client.get('users/11234')

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_positive_update_user(client, user, token):
    response = client.put(
        f'/users/{user.id}',
        json={
            'username': 'diego jose',
            'email': 'diego@email.com',
            'password': '65+655345',
        },
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': user.id,
        'username': 'diego jose',
        'email': 'diego@email.com',
    }


@pytest.mark.skip
def test_update_user_not_found(client):
    response = client.put(
        '/users/45741',
        json={
            'username': 'diego jose',
            'email': 'diego@email.com',
            'password': '65+655345',
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_update_user_without_username(client, token):
    response = client.put(
        '/users/1',
        json={'email': 'diego@email.com', 'password': '65+655345'},
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_update_user_with_duplicated_data(client, user, token):
    client.post(
        '/users',
        json={
            'username': 'jose',
            'email': 'jose@email.com',
            'password': '1234',
        },
    )

    response = client.put(
        f'/users/{user.id}',
        json={
            'username': 'jose',
            'email': 'diego@email.com',
            'password': '65+655345',
        },
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'username or email already in use'}


def test_positive_delete_user(client, user, token):
    response = client.delete(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.NO_CONTENT


# TODO: faz sentido não tem mais um retorno 404?
# se consegui o token é pq o usuário existe, logo não deve retornar 404 e sim
# 403 pq é o token de um usuário tentanto acessar o contexto de outro
# faz sentido se existir o contexto de admin que tem uma visão geral
@pytest.mark.skip
def test_delete_user_not_found(client):
    response = client.delete('/users/100')
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_positive_create_token(client, user):
    response = client.post(
        '/token',
        data={'username': user.email, 'password': user.plain_password},
    )

    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in token
    assert 'token_type' in token


def test_create_token_unauthorized_user_invalid_password(client, user):
    response = client.post(
        '/token', data={'username': user.email, 'password': '123'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_create_token_unauthorized_user_not_found(client):
    response = client.post(
        '/token', data={'username': 'user@mail.com', 'password': '123'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
