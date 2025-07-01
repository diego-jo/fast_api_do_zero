from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest
from fastapi.exceptions import HTTPException
from freezegun import freeze_time
from jwt import decode

from fast_zero.auth.security import (
    create_access_token,
    get_current_user,
    hash_password,
    settings,
    verify_password,
)


def test_hash_password():
    plain_password = '123@asd'
    hashed_password = hash_password(plain_password)

    assert plain_password != hashed_password
    assert verify_password(plain_password, hashed_password)


def test_create_access_token():
    token, _ = create_access_token(data={'sub': 'teste@email.com'})

    decoded_token = decode(
        token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
    )

    assert 'sub' in decoded_token
    assert 'exp' in decoded_token
    assert decoded_token.get('sub') == 'teste@email.com'


@freeze_time('2025-06-27 12:00:00')
def test_create_access_token_with_valid_expiration_time():
    token, _ = create_access_token(data={'sub': 'teste'})

    decoded_token = decode(
        token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
    )
    expires_in = decoded_token.get('exp')
    expected_exp = datetime.now(tz=ZoneInfo('UTC')) + timedelta(
        seconds=settings.TOKEN_TIME_EXPIRATION_SECS
    )

    assert expires_in == int(expected_exp.timestamp())


@pytest.mark.asyncio
async def test_get_current_user(session, user):
    token, _ = create_access_token(data={'sub': user.email})
    current_user = await get_current_user(session, token)

    assert current_user.id == user.id


@pytest.mark.asyncio
async def test_get_current_user_with_invalid_token(session):
    token = 'invalid_token'

    with pytest.raises(HTTPException, match='Could not validate credentials'):
        await get_current_user(session, token)


@pytest.mark.asyncio
async def test_get_current_user_with_no_sub(session):
    token, _ = create_access_token(data={'test': 'test'})

    with pytest.raises(HTTPException, match='Could not validate credentials'):
        await get_current_user(session, token)


@pytest.mark.asyncio
async def test_get_current_user_with_not_found_user(session, user):
    token, _ = create_access_token(data={'sub': 'diego@mail.com'})

    with pytest.raises(HTTPException, match='Could not validate credentials'):
        await get_current_user(session, token)


@pytest.mark.asyncio
async def test_get_current_user_with_expired_token(session, user):
    with freeze_time('2025-06-27 12:00:00') as frozen_time:
        token, _ = create_access_token(data={'sub': user.email})

        frozen_time.tick(delta=timedelta(minutes=6))

        with pytest.raises(
            HTTPException, match='Could not validate credentials'
        ):
            await get_current_user(session, token)
