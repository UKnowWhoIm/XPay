"""
HTTPExceptions defined in application
"""
from fastapi import HTTPException

PERMISSION_DENIED = HTTPException(
    status_code=403,
    detail="Permission denied"
)

NOT_AUTHENTICATED = HTTPException(
    status_code=401,
    detail="Not authenticated"
)
