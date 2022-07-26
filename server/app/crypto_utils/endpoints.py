"""
Routers for crypto_utils
"""
import base64
from fastapi import Response
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
    return Response(
        content=base64.b64encode(ServerKeys.serialized_public_key()),
        media_type="text/plain"
    )
