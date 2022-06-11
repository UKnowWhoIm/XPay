"""
Data models for response and requests
"""
from pydantic import BaseModel
from app.datamodels import Password, PhoneNumber


class UserCreate(PhoneNumber, Password):
    """
    Request datamodel for user sign up
    """
    name: str


class User(PhoneNumber):
    """
    Response datamodel for user
    """
    name: str
    id: str

    class Config:
        """Enable ORM mode"""
        orm_mode = True


class TokenData(BaseModel):
    """
    Response datamodel for token
    """
    access_token: str
    token_type: str = "Bearer"
