from datetime import timedelta, timezone, datetime
from fastapi import Request
from bezdarsql import select

from users.models import User

from passlib.context import CryptContext
from jose import jwt

pwd_context = CryptContext(schemes=['bcrypt'])


async def get_hash_password(password: str):
    return pwd_context.hash(password)


async def verify_password(password: str, hashed_password: str):
    return pwd_context.verify(password, hashed_password)


async def jwt_encode(data: dict):
    expire_date = datetime.now(timezone.utc) + timedelta(days=1)
    data.update({'exp': expire_date})
    return jwt.encode(data, key='hauptbahnhof', algorithm='HS256')


async def jwt_decode(token: str):
    data = jwt.decode(token, key='hauptbahnhof', algorithms='HS256')
    return data


async def get_current_user(request: Request):
    token = request.cookies.get('access_token')
    if token:
        data = await jwt_decode(token)
        return select(User, filter_by={User.id: data['uid']})[0]
    return None
