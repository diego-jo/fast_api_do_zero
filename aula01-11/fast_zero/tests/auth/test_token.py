from datetime import timedelta
from http import HTTPStatus

import pytest
from freezegun import freeze_time


def test_create_token(client, user):
    response = client.post(
        '/auth/token',
        data={
            'username': user.email,
            'password': user.plain_password,
        },
    )

    data = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in data
    assert 'token_type' in data
    assert 'expires_in' in data


def test_create_token_user_not_found(client, user):
    response = client.post(
        '/auth/token',
        data={
            'username': 'any_email@mail.com',
            'password': user.plain_password,
        },
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Invalid username or password'}


def test_create_token_with_invalid_password(client, user):
    response = client.post(
        '/auth/token',
        data={
            'username': user.email,
            'password': 'wrong_pass',
        },
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Invalid username or password'}


def test_refresh_token(client, user):
    with freeze_time('2025-06-30 12:00:00') as frozen_time:
        response_token = client.post(
            '/auth/token',
            data={
                'username': user.email,
                'password': user.plain_password,
            },
        )

        assert response_token.status_code == HTTPStatus.OK
        token = response_token.json().get('access_token')

        # TODO: Nota, aidicionado o congelamento de tempo pois nesse caso de
        # geração de token e refresh de token a execução é tão rápida que
        # o mesmo token e tempo de expiração são gerados nas 2 chamadas de
        # endpoint.
        frozen_time.tick(timedelta(seconds=290))

        response_refresh = client.post(
            '/auth/refresh_token',
            headers={'Authorization': f'Bearer {token}'},
        )

        data = response_refresh.json()

        assert response_refresh.status_code == HTTPStatus.OK
        assert data.get('access_token') != token


def test_refresh_token_with_expired_token(client, user):
    with freeze_time('2025-06-30 12:00:00') as frozen_time:
        response_token = client.post(
            '/auth/token',
            data={
                'username': user.email,
                'password': user.plain_password,
            },
        )

        assert response_token.status_code == HTTPStatus.OK
        token = response_token.json().get('access_token')

        frozen_time.tick(timedelta(seconds=301))

        response_refresh = client.post(
            '/auth/refresh_token',
            headers={'Authorization': f'Bearer {token}'},
        )

        assert response_refresh.status_code == HTTPStatus.UNAUTHORIZED
        assert response_refresh.json() == {
            'detail': 'Could not validate credentials'
        }


@pytest.mark.asyncio
async def test_refresh_token_with_user_deleted_token(client, user, session):
    with freeze_time('2025-06-30 12:00:00') as frozen_time:
        response_token = client.post(
            '/auth/token',
            data={
                'username': user.email,
                'password': user.plain_password,
            },
        )

        assert response_token.status_code == HTTPStatus.OK
        token = response_token.json().get('access_token')

        await session.delete(user)
        await session.commit()

        frozen_time.tick(timedelta(seconds=290))

        response_refresh = client.post(
            '/auth/refresh_token',
            headers={'Authorization': f'Bearer {token}'},
        )

        assert response_refresh.status_code == HTTPStatus.UNAUTHORIZED
        assert response_refresh.json() == {
            'detail': 'Could not validate credentials'
        }
