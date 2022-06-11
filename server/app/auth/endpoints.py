"""
Endpoints for authorization and user management

Prefix: /auth
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.auth.datamodels import TokenData, UserCreate, User
from app.auth.policies import get_current_user, no_auth
from app.auth.db_crud import db_create_user, db_get_user_by_phone_number
from app.auth.utils import create_access_token, verify_password
from app.database.dependency import get_db
from app.payments.db_crud import db_calculate_balance


router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)


@router.post("/users", dependencies=[Depends(no_auth)], response_model=User)
def create_user(new_user: UserCreate, database = Depends(get_db)):
    """
    POST /auth/users

    Create a new user

    raises 409 if phone number is already used

    raises 403 if authenticated
    """
    try:
        return User.from_orm(db_create_user(database, new_user))
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/login", dependencies=[Depends(no_auth)])
def login(data: OAuth2PasswordRequestForm = Depends(), database = Depends(get_db)):
    """
    POST /auth/login

    Get access token for user by entering username and password

    raises 403 if authenticated

    raises 401 if username, password wrong
    """
    user_in_db = db_get_user_by_phone_number(database, data.username)
    if user_in_db is not None:
        if verify_password(data.password, user_in_db.password):
            return TokenData(access_token=create_access_token(user_in_db.id))
    raise HTTPException(
        status_code=401,
        detail="Not Authenticated"
    )


@router.get("/me", response_model=User)
def get_me(database = Depends(get_db), current_user = Depends(get_current_user)):
    """
    GET /auth/me

    Get details of currently authenticated user
    """
    user = User.from_orm(current_user)
    user.balance = db_calculate_balance(database, current_user.id)
    return user
