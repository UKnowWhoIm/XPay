"""
Common utility functions
"""
from datetime import datetime
from uuid import uuid4
import base64

from app.crypto_utils.encryption_provider import EncryptionProvider

def uuid_to_string() -> str:
    """
    Create a random uuid and convert it to string
    """
    return str(uuid4())


def sign_balance(balance):
    """
    Create balance token
    """
    now = datetime.utcnow().isoformat()
    return {
        "amount": balance,
        "timestamp": now,
        "signature": base64.b64encode(
            EncryptionProvider.sign((f"{float(balance):.2f}{now}").encode("utf-8"))
        )
    }
