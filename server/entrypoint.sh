#!/bin/sh

if [[ "$DEBUG" = "True" ]]; then
    alembic upgrade head
    uvicorn app.main:app --reload --port ${PORT:-8000} --host 0.0.0.0
else
    uvicorn app.main:app --port ${PORT:-8000} --host 0.0.0.0
fi