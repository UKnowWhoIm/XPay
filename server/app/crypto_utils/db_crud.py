"""
DB layer for crypto_utils
"""
from app.crypto_utils import create_user_key_pair
from app.crypto_utils.db_models import Key


def db_create_user_key_pair(database, user, commit=False):
    """
    Create a key pair for the user
    """
    private_key, public_key = create_user_key_pair()
    key = Key(user=user, public_key=public_key, private_key=private_key)
    database.add(key)
    if commit:
        database.commit()
    return key


def db_get_public_keys_of_users(database, user_ids):
    """
    Get public keys of users
    """
    raw_data = database.query(Key.public_key, Key.user_id)\
        .filter(Key.user_id.in_(user_ids))\
        .filter(Key.status == Key.ACTIVE)\
        .all()

    return {user_id: public_key for public_key, user_id in raw_data}
