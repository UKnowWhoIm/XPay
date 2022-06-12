"""
DB layer for auth and users
"""
from sqlalchemy.exc import IntegrityError

from app.auth.db_models import User
from app.auth.utils import get_password_hash

def db_create_user(database, new_user, commit=True):
    """
    Create new user in database
    """
    try:
        user_obj = User(**new_user.dict())
        user_obj.password = get_password_hash(user_obj.password)
        database.add(user_obj)
        if commit:
            database.commit()
            database.refresh(user_obj)

    except IntegrityError as exc:
        raise ValueError("Phone number is already registered") from exc
    return user_obj


def db_get_user_by_id(database, user_id):
    """
    Select user by id in database
    """
    return database.query(User).get(user_id)


def db_get_user_by_phone_number(database, phone_number):
    """
    Select user by phone number in database
    """
    return database.query(User).filter_by(phone_number=phone_number).first()
