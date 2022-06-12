"""
Test fixtures
"""
import pytest

from app.database.connection import SessionLocal


@pytest.fixture
def db_session():
    """
    Yield a test db session that rolls back after each test
    """
    database = SessionLocal()
    try:
        yield database
    finally:
        database.rollback()
        database.close()
