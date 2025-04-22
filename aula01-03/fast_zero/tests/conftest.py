import pytest
from fastapi.testclient import TestClient

from fast_zero.app import app


@pytest.fixture
def client():
    client = TestClient(app)
    return client


# @pytest.fixture()
# def reset_client(client)
