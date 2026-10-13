import hashlib
import hmac
import json
import time
from urllib.parse import urlencode

import pytest

from app.core.security import InitDataError, validate_init_data

TOKEN = "123:TEST"


def make_init_data(auth_date: int, token: str = TOKEN, user_id: int = 42) -> str:
    fields = {"auth_date": str(auth_date), "user": json.dumps({"id": user_id, "first_name": "Ali"})}
    check = "\n".join(f"{k}={v}" for k, v in sorted(fields.items()))
    secret = hmac.new(b"WebAppData", token.encode(), hashlib.sha256).digest()
    fields["hash"] = hmac.new(secret, check.encode(), hashlib.sha256).hexdigest()
    return urlencode(fields)


def test_valid_init_data():
    user = validate_init_data(make_init_data(int(time.time())), TOKEN, 3600)
    assert user["id"] == 42


def test_tampered_signature_rejected():
    data = make_init_data(int(time.time())).replace("Ali", "Eve")
    with pytest.raises(InitDataError):
        validate_init_data(data, TOKEN, 3600)


def test_wrong_token_rejected():
    with pytest.raises(InitDataError):
        validate_init_data(make_init_data(int(time.time()), token="other"), TOKEN, 3600)


def test_expired_rejected():
    with pytest.raises(InitDataError):
        validate_init_data(make_init_data(int(time.time()) - 7200), TOKEN, 3600)
