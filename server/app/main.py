"""
Entrypoint for the server
"""
from fastapi import FastAPI, Request

from starlette.middleware.cors import CORSMiddleware

from app.crypto_utils import load_server_keys
from app.database.connection import verify_postgres
from app.middleware import inject_user_to_request
from app.auth.endpoints import router as auth_router
from app.payments.endpoints import router as payments_router
from app.crypto_utils.endpoints import router as crypto_router

app = FastAPI()

app.add_event_handler("startup", verify_postgres)
app.add_event_handler("startup", load_server_keys)
app.include_router(auth_router)
app.include_router(payments_router)
app.include_router(crypto_router)

app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

@app.middleware("http")
async def inject_user(request: Request, call_next):
    """
    Middleware to inject user into request state
    """
    return await inject_user_to_request(request, call_next)

@app.get("/")
def hello_world():
    """Hello World Entrypoint"""
    return "Hello"
