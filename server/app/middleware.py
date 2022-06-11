"""
Middleware for the application
"""
from fastapi import Request
from app.auth.db_crud import db_get_user_by_id

from app.database.connection import SessionLocal
from app.auth.utils import decode_token


async def inject_user_to_request(request: Request, call_next):
    """
    Inject user if authenticated to request
    """
    try:
        token = request.headers.get("Authorization", "").split(" ")[1]
        user_id = decode_token(token)
        if user_id is None:
            request.state.user = None
        else:
            try:
                database = SessionLocal()
                request.state.user = db_get_user_by_id(database, user_id)
            finally:
                database.close()

    except IndexError:
        request.state.user = None

    return await call_next(request)
