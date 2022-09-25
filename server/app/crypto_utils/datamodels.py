"""
Datamodels for CryptoUtils like Keys
"""
import base64
from typing import Optional
from pydantic import BaseModel, validator
from app.crypto_utils import (
    create_private_key,
    create_pub_key_certificate,
    create_user_key_pair,
    decrypt_private_key,
    serialize_private_key,
    serialize_public_key
)
from app.crypto_utils.encryption_provider import EncryptionProvider

class UserKeys(BaseModel):
    """
    Data model for user keys
    """
    public_key: bytes
    private_key: bytes
    public_key_signature: Optional[bytes]
    certificate: Optional[bytes]

    @validator("private_key")
    # pylint: disable=fixme,unused-argument
    def decrypt_key(cls, value, **kwargs):
        """
        Decrypt and enccode private key for user
        """
        return base64.b64encode(decrypt_private_key(value))

    @validator("public_key", "certificate")
    # pylint: disable=fixme,unused-argument
    def encode_public_key(cls, value, **kwargs):
        """
        Encode public key for user
        """
        if value:
            return base64.b64encode(value)
        return None

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

    @classmethod
    def create_key_pair(cls):
        """
        Create a key pair for the user and return as `UserKeys` object
        """
        private_key, public_key = create_user_key_pair()
        keys = cls(private_key=private_key, public_key=public_key)
        return cls.validate(keys)

    @classmethod
    def create_cert(cls):
        """
        Create a certificate for the keypair and return as `UserKeys` object
        """
        private_key = create_private_key()
        public_key = private_key.public_key()
        public_cert = create_pub_key_certificate(public_key)
        keys = cls(
            private_key=serialize_private_key(private_key),
            public_key=serialize_public_key(public_key),
            certificate=public_cert
        )
        return cls.validate(keys)

    class Config:
        """Config"""
        orm_mode = True
