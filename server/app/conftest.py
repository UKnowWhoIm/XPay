"""
Test fixtures
"""
import pytest
from app.auth.utils import create_access_token

from app.database.connection import SessionLocal
from app.crypto_utils import load_server_keys


@pytest.fixture
def db_session():
    """
    Yield a test db session that rolls back after each test
    """
    load_server_keys()
    database = SessionLocal()
    try:
        yield database
    finally:
        database.rollback()
        database.close()


def get_auth_header(user):
    """
    Get Authorization header for requests
    """
    token = create_access_token(user.id)
    return {"Authorization": f"Bearer {token}"}
