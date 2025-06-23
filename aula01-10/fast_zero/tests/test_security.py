import pytest
from fastapi import HTTPException
from jwt import decode

from fast_zero.security.auth import create_jwt_token, env, get_current_user


def test_create_jwt_token():
    token = create_jwt_token(data={'sub': 'test'})

    d_token = decode(token, env.SECRET_KEY, algorithms=[env.ALGORITHM])

    assert d_token.get('sub') == 'test'
    assert 'exp' in d_token


@pytest.mark.asyncio
async def test_get_current_user(session, user):
    token = create_jwt_token(data={'sub': user.email})

    valid_user = await get_current_user(session, token)

    assert user.id == valid_user.id


@pytest.mark.asyncio
async def test_get_current_user_without_sub(session):
    token = create_jwt_token(data={'mail': 'diego@email.com'})

    with pytest.raises(HTTPException, match='invalid credentials'):
        await get_current_user(session, token)


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(session):
    with pytest.raises(HTTPException, match='invalid credentials'):
        await get_current_user(session, 'token')


@pytest.mark.asyncio
async def test_get_current_user_user_not_found(session):
    token = create_jwt_token(data={'sub': 'd@email.com'})

    with pytest.raises(HTTPException, match='invalid credentials'):
        await get_current_user(session, token)


@pytest.mark.asyncio
async def test_get_current_user_expired_token(session, monkeypatch):
    monkeypatch.setattr(
        'fast_zero.security.auth.env.TOKEN_TIME_EXPIRATION_SECS', 0
    )
    token = create_jwt_token(data={'sub': 'diego@email.com'})

    with pytest.raises(HTTPException, match='invalid credentials'):
        await get_current_user(session, token)
