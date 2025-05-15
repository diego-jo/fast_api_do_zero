from http import HTTPStatus


def test_app_return_right_payload(client):
    response = client.get('/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'aula01-02'}


def test_app_html_route_right_value(client):
    response = client.get('/html')

    assert response.status_code == HTTPStatus.OK
    assert 'text/html' in response.headers.get('content-type')
    assert 'Teste de api com html!' in response.text


def test_create_new_user(client):
    response = client.post(
        '/users',
        json={
            'username': 'maria',
            'email': 'maria@email.com',
            'password': '123asd',
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'username': 'maria',
        'email': 'maria@email.com',
        'id': 1,
    }


def test_read_users(client):
    client.post(
        '/users',
        json={
            'username': 'diego',
            'email': 'diego@email.com',
            'password': '123asd',
        },
    )
    response = client.get('/users')

    assert response.status_code == HTTPStatus.OK
    assert len(response.json().get('users')) > 0


def test_positive_update_user(client):
    updated_user = {
        'username': 'diego-jose',
        'email': 'diego-jose@email.com',
        'password': '123asd',
    }

    response = client.put('/users/2', json=updated_user)
    updated_user_response = response.json()

    assert response.status_code == HTTPStatus.OK
    assert updated_user_response.get('username') == 'diego-jose'
    assert updated_user_response.get('email') == 'diego-jose@email.com'


# TODO: Entender pq o client está chegando poluído nesta função fazendo com
# que o PUT seja enviado com o id = 2 ao invés de 130

# entendimento: a validação do payload com o pydantic acontece antes da
# validação de existencia do id do recurso por isso o erro 422 ao inves do 404
def test_negative_update_user(client):
    updated_user = {
        'username': 'a',
        'email': 'aa@email.com',
        'password': '123',
    }
    response = client.put('/users/130', json=updated_user)

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json().get('detail') == 'User not found'


def test_positive_delete_user(client):
    client.delete('users/2')
    response = client.get('/users')

    assert len(response.json().get('users')) == 1


def test_negative_delete_user(client):
    response = client.delete('users/20')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json().get('detail') == 'User not found'
