from dataclasses import asdict

from sqlalchemy import select

from fast_zero.models import User


def test_create_user_db(session, mock_db_time):
    user = User(
        username='diego',
        email='diego@email.com',
        password='1234'
    )

    with mock_db_time(model=User) as time:
        session.add(user)
        session.commit()
        session.flush(user)

    db_user = session.scalar(
        select(User).where(User.username == user.username)
    )

    assert asdict(db_user) == {
        'id': 1,
        'username': 'diego',
        'email': 'diego@email.com',
        'password': '1234',
        'created_at': time,
        'updated_at': time,
    }
