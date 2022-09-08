#!/bin/sh

if [[ "$DEBUG" = "True" ]]; then
    alembic upgrade head
    uvicorn app.main:app --root-path ${BASE_PATH:-""} --port ${PORT:-8000} --host 0.0.0.0 --reload 
else
    uvicorn app.main:app --root-path ${BASE_PATH:-""} --port ${PORT:-8000} --host 0.0.0.0
fi