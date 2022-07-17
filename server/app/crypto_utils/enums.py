"""
Crypto Enums
"""
from enum import Enum

class KeyStatus(str, Enum):
    """
    KeyStates enum

    If key rotation is to be implemented
    """
    ACTIVE = "ACTIVE"
    DEPRECATED = "DEPRECATED"
    DISABLED = "DISABLED"
    DELETED = "DELETED"
