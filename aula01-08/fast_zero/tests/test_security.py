from datetime import datetime, timedelta

import pytest
from fastapi import HTTPException
from jwt import decode

from fast_zero.security.auth import (
    create_jwt_token,
    env,
    get_current_user,
    hash_password,
    verify_password,
)


def test_hash_plain_password():
    plain_password = 'asd@123'
    hashed_password = hash_password(plain_password)

    assert plain_password != hashed_password
    assert verify_password(plain_password, hashed_password)


def test_create_jwt_token_successful():
    TOKEN_TIME = timedelta(seconds=299)
    data = {'sub': 'email@email.com'}

    token = create_jwt_token(data)
    decoded_token = decode(token, env.SECRET_KEY, algorithms=[env.ALGORITHM])
    token_exp_time = (
        datetime.fromtimestamp(decoded_token.get('exp')) - datetime.now()
    )

    assert decoded_token.get('sub') == 'email@email.com'
    assert token_exp_time >= TOKEN_TIME


def test_get_current_user(session, user, token):
    current_user = get_current_user(session, token)

    assert current_user.id == user.id


def test_get_current_user_with_invalid_token(session):
    with pytest.raises(HTTPException, match='not enough permissions'):
        get_current_user(session, 'token')


def test_get_current_user_without_sub(session):
    token = create_jwt_token(data={'test': 'test'})

    with pytest.raises(HTTPException, match='not enough permissions'):
        get_current_user(session, token)


def test_get_current_user_with_expired_token(session, monkeypatch):
    monkeypatch.setattr(
        'fast_zero.security.auth.env.TOKEN_EXPIRATION_TIME_SECONDS', 0
    )
    token = create_jwt_token(data={'test': 'test'})

    with pytest.raises(HTTPException, match='expired token'):
        get_current_user(session, token)


def test_get_current_user_with_no_valid_user(session):
    token = create_jwt_token(data={'sub': 'invalid_@email.com'})

    with pytest.raises(HTTPException, match='not enough permissions'):
        get_current_user(session, token)
