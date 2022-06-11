"""
Database models for users and auth
"""
from sqlalchemy import Column, Integer, String
from app.database.connection import Base


class User(Base):
    """
    Mapper class for users table
    """
    __tablename__ = "users"

    id = Column("id", Integer, primary_key=True)
    phone_number = Column("phone_number", String, nullable=False)
    name = Column("name", String, nullable=False)
    password = Column("password", String, nullable=False)
