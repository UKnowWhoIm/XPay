"""
Entrypoint for the server
"""
from fastapi import FastAPI, Request

from app.database.connection import verify_postgres
from app.middleware import inject_user_to_request
from app.auth.endpoints import router as auth_router
from app.payments.endpoints import router as payments_router

app = FastAPI()

app.add_event_handler("startup", verify_postgres)
app.include_router(auth_router)
app.include_router(payments_router)

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
