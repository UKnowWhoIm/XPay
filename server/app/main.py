"""
Entrypoint for the server
"""
from fastapi import FastAPI

from app.database.connection import verify_postgres

app = FastAPI()

app.add_event_handler("startup", verify_postgres)

@app.get("/")
def hello_world():
    """Hello World Entrypoint"""
    return "Hello"
