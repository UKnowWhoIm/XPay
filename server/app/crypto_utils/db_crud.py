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
