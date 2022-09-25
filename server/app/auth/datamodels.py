"""
Data models for response and requests
"""
from typing import Optional

from pydantic import BaseModel

from app.datamodels import Password, PhoneNumber
from app.crypto_utils.datamodels import UserKeys
from app.utils import sign_balance


class UserCreate(PhoneNumber, Password):
    """
    Request datamodel for user sign up
    """
    name: str

class TokenData(BaseModel):
    """
    Response datamodel for token
    """
    access_token: str
    token_type: str = "Bearer"


class User(PhoneNumber):
    """
    Response datamodel for user
    """
    name: str
    id: str
    balance: Optional[dict]
    keys: UserKeys
    access_token: Optional[TokenData]

    def set_balance(self, amount):
        """
        Set balance and signature
        """
        self.balance = sign_balance(amount)

    class Config:
        """Enable ORM mode"""
        orm_mode = True
