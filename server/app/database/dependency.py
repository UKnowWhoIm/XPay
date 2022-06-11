"""
Database dependencies
"""
from app.database.connection import SessionLocal


def get_db():
    """
    Dependency to inject database session to controller
    """
    database = SessionLocal()
    try:
        yield database
    finally:
        database.close()
