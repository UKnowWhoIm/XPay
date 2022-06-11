# XPay - Offline Payments

## Prerequisites

- docker and docker-compose

## Installation

- Setup pylint pre-commit hook by running `./pre_commit.sh`

- `docker-compose up -d` && goto http://localhost:6969 after its done


### Installing New Dependencies

- Add the dependency and its version constraint to server/pyproject.toml in `tool.poetry.dependencies` or `tool.poetry.dev-dependencies` section and run `docker-compose build`

- You can also install by running the command `poetry add <name>` command inside the container. But many external libraries won't be present in the container so it may fail

### Adding new revisions in alembic

- `docker-compose run server alembic revision -m "<revision_name">`

### Migrating or Downgrading Database

- `docker-compose run server alembic upgrade HEAD`

- `docker-compose run server alembic downgrade -<number_of revisions to be downgraded>`
