"""
Router for payments

Prefix: /payments
"""

import json
import logging
from typing import List, Union, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import ValidationError

from app.auth.policies import get_current_user
from app.auth.db_crud import db_get_user_by_id, db_list_users
from app.crypto_utils import deserialize_public_key
from app.exceptions import PERMISSION_DENIED
from app.payments.datamodels import (
    OfflineEncryptedTransaction,
    PaymentRequestResponse,
    Transaction,
    TransactionCreate
)
from app.payments.db_crud import (
    db_calculate_balance,
    db_create_offline_transaction,
    db_create_transaction,
    db_get_transaction_by_id,
    db_has_pending_requests,
    db_list_transactions,
    db_update_payment_request
)
from app.database.dependency import get_db
from app.payments.enums import RequestStates, TransactionTypes
from app.crypto_utils.encryption_provider import EncryptionProvider
from app.settings import SERVER_RSA_KEY_SIZE, USER_RSA_KEY_SIZE
from app.utils import sign_balance

router = APIRouter(
    prefix="/payments"
)


@router.post("")
def create_payment(
    transaction: Union[TransactionCreate, PaymentRequestResponse],
    database = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    POST /payments

    Create a transaction, recharge or payment request
    """
    if isinstance(transaction, PaymentRequestResponse):
        transaction_in_db = db_get_transaction_by_id(database, transaction.id)

        if transaction_in_db.receiver_id != current_user.id:
            raise PERMISSION_DENIED

        try:
            db_update_payment_request(transaction_in_db, transaction.status)
            rollback = True
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        if transaction.status == RequestStates.REJECTED:
            database.commit()
            database.refresh(transaction_in_db)
            return transaction_in_db

        transaction = TransactionCreate.from_payment_request(transaction_in_db)
    else:
        rollback = False
    balance = db_calculate_balance(database, current_user.id)

    if transaction.type == TransactionTypes.TRANSFER:
        if balance < transaction.amount:
            if rollback:
                database.rollback()
            raise HTTPException(
                status_code=400,
                detail="Insufficent balance"
            )

    if transaction.receiver_id is not None:
        target_user = db_get_user_by_id(database, transaction.receiver_id)
        if target_user is None:
            raise HTTPException(
                status_code=400,
                detail="Receiver not found"
            )

    if transaction.type == TransactionTypes.REQUEST and \
        db_has_pending_requests(database, current_user.id, transaction.receiver_id):
        raise HTTPException(
            status_code=400,
            detail="Too many pending requests, unable to create a new one"
        )

    transaction = Transaction.from_orm(
        db_create_transaction(database, transaction, current_user.id)
    )
    new_balance = balance - transaction.amount if current_user.id == transaction.sender_id\
                else balance + transaction.amount
    return {
        **sign_balance(new_balance),
        "transaction": transaction.dict(),
    }


@router.get("", response_model=List[Transaction])
def list_all_transactions(
    current_user = Depends(get_current_user),
    database = Depends(get_db),
    limit: Optional[int] = 0,
    offset: Optional[int] = 0
):
    """
    GET /payments

    List all transactions involving the authenticated user
    """
    return db_list_transactions(database, user_id=current_user.id, limit=limit, offset=offset)


@router.post("/offline", status_code=201)
async def sync_offline_payments(
    request: Request,
    database = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    POST /payments/offline

    Sync offline transactions
    """
    ledger_modified_error = HTTPException(
        status_code=403,
        detail="Ledger has been modified by unauthorized entities"
    )
    transactions = []
    transaction_ids = []
    user_ids = set()
    raw_transactions = await request.body()
    try:
        user_signature_size = USER_RSA_KEY_SIZE // 8
        server_signature_size = SERVER_RSA_KEY_SIZE // 8
        public_key_trailer = b"-----END PUBLIC KEY-----\n"
        ledger_seperator = b"-----LEDGER SERPERATOR-----\n"
        for raw_transaction in raw_transactions.split(ledger_seperator):
            signature = raw_transaction[:user_signature_size]
            public_key_signature = raw_transaction[
                user_signature_size
                :user_signature_size + server_signature_size
            ]

            start_index = user_signature_size + server_signature_size
            [public_key, raw_data] = raw_transaction[start_index:].split(public_key_trailer)
            public_key += public_key_trailer
            data = json.loads(raw_data)
            transactions.append(
                OfflineEncryptedTransaction(
                    signature=signature,
                    public_key=public_key,
                    public_key_signature=public_key_signature,
                    raw_data=raw_data,
                    **data
                )
            )

    except (json.JSONDecodeError, ValidationError, IndexError) as exc:
        raise ledger_modified_error from exc

    for transaction in transactions:
        try:
            # User has to be either receiver or sender
            if current_user.id not in (transaction.receiver_id, transaction.sender_id):
                raise ledger_modified_error

            if transaction.receiver_id == current_user.id:
                user_ids.update({transaction.sender_id,})
            else:
                user_ids.update({transaction.receiver_id,})

            # Public key cannot be user's
            if current_user.keys.public_key == transaction.public_key:
                raise ledger_modified_error

            # Verify user public key integrity
            if not EncryptionProvider.verify(
                transaction.public_key,
                transaction.public_key_signature
            ):
                raise ledger_modified_error

            # Verify data integrity
            if not EncryptionProvider.verify(
                transaction.raw_data,
                transaction.signature,
                deserialize_public_key(transaction.public_key)
            ):
                raise ledger_modified_error
            transaction_ids.append(transaction.id)
        except ValueError as exc:
            raise ledger_modified_error from exc

    processed_transactions = [
        transaction.id for transaction in
        db_list_transactions(database, transaction_ids)
    ]
    users = db_list_users(database, user_ids)

    if len(users) != len(user_ids):
        raise ledger_modified_error

    new_transactions = list(filter(
        lambda transaction: transaction.id not in processed_transactions, transactions
    ))
    logging.debug([transaction.id for transaction in new_transactions])
    for transaction in new_transactions:
        db_create_offline_transaction(database, Transaction.from_offline_transaction(transaction))
    database.commit()

    return {
        "count": len(new_transactions),
        **sign_balance(db_calculate_balance(database, current_user.id))
    }
