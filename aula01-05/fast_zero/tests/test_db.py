from dataclasses import asdict

from sqlalchemy import select

from fast_zero.models.user_model import User


def test_positive_create_user(session, mock_db_time):
    with mock_db_time(model=User) as time:
        new_user = User(
            username='diego', email='diego@email.com', password='123'
        )
        session.add(new_user)
        session.commit()

    user = session.scalar(select(User).where(User.username == 'diego'))

    assert asdict(user) == {
        'id': 1,
        'username': 'diego',
        'email': 'diego@email.com',
        'password': '123',
        'created_at': time,
        'updated_at': time,
    }
