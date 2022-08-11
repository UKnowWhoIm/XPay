"""
Tests for payments
"""
from datetime import datetime
import json
from random import sample, choice

from fastapi.testclient import TestClient
from faker import Faker

from app.auth.utils import create_access_token
from app.conftest import get_auth_header
from app.crypto_utils import deserialize_private_key, load_server_keys
from app.crypto_utils.encryption_provider import EncryptionProvider
from app.database.seed import create_users
from app.main import app
from app.payments.db_crud import (
    db_calculate_balance,
    db_create_transaction,
    db_get_transaction_by_id
)
from app.payments.datamodels import PaymentRequestResponse, TransactionCreate
from app.payments.enums import RequestStates, TransactionTypes
from app.utils import uuid_to_string


client = TestClient(app)

fake = Faker()

def test_create_transaction(db_session):
    """
    TEST POST /payments

    Test insufficent balance for transfer, request
    Test invalid/missing receiver for transfer, request
    Test recharge
    Test permission denied for request
    Test multiple pending requests for request
    Test approve/reject request
    Test approve/reject transfer and processed request
    """
    url = "/payments"
    users = create_users(db_session)

    # No Balance transfers will fail
    for _ in range(3):
        [sender, receiver] = sample(users, 2)
        data = TransactionCreate(
            receiver_id=receiver.id,
            type=TransactionTypes.TRANSFER,
            amount=fake.random_int(min=100, max=10000)
        ).dict()
        token = create_access_token(sender.id)
        req = client.post(url, json=data, headers={"Authorization": f"Bearer {token}"})
        assert req.status_code == 400

    for user in users:
        amount = fake.random_int(min=1000, max=10000)
        data = TransactionCreate(
            type=TransactionTypes.RECHARGE,
            amount=amount
        ).dict()
        req = client.post(url, json=data, headers=get_auth_header(user))
        assert req.status_code == 200
        assert db_calculate_balance(db_session, user.id) == amount

    # Invalid receiver
    data = TransactionCreate(
        receiver_id=str(fake.random_int(min=1000, max=10**7)),
        type=TransactionTypes.TRANSFER,
        amount=fake.random_int(min=10, max=100)
    ).dict()
    req = client.post(url, json=data, headers=get_auth_header(choice(users)))
    assert req.status_code == 400

    # Missing receiver for transfer
    data.pop("receiver_id")
    req = client.post(url, json=data, headers=get_auth_header(choice(users)))
    assert req.status_code == 422

    # Missing receiver for request
    data["type"] = TransactionTypes.REQUEST
    req = client.post(url, json=data, headers=get_auth_header(choice(users)))
    assert req.status_code == 422

    for _ in range(3):
        # Insufficent balance
        [sender, receiver] = sample(users, 2)
        old_balance_sender = db_calculate_balance(db_session, sender.id)
        old_balance_receiver = db_calculate_balance(db_session, receiver.id)
        data = TransactionCreate(
            receiver_id=receiver.id,
            type=TransactionTypes.TRANSFER,
            amount=old_balance_sender + 1
        ).dict()
        req = client.post(url, json=data, headers=get_auth_header(sender))
        assert req.status_code == 400

        # Successful transfer
        data["amount"] = fake.random_int(
            min=max(old_balance_receiver//1000, 1),
            max=old_balance_receiver//10
        )
        req = client.post(url, json=data, headers=get_auth_header(sender))
        transaction_id = req.json()["transaction"]["id"]
        assert req.status_code == 200
        new_balance_sender = db_calculate_balance(db_session, sender.id)
        new_balance_receiver = db_calculate_balance(db_session, receiver.id)
        assert new_balance_sender == old_balance_sender - data["amount"]
        assert new_balance_receiver == old_balance_receiver + data["amount"]

        # Transfer transactions cannot be APPROVED/REJECTED like requests
        data = PaymentRequestResponse(
            id=transaction_id,
            status=RequestStates.APPROVED
        ).dict()
        req = client.post(url, json=data, headers=get_auth_header(receiver))
        assert req.status_code == 400

        old_balance_receiver = db_calculate_balance(db_session, receiver.id)
        old_balance_sender =  db_calculate_balance(db_session, sender.id)
        data = TransactionCreate(
            receiver_id=receiver.id,
            type=TransactionTypes.REQUEST,
            amount=fake.random_int(
                min=max(old_balance_receiver//1000, 1),
                max=old_balance_receiver//10
            )
        ).dict()
        req = client.post(url, json=data, headers=get_auth_header(sender))
        assert req.status_code == 200
        resp = req.json()
        assert resp["transaction"]["request_state"] == RequestStates.PENDING
        transaction_id = resp["transaction"]["id"]

        # No new request with this user until pending request is processed
        req = client.post(url, json=data, headers=get_auth_header(sender))
        assert req.status_code == 400

        # status can't be updated as PENDING, only APPROVED/REJECTED
        data = {"id": transaction_id, "status": RequestStates.PENDING}
        req = client.post(url, json=data, headers=get_auth_header(receiver))
        assert req.status_code == 422

        # User has to be the receiver of request to APPROVE/REJECT it
        data = PaymentRequestResponse(
            id=transaction_id,
            status=RequestStates.APPROVED
        ).dict()
        # pylint:disable=cell-var-from-loop
        rand_user = choice(list(filter(lambda x: x.id != receiver.id, users)))
        req = client.post(url, json=data, headers=get_auth_header(rand_user))
        assert req.status_code == 403

        # Successful approval
        req = client.post(url, json=data, headers=get_auth_header(receiver))
        transaction = db_get_transaction_by_id(db_session, transaction_id)
        assert req.status_code == 200
        assert transaction.request_state == RequestStates.APPROVED
        assert db_calculate_balance(db_session, receiver.id) == \
            old_balance_receiver - transaction.amount
        assert db_calculate_balance(db_session, sender.id) == \
            old_balance_sender + transaction.amount

        # Completed request can't be modified
        req = client.post(url, json=data, headers=get_auth_header(receiver))
        assert req.status_code == 400

        # Insufficent balance while approving request
        old_balance_receiver = db_calculate_balance(db_session, receiver.id)
        old_balance_sender = db_calculate_balance(db_session, sender.id)
        data = TransactionCreate(
            receiver_id=receiver.id,
            type=TransactionTypes.REQUEST,
            amount=old_balance_receiver + 1
        ).dict()
        req = client.post(url, json=data, headers=get_auth_header(sender))
        transaction_id = req.json()["transaction"]["id"]
        assert req.status_code == 200
        data = PaymentRequestResponse(id=transaction_id, status=RequestStates.APPROVED).dict()
        req = client.post(url, json=data, headers=get_auth_header(receiver))
        assert req.status_code == 400
        assert old_balance_sender == db_calculate_balance(db_session, sender.id)
        assert old_balance_receiver == db_calculate_balance(db_session, receiver.id)

        # Reject request
        data = PaymentRequestResponse(id=transaction_id, status=RequestStates.REJECTED).dict()
        req = client.post(url, json=data, headers=get_auth_header(receiver))
        assert req.status_code == 200
        assert old_balance_sender == db_calculate_balance(db_session, sender.id)
        assert old_balance_receiver == db_calculate_balance(db_session, receiver.id)

        # Can't reject a rejected request
        req = client.post(url, json=data, headers=get_auth_header(receiver))
        assert req.status_code == 400


def create_user_ledger_entry(user, data):
    """
    Creation of user's ledger
    """
    raw_data = json.dumps(data).encode("utf-8")
    public_bytes = user.keys.public_key
    public_signature = EncryptionProvider.sign(public_bytes)
    data_signature = EncryptionProvider.sign(
        raw_data,
        deserialize_private_key(user.keys.private_key)
    )

    return data_signature + public_signature + public_bytes + raw_data


def create_ledger_entry(sender, receiver, amount):
    """
    Creation and configuration of both sender's and receiver's ledger
    """
    timestamp = datetime.utcnow().timestamp()
    data = {
        "sender_id": sender.id,
        "receiver_id": receiver.id,
        "amount": amount,
        "timestamp": timestamp,
        "id": uuid_to_string()[:-10] + str(int(timestamp))
    }
    return create_user_ledger_entry(receiver, data), create_user_ledger_entry(sender, data)


def test_offline_payments(db_session):
    """
    TEST POST /payments/offline

    TODO Write fail cases too
    """
    users = create_users(db_session)
    url = "/payments/offline"
    load_server_keys()
    ledger_seperator = b"-----LEDGER SERPERATOR-----\n"

    # Recharge all users
    for user in users:
        data = TransactionCreate(
            amount=fake.random_int(min=5000, max=10000),
            type=TransactionTypes.RECHARGE
        )
        db_create_transaction(db_session, data, user.id, False)
    db_session.commit()

    user_ledgers = {user.id: b"" for user in users}
    user_balances = {user.id: db_calculate_balance(db_session, user.id) for user in users}

    for _ in range(10):
        [sender, receiver] = sample(users, 2)
        if user_balances[sender.id] < 10:
            continue
        amount = fake.random_int(min=1, max=user_balances[sender.id] // 10)
        sender_ledger, receiver_ledger = create_ledger_entry(sender, receiver, amount)
        user_ledgers[sender.id] += sender_ledger + ledger_seperator
        user_ledgers[receiver.id] += receiver_ledger + ledger_seperator
        user_balances[sender.id] -= amount
        user_balances[receiver.id] += amount

    for user_id, ledger in user_ledgers.items():
        if len(ledger) == 0:
            continue
        # skip last seperator
        ledger = ledger_seperator.join(ledger.split(ledger_seperator)[:-1])
        # pylint: disable=cell-var-from-loop
        headers = get_auth_header(next(filter(lambda user: user.id == user_id, users)))
        headers["Content-Type"] = "application/octet-stream"
        req = client.post(url, data=ledger, headers=headers)
        assert req.status_code == 201
        assert db_calculate_balance(db_session, user_id) == user_balances[user_id]
