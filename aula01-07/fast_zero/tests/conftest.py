from contextlib import contextmanager
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import StaticPool, create_engine, event
from sqlalchemy.orm import Session

from fast_zero.app import app
from fast_zero.database import get_session
from fast_zero.models import User, table_registry
from fast_zero.security import create_jwt_token, hash_password


@pytest.fixture
def client(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def user(session):
    user = User(
        username='diego',
        email='diego@email.com',
        password=hash_password('1234'),
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    user.plain_password = '1234'

    return user


@pytest.fixture
def token(user):
    return create_jwt_token(data={'sub': user.email})


@pytest.fixture
def session():
    engine = create_engine(
        'sqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )
    table_registry.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    table_registry.metadata.drop_all(engine)


@pytest.fixture
def mock_time_db():
    return _mock_time_db


@contextmanager
def _mock_time_db(*, model, time=datetime(2025, 6, 10)):
    def event_hook(mapper, connection, target):
        if hasattr(target, 'created_at'):
            target.created_at = time
        if hasattr(target, 'updated_at'):
            target.updated_at = time

    event.listen(model, 'before_insert', event_hook)
    yield time
    event.remove(model, 'before_insert', event_hook)
