#!/bin/sh

if [[ "$DEBUG" = "True" ]]; then
    poetry run alembic upgrade head
    poetry run uvicorn app.main:app --reload --port ${PORT:-8000} --host 0.0.0.0
else
    poetry run uvicorn app.main:app --port ${PORT:-8000} --host 0.0.0.0
fi