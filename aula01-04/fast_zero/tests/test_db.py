from dataclasses import asdict

from sqlalchemy import select

from fast_zero.models import User


def test_create_user(session, mock_db_time):
    with mock_db_time(model=User) as (created_time, updated_time):
        new_user = User(
            username='diego', password='123asd', email='diego@e3.com'
        )
        session.add(new_user)
        session.commit()

    user = session.scalar(select(User).where(User.username == 'diego'))
    breakpoint()
    assert asdict(user) == {
        'id': 1,
        'username': 'diego',
        'password': '123asd',
        'email': 'diego@e3.com',
        'created_at': created_time,
        'updated_at': updated_time
    }
