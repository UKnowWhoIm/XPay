"""
Auth policies
"""
from fastapi import Depends, HTTPException, Request

from app.auth.utils import oauth2_scheme

def get_current_user(request: Request, _ = Depends(oauth2_scheme)):
    """
    Only allow authenticated users and return current user
    """
    if request.state.user is None:
        raise HTTPException(
            status_code=401,
            detail="Not Authenticated"
        )
    return request.state.user


def no_auth(request: Request):
    """
    Only allow non authenticated users
    """
    if request.state.user is not None:
        raise HTTPException(
            status_code=403,
            detail="Permission Denied"
        )
