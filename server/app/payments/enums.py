"""
Enums of payment module
"""
from enum import Enum


class TransactionTypes(str, Enum):
    """
    Transaction types for payments
    """
    RECHARGE = "RECHARGE"
    TRANSFER = "TRANSFER"
    REQUEST = "REQUEST"


class RequestStates(str, Enum):
    """
    States of payment request
    """
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
