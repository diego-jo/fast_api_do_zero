from dataclasses import asdict

import pytest
from sqlalchemy import select

from fast_zero.models.user import User


@pytest.mark.asyncio
async def test_create_user_to_validate_db(session, mock_db_time):
    user = User(username='diego', email='diego@email.com', password='1234')

    with mock_db_time(model=User) as time:
        session.add(user)
        await session.commit()

    db_user = await session.scalar(
        select(User).where(User.username == user.username)
    )

    assert asdict(db_user) == {
        'id': user.id,
        'username': 'diego',
        'email': 'diego@email.com',
        'password': user.password,
        'created_at': time,
        'updated_at': time,
    }
