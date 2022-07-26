"""
Encryption provider class used for signing and verifying
"""
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature

from app.crypto_utils import ServerKeys

class EncryptionProvider:
    """
    Encryption provider class
    """
    @classmethod
    def sign(cls, data, private_key=None):
        """
        Sign a message
        """
        if private_key is None:
            private_key = ServerKeys.private_key
        return private_key.sign(
            data,
            padding.PKCS1v15(),
            hashes.SHA256()
        )


    @classmethod
    def verify(cls, data, signature, public_key=None):
        """
        Verify a message
        """
        if public_key is None:
            public_key = ServerKeys.public_key
        try:
            public_key.verify(
                signature,
                data,
                padding.PKCS1v15(),
                hashes.SHA256()
            )
            return True
        except InvalidSignature:
            return False

    @classmethod
    def encrypt(cls, data, public_key=None):
        """
        Encrypt a message

        :raises ValueError if message is too long:
        """
        if public_key is None:
            public_key = ServerKeys.public_key
        return public_key.encrypt(
            data,
            padding.PKCS1v15()
        )

    @classmethod
    def decrypt(cls, data, private_key=None):
        """
        Decrypt a message

        :raises ValueError: if the message is invalid
        """
        if private_key is None:
            private_key = ServerKeys.private_key

        return private_key.decrypt(
            data,
            padding.PKCS1v15()
        )
