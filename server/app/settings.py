"""
Load all app settings from environment here
"""
from os import environ
from app import DEBUG as _debug

DEBUG = _debug

SECRET_KEY = environ["SECRET_KEY"]

ALGORITHM = "HS256"

# 1 week default
ACCESS_TOKEN_EXPIRE_MINUTES = int(environ.get("ACCESS_TOKEN_EXPIRY", 60 * 24 * 7))
