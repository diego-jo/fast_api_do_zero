from contextlib import contextmanager
from datetime import datetime

import factory
import factory.fuzzy
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import StaticPool, event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from fast_zero.app import app
from fast_zero.auth.security import hash_password
from fast_zero.database.config import get_session
from fast_zero.database.tables import table_registry
from fast_zero.todo.enums import TodoState
from fast_zero.todo.models import Todo
from fast_zero.user.models import User


class UserFactory(factory.Factory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@email.com')
    password = factory.LazyAttribute(lambda obj: f'{obj.username}@123')


class TodoFactory(factory.Factory):
    class Meta:
        model = Todo

    title = factory.Sequence(lambda n: f'task {n}')
    description = factory.fuzzy.FuzzyText(prefix='task ', length=20)
    state = factory.fuzzy.FuzzyChoice(TodoState)


@pytest_asyncio.fixture
async def user(session):
    plain_password = '123@asd'
    user = UserFactory(password=hash_password(plain_password))

    session.add(user)
    await session.commit()
    await session.refresh(user)

    user.plain_password = plain_password

    return user


@pytest_asyncio.fixture
async def session():
    engine = create_async_engine(
        url='sqlite+aiosqlite:///:memory:',
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
def _mock_db_time(*, model, time=datetime(2025, 6, 27)):
    def hook(mapper, connection, target):
        if hasattr(target, 'created_at'):
            target.created_at = time
        if hasattr(target, 'updated_at'):
            target.updated_at = time

    event.listen(model, 'before_insert', hook)
    yield time
    event.remove(model, 'before_insert', hook)


@pytest.fixture
def client(session):
    def overrided_session():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = overrided_session
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def token(client, user):
    response = client.post(
        '/auth/token',
        data={
            'username': user.email,
            'password': user.plain_password,
        },
    )

    return response.json()['access_token']


@pytest_asyncio.fixture
async def todo(session, user):
    todo = TodoFactory(user_id=user.id, state='todo')
    session.add(todo)
    await session.commit()
    await session.refresh(todo)

    return todo
