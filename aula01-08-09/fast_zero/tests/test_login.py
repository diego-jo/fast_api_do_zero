from http import HTTPStatus


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
