from http import HTTPStatus

from fast_zero.schemas.user import UserResponse


def test_create_user_successful(client):
    response = client.post(
        '/users',
        json={
            'username': 'diego',
            'email': 'diego@email.com',
            'password': '123',
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'username': 'diego',
        'email': 'diego@email.com',
    }


# TODO: alterar para usar fixture de criação de usuário fixo
def test_create_user_with_already_in_use_username(client):
    client.post(
        '/users',
        json={
            'username': 'diego',
            'email': 'djol@email.com',
            'password': '123',
        },
    )

    response = client.post(
        '/users',
        json={
            'username': 'diego',
            'email': 'asd@email.com',
            'password': '123',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'username or email already in use'}


# TODO: alterar para usar fixture de criação de usuário fixo
def test_create_user_with_already_in_use_email(client):
    client.post(
        '/users',
        json={
            'username': 'a234sdfs',
            'email': 'diego@email.com',
            'password': '123',
        },
    )

    response = client.post(
        '/users',
        json={
            'username': 'asd',
            'email': 'diego@email.com',
            'password': '123',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'username or email already in use'}


def test_create_user_with_no_email(client):
    response = client.post(
        '/users',
        json={
            'username': 'asd',
            'password': '123',
        },
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT


def test_get_all_users_default_query_filters(client, user):
    user_schema = UserResponse.model_validate(user).model_dump()
    response = client.get('/users')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema]}


def test_get_all_users_with_query_filters(client, user):
    response = client.get('/users', params={'offset': 0, 'limit': 1})

    assert response.status_code == HTTPStatus.OK
    assert len(response.json().get('users')) == 1


def test_get_all_users_with_query_filter_limit(client, user, other_user):
    USERS_NUMBER = 2
    response = client.get('/users', params={'offset': 0, 'limit': 2})

    assert response.status_code == HTTPStatus.OK
    assert len(response.json().get('users')) == USERS_NUMBER


def test_get_user_by_id(client, user):
    user_response = UserResponse.model_validate(user).model_dump()
    response = client.get(f'/users/{user.id}')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == user_response


def test_get_user_by_id_not_found(client):
    response = client.get('/users/111')

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_update_user(client, user, token):
    response = client.put(
        f'/users/{user.id}',
        json={
            'username': 'fulano',
            'email': 'fulano@email.com',
            'password': '123',
        },
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': user.id,
        'username': 'fulano',
        'email': 'fulano@email.com',
    }


# TODO: alterar para usar fixture de criação de usuário fixo
def test_update_user_with_already_in_use_username(client, user, token):
    client.post(
        '/users',
        json={
            'username': 'a234sdfs',
            'email': 'diego@email.com',
            'password': '123',
        },
    )

    response = client.put(
        f'/users/{user.id}',
        json={
            'username': 'a234sdfs',
            'email': 'diego@email.com',
            'password': '123',
        },
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'username or email already in use'}


def test_update_user_with_wrong_user(client, other_user, token):
    response = client.put(
        f'/users/{other_user.id}',
        json={
            'username': 'jose',
            'email': 'jose@email.com',
            'password': '123',
        },
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'not enough permissions'}


def test_delete_user(client, user, token):
    response = client.delete(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )
    get_response = client.get(f'/users/{user.id}')

    assert response.status_code == HTTPStatus.NO_CONTENT
    assert get_response.status_code == HTTPStatus.NOT_FOUND


def test_delete_user_with_wrong_user(client, other_user, token):
    response = client.delete(
        f'/users/{other_user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'not enough permissions'}
