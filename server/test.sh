#!/bin/sh

export DATABASE_URL="$DATABASE_URL"_test

alembic upgrade head

pytest app