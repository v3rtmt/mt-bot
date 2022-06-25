from os import getenv
from jwt import encode, decode, exceptions
from datetime import datetime, timedelta
from flask import jsonify

def expire_token(days: int):
    now = datetime.now()
    new_date = now + timedelta(days)
    return new_date

def create_token(data: dict):
    token = encode(payload={**data, "exp": expire_token(2)}, key=getenv("SECRET"), algorithm="HS256")
    return token.encode("UTF-8")

def validate_token(token, output=False):
    try:
        if output:
            return decode(token, key=getenv("SECRET"), algorithms=["256"])
        decode(token, key=getenv("SECRET"), algorithms=["256"])

    except exceptions.DecodeError:
        response = jsonify({"message": "Invalid Token"})
        response.status_code = 401
        return response

    except exceptions.ExpiredSignatureError:
        response = jsonify({"message": "Expired Token"})
        response.status_code = 401
        return response