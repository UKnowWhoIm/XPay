"""
Tests for auth
"""
from faker import Faker
from fastapi.testclient import TestClient
from app.auth.db_crud import db_create_user, db_get_user_by_phone_number
from app.auth.utils import create_access_token, decode_token

from app.database.seed import create_user
from app.main import app

client = TestClient(app)

fake = Faker()


def valid_phone_number():
    """
    Returns a valid phone number
    """
    return f"+{fake.random_int(min=10**9, max=10**14)}"


def invalid_passwords():
    """
    Returns a list of `UserCreate.dict` with invalid passwords
    """
    return [
        # Short password
        {
            "phone_number": valid_phone_number(),
            "name": fake.name(),
            "password": fake.pystr(min_chars=1, max_chars=7)
        },
    ]


def invalid_phone_numbers(key="phone_number"):
    """
    Returns a list of `UserCreate.dict` with invalid phone numbers
    """
    invalid_numbers = [
        str(fake.random_int(min=10**9, max=10**14)),
        f"+{fake.random_int(min=0, max=10**8)}"
    ]
    return [
        {
            key: invalid,
            "name": fake.name(),
            "password": fake.password()
        }
        for invalid in invalid_numbers
    ]


def _create_request(url, data, is_url_encoded):
    """
    Creates a urlencoded or json request
    """
    if is_url_encoded:
        return client.post(url, data=data)
    return client.post(url, json=data)


def missing_data_checker(url, missing_data, is_url_encoded=False):
    """
    Test for missing fields yielding 422 status code
    """
    for [missing, data] in missing_data.items():
        req = _create_request(url, data, is_url_encoded)
        assert req.status_code == 422
        resp = req.json()
        assert resp["detail"][0]["type"] == "value_error.missing"
        assert resp["detail"][0]["loc"][-1] == missing


def valid_data_checker(url, valid_data, is_url_encoded=False):
    """
    Test for valid data
    """
    for data in valid_data:
        req = _create_request(url, data, is_url_encoded)
        assert 200 <= req.status_code <= 299


def invalid_data_checker(url, invalid_data, is_url_encoded=False):
    """
    Test for invalid data in serializer layer(yielding 422)
    """
    for [invalid, datas] in invalid_data.items():
        for data in datas:
            req = _create_request(url, data, is_url_encoded)
            assert req.status_code == 422
            resp = req.json()
            assert resp["detail"][0]["loc"][-1] == invalid


def test_create_user_endpoint(db_session):
    """
    TEST POST /auth/users

    Test invalid,missing fields
    Test unique phone number constraint
    """
    missing_data = {
        "phone_number": {
            "name": fake.name(),
            "password": fake.password(),
        },
        "password": {
            "phone_number": valid_phone_number(),
            "name": fake.name(),
        },
        "name": {
            "password": fake.password(),
            "phone_number": valid_phone_number(),
        }
    }
    invalid_data = {
        "phone_number": invalid_phone_numbers(),
        "password": invalid_passwords()
    }
    valid_data = [create_user().dict() for i in range(3)]
    url = "/auth/users"

    missing_data_checker(url, missing_data)
    invalid_data_checker(url, invalid_data)
    valid_data_checker(url, valid_data)

    for data in valid_data:
        assert db_get_user_by_phone_number(db_session, data["phone_number"]) is not None

    # Duplicate phone number
    req = client.post(url, json=valid_data[0])
    assert req.status_code == 409


def test_login(db_session):
    """
    TEST POST /auth/login

    Test missing fields
    Test invalid credentials
    Test JWT token decode/encode
    """
    password = fake.password()
    user = db_create_user(db_session, create_user(password))
    missing_data = {
        "username": {
            "password": fake.password(),
        },
        "password": {
            "username": valid_phone_number(),
        }
    }

    url = "/auth/login"

    missing_data_checker(url, missing_data, True)

    random_phone_num = valid_phone_number()
    while db_get_user_by_phone_number(db_session, random_phone_num) is not None:
        random_phone_num = valid_phone_number()
    req = client.post(
        url,
        data={"username": random_phone_num, "password": password},
    )
    assert req.status_code == 401

    random_password = fake.password()
    while user.password == random_password:
        random_password = fake.password()
    req = client.post(
        url,
        data={"username": user.phone_number, "password": random_password},
    )
    assert req.status_code == 401

    req = client.post(
        url,
        data={"username": user.phone_number, "password": password},
    )
    assert req.status_code == 200
    token = req.json()["access_token"]
    assert decode_token(token) == user.id


def test_me(db_session):
    """
    Test /auth/me

    Test Authorization
    """
    url = "/auth/me"
    req = client.get(url)
    assert req.status_code == 401

    user = db_create_user(db_session, create_user())
    token = create_access_token(user.id)
    req = client.get(url, headers={"Authorization": f"Bearer {token}"})
    assert req.status_code == 200
    assert req.json()["id"] == user.id
