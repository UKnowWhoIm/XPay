"""
Auth policies
"""
from fastapi import Depends, Request

from app.auth.utils import oauth2_scheme
from app.exceptions import NOT_AUTHENTICATED, PERMISSION_DENIED

def get_current_user(request: Request, _ = Depends(oauth2_scheme)):
    """
    Only allow authenticated users and return current user
    """
    if request.state.user is None:
        raise NOT_AUTHENTICATED
    return request.state.user


def no_auth(request: Request):
    """
    Only allow non authenticated users
    """
    if request.state.user is not None:
        raise PERMISSION_DENIED
