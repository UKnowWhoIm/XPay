"""
Database functions of payments
"""
from app.payments.db_models import Transaction
from app.payments.enums import RequestStates, TransactionTypes


def db_calculate_balance(database, user_id):
    """
    Calculate balance from transaction history
    """
    transactions = database.query(Transaction).filter(
        (Transaction.sender_id == user_id)
        | (Transaction.receiver_id == user_id)
    ).filter(Transaction.type != TransactionTypes.REQUEST).all()

    recieved = sum((
        transaction.amount
        for transaction in transactions
        if user_id == transaction.receiver_id
    ))

    sent = sum((
        transaction.amount
        for transaction in transactions
        if user_id == transaction.sender_id
    ))

    balance = recieved - sent

    return balance


def db_get_transaction_by_id(database, transaction_id):
    """
    Select transaction from db by pk
    """
    return database.query(Transaction).get(transaction_id)


def db_update_payment_request(transaction: Transaction, state):
    """
    Update status of payment request to APPROVED/REJECTED
    """
    if transaction.type == TransactionTypes.REQUEST and \
        transaction.request_state == RequestStates.PENDING:

        transaction.request_state = state
    else:
        raise ValueError("Not a valid request or request already processed")


def db_has_pending_requests(database, sender, receiver):
    """
    Checks if sender has already requested money from receiver which is still pending
    """
    return len(database.query(Transaction).filter(
        Transaction.receiver_id == receiver,
        Transaction.sender_id == sender,
        Transaction.request_state == RequestStates.PENDING
    ).all()) > 0


def db_create_transaction(database, data, current_user_id, commit=True):
    """
    Create a transaction record
    """
    transaction = Transaction(
        sender_id=current_user_id,
        **data.dict()
    )

    if transaction.type == TransactionTypes.RECHARGE:
        transaction.receiver_id = transaction.sender_id
        transaction.sender_id = None

    if transaction.type == TransactionTypes.REQUEST:
        transaction.request_state = RequestStates.PENDING

    database.add(transaction)
    if commit:
        database.commit()
        database.refresh(transaction)

    return transaction


def db_create_offline_transaction(database, data, commit = False):
    """
    Create an offline transaction record
    """
    database.add(Transaction(is_offline=True, **data.dict()))
    if commit:
        database.commit()


def db_list_transactions(database, transaction_ids = None, user_id = None, limit = 0, offset = 0):
    """
    List all transactions
    """

    query = database.query(Transaction)

    if user_id:
        query = query.filter(
            (Transaction.sender_id == user_id)
            | (Transaction.receiver_id == user_id)
        )

    if transaction_ids:
        query = query.filter(Transaction.id.in_(transaction_ids))

    query = query.order_by(Transaction.timestamp.desc())

    if limit:
        query = query.limit(limit)
    query = query.offset(offset)

    return query.all()
