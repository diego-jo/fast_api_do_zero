from http import HTTPStatus

from jwt import decode

from fast_zero.security import (
    SECRET_KEY,
    create_access_token,
    get_password_hash,
    verify_password,
)


def test_positive_create_token():
    # Arrange
    data = {'name': 'fulano'}

    # Act
    token = create_access_token(data)
    decoded = decode(token, SECRET_KEY, algorithms=['HS256'])

    # Assert
    assert decoded['name'] == 'fulano'
    assert 'exp' in decoded


def test_positive_get_password_hash():
    plain_password = 'qualquer_senha123'

    hashed_pass = get_password_hash(plain_password)
    assert hashed_pass != plain_password


def test_positive_password_verify():
    plain_password = 'qualquer_senha123'
    hashed_pass = get_password_hash(plain_password)
    verified_password = verify_password(plain_password, hashed_pass)

    assert verified_password is True


def test_jwt_invalid_token(client):
    response = client.delete(
        '/users/11', headers={'Authorization': 'Bearer invalid-token'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}
    assert 'WWW-Authenticate' in response.headers


def test_empty_token_sub(client):
    token = create_access_token({'sub': ''})
    response = client.delete(
        '/users/11', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}
    assert 'WWW-Authenticate' in response.headers


def test_user_not_found_for_authorization(client):
    token = create_access_token({'sub': 'unknown@unknown'})
    response = client.delete(
        '/users/11', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}
    assert 'WWW-Authenticate' in response.headers
