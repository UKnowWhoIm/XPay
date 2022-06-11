"""
Database models for users and auth
"""
from sqlalchemy import Column, String
from app.database.connection import Base
from app.utils import uuid_to_string


class User(Base):
    """
    Mapper class for users table
    """
    __tablename__ = "users"

    id = Column("id", String, primary_key=True, default=uuid_to_string)
    phone_number = Column("phone_number", String, nullable=False)
    name = Column("name", String, nullable=False)
    password = Column("password", String, nullable=False)
