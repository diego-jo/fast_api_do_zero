import pytest
from fastapi.testclient import TestClient
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import Session

from fast_zero.app import app
from fast_zero.config.database import get_session
from fast_zero.models.tables import table_registry
from fast_zero.models.user import User
from fast_zero.security.auth import hash_password


@pytest.fixture
def client(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client

    app.dependency_overrides.clear()


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
    # adicionado devido ao warning ResourceWarning: Enable tracemalloc to get
    # the object allocation traceback
    # lançado após a atualização do pytest-cov de 6.1.1 -> 6.2.1
    engine.dispose()


@pytest.fixture
def user(session):
    passwd = '123'
    user = User(
        username='diego',
        email='diego@email.com',
        password=hash_password(passwd),
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    user.plain_password = passwd

    return user


@pytest.fixture
def token(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': user.plain_password},
    )

    return response.json().get('access_token')
