from http import HTTPStatus

from fast_zero.schemas import UserResponse


def test_positive_create_user(client):
    # arrange
    # act
    response = client.post(
        '/users',
        json={
            'username': 'diego',
            'email': 'diego2@email.com',
            'password': 'asd@123',
        },
    )

    # assert
    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'username': 'diego',
        'email': 'diego2@email.com',
    }


def test_create_user_with_already_in_use_username(client, user):
    response = client.post(
        '/users',
        json={
            'username': 'diego',
            'email': 'djol@email.com',
            'password': 'asd@123',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'username already in use'}


def test_create_user_with_already_in_use_email(client, user):
    response = client.post(
        '/users',
        json={
            'username': 'testetss',
            'email': 'diego@email.com',
            'password': 'asd@123',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'email already in use'}


def test_get_all_users_default_params(client, user):
    user_schema = UserResponse.model_validate(user).model_dump()
    response = client.get('/users')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema]}


def test_positive_get_user_by_id(client, user):
    user_schema = UserResponse.model_validate(user).model_dump()
    response = client.get('/users/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == user_schema


def test_get_user_by_id_not_found(client):
    response = client.get('/users/10111')
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_positive_update_user(client, user, token):
    response = client.put(
        f'/users/{user.id}',
        json={
            'username': 'joao',
            'email': 'joao2@email.com',
            'password': '123456',
        },
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'username': 'joao',
        'email': 'joao2@email.com',
    }


def test_update_user_with_already_in_use_username(client, user, token):
    client.post(
        '/users',
        json={
            'username': 'joao',
            'email': 'joao@email.com',
            'password': 'asd@123',
        },
    )

    update_response = client.put(
        f'/users/{user.id}',
        json={
            'username': 'joao',
            'email': 'diego@email.com',
            'password': '123456',
        },
        headers={'Authorization': f'Bearer {token}'},
    )

    assert update_response.status_code == HTTPStatus.CONFLICT
    assert update_response.json() == {'detail': 'username already in use'}


def test_update_user_with_already_in_use_email(client, user, token):
    client.post(
        '/users',
        json={
            'username': 'joao',
            'email': 'joao@email.com',
            'password': 'asd@123',
        },
    )

    update_response = client.put(
        f'/users/{user.id}',
        json={
            'username': 'diego',
            'email': 'joao@email.com',
            'password': '123456',
        },
        headers={'Authorization': f'Bearer {token}'},
    )

    assert update_response.status_code == HTTPStatus.CONFLICT
    assert update_response.json() == {'detail': 'email already in use'}


def test_update_user_with_diferent_id(client, token):
    response = client.put(
        '/users/19',
        json={
            'username': 'joao',
            'email': 'joao@email.com',
            'password': 'asd@123',
        },
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN


def test_positive_delete_user(client, user, token):
    del_response = client.delete(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )
    get_response = client.get(f'/users/{user.id}')

    assert del_response.status_code == HTTPStatus.NO_CONTENT
    assert get_response.status_code == HTTPStatus.NOT_FOUND


def test_delete_user_with_diferent_id(client, token):
    response = client.delete(
        '/users/19',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
