"""
Database seeder
"""
from faker import Faker

from app.auth.datamodels import UserCreate
from app.auth.db_crud import db_create_user
from app.payments.db_crud import db_create_transaction
from app.payments.datamodels import TransactionCreate
from app.database.connection import SessionLocal
from app.payments.enums import TransactionTypes

fake = Faker()


def create_user(password=None) -> UserCreate:
    """
    Create a userdata with password as `password` if provided else a random string
    """
    data = UserCreate(
        name=fake.name(),
        password=fake.password(),
        phone_number=f"+{fake.random_int(min=10**9, max=10**14)}",
    )
    if password:
        data.password = password
    return data


def create_users(database, password=None, count=5):
    """
    Create `count` number of users
    """
    users = []
    for _ in range(count):
        users.append(db_create_user(database, create_user(password), False))
    database.commit()
    for user in users:
        database.refresh(user)
    return users


def recharge_users(database, users):
    """
    Recharge all users
    """
    for user in users:
        db_create_transaction(
            database,
            TransactionCreate(
                amount=fake.random_int(min=1000, max=10000),
                type=TransactionTypes.RECHARGE
            ),
            user.id,
            False
        )
    database.commit()


def main():
    """
    Seeder entrypoint
    """
    try:
        session = SessionLocal()
        users = create_users(session)
        recharge_users(session, users)
        return users
    finally:
        session.close()


if __name__ == "__main__":
    main()
