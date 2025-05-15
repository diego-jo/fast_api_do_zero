from http import HTTPStatus

# TODO: implementar fixture para zerar base de dados em memória


def test_positive_list_users(client):
    # TODO: deve ser substituído por uma fixture que popula o
    # banco previamente?!
    client.post(
        '/users',
        json={
            'username': 'diego',
            'email': 'diego@email.com',
            'password': 'asd123',
        },
    )

    response = client.get('/users')

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == 1
    assert response.json() == {
        'users': [
            {
                'username': 'diego',
                'email': 'diego@email.com',
                'id': 1,
            }
        ]
    }


def test_positive_get_user_by_id(client):
    client.post(
        '/users',
        json={
            'username': 'diego',
            'email': 'diego@email.com',
            'password': 'asd123',
        },
    )

    response = client.get('/users/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'username': 'diego',
        'email': 'diego@email.com',
    }


def test_get_by_id_not_found(client):
    response = client.get('/users/124354')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_positive_create_user(client):
    response = client.post(
        '/users',
        json={
            'username': 'diego',
            'email': 'diego@email.com',
            'password': 'asd123',
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json()['email'] == 'diego@email.com'


def test_positive_update_user(client):
    response = client.post(
        '/users',
        json={
            'username': 'first_user',
            'email': 'first_user@email.com',
            'password': 'asd123',
        },
    )
    user_id = response.json()['id']

    updated_user = client.put(
        f'/users/{user_id}',
        json={
            'username': 'android',
            'email': 'android18@email.com',
            'password': '1818',
        },
    )

    assert updated_user.status_code == HTTPStatus.OK
    assert updated_user.json()['id'] == user_id
    assert updated_user.json()['username'] == 'android'


def test_update_user_not_found(client):
    # TODO: Faz sentido ter que informar o payload de update para um teste em
    # que a validação é encima do ID do recurso que não existe?

    # R: Talvez faça, pensando que todo contexto deve atender as regras de
    # validação, exceto pelo ID que se refere ao um recurso inexistente.
    response = client.put(
        '/users/124354',
        json={
            'username': 'android',
            'email': 'android18@email.com',
            'password': '1818',
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_positive_delete_user(client):
    response = client.delete('/users/1')

    assert response.status_code == HTTPStatus.NO_CONTENT


def test_delete_user_not_found(client):
    response = client.delete('/users/124354')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}
