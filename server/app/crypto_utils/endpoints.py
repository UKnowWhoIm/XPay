"""
Routers for crypto_utils
"""
import base64
from fastapi import Response, Depends
from fastapi.routing import APIRouter
from app.auth.policies import get_current_user
from app.crypto_utils import ServerKeys
from app.crypto_utils.datamodels import UserKeys

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

@router.get("/key/generate/ledger-integrity-pair", dependencies=[Depends(get_current_user)])
def generate_ledger_integrity_keypair():
    """
    GET /key/generate/ledger-integrity-pair

    Generate a keypair for ensuring ledger integrity
    """
    return UserKeys.create_cert()
