from contextlib import contextmanager
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session

from fast_zero.app import app
from fast_zero.app import database as mocked_database
from fast_zero.models.user_model import table_registry
from fast_zero.schemas.user_schema import UserEntity


@pytest.fixture
def client(database):
    return TestClient(app=app)


@pytest.fixture
def database():
    mocked_database.clear()

    user = UserEntity(
        id=1,
        username='diego',
        password='1234',
        email='diego@email.com',
    )

    mocked_database.append(user)
    yield
    mocked_database.clear()


@pytest.fixture
def session():
    engine = create_engine('sqlite:///:memory:')
    table_registry.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    table_registry.metadata.drop_all(engine)


@contextmanager
def _mock_db_time(*, model, time=datetime(2025, 1, 1)):
    def fake_time_hook(mapper, connection, target):
        if hasattr(target, 'created_at'):
            target.created_at = time
        if hasattr(target, 'updated_at'):
            target.updated_at = time

    event.listen(model, 'before_insert', fake_time_hook)
    yield time
    event.remove(model, 'before_insert', fake_time_hook)


@pytest.fixture
def mock_db_time():
    return _mock_db_time
