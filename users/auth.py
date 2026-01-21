from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'])


async def get_hash_password(password: str):
    return pwd_context.hash(password)
