"""
Encryption provider class used for signing and verifying
"""
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

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
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )


    @classmethod
    def verify(cls, data, signature, public_key=None):
        """
        Verify a message
        """
        if public_key is None:
            public_key = ServerKeys.public_key

        return public_key.verify(
            signature,
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
