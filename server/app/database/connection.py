"""
Database connection utils
"""
from os import environ

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm.session import sessionmaker


def set_up_database(env_variable="DATABASE_URL"):
    """Set up connection to a db"""
    database_url = environ.get(env_variable)

    if database_url is None:
        return None

    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    return create_engine(database_url)


def verify_postgres():
    """
    Connects to postgres database and raises exception if failed
    """
    engine = set_up_database()
    engine.connect()


Base = declarative_base()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=set_up_database())
