from http import HTTPStatus

from freezegun import freeze_time


def test_login_with_valid_credendials(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': user.plain_password},
    )

    data = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in data
    assert 'token_type' in data


def test_login_with_invalid_password(client, user):
    response = client.post(
        '/auth/token', data={'username': user.email, 'password': '123'}
    )

    data = response.json()

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert data == {'detail': 'invalid credentials'}


def test_login_with_invalid_username(client, user):
    response = client.post(
        '/auth/token',
        data={'username': 'jose@email.com', 'password': '123@asd'},
    )

    data = response.json()

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert data == {'detail': 'invalid credentials'}


def test_login_with_not_registred_user(client):
    response = client.post(
        '/auth/token',
        data={'username': 'amenda@email.com', 'password': '456789'},
    )

    data = response.json()

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert data == {'detail': 'invalid credentials'}


def test_expired_token_after_time(client, user):
    with freeze_time('2025-06-20 12:00:00'):
        response = client.post(
            '/auth/token',
            data={'username': user.email, 'password': user.plain_password},
        )

        token = response.json().get('access_token')

    with freeze_time('2025-06-20 12:06:00'):
        update_response = client.put(
            f'/users/{user.id}',
            json={
                'username': 'jose',
                'email': 'diego@email.com',
                'password': '123',
            },
            headers={'Authorization': f'Bearer {token}'},
        )

        assert update_response.status_code == HTTPStatus.UNAUTHORIZED
        assert update_response.json() == {'detail': 'invalid credentials'}


def test_refresh_token(client, token):
    response = client.post(
        '/auth/refresh_token',
        headers={'Authorization': f'Bearer {token}'},
    )
    data = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in data
    assert 'token_type' in data
    assert data['token_type'] == 'Bearer'


def test_refresh_token_with_expired_token(client, user):
    with freeze_time('2025-06-23 12:00:00'):
        token_response = client.post(
            '/auth/token',
            data={'username': user.email, 'password': user.plain_password},
        )

        token = token_response.json().get('access_token')

    with freeze_time('2025-06-23 12:06:00'):
        response = client.post(
            '/auth/refresh_token',
            headers={'Authorization': f'Bearer {token}'},
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {'detail': 'invalid credentials'}
