from http import HTTPStatus

from fastapi.testclient import TestClient

from fast_zero.app import app


def test_root_deve_retornar_ok_e_body_correto():
    # arrange
    client = TestClient(app)

    # act
    response = client.get('/')

    # assert
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'aula01-02'}


def test_html_deve_retornar_conteudo_esperado():
    client = TestClient(app)

    response = client.get('/html')

    assert '<body>' in response.text
    assert 'Teste de api com html!' in response.text
