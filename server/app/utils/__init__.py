"""
Common utility functions
"""
from uuid import uuid4

def uuid_to_string() -> str:
    """
    Create a random uuid and convert it to string
    """
    return str(uuid4())
