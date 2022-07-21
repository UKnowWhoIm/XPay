"""
Datamodels for CryptoUtils like Keys
"""
from pydantic import BaseModel, validator
from app.crypto_utils import decrypt_private_key

class UserKeys(BaseModel):
    """
    Data model for user keys
    """
    public_key: bytes
    private_key: bytes

    @validator("private_key")
    # pylint: disable=fixme,unused-argument
    def decrypt_key(cls, value, **kwargs):
        """
        Decrypt private key for user
        """
        try:
            # TODO Find alternative
            # This is because this func is called twice
            return decrypt_private_key(value)
        except TypeError:
            return value

    class Config:
        """Config"""
        orm_mode = True
