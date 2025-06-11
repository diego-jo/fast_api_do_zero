from http import HTTPStatus


def test_positive_create_token(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': user.plain_password},
    )

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in response.json()
    assert 'token_type' in response.json()


def test_create_token_invalid_username(client):
    response = client.post(
        '/auth/token', data={'username': 'unknown', 'password': 'passwd'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'invalid username or password'}


def test_create_token_invalid_password(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': 'wrong_passwd'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'invalid username or password'}
