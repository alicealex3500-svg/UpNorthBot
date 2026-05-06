import secrets
from datetime import datetime, timedelta

def make_order_code() -> str:
    return 'FXH-' + secrets.token_hex(5).upper()

def make_license_key() -> str:
    return 'FXH-LIC-' + secrets.token_hex(12).upper()

def next_expiry(days: int = 30):
    return datetime.utcnow() + timedelta(days=days)
