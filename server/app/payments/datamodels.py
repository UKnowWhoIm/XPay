"""
Request/Response datamodels for payments
"""
from datetime import datetime
from typing import Literal, Optional

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

    @classmethod
    def from_payment_request(cls, request):
        """
        Create a new object from payment request orm object
        """
        obj = cls.from_orm(request)
        obj.receiver_id = request.sender_id
        obj.type = TransactionTypes.TRANSFER
        return obj

    class Config:
        """Config"""
        orm_mode = True


class PaymentRequestResponse(BaseModel):
    """
    Request datamodel to handle sender's response to request to pay
    """
    id: str
    status: Literal[RequestStates.APPROVED, RequestStates.REJECTED]


class Transaction(TransactionCreate):
    """
    Response datamodel for transactions
    """
    id: str
    sender_id: Optional[str]
    timestamp: datetime
    request_state: Optional[RequestStates]

    class Config:
        """Config"""
        orm_mode = True
