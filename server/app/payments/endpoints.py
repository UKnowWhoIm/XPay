"""
Router for payments

Prefix: /payments
"""
import logging
from typing import List, Union, Optional
from fastapi import APIRouter, Depends, HTTPException

from app.auth.policies import get_current_user
from app.auth.db_crud import db_get_user_by_id
from app.exceptions import PERMISSION_DENIED
from app.payments.datamodels import PaymentRequestResponse, Transaction, TransactionCreate
from app.payments.db_crud import (
    db_calculate_balance,
    db_create_transaction,
    db_get_transaction_by_id,
    db_has_pending_requests,
    db_list_transactions,
    db_update_payment_request
)
from app.database.dependency import get_db
from app.payments.enums import RequestStates, TransactionTypes

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
            raise HTTPException(status_code=409, detail=str(exc)) from exc

        if transaction.status == RequestStates.REJECTED:
            database.commit(transaction_in_db)
            database.refresh(transaction_in_db)
            return transaction_in_db

        transaction = TransactionCreate.from_payment_request(transaction_in_db)
    else:
        rollback = False

    if transaction.type == TransactionTypes.TRANSFER:
        balance = db_calculate_balance(database, current_user.id)
        logging.info(balance)
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
    return db_list_transactions(database, current_user.id, limit, offset)
