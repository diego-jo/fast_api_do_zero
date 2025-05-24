from http import HTTPStatus

from fast_zero.schemas.user_schema import UserResponse


def test_positive_user_create(client):
    response = client.post(
        '/users',
        json={
            'username': 'jose',
            'email': 'jose@email.com',
            'password': '123456',
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'username': 'jose',
        'email': 'jose@email.com',
    }


def test_create_user_with_already_used_email(client, user):
    response = client.post(
        '/users',
        json={
            'username': 'djol',
            'email': 'diego@email.com',
            'password': '1234d',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {
        'detail': 'Email diego@email.com already exists'
    }


def test_create_user_with_already_used_username(client, user):
    response = client.post(
        '/users',
        json={
            'username': 'diego',
            'email': 'joao@email.com',
            'password': '1234d',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {
        'detail': 'Username diego already exists'
    }


def test_positive_user_list(client, user):
    # TODO: entender como funciona o mode_validate e pq no endpoint a conversão
    # entre model -> squema é feita normalmente
    user_schema = UserResponse.model_validate(user).model_dump()
    response = client.get('/users')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema]}
    assert len(response.json().get('users')) >= 1


def test_positive_get_user_by_id(client, user):
    user_schema = UserResponse.model_validate(user).model_dump()
    response = client.get('/users/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == user_schema


def test_negative_get_user_not_found(client):
    response = client.get('/users/101')

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_positive_update_user(client, user):
    response = client.put(
        '/users/1',
        json={
            'username': 'abobora',
            'email': 'ab@gmail.com',
            'password': '1234',
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json().get('email') == 'ab@gmail.com'


def test_negative_update_user_not_found(client):
    response = client.put(
        '/users/101',
        json={
            'username': 'abobora',
            'email': 'ab@gmail.com',
            'password': '1234',
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_update_integrity_error(client, user):
    client.post(
        '/users',
        json={
            'username': 'abobora',
            'email': 'ab@gmail.com',
            'password': '1234',
        },
    )

    response_update = client.put(
        f'/users/{user.id}',
        json={
            'username': 'abobora',
            'email': 'diego@gmail.com',
            'password': '1234',
        },
    )

    assert response_update.status_code == HTTPStatus.CONFLICT
    assert response_update.json() == {
        'detail': 'username or email already in use'
    }


def test_positive_delete_user(client, user):
    response_del = client.delete(f'/users/{user.id}')
    response_get = client.get(f'/users/{user.id}')

    assert response_del.status_code == HTTPStatus.NO_CONTENT
    assert response_get.status_code == HTTPStatus.NOT_FOUND


def test_negative_delete_user_not_found(client):
    response = client.delete('/users/101')

    assert response.status_code == HTTPStatus.NOT_FOUND
