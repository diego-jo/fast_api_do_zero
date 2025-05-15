from http import HTTPStatus


def test_positive_user_create(client):
    response = client.post(
        '/users',
        json={
            'username': 'diego',
            'email': 'diego@email.com',
            'password': '123456',
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 2,
        'username': 'diego',
        'email': 'diego@email.com',
    }


def test_positive_user_list(client):
    response = client.get('/users')

    assert response.status_code == HTTPStatus.OK
    assert len(response.json().get('users')) >= 1


def test_positive_get_user_by_id(client):
    response = client.get('/users/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'username': 'diego',
        'email': 'diego@email.com',
    }


def test_negative_get_user_not_found(client):
    response = client.get('/users/101')

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_positive_update_user(client):
    response = client.put(
        '/users/1',
        json={
            'username': 'abobora',
            'email': 'ab@gmail.com',
            'password': '1234',
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json().get('email') == 'ab@gmail.com'


def test_negative_update_user_not_found(client):
    response = client.put(
        '/users/101',
        json={
            'username': 'abobora',
            'email': 'ab@gmail.com',
            'password': '1234',
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_positive_delete_user(client):
    response_del = client.delete('/users/1')
    response_get = client.get('/users/1')

    assert response_del.status_code == HTTPStatus.NO_CONTENT
    assert response_get.status_code == HTTPStatus.NOT_FOUND


def test_negative_delete_user_not_found(client):
    response = client.delete('/users/101')

    assert response.status_code == HTTPStatus.NOT_FOUND
