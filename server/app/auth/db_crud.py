"""
DB layer for auth and users
"""
from app.auth.db_models import User
from app.auth.utils import get_password_hash
from app.crypto_utils.db_crud import db_create_user_key_pair

def db_create_user(database, new_user, commit=True):
    """
    Create new user in database
    """
    conflict = db_get_user_by_phone_number(database, new_user.phone_number)
    if conflict:
        raise ValueError("Phone number already used")
    user_obj = User(**new_user.dict())
    user_obj.password = get_password_hash(user_obj.password)
    database.add(user_obj)
    if commit:
        database.commit()
        database.refresh(user_obj)
    db_create_user_key_pair(database, user_obj, commit)

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


def db_list_users(database, user_ids = None):
    """
    List all users from database
    """
    query = database.query(User)

    if user_ids is not None:
        query = query.filter(
            User.id.in_(user_ids)
        )

    return query.all()
