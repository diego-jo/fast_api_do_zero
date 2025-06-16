from sqlalchemy import select

from fast_zero.models.user import User


def test_create_user_db(session):
    user = User(username='diego', email='diego@email.com', password='123')

    session.add(user)
    session.commit()

    db_user = session.scalar(
        select(User).where(User.username == user.username)
    )

    assert db_user.id == 1
    assert db_user.username == user.username
