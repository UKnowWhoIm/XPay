"""
Common datamodels
"""
from pydantic import BaseModel, constr


class PhoneNumber(BaseModel):
    """
    Phone number field with regex check
    """
    phone_number: constr(regex=r"^\+\d{10,15}$")


class Password(BaseModel):
    """
    Password field with regex check
    """
    password: constr(min_length=8)
