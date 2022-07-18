"""
DB Models for payments
"""
from sqlalchemy import Column, Enum, Float, ForeignKey, String, DateTime, func

from app.database.connection import Base
from app.payments.enums import RequestStates, TransactionTypes
from app.utils import uuid_to_string


class Transaction(Base):
    """
    Mapper class for transactions table
    """
    __tablename__ = "transactions"

    id = Column("id", String, primary_key=True, default=uuid_to_string)
    type = Column("type", Enum(TransactionTypes), nullable=False)
    sender_id = Column("sender_id", String, ForeignKey("users.id"), nullable=True)
    receiver_id = Column("receiver_id", String, ForeignKey("users.id"), nullable=False)
    amount = Column("amount", Float, nullable=False)
    timestamp = Column("timestamp", DateTime, nullable=False, server_default=func.now())
    request_state = Column("request_state", Enum(RequestStates), nullable=True)
    is_offline = Column("is_offline", nullable=False, default=False)
