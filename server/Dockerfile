FROM python:3.9-alpine

RUN python -m pip install --upgrade pip

COPY pyproject.toml /app/

WORKDIR /app

RUN apk --no-cache add --virtual build-dependencies build-base musl-dev postgresql-dev libffi-dev \
    && pip install poetry &&  poetry install  \
    && apk del build-dependencies

COPY . /app

RUN chmod +x ./entrypoint.sh && chmod +x ./lint.sh

CMD [ "./entrypoint.sh" ]