import pytest
from fastapi import HTTPException
from jwt import decode

from fast_zero.security import (
    create_jwt_token,
    env,
    get_current_user,
    hash_password,
    verify_password,
)


def test_positive_create_jwt_token():
    token = create_jwt_token(data={'sub': 'teste'})
    decoded_token = decode(token, env.SECRET_KEY, algorithms=[env.ALGORITHM])

    assert decoded_token.get('sub') == 'teste'
    assert 'exp' in decoded_token


def test_positive_get_current_user(session, user):
    token = create_jwt_token(data={'sub': user.email})
    current_user = get_current_user(token, session)

    assert current_user.email == user.email


def test_get_current_user_invalid_token():
    with pytest.raises(HTTPException, match='Could not validate credentials'):
        get_current_user(token='invalid_token')


def test_get_current_user_without_sub_in_token():
    token = create_jwt_token(data={'un_sub': 'sem_sub'})
    with pytest.raises(HTTPException, match='Could not validate credentials'):
        get_current_user(token=token)


def test_get_current_user_expired_token(monkeypatch):
    monkeypatch.setattr(
        'fast_zero.security.env.TOKEN_EXPIRATION_TIME_SECONDS', 0
    )
    token = create_jwt_token(data={'sub': 'email'})

    with pytest.raises(HTTPException, match='Expired token'):
        get_current_user(token=token)


def test_get_current_user_not_found(session):
    token = create_jwt_token(data={'sub': 'unknown'})
    with pytest.raises(HTTPException, match='Could not validate credentials'):
        get_current_user(token, session)


def test_positive_hash_password(user):
    hashed_passwd = hash_password(user.plain_password)

    assert verify_password(user.plain_password, hashed_passwd)
