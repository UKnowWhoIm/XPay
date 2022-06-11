"""
Request/Response datamodels for payments
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, validator

from app.payments.enums import RequestStates, TransactionTypes


class TransactionCreate(BaseModel):
    """
    Request datamodel for transaction
    """
    receiver_id: Optional[str]
    amount: float
    type: TransactionTypes

    @validator("type")
    def _validate_type(cls, val, values):
        """
        Check if receiver_id is not None for TRANSFER and REQUEST types
        """
        if val != TransactionTypes.RECHARGE and values.get("receiver_id") is None:
            raise ValueError(f"receiver_id cannot be null for the type {val}")
        return val


class PaymentRequestResponse(BaseModel):
    """
    Request datamodel to handle sender's response to request to pay
    """
    id: str
    status: RequestStates


class Transaction(TransactionCreate):
    """
    Response datamodel for transactions
    """
    id: str
    sender_id: str
    timestamp: datetime
    request_state: str

    class Config:
        """Config"""
        orm_mode = True
