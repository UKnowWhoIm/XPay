FROM python:3.9-alpine

RUN python -m pip install --upgrade pip

COPY pyproject.toml /app/

WORKDIR /app

ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1

RUN apk --no-cache add --virtual build-dependencies musl-dev build-base libffi-dev \
    && apk add postgresql-dev \
    && pip install poetry \
    && poetry config virtualenvs.create false \
    && poetry install  \
    && apk del build-dependencies

COPY . /app

RUN chmod +x ./entrypoint.sh && chmod +x ./lint.sh

CMD [ "./entrypoint.sh" ]