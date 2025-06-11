from dataclasses import asdict

from sqlalchemy import select

from fast_zero.models import User


def test_create_user(session, mock_time_db):
    user = User(username='diego', email='diego@email.com', password='123')

    with mock_time_db(model=User) as time:
        session.add(user)
        session.commit()
        session.flush(user)

    db_user = session.scalar(select(User).where(User.email == user.email))

    assert asdict(db_user) == {
        'id': 1,
        'username': 'diego',
        'email': 'diego@email.com',
        'password': '123',
        'created_at': time,
        'updated_at': time,
    }
