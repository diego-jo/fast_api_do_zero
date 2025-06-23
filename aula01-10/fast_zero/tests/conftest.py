from contextlib import contextmanager
from datetime import datetime

import factory
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import StaticPool, event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from fast_zero.app import app
from fast_zero.config.database import get_session
from fast_zero.models.tables import table_registry
from fast_zero.models.user import User


class UserFactory(factory.Factory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'test{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@email.com')
    password = factory.LazyAttribute(lambda obj: f'{obj.username}@pass.com')


@pytest.fixture
def client(session):
    def overrided_session():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = overrided_session
        yield client

    app.dependency_overrides.clear()


# TODO: este usuário existe na memoria no contexto do modulo testado?
# se sim mesmo não injetando ele na função, as funcionalidades enchergam ele
@pytest.fixture
def token(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': user.plain_password},
    )

    return response.json().get('access_token')


@pytest_asyncio.fixture
async def user(session):
    plain_password = '123@asd'
    user = UserFactory(password=plain_password)

    session.add(user)
    await session.commit()
    await session.refresh(user)

    user.plain_password = plain_password
    return user


@pytest_asyncio.fixture
async def other_user(session):
    plain_password = '123@asd'
    user = UserFactory(password=plain_password)

    session.add(user)
    await session.commit()
    await session.refresh(user)

    user.plain_password = plain_password
    return user


@pytest_asyncio.fixture
async def session():
    engine = create_async_engine(
        'sqlite+aiosqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.create_all)

    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.drop_all)


@pytest.fixture
def mock_db_time():
    return _mock_db_time


@contextmanager
def _mock_db_time(*, model, time=datetime(2025, 6, 18)):
    def hook(mapper, connection, target):
        if hasattr(target, 'created_at'):
            target.created_at = time
        if hasattr(target, 'updated_at'):
            target.updated_at = time

    event.listen(model, 'before_insert', hook)
    yield time
    event.remove(model, 'before_insert', hook)
