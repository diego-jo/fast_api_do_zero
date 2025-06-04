from http import HTTPStatus

from fast_zero.schemas import UserResponse


def test_positive_create_user(client):
    response = client.post(
        '/users',
        json={
            'username': 'diego',
            'email': 'diego@email.com',
            'password': '1234'
        }
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
            'id': 1,
            'username': 'diego',
            'email': 'diego@email.com'
        }


def test_create_user_without_username(client):
    response = client.post(
        '/users',
        json={
            'email': 'diego@email.com',
            'password': '1234'
        }
    )

    # TODO: alterar retorno referente ao payload para 400 bad request
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


# TODO: só funciona nessa ordem POST -> GETs
def test_positive_get_all_users(client, user):
    user_schema = UserResponse.model_validate(user).model_dump()
    response = client.get('/users')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema]}


def test_positive_get_by_id(client, user):
    response = client.get('users/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
            'id': 1,
            'username': 'diego',
            'email': 'diego@email.com'
        }


def test_get_user_by_id_not_found(client):
    response = client.get('users/11234')

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_positive_update_user(client, user):
    response = client.put(
        '/users/1',
        json={
            'username': 'diego jose',
            'email': 'diego@email.com',
            'password': '65+655345'
        }
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
            'id': 1,
            'username': 'diego jose',
            'email': 'diego@email.com',
        }


def test_update_user_not_found(client, user):
    response = client.put(
        '/users/45741',
        json={
            'username': 'diego jose',
            'email': 'diego@email.com',
            'password': '65+655345'
        }
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_update_user_without_username(client):
    response = client.put(
        '/users/1',
        json={
            'email': 'diego@email.com',
            'password': '65+655345'
        }
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_positive_delete_user(client, user):
    response = client.delete('/users/1')

    assert response.status_code == HTTPStatus.NO_CONTENT


def test_delete_user_not_found(client):
    response = client.delete('/users/100')

    assert response.status_code == HTTPStatus.NOT_FOUND
