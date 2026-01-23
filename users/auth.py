import asyncio
from datetime import timedelta, timezone, datetime
from passlib.context import CryptContext
from jose import jwt

pwd_context = CryptContext(schemes=['bcrypt'])


async def get_hash_password(password: str):
    return pwd_context.hash(password)


async def jwt_encode(data: dict):
    expire_date = datetime.now(timezone.utc) + timedelta(days=1)
    data.update({'exp': expire_date})
    return jwt.encode(data, key='hauptbahnhof', algorithm='HS256')


async def jwt_decode(token: str):
    data = jwt.decode(token, key='hauptbahnhof', algorithms='HS256')
    return data
