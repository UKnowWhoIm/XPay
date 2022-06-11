"""
Router for payments

Prefix: /payments
"""
from typing import Union
from fastapi import APIRouter, Depends, HTTPException

from app.auth.policies import get_current_user
from app.auth.db_crud import db_get_user_by_id
from app.payments.datamodels import PaymentRequestResponse, Transaction, TransactionCreate
from app.payments.db_crud import (
    db_calculate_balance,
    db_create_transaction,
    db_get_transaction_by_id,
    db_has_pending_requests,
    db_update_payment_request
)
from app.database.dependency import get_db
from app.payments.enums import TransactionTypes

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
        if transaction_in_db.receiver_id != current_user.id \
            or transaction_in_db.type != TransactionTypes.TRANSFER:
            raise HTTPException(
                detail="Permission denied",
                status_code=403
            )
        rollback = True
        db_update_payment_request(transaction_in_db, transaction.status)
        transaction = Transaction.from_orm(transaction_in_db)
    else:
        rollback = False

    if transaction.type != TransactionTypes.RECHARGE:
        balance = db_calculate_balance(database, current_user.id)
        if balance < transaction.amount:
            if rollback:
                database.rollback()
            raise HTTPException(
                status_code=400,
                detail="Insufficent balance"
            )

    if transaction.receiver_id:
        target_user = db_get_user_by_id(database, transaction.receiver_id) is None
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

    return db_create_transaction(database, transaction, current_user.id)
