"""
Datamodels for CryptoUtils like Keys
"""
import base64
from typing import Optional
from pydantic import BaseModel, validator
from app.crypto_utils import decrypt_private_key
from app.crypto_utils.encryption_provider import EncryptionProvider

class UserKeys(BaseModel):
    """
    Data model for user keys
    """
    public_key: bytes
    private_key: bytes
    public_key_signature: Optional[bytes]

    @validator("private_key")
    # pylint: disable=fixme,unused-argument
    def decrypt_key(cls, value, **kwargs):
        """
        Decrypt and enccode private key for user
        """
        return base64.b64encode(decrypt_private_key(value))

    @validator("public_key")
    # pylint: disable=fixme,unused-argument
    def encode_public_key(cls, value, **kwargs):
        """
        Encode public key for user
        """
        return base64.b64encode(value)

    @validator("public_key_signature", always=True, pre=True)
    # pylint: disable=fixme,unused-argument
    def create_public_key_signature(cls, value, values, **kwargs):
        """
        Create public key signature for user
        """
        return base64.b64encode(
            EncryptionProvider.sign(
                base64.b64decode(values.get("public_key"))
        ))

    class Config:
        """Config"""
        orm_mode = True
