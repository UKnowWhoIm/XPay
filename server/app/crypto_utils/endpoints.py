"""
Routers for crypto_utils
"""
from fastapi.routing import APIRouter
from app.crypto_utils import ServerKeys

router = APIRouter(
    prefix=""
)

@router.get("/key")
def get_server_public_key():
    """
    GET /key

    GET the server public key
    """
    return ServerKeys.serialized_public_key()