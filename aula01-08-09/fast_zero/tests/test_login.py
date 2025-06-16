from http import HTTPStatus

from freezegun import freeze_time


def test_login_successful(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': user.plain_password},
    )

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in response.json()
    assert 'token_type' in response.json()


def test_login_with_invalid_password(client, user):
    response = client.post(
        '/auth/token', data={'username': user.email, 'password': 'any'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'invalid username or password'}


def test_login_no_registred_user(client):
    response = client.post(
        '/auth/token', data={'username': 'any@email.com', 'password': 'any'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'invalid username or password'}


def test_expired_token_after_time(client, user):
    with freeze_time('2025-06-16 12:00:00'):
        response_login = client.post(
            '/auth/token',
            data={'username': user.email, 'password': user.plain_password},
        )
        assert response_login.status_code == HTTPStatus.OK
        token = response_login.json()['access_token']

    with freeze_time('2025-06-16 12:06:00'):
        response = client.put(
            f'/users/{user.id}',
            json={
                'username': 'jose',
                'email': 'jose@email.com',
                'password': '123',
            },
            headers={'Authorization': f'Bearer {token}'},
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {'detail': 'Could not validate credentials'}


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
    with freeze_time('2025-06-16 12:00:00'):
        response_login = client.post(
            '/auth/token',
            data={'username': user.email, 'password': user.plain_password},
        )
        assert response_login.status_code == HTTPStatus.OK
        token = response_login.json()['access_token']

    with freeze_time('2025-06-16 12:06:00'):
        response = client.post(
            '/auth/refresh_token',
            headers={'Authorization': f'Bearer {token}'},
        )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}
