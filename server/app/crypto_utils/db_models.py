"""
Database models for keys
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, func, Enum, Integer, LargeBinary
from sqlalchemy.orm import relationship

from app.database.connection import Base
from app.crypto_utils.enums import KeyStatus


class Key(Base):
    """
    Mapper class for keys table
    """
    __tablename__ = "keys"

    id = Column("id", Integer, primary_key=True)
    user_id = Column("user_id", String, ForeignKey("users.id"), nullable=False)
    public_key = Column("public_key", LargeBinary, nullable=False)
    private_key = Column("private_key", LargeBinary, nullable=False)
    created_at = Column("created_at", DateTime, nullable=False, server_default=func.now())
    status = Column("status", Enum(KeyStatus), nullable=False, default=KeyStatus.ACTIVE)

    user = relationship("User")
